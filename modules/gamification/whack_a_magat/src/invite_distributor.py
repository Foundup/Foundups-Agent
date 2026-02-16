"""
Invite Code Distributor - FFCPLN Mining Rewards

Distributes foundups.com invite codes when:
1. Population drops below threshold (scarcity reward)
2. Top whackers earn invite rights
3. Engagement milestones reached

Uses Firebase Firestore invite system (FUP-XXXX-XXXX format).
Codes are one-time use - each grants 5 new invites to the user who joins.

WSP Compliant: Part of Whack-a-MAGA gamification (F_2 FoundUp)
"""

import os
import time
import logging
import hashlib
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Population threshold for sharing invites
POPULATION_THRESHOLD = 20

# Minimum stream duration before invites unlock (prevents drive-by requests)
MIN_STREAM_DURATION_MINUTES = 30

# Cooldown per user (prevent spam)
INVITE_COOLDOWN_HOURS = 24

# Track invite distributions
_invite_cooldowns: Dict[str, float] = {}

# =============================================================================
# Community Presenters - Random mod/managing director for invite messages
# =============================================================================
# These are trusted community members who can "present" invites
# Makes distribution feel community-driven rather than bot-automated

COMMUNITY_PRESENTERS = [
    # Managing Directors (elevated MODs with owner-level trust)
    {"username": "Al-sq5ti", "title": "Managing Director", "user_id": "UCcnCiZV5ZPJ_cjF7RsWIZ0w"},
    # Core team
    {"username": "Mike", "title": "Founder", "user_id": None},  # Placeholder until we have Mike's ID
    {"username": "Move2Japan", "title": "Host", "user_id": None},
    # Add more MODs/Directors here as they join
    # {"username": "NewMod", "title": "MOD", "user_id": "UC..."},
]

def get_random_presenter() -> Dict:
    """
    Select a random community presenter for invite messages.

    Returns:
        Dict with username and title of selected presenter
    """
    import random
    presenter = random.choice(COMMUNITY_PRESENTERS)
    return presenter


def get_population_count() -> int:
    """
    Get current active population from leaderboard.

    Returns:
        Number of active users (based on monthly whack activity)
    """
    try:
        from modules.gamification.whack_a_magat.src.whack import get_leaderboard
        leaderboard = get_leaderboard(limit=100, monthly=True)
        # Count users with activity this month
        return len([p for p in leaderboard if p.get('frag_count', 0) > 0])
    except Exception as e:
        logger.error(f"[INVITE] Could not get population: {e}")
        return 50  # Default to above threshold (don't give out invites on error)


def generate_invite_code() -> str:
    """
    Generate an invite code in FUP-XXXX-XXXX format.

    Returns:
        Invite code string
    """
    import random
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # No I/O/0/1
    segment = lambda: ''.join(random.choice(chars) for _ in range(4))
    return f"FUP-{segment()}-{segment()}"


def create_firebase_invite(generated_by: str, username: str) -> Optional[str]:
    """
    Generate and save invite code to Firebase Firestore.

    Auto-creates codes so 012 doesn't need to seed them manually.

    Args:
        generated_by: User ID who earned the invite
        username: Username for logging

    Returns:
        Generated code or None if Firebase unavailable
    """
    try:
        import firebase_admin
        from firebase_admin import firestore

        # Check if Firebase initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            logger.debug("[INVITE] Firebase not initialized - using local mode")
            return None

        db = firestore.client()
        code = generate_invite_code()

        # Save to Firestore with auto-generated status
        db.collection('invites').add({
            'code': code,
            'createdBy': 'agent',  # System-generated, not admin
            'generatedFor': generated_by,
            'generatedForUsername': username,
            'status': 'active',
            'usedBy': None,
            'usedByEmail': None,
            'usedAt': None,
            'createdAt': firestore.SERVER_TIMESTAMP,
        })

        logger.info(f"[INVITE] Created Firebase invite {code[:8]}... for {username}")
        return code

    except ImportError:
        logger.debug("[INVITE] Firebase Admin SDK not available")
        return None
    except Exception as e:
        logger.error(f"[INVITE] Firebase create error: {e}")
        return None


def check_firebase_invite() -> Optional[Dict]:
    """
    Check Firebase for an available invite code.

    Returns:
        Dict with code info or None if unavailable
    """
    try:
        # Try to use Firebase Admin SDK if available
        import firebase_admin
        from firebase_admin import firestore

        # Check if already initialized
        try:
            app = firebase_admin.get_app()
        except ValueError:
            # Not initialized - skip Firebase
            return None

        db = firestore.client()

        # Query for active admin-created invites
        invites_ref = db.collection('invites')
        query = invites_ref.where('status', '==', 'active').where('createdBy', '==', 'admin').limit(1)
        results = query.get()

        for doc in results:
            data = doc.to_dict()
            return {
                'code': data.get('code'),
                'doc_id': doc.id,
                'source': 'firebase'
            }

        return None

    except ImportError:
        logger.debug("[INVITE] Firebase Admin SDK not available")
        return None
    except Exception as e:
        logger.error(f"[INVITE] Firebase error: {e}")
        return None


