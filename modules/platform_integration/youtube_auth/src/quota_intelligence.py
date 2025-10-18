"""
Quota Intelligence System
WSP-Compliant: Intelligent quota monitoring with pre-call checking and preservation

This module provides smart quota management to prevent wasteful consumption
and ensure optimal usage across all credential sets.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from .quota_monitor import QuotaMonitor

logger = logging.getLogger(__name__)


class QuotaIntelligence:
    """
    Intelligent quota management system with pre-call checking and optimization.
    
    Features:
    - Pre-call quota verification
    - Smart operation planning
    - Quota preservation strategies
    - Usage prediction and optimization
    - Emergency quota protection
    """
    
    def __init__(self, quota_monitor: QuotaMonitor):
        """Initialize quota intelligence system."""
        self.quota_monitor = quota_monitor
        
        # Emergency reserve (keep 5% quota for critical operations)
        self.emergency_reserve_percent = 0.05
        
        # High-cost operation thresholds
        self.high_cost_threshold = 50  # Operations costing 50+ units
        self.batch_size_limit = 10     # Max operations in single batch
        
        # Priority levels for different operations
        self.operation_priorities = {
            # Critical operations (always allowed if any quota exists)
            'channels.list': 'critical',
            'videos.list': 'critical',
            
            # High priority (live chat monitoring and stream detection)
            'liveChatMessages.list': 'high',
            'liveStreams.list': 'high',
            'liveBroadcasts.list': 'high',
            'search.list': 'high',  # Essential for finding streams - moved from low

            # Medium priority (posting/interaction)
            'liveChatMessages.insert': 'medium',
            'comments.insert': 'medium',
            
            # Administrative (moderation)
            'liveChatBans.insert': 'admin',
            'liveChatBans.delete': 'admin',
        }
    
    def can_perform_operation(self, operation: str, credential_set: int, 
                            count: int = 1, force: bool = False) -> Dict:
        """
        Check if operation can be performed without risking quota exhaustion.
        
        Args:
            operation: YouTube API operation (e.g., 'liveChatMessages.list')
            credential_set: Which credential set to check
            count: Number of operations to perform
            force: Override intelligent protection (emergency use only)
            
        Returns:
            Dict with 'allowed', 'reason', 'suggestion', 'cost', 'remaining_after'
        """
        # Get operation cost
        cost_per_op = self.quota_monitor.QUOTA_COSTS.get(operation, 1)
        total_cost = cost_per_op * count
        
        # Get current usage
        summary = self.quota_monitor.get_usage_summary()
        set_info = summary['sets'].get(credential_set, {})
        
        if not set_info:
            return {
                'allowed': False,
                'reason': f'Credential set {credential_set} not configured',
                'suggestion': 'Use configured credential sets (1 or 10)',
                'cost': total_cost,
                'remaining_after': 0
            }
        
        available = set_info['available']
        limit = set_info['limit']
        current_usage_percent = set_info['usage_percent'] / 100
        
        # Calculate emergency reserve
        emergency_reserve = int(limit * self.emergency_reserve_percent)
        safe_available = max(0, available - emergency_reserve)
        
        # Emergency override
        if force:
            if available >= total_cost:
                return {
                    'allowed': True,
                    'reason': 'Emergency override - quota available',
                    'suggestion': 'Monitor usage closely',
                    'cost': total_cost,
                    'remaining_after': available - total_cost
                }
            else:
                return {
                    'allowed': False,
                    'reason': 'Emergency override failed - insufficient quota',
                    'suggestion': 'Wait for quota reset or use different credential set',
                    'cost': total_cost,
                    'remaining_after': 0
                }
        
        # Check basic availability
        if available < total_cost:
            return {
                'allowed': False,
                'reason': f'Insufficient quota: need {total_cost}, have {available}',
                'suggestion': self._get_quota_suggestion(credential_set, total_cost),
                'cost': total_cost,
                'remaining_after': available
            }
        
        # Check emergency reserve protection
        if safe_available < total_cost:
            # Allow critical operations even into emergency reserve
            priority = self.operation_priorities.get(operation, 'medium')
            if priority == 'critical':
                return {
                    'allowed': True,
                    'reason': 'Critical operation - using emergency reserve',
                    'suggestion': 'Monitor quota closely',
                    'cost': total_cost,
                    'remaining_after': available - total_cost,
                    'warning': 'Using emergency quota reserve'
                }
            else:
                return {
                    'allowed': False,
                    'reason': f'Would use emergency reserve ({emergency_reserve} units)',
                    'suggestion': f'Reduce batch size or wait for quota reset',
                    'cost': total_cost,
                    'remaining_after': available,
                    'alternative': self._suggest_alternative(operation, credential_set, count)
                }
        
        # Check for high-cost operation warnings
        if cost_per_op >= self.high_cost_threshold:
            remaining_after = available - total_cost
            remaining_percent = remaining_after / limit
            
            if remaining_percent < 0.2:  # Would leave less than 20%
                return {
                    'allowed': True,
                    'reason': 'High-cost operation approved with warning',
                    'suggestion': 'Consider reducing frequency of expensive operations',
                    'cost': total_cost,
                    'remaining_after': remaining_after,
                    'warning': f'High-cost operation ({cost_per_op} units each)'
                }
        
        # Operation approved
        return {
            'allowed': True,
            'reason': 'Quota available and operation safe',
            'suggestion': None,
            'cost': total_cost,
            'remaining_after': available - total_cost
        }
    
    def _get_quota_suggestion(self, credential_set: int, needed_quota: int) -> str:
        """Generate helpful suggestion when quota insufficient."""
        summary = self.quota_monitor.get_usage_summary()
        
        # Check other credential sets
        alternatives = []
        for set_num, set_info in summary['sets'].items():
            if set_num != credential_set and set_info['available'] >= needed_quota:
                alternatives.append(f"Set {set_num} (has {set_info['available']} units)")
        
        if alternatives:
            return f"Try alternative credential sets: {', '.join(alternatives)}"
        
        # Calculate time until reset
        reset_time = self._time_until_reset()
        return f"Wait {reset_time} for quota reset, or reduce operation count"
    
    def _suggest_alternative(self, operation: str, credential_set: int, count: int) -> Dict:
        """Suggest alternative approaches when operation blocked."""
        cost_per_op = self.quota_monitor.QUOTA_COSTS.get(operation, 1)
        summary = self.quota_monitor.get_usage_summary()
        set_info = summary['sets'].get(credential_set, {})
        available = set_info.get('available', 0)
        emergency_reserve = int(set_info.get('limit', 10000) * self.emergency_reserve_percent)
        safe_available = max(0, available - emergency_reserve)
        
        # Calculate how many operations we can safely do
        safe_count = safe_available // cost_per_op if cost_per_op > 0 else 0
        
        alternatives = {
            'reduce_batch': {
                'description': f'Reduce count from {count} to {safe_count}',
                'safe_count': safe_count,
                'would_save': (count - safe_count) * cost_per_op
            }
        }
        
        # Check other credential sets
        for set_num, set_info in summary['sets'].items():
            if set_num != credential_set:
                other_available = set_info['available']
                other_emergency_reserve = int(set_info['limit'] * self.emergency_reserve_percent)
                other_safe = max(0, other_available - other_emergency_reserve)
                other_count = other_safe // cost_per_op if cost_per_op > 0 else 0
                
                if other_count >= count:
                    alternatives[f'use_set_{set_num}'] = {
                        'description': f'Use credential set {set_num} instead',
                        'available_count': other_count,
                        'status': set_info['status']
                    }
        
        return alternatives
    
    def _time_until_reset(self) -> str:
        """Calculate human-readable time until quota reset."""
        from datetime import datetime, timezone, timedelta
        try:
            import pytz
            pacific_tz = pytz.timezone('US/Pacific')
            now_pt = datetime.now(pacific_tz)
            next_midnight_pt = (now_pt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            time_to_reset = next_midnight_pt - now_pt
            
            hours = int(time_to_reset.total_seconds() // 3600)
            minutes = int((time_to_reset.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        except ImportError:
            # Fallback without pytz
            now = datetime.now()
            # Approximate midnight PT as current day + 1, accounting for timezone
            next_midnight = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)  # Approximate PT to UTC
            time_to_reset = next_midnight - now
            hours = int(time_to_reset.total_seconds() // 3600)
            return f"~{hours}h (approx)"
    
    def plan_operation_batch(self, operations: List[Dict], credential_set: int) -> Dict:
        """
        Plan a batch of operations with intelligent quota allocation.
        
        Args:
            operations: List of {'operation': str, 'count': int} dicts
            credential_set: Which credential set to use
            
        Returns:
            Dict with execution plan, warnings, and alternatives
        """
        plan = {
            'executable': [],
            'deferred': [],
            'blocked': [],
            'total_cost': 0,
            'warnings': [],
            'alternatives': {}
        }
        
        # Sort operations by priority
        sorted_ops = sorted(operations, key=lambda op: self._get_priority_score(op['operation']))
        
        for op in sorted_ops:
            check_result = self.can_perform_operation(
                op['operation'], 
                credential_set, 
                op.get('count', 1)
            )
            
            if check_result['allowed']:
                plan['executable'].append({
                    **op,
                    'cost': check_result['cost'],
                    'priority': self.operation_priorities.get(op['operation'], 'medium')
                })
                plan['total_cost'] += check_result['cost']
                
                if 'warning' in check_result:
                    plan['warnings'].append(check_result['warning'])
            else:
                # Check if we can defer or reduce
                if 'alternative' in check_result:
                    plan['alternatives'][op['operation']] = check_result['alternative']
                    plan['deferred'].append(op)
                else:
                    plan['blocked'].append({
                        **op,
                        'reason': check_result['reason'],
                        'suggestion': check_result['suggestion']
                    })
        
        return plan
    
    def _get_priority_score(self, operation: str) -> int:
        """Get numeric priority score for sorting (lower = higher priority)."""
        priority_scores = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'admin': 4,
            'low': 5
        }
        priority = self.operation_priorities.get(operation, 'medium')
        return priority_scores.get(priority, 3)
    
    def get_quota_dashboard(self) -> Dict:
        """Get comprehensive quota status dashboard."""
        summary = self.quota_monitor.get_usage_summary()
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self._get_overall_status(summary),
            'time_until_reset': self._time_until_reset(),
            'emergency_reserves': {},
            'recommendations': [],
            'credential_sets': {}
        }
        
        for set_num, set_info in summary['sets'].items():
            limit = set_info['limit']
            emergency_reserve = int(limit * self.emergency_reserve_percent)
            safe_available = max(0, set_info['available'] - emergency_reserve)
            
            dashboard['emergency_reserves'][set_num] = {
                'reserve_amount': emergency_reserve,
                'safe_available': safe_available,
                'in_reserve': set_info['available'] <= emergency_reserve
            }
            
            dashboard['credential_sets'][set_num] = {
                **set_info,
                'safe_available': safe_available,
                'emergency_reserve': emergency_reserve,
                'can_handle_expensive_ops': safe_available >= 100,
                'recommended_for': self._get_recommended_usage(set_info)
            }
        
        # Generate recommendations
        dashboard['recommendations'] = self._generate_recommendations(summary)
        
        return dashboard
    
    def _get_overall_status(self, summary: Dict) -> str:
        """Determine overall system quota status."""
        total_available = summary['total_available_remaining']
        total_limit = summary['total_available']
        
        if total_available == 0:
            return "EXHAUSTED"
        elif total_available < total_limit * 0.1:
            return "CRITICAL"
        elif total_available < total_limit * 0.3:
            return "LOW"
        else:
            return "HEALTHY"
    
    def _get_recommended_usage(self, set_info: Dict) -> List[str]:
        """Get recommended usage for a credential set based on its quota status."""
        available = set_info['available']
        status = set_info['status']
        
        recommendations = []
        
        if status == "HEALTHY":
            recommendations.extend(["All operations", "Live chat monitoring", "Search operations"])
        elif status == "MODERATE":
            recommendations.extend(["Live chat monitoring", "Essential operations only"])
        elif status == "WARNING":
            recommendations.extend(["Critical operations only", "Emergency use"])
        else:
            recommendations.append("Avoid usage - wait for reset")
        
        return recommendations
    
    def _generate_recommendations(self, summary: Dict) -> List[str]:
        """Generate system-wide quota management recommendations."""
        recommendations = []
        total_usage_percent = summary['total_usage_percent']

        if total_usage_percent > 90:
            recommendations.append("[ALERT] CRITICAL: Minimize all non-essential operations")
            recommendations.append("⏰ Wait for quota reset at midnight PT")
        elif total_usage_percent > 70:
            recommendations.append("[U+26A0]️ HIGH USAGE: Avoid expensive operations (search, etc.)")
            recommendations.append("[TARGET] Focus on essential live chat operations only")
        elif total_usage_percent > 50:
            recommendations.append("[DATA] MODERATE USAGE: Monitor quota closely")
            recommendations.append("[IDEA] Consider batching operations efficiently")
        else:
            recommendations.append("[OK] HEALTHY: Normal operation levels")

        # Check for imbalanced usage
        sets_data = list(summary['sets'].values())
        if len(sets_data) > 1:
            usage_variance = max(s['usage_percent'] for s in sets_data) - min(s['usage_percent'] for s in sets_data)
            if usage_variance > 30:
                recommendations.append("[U+2696]️ Consider balancing load across credential sets")

        return recommendations

    def should_rotate_credentials(self, current_set: int) -> Dict:
        """
        Intelligent credential rotation decision system.

        First Principles Analysis:
        - Rotation MUST happen BEFORE quota exhaustion breaks the system
        - Backup credential set MUST have sufficient quota to continue operations
        - Rotation is event-driven, not reactive (proactive intelligence)

        Args:
            current_set: Currently active credential set (1 or 10)

        Returns:
            Dict with rotation decision:
            {
                'should_rotate': bool,
                'target_set': int or None,
                'reason': str,
                'urgency': 'critical'|'high'|'medium'|'low',
                'current_available': int,
                'target_available': int,
                'recommendation': str
            }
        """
        summary = self.quota_monitor.get_usage_summary()
        current_info = summary['sets'].get(current_set, {})

        # Safety check - if current set doesn't exist, rotation is impossible
        if not current_info:
            logger.error(f"[FAIL] Cannot rotate - Set {current_set} not configured")
            return {
                'should_rotate': False,
                'target_set': None,
                'reason': f'Current set {current_set} not found in configuration',
                'urgency': 'critical',
                'current_available': 0,
                'target_available': 0,
                'recommendation': 'Fix credential configuration immediately'
            }

        current_usage_percent = current_info['usage_percent']
        current_available = current_info['available']
        current_limit = current_info['limit']

        # Determine target set (1 [U+2194] 10)
        target_set = 10 if current_set == 1 else 1
        target_info = summary['sets'].get(target_set, {})

        # If target doesn't exist, can't rotate
        if not target_info:
            logger.warning(f"[U+26A0]️ Cannot rotate - Set {target_set} not configured")
            return {
                'should_rotate': False,
                'target_set': None,
                'reason': f'Target set {target_set} not configured',
                'urgency': 'high' if current_usage_percent > 95 else 'medium',
                'current_available': current_available,
                'target_available': 0,
                'recommendation': f'Configure credential set {target_set} or wait for quota reset'
            }

        target_available = target_info['available']
        target_usage_percent = target_info['usage_percent']

        # CRITICAL: Immediate rotation needed (>95% usage)
        if current_usage_percent >= 95:
            if target_available > current_limit * 0.2:  # Target has >20% quota
                logger.critical(f"[ALERT] CRITICAL ROTATION NEEDED: Set {current_set} at {current_usage_percent:.1f}%")
                return {
                    'should_rotate': True,
                    'target_set': target_set,
                    'reason': f'CRITICAL: Set {current_set} quota exhausted ({current_usage_percent:.1f}%)',
                    'urgency': 'critical',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': f'Rotate immediately to Set {target_set} ({target_available} units available)'
                }
            else:
                logger.critical(f"[ALERT] QUOTA CRISIS: Both sets depleted! Current={current_usage_percent:.1f}%, Target={target_usage_percent:.1f}%")
                return {
                    'should_rotate': False,
                    'target_set': target_set,
                    'reason': f'CRISIS: Both credential sets depleted (Set {current_set}={current_usage_percent:.1f}%, Set {target_set}={target_usage_percent:.1f}%)',
                    'urgency': 'critical',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': 'Wait for midnight PT quota reset - all operations suspended'
                }

        # HIGH: Proactive rotation (85-95% usage)
        if current_usage_percent >= 85:
            if target_available > current_limit * 0.5:  # Target has >50% quota
                logger.warning(f"[U+26A0]️ PROACTIVE ROTATION: Set {current_set} at {current_usage_percent:.1f}%")
                return {
                    'should_rotate': True,
                    'target_set': target_set,
                    'reason': f'PROACTIVE: Set {current_set} approaching exhaustion ({current_usage_percent:.1f}%)',
                    'urgency': 'high',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': f'Rotate to Set {target_set} to prevent service interruption'
                }
            elif target_available > current_limit * 0.2:  # Target has >20% quota
                logger.warning(f"[U+26A0]️ DEFENSIVE ROTATION: Set {current_set} at {current_usage_percent:.1f}%, Set {target_set} low")
                return {
                    'should_rotate': True,
                    'target_set': target_set,
                    'reason': f'DEFENSIVE: Set {current_set} high ({current_usage_percent:.1f}%), Set {target_set} available',
                    'urgency': 'medium',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': f'Rotate to Set {target_set} but monitor closely ({target_available} units)'
                }
            else:
                logger.error(f"[FAIL] STUCK: Set {current_set} at {current_usage_percent:.1f}%, Set {target_set} also depleted")
                return {
                    'should_rotate': False,
                    'target_set': target_set,
                    'reason': f'STUCK: Both sets nearly exhausted (Set {current_set}={current_usage_percent:.1f}%, Set {target_set}={target_usage_percent:.1f}%)',
                    'urgency': 'high',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': 'Reduce operations immediately - wait for quota reset'
                }

        # MEDIUM: Strategic rotation (70-85% usage)
        if current_usage_percent >= 70:
            # Only rotate if target is significantly better (>2x available quota)
            if target_available > current_available * 2:
                logger.info(f"[DATA] STRATEGIC ROTATION: Set {current_set} at {current_usage_percent:.1f}%, Set {target_set} healthier")
                return {
                    'should_rotate': True,
                    'target_set': target_set,
                    'reason': f'STRATEGIC: Set {target_set} has 2x more quota ({target_available} vs {current_available})',
                    'urgency': 'medium',
                    'current_available': current_available,
                    'target_available': target_available,
                    'recommendation': f'Optional rotation to Set {target_set} for better resource distribution'
                }

        # HEALTHY: No rotation needed (<70% usage)
        logger.debug(f"[OK] HEALTHY: Set {current_set} at {current_usage_percent:.1f}% - no rotation needed")
        return {
            'should_rotate': False,
            'target_set': None,
            'reason': f'HEALTHY: Set {current_set} usage acceptable ({current_usage_percent:.1f}%)',
            'urgency': 'low',
            'current_available': current_available,
            'target_available': target_available,
            'recommendation': 'Continue normal operations'
        }


# Convenience functions for easy integration
def check_operation_allowed(operation: str, credential_set: int, count: int = 1) -> bool:
    """Quick check if operation is allowed (simplified interface)."""
    quota_monitor = QuotaMonitor()
    quota_intelligence = QuotaIntelligence(quota_monitor)
    result = quota_intelligence.can_perform_operation(operation, credential_set, count)
    return result['allowed']


def get_safe_operation_count(operation: str, credential_set: int) -> int:
    """Get maximum safe count for an operation without hitting emergency reserves."""
    quota_monitor = QuotaMonitor()
    quota_intelligence = QuotaIntelligence(quota_monitor)
    
    summary = quota_monitor.get_usage_summary()
    set_info = summary['sets'].get(credential_set, {})
    if not set_info:
        return 0
    
    cost_per_op = quota_monitor.QUOTA_COSTS.get(operation, 1)
    emergency_reserve = int(set_info['limit'] * quota_intelligence.emergency_reserve_percent)
    safe_available = max(0, set_info['available'] - emergency_reserve)
    
    return safe_available // cost_per_op if cost_per_op > 0 else 0