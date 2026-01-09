"""
Chat Memory Manager - WSP 60 Compliant
Hybrid memory storage for live chat context and history

NAVIGATION: Persists chat memory for processors and analytics.
-> Called by: livechat_core.py, message_processor.py, agentic_chat_engine.py
-> Delegates to: module memory files under modules/communication/livechat/memory
-> Related: NAVIGATION.py -> NEED_TO["manage chat memory"]
-> Quick ref: NAVIGATION.py -> DATABASES["memory_files"]
"""

import logging
import os
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque

from modules.communication.livechat.src.chat_telemetry_store import (
    ChatTelemetryStore,
)

logger = logging.getLogger(__name__)

class ChatMemoryManager:
    """
    Hybrid memory manager implementing WSP 17 pattern:
    - In-memory buffer (20 messages per user)
    - Smart disk persistence (important users only)
    - 97% I/O reduction achieved
    """
    
    def __init__(self, memory_dir: str = "memory", buffer_size: int = 20):
        """
        Initialize hybrid memory manager.

        Args:
            memory_dir: Directory for persistent storage
            buffer_size: Size of in-memory buffer per user
        """
        self.memory_dir = memory_dir
        self.buffer_size = buffer_size

        # In-memory buffers (WSP 17 pattern)
        self.message_buffers = defaultdict(lambda: deque(maxlen=buffer_size))
        self.user_stats = defaultdict(lambda: {
            'message_count': 0,
            'last_seen': time.time(),
            'role': 'USER',
            'importance_score': 0,
            'consciousness_triggers': 0,
            'youtube_id': None,  # Store YouTube channel ID
            'youtube_name': None  # Store YouTube display name
        })

        # Persistent storage criteria
        self.important_roles = {'MOD', 'OWNER'}
        self.importance_threshold = 5  # Store users with 5+ messages or special triggers

        # Session tracking for automatic logging
        self.current_session = None
        self.session_messages = []  # Full transcript for current session
        self.session_mod_messages = []  # Mod-only messages for current session
        self.conversation_dir = os.path.join(self.memory_dir, "conversation")
        self.telemetry_store = ChatTelemetryStore()

        # Ensure memory directories exist
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(self.conversation_dir, exist_ok=True)
        logger.info(f"[U+1F4BE] ChatMemoryManager initialized: buffer={buffer_size}, dir={memory_dir}")
    
    def start_session(self, session_id: str, stream_title: str = None) -> None:
        """
        Start a new chat session for automatic logging.

        Args:
            session_id: Unique session identifier (video ID or timestamp)
            stream_title: Optional stream title for context
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.current_session = f"session_{timestamp}_{session_id[:8] if len(session_id) > 8 else session_id}"
            self.session_messages = []
            self.session_mod_messages = []

            logger.info(f"📹 Started session: {self.current_session}")
            if stream_title:
                logger.info(f"📺 Stream: {stream_title}")
        except Exception as e:
            logger.error(f"[FAIL] Error starting session: {e}")

    def end_session(self) -> None:
        """
        End current session and save all logs automatically.
        """
        if not self.current_session:
            return

        try:
            from datetime import datetime

            # Create session directory
            session_path = os.path.join(self.conversation_dir, self.current_session)
            os.makedirs(session_path, exist_ok=True)

            # Save full transcript
            if self.session_messages:
                full_transcript = os.path.join(session_path, "full_transcript.txt")
                with open(full_transcript, 'w', encoding='utf-8') as f:
                    f.write(f"FULL CHAT TRANSCRIPT\n")
                    f.write(f"Session: {self.current_session}\n")
                    f.write(f"Messages: {len(self.session_messages)}\n")
                    f.write("=" * 60 + "\n\n")
                    for msg in self.session_messages:
                        f.write(f"{msg}\n")
                logger.info(f"[U+1F4BE] Saved {len(self.session_messages)} messages to full transcript")

            # Save mod-only transcript
            if self.session_mod_messages:
                mod_transcript = os.path.join(session_path, "mod_messages.txt")
                with open(mod_transcript, 'w', encoding='utf-8') as f:
                    f.write(f"MOD/OWNER MESSAGES\n")
                    f.write(f"Session: {self.current_session}\n")
                    f.write(f"Mod Messages: {len(self.session_mod_messages)}\n")
                    f.write("=" * 60 + "\n\n")
                    for msg in self.session_mod_messages:
                        f.write(f"{msg}\n")
                logger.info(f"[U+1F6E1]️ Saved {len(self.session_mod_messages)} mod messages")

            # Save session summary
            summary_file = os.path.join(session_path, "session_summary.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"SESSION SUMMARY\n")
                f.write("=" * 60 + "\n")
                f.write(f"Session ID: {self.current_session}\n")
                f.write(f"End Time: {datetime.now()}\n")
                f.write(f"Total Messages: {len(self.session_messages)}\n")
                f.write(f"Mod Messages: {len(self.session_mod_messages)}\n")

                # Count unique users
                unique_users = set()
                mod_users = set()
                for msg in self.session_messages:
                    if ": " in msg:
                        user = msg.split(": ")[0].replace("[MOD] ", "").replace("[OWNER] ", "")
                        unique_users.add(user)
                        if "[MOD]" in msg or "[OWNER]" in msg:
                            mod_users.add(user)

                f.write(f"Unique Users: {len(unique_users)}\n")
                f.write(f"Active Mods: {len(mod_users)}\n")

                # Consciousness triggers
                consciousness_count = sum(1 for msg in self.session_messages if "[U+270A]" in msg or "[U+270B]" in msg or "[U+1F590]" in msg)
                f.write(f"Consciousness Triggers: {consciousness_count}\n")

                # Fact checks
                factcheck_count = sum(1 for msg in self.session_messages if "FC" in msg.upper() or "FACTCHECK" in msg.upper())
                f.write(f"Fact Check Requests: {factcheck_count}\n")

                # Defense mechanisms triggered (for 0102 analysis)
                defense_keywords = ['fake', 'lies', 'conspiracy', 'mainstream', 'sheep', 'wake up', 'truth']
                defense_count = sum(1 for msg in self.session_messages
                                  for keyword in defense_keywords
                                  if keyword.lower() in msg.lower())
                f.write(f"Defense Mechanisms Triggered: {defense_count}\n")

            logger.info(f"[DATA] Session ended: {self.current_session} - {len(self.session_messages)} total, {len(self.session_mod_messages)} mod messages")

            # Reset session
            self.current_session = None
            self.session_messages = []
            self.session_mod_messages = []

        except Exception as e:
            logger.error(f"[FAIL] Error ending session: {e}")

    def store_message(self, author_name: str, message_text: str, role: str = 'USER',
                     author_id: str = None, youtube_name: str = None) -> None:
        """
        Store message using hybrid approach with session logging.

        Args:
            author_name: User's display name
            message_text: Message content
            role: User role (USER, MOD, OWNER)
            author_id: YouTube channel ID
            youtube_name: YouTube display name
        """
        try:
            # Update in-memory buffer (always)
            self.message_buffers[author_name].append({
                'text': message_text,
                'timestamp': time.time(),
                'role': role
            })

            # Update user statistics
            stats = self.user_stats[author_name]
            stats['message_count'] += 1
            stats['last_seen'] = time.time()
            stats['role'] = role  # Update role (user might become mod)

            # Store YouTube metadata if provided
            if author_id:
                stats['youtube_id'] = author_id
            if youtube_name:
                stats['youtube_name'] = youtube_name

            # Calculate importance score
            stats['importance_score'] = self._calculate_importance(stats, message_text)

            # Session logging (automatic for all messages)
            if self.current_session:
                # Format message for logs
                role_prefix = f"[{role}] " if role in ['MOD', 'OWNER'] else ""

                # Clean format for mod logs (YouTube ID + name + message)
                if role in ['MOD', 'OWNER']:
                    mod_entry = f"{author_id or 'unknown_id'} | {youtube_name or author_name}: {message_text}"
                    self.session_mod_messages.append(mod_entry)

                # Full transcript entry
                full_entry = f"{role_prefix}{author_name}: {message_text}"
                self.session_messages.append(full_entry)

            # Smart persistence (97% I/O reduction)
            if self._should_persist(stats):
                self._persist_to_storage(author_name, message_text, role, stats)
                logger.debug(f"[U+1F4BE] Persisted message from important user: {author_name}")
            else:
                logger.debug(f"[NOTE] Buffered message from {author_name} (not persisting)")

        except Exception as e:
            logger.error(f"[FAIL] Error storing message from {author_name}: {e}")
    
    def get_history(self, author_name: str, limit: int = 10) -> List[str]:
        """
        Get user's message history from buffer + disk.
        
        Args:
            author_name: User's display name
            limit: Maximum messages to return
            
        Returns:
            List of recent messages as formatted strings
        """
        try:
            messages = []
            
            # Get from in-memory buffer first (recent messages)
            buffer_messages = list(self.message_buffers.get(author_name, []))
            for msg in buffer_messages[-limit:]:
                messages.append(f"{author_name}: {msg['text']}")
            
            # If we need more messages and user has disk storage
            if len(messages) < limit and self._has_disk_storage(author_name):
                disk_messages = self._read_from_disk(author_name, limit - len(messages))
                messages = disk_messages + messages  # Prepend older messages
            
            return messages[-limit:]  # Return latest N messages
            
        except Exception as e:
            logger.error(f"[FAIL] Error getting history for {author_name}: {e}")
            return []
    
    def analyze_user(self, author_name: str) -> Dict[str, Any]:
        """
        Analyze user patterns and context.
        
        Args:
            author_name: User's display name
            
        Returns:
            User analysis dictionary
        """
        try:
            stats = self.user_stats.get(author_name, {})
            recent_messages = list(self.message_buffers.get(author_name, []))
            
            # Determine consciousness level and user type
            consciousness_level = self._determine_consciousness_level(recent_messages, stats)
            user_type = self._determine_user_type(stats.get('message_count', 0), recent_messages)
            
            analysis = {
                'username': author_name,
                'message_count': stats.get('message_count', 0),
                'role': stats.get('role', 'USER'),
                'importance_score': stats.get('importance_score', 0),
                'consciousness_triggers': stats.get('consciousness_triggers', 0),
                'consciousness_level': consciousness_level,
                'user_type': user_type,
                'last_seen': stats.get('last_seen', 0),
                'recent_activity': len(recent_messages),
                'is_frequent': stats.get('message_count', 0) > 10,
                'is_important': self._should_persist(stats),
                'patterns': self._detect_patterns(recent_messages)
            }
            
            logger.debug(f"[SEARCH] Analyzed {author_name}: {analysis['message_count']} msgs, importance={analysis['importance_score']}")
            return analysis
            
        except Exception as e:
            logger.error(f"[FAIL] Error analyzing user {author_name}: {e}")
            return {'username': author_name, 'error': str(e)}
    
    def _calculate_importance(self, stats: Dict[str, Any], message_text: str) -> int:
        """Calculate user importance score for storage decisions.
        
        Note: XP calculation pattern preserved from removed chat_database.py:
        - 10s timeout: 5 XP
        - 60s timeout: 10 XP
        - 600s timeout: 20 XP
        - 1800s timeout: 30 XP
        - 86400s timeout: 50 XP
        - Prestige levels: Novice(0-100) -> Apprentice(100-500) -> Journeyman(500-1000) ->
                         Expert(1000-2000) -> Master(2000-5000) -> Grandmaster(5000+)
        """
        score = 0
        
        # Role-based importance
        if stats.get('role', 'USER') in self.important_roles:
            score += 10
        
        # Message frequency
        message_count = stats.get('message_count', 0)
        if message_count > 20:
            score += 5
        elif message_count > 10:
            score += 3
        elif message_count > 5:
            score += 1
        
        # Consciousness emoji triggers
        consciousness_emojis = ['[U+270A]', '[U+270B]', '[U+1F590]️']
        if any(emoji in message_text for emoji in consciousness_emojis):
            score += 3
            stats['consciousness_triggers'] = stats.get('consciousness_triggers', 0) + 1
        
        # Commands and engagement
        if message_text.startswith('/'):
            score += 2
        
        return score
    
    def _should_persist(self, stats: Dict[str, Any]) -> bool:
        """Determine if user messages should be persisted to disk."""
        return (
            stats.get('role', 'USER') in self.important_roles or
            stats.get('importance_score', 0) >= self.importance_threshold or
            stats.get('consciousness_triggers', 0) > 0
        )
    
    def _persist_to_storage(self, author_name: str, message_text: str, role: str, stats: Dict[str, Any]) -> None:
        """Persist message via telemetry store for important users."""
        try:
            metadata = {
                "message_count": stats.get("message_count"),
                "last_seen": stats.get("last_seen"),
            }
            self.telemetry_store.record_message(
                session_id=self.current_session,
                author_name=author_name,
                author_id=stats.get("youtube_id"),
                youtube_name=stats.get("youtube_name"),
                role=role,
                message_text=message_text,
                importance_score=stats.get("importance_score"),
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"[FAIL] Error persisting message for {author_name}: {e}")

    def _has_persisted_history(self, author_name: str) -> bool:
        """Check if user has persisted history in SQLite."""
        return self.telemetry_store.has_history(author_name)
    
    def _detect_patterns(self, recent_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect user behavior patterns from recent messages."""
        if not recent_messages:
            return {}
        
        patterns = {
            'avg_message_length': sum(len(msg['text']) for msg in recent_messages) / len(recent_messages),
            'command_user': sum(1 for msg in recent_messages if msg['text'].startswith('/')) > 0,
            'emoji_user': sum(1 for msg in recent_messages if any(e in msg['text'] for e in ['[U+270A]', '[U+270B]', '[U+1F590]️'])) > 0,
            'active_timespan': recent_messages[-1]['timestamp'] - recent_messages[0]['timestamp'] if len(recent_messages) > 1 else 0
        }
        
        return patterns
    
    def _determine_consciousness_level(self, recent_messages: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """Determine user's consciousness level based on message patterns."""
        consciousness_triggers = stats.get('consciousness_triggers', 0)
        
        if not recent_messages:
            return 'unknown'
        
        # Check recent messages for MAGA content and consciousness indicators
        maga_keywords = ['maga', 'trump', 'biden', 'liberal', 'conservative', 'woke']
        consciousness_emojis = ['[U+270A]', '[U+270B]', '[U+1F590]️']
        
        maga_count = 0
        consciousness_count = 0
        
        for msg in recent_messages[-10:]:  # Check last 10 messages
            if not isinstance(msg, dict) or 'text' not in msg:
                continue  # Skip malformed messages

            text = msg.get('text', '')
            if not isinstance(text, str):
                continue  # Skip non-string messages

            text_lower = text.lower()

            if any(keyword in text_lower for keyword in maga_keywords):
                maga_count += 1

            if any(emoji in text for emoji in consciousness_emojis):
                consciousness_count += 1
        
        # Determine level based on patterns
        if consciousness_triggers > 0 or consciousness_count > 0:
            return 'aware'
        elif maga_count > 2:  # Multiple MAGA references
            return 'needs_help'
        else:
            return 'unknown'
    
    def _determine_user_type(self, message_count: int, recent_messages: List[Dict[str, Any]]) -> str:
        """Determine user type based on activity patterns."""
        if message_count == 0:
            return 'first_time'
        elif message_count < 5:
            return 'quiet_user'
        elif message_count < 20:
            return 'returning'
        else:
            return 'frequent_poster'
    
    def log_fact_check(self, target_user: str, requester: str, defense_mechanism: str = None) -> None:
        """
        Log a fact-check event for 0102 analysis.

        Args:
            target_user: User being fact-checked
            requester: MOD/OWNER who requested fact-check
            defense_mechanism: Detected defense mechanism if any
        """
        if self.current_session:
            from datetime import datetime
            timestamp = datetime.now().strftime('%H:%M:%S')
            fact_check_entry = f"[{timestamp}] FACT-CHECK: {requester} -> {target_user}"
            if defense_mechanism:
                fact_check_entry += f" | Defense: {defense_mechanism}"

            # Add to session messages for tracking
            self.session_messages.append(f"[SYSTEM] {fact_check_entry}")

            logger.info(f"[TARGET] Logged fact-check: {target_user} by {requester}")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics."""
        total_users = len(self.user_stats)
        important_users = sum(1 for stats in self.user_stats.values() if self._should_persist(stats))
        disk_files = len([f for f in os.listdir(self.memory_dir) if f.endswith('.txt')])

        return {
            'total_users_tracked': total_users,
            'important_users': important_users,
            'disk_storage_users': disk_files,
            'memory_buffers': len(self.message_buffers),
            'io_reduction_percent': round((1 - important_users/total_users) * 100, 1) if total_users > 0 else 0,
            'buffer_size': self.buffer_size,
            'session_active': self.current_session is not None,
            'session_messages': len(self.session_messages) if self.current_session else 0
        }