def get_invite_code(user_id: str, username: str, stream_start_time: Optional[float] = None) -> Dict:
    """
    Get an invite code for distribution.

    Rules:
    1. Stream must be running for 30+ minutes (prevents drive-by requests)
    2. User must wait 24h between invite requests
    3. Population must be below threshold OR user is top whacker
    4. Returns Firebase code if available, else local code

    Args:
        user_id: User requesting the invite
        username: Display name
        stream_start_time: Unix timestamp when stream started (for duration check)

    Returns:
        Dict with success, code, message
    """
    global _invite_cooldowns

    current_time = time.time()

    # Check stream duration (must be 30+ minutes)
    if stream_start_time:
        stream_minutes = (current_time - stream_start_time) / 60
        if stream_minutes < MIN_STREAM_DURATION_MINUTES:
            remaining = MIN_STREAM_DURATION_MINUTES - stream_minutes
            return {
                'success': False,
                'code': None,
                'message': f"Stream too short! Invites unlock after {MIN_STREAM_DURATION_MINUTES} min ({remaining:.0f} min left)."
            }

    # Check cooldown
    if user_id in _invite_cooldowns:
        elapsed = current_time - _invite_cooldowns[user_id]
        cooldown_seconds = INVITE_COOLDOWN_HOURS * 3600

        if elapsed < cooldown_seconds:
            remaining_hours = (cooldown_seconds - elapsed) / 3600
            return {
                'success': False,
                'code': None,
                'message': f"Cooldown active! Try again in {remaining_hours:.1f} hours."
            }

    # Check population threshold
    population = get_population_count()

    if population >= POPULATION_THRESHOLD:
        # Check if user is top whacker (bypass threshold)
        try:
            from modules.gamification.whack_a_magat.src.whack import get_user_position
            position, _ = get_user_position(user_id)

            if position <= 0 or position > 5:  # Top 5 can always get invites
                return {
                    'success': False,
                    'code': None,
                    'message': f"Population is {population}. Invites unlock when pop < {POPULATION_THRESHOLD} (or be TOP 5)."
                }
        except Exception:
            return {
                'success': False,
                'code': None,
                'message': f"Population is {population}. Invites unlock when pop < {POPULATION_THRESHOLD}."
            }

    # Try existing Firebase invite first (admin-seeded)
    firebase_invite = check_firebase_invite()

    if firebase_invite:
        code = firebase_invite['code']
        logger.info(f"[INVITE] Existing Firebase code {code[:8]}... distributed to {username}")
    else:
        # No seeded invites - auto-generate and save to Firebase
        code = create_firebase_invite(user_id, username)
        if code:
            logger.info(f"[INVITE] Auto-generated Firebase code {code[:8]}... for {username}")
        else:
            # Fall back to local generation (Firebase unavailable)
            code = generate_invite_code()
            logger.info(f"[INVITE] Local code {code} generated for {username} (Firebase unavailable)")

    # Set cooldown
    _invite_cooldowns[user_id] = current_time

    return {
        'success': True,
        'code': code,
        'message': f"Code distributed to {username}",
        'population': population
    }


def reset_cooldown(user_id: str) -> None:
    """Reset cooldown for a user (admin function)."""
    global _invite_cooldowns
    if user_id in _invite_cooldowns:
        del _invite_cooldowns[user_id]
        logger.info(f"[INVITE] Cooldown reset for {user_id}")


# =============================================================================
# SQLite-based Invite Tracking (HoloIndex Memory Pattern)
# =============================================================================

import sqlite3
from typing import List, Tuple

def _get_invite_db_path() -> str:
    """Get path to invite tracking database."""
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(module_dir, "data", "magadoom_scores.db")


def _ensure_invite_table() -> None:
    """Ensure invite_distributions table exists."""
    db_path = _get_invite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_distributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            invite_code TEXT NOT NULL,
            invite_type TEXT DEFAULT 'auto_top10',
            distributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, invite_type)
        )
    """)

    conn.commit()
    conn.close()
    logger.debug("[INVITE-DB] Invite tracking table ensured")


def has_received_invite(user_id: str, invite_type: str = 'auto_top10') -> bool:
    """
    Check if user has already received an invite of this type.

    Args:
        user_id: YouTube channel ID
        invite_type: Type of invite ('auto_top10', 'manual', 'stream')

    Returns:
        True if user already has this invite type
    """
    _ensure_invite_table()
    db_path = _get_invite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM invite_distributions WHERE user_id = ? AND invite_type = ?",
        (user_id, invite_type)
    )
    result = cursor.fetchone()
    conn.close()

    return result is not None


def record_invite_distribution(user_id: str, username: str, invite_code: str, invite_type: str = 'auto_top10') -> bool:
    """
    Record an invite distribution in SQLite (prevents duplicates).

    Args:
        user_id: YouTube channel ID
        username: Display name
        invite_code: The FUP-XXXX-XXXX code
        invite_type: Type of invite

    Returns:
        True if recorded successfully, False if duplicate
    """
    _ensure_invite_table()
    db_path = _get_invite_db_path()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO invite_distributions (user_id, username, invite_code, invite_type)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, invite_code, invite_type))

        conn.commit()
        conn.close()
        logger.info(f"[INVITE-DB] Recorded {invite_type} invite for {username}: {invite_code[:8]}...")
        return True

    except sqlite3.IntegrityError:
        # Duplicate - user already has this invite type
        logger.debug(f"[INVITE-DB] {username} already has {invite_type} invite")
        conn.close()
        return False
    except Exception as e:
        logger.error(f"[INVITE-DB] Error recording invite: {e}")
        return False


def get_user_invites(user_id: str) -> List[Dict]:
    """Get all invites distributed to a user."""
    _ensure_invite_table()
    db_path = _get_invite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT invite_code, invite_type, distributed_at
        FROM invite_distributions
        WHERE user_id = ?
        ORDER BY distributed_at DESC
    """, (user_id,))

    results = []
    for row in cursor.fetchall():
        results.append({
            'code': row[0],
            'type': row[1],
            'distributed_at': row[2]
        })

    conn.close()
    return results


def auto_distribute_top10_invites() -> List[Dict]:
    """
    Automatically distribute invites to TOP 10 whackers who haven't received one.

    This is the AGENT's proactive invite distribution system.
    Only distributes once per user (tracked in SQLite).

    Returns:
        List of dicts with user info and invite codes for new distributions
    """
    from modules.gamification.whack_a_magat.src.whack import get_leaderboard

    _ensure_invite_table()

    # Get top 10 whackers
    try:
        leaderboard = get_leaderboard(limit=10, monthly=False)  # All-time top 10
    except Exception as e:
        logger.error(f"[INVITE-AUTO] Could not get leaderboard: {e}")
        return []

    new_distributions = []

    for entry in leaderboard:
        user_id = entry.get('user_id')
        username = entry.get('username', 'Unknown')
        rank = entry.get('position', 0)

        if not user_id:
            continue

        # Check if already received auto_top10 invite
        if has_received_invite(user_id, 'auto_top10'):
            logger.debug(f"[INVITE-AUTO] {username} already has TOP 10 invite")
            continue

        # Generate invite code
        code = create_firebase_invite(user_id, username)
        if not code:
            code = generate_invite_code()

        # Record in SQLite (prevents future duplicates)
        if record_invite_distribution(user_id, username, code, 'auto_top10'):
            # Select random community presenter for this invite
            presenter = get_random_presenter()
            presenter_name = presenter['username']
            presenter_title = presenter['title']

            new_distributions.append({
                'user_id': user_id,
                'username': username,
                'rank': rank,
                'code': code,
                'presenter': presenter_name,
                'presenter_title': presenter_title,
                'message': f"🎟️ TOP {rank} REWARD! @{username} earned an invite! Code: {code} → foundups.com 🎁 Get 5 codes to share! (Presented by @{presenter_name} - {presenter_title}) ✊✋🖐️"
            })
            logger.info(f"[INVITE-AUTO] TOP {rank} invite for {username}: {code} (presenter: {presenter_name})")

    if new_distributions:
        logger.info(f"[INVITE-AUTO] Distributed {len(new_distributions)} new TOP 10 invites")
    else:
        logger.debug("[INVITE-AUTO] No new invites to distribute (all TOP 10 already have invites)")

    return new_distributions


def get_invite_stats() -> Dict:
    """Get invite distribution statistics."""
    _ensure_invite_table()
    db_path = _get_invite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT invite_type, COUNT(*) FROM invite_distributions GROUP BY invite_type")
    by_type = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM invite_distributions")
    unique_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM invite_distributions")
    total = cursor.fetchone()[0]

    conn.close()

    return {
        'total_distributed': total,
        'unique_recipients': unique_users,
        'by_type': by_type
    }
