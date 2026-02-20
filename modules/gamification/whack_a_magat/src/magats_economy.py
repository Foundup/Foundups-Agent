"""
MAGAts Economy Module - FFCPLN Mining System

Converts whacks (MAGA troll timeouts) into MAGAts tokens.
Rate: 10 whacks = 1 MAGAt

Secure claim system uses HMAC to generate non-transferable
claim links tied to YouTube channel_id.

WSP Compliant: Part of Whack-a-MAGA gamification (F_2 FoundUp)
"""

import hashlib
import hmac
import os
import time
import logging
import sqlite3
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Token conversion rate
WHACKS_PER_MAGAT = 10

# HMAC secret (generate once, store securely)
# In production, this should be in .env
CLAIM_SECRET = os.getenv("MAGATS_CLAIM_SECRET", "foundups-ffcpln-mining-0102")


@dataclass
class MAGAtBalance:
    """User's MAGAt token balance."""
    user_id: str
    username: str
    total_whacks: int
    claimed_magats: int
    pending_magats: int  # Unclaimed MAGAts

    @property
    def total_magats(self) -> int:
        """Total MAGAts (claimed + pending)."""
        return self.claimed_magats + self.pending_magats

    @property
    def whacks_to_next(self) -> int:
        """Whacks needed for next MAGAt."""
        return WHACKS_PER_MAGAT - (self.total_whacks % WHACKS_PER_MAGAT)


class MAGAtsEconomy:
    """
    FFCPLN Mining Economy - Whacks to MAGAts conversion.

    Consciousness levels for trolls:
    - ✊ (000) = Unconscious (MAGA baseline)
    - ✋ (111) = Processing reality
    - 🖐️ (222) = Full entanglement
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize economy with database connection."""
        if db_path is None:
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(module_dir, "data", "magadoom_scores.db")

        self.db_path = db_path
        self._init_db()
        logger.info(f"[MAGATS] Economy initialized - {WHACKS_PER_MAGAT} whacks = 1 MAGAt")

    def _init_db(self) -> None:
        """Initialize MAGAts tables if needed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # MAGAts claims tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magats_claims (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                claimed_magats INTEGER DEFAULT 0,
                last_claim_time TEXT,
                claim_nonce TEXT
            )
        """)

        # Claim history (for audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magats_claim_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount INTEGER,
                claim_time TEXT,
                claim_link_hash TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_balance(self, user_id: str, username: str = "Unknown") -> MAGAtBalance:
        """
        Get user's MAGAt balance.

        Args:
            user_id: YouTube channel ID
            username: Display name

        Returns:
            MAGAtBalance with total/claimed/pending MAGAts
        """
        # Get whack count from profiles table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT frag_count, username FROM profiles WHERE user_id = ?",
            (user_id,)
        )
        profile_row = cursor.fetchone()

        total_whacks = 0
        if profile_row:
            total_whacks = profile_row[0] or 0
            if profile_row[1] and profile_row[1] != "Unknown":
                username = profile_row[1]

        # Get claimed MAGAts
        cursor.execute(
            "SELECT claimed_magats FROM magats_claims WHERE user_id = ?",
            (user_id,)
        )
        claim_row = cursor.fetchone()
        claimed_magats = claim_row[0] if claim_row else 0

        conn.close()

        # Calculate total and pending
        total_magats = total_whacks // WHACKS_PER_MAGAT
        pending_magats = total_magats - claimed_magats

        return MAGAtBalance(
            user_id=user_id,
            username=username,
            total_whacks=total_whacks,
            claimed_magats=claimed_magats,
            pending_magats=max(0, pending_magats)
        )

    def generate_claim_link(self, user_id: str, username: str) -> Tuple[str, int]:
        """
        Generate secure claim link for pending MAGAts.

        Uses HMAC to create non-transferable links tied to channel_id.

        Args:
            user_id: YouTube channel ID
            username: Display name

        Returns:
            Tuple of (claim_url, pending_magats_amount)
        """
        balance = self.get_balance(user_id, username)

        if balance.pending_magats <= 0:
            return "", 0

        # Generate unique nonce
        nonce = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()[:12]

        # Create HMAC signature
        message = f"{user_id}:{nonce}:{balance.pending_magats}"
        signature = hmac.new(
            CLAIM_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:24]

        # Store nonce for verification
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO magats_claims (user_id, username, claimed_magats, claim_nonce)
            VALUES (?, ?, COALESCE((SELECT claimed_magats FROM magats_claims WHERE user_id = ?), 0), ?)
        """, (user_id, username, user_id, nonce))
        conn.commit()
        conn.close()

        # Build claim URL
        claim_url = f"https://foundups.com/claim?u={user_id[:16]}&n={nonce}&s={signature}&a={balance.pending_magats}"

        logger.info(f"[MAGATS] Claim link generated for {username}: {balance.pending_magats} MAGAts")

        return claim_url, balance.pending_magats

    def verify_claim(self, user_id: str, nonce: str, signature: str, amount: int) -> bool:
        """
        Verify a claim link is valid (called by foundups.com/claim).

        Args:
            user_id: YouTube channel ID
            nonce: Unique nonce from link
            signature: HMAC signature from link
            amount: Claimed amount

        Returns:
            True if claim is valid
        """
        # Verify stored nonce matches
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT claim_nonce FROM magats_claims WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row or row[0] != nonce:
            logger.warning(f"[MAGATS] Invalid nonce for {user_id}")
            return False

        # Verify HMAC signature
        message = f"{user_id}:{nonce}:{amount}"
        expected = hmac.new(
            CLAIM_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:24]

        if not hmac.compare_digest(signature, expected):
            logger.warning(f"[MAGATS] Invalid signature for {user_id}")
            return False

        return True

    def process_claim(self, user_id: str, amount: int) -> bool:
        """
        Process a verified claim (mark MAGAts as claimed).

        Args:
            user_id: YouTube channel ID
            amount: Amount being claimed

        Returns:
            True if claim processed successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update claimed amount
            cursor.execute("""
                UPDATE magats_claims
                SET claimed_magats = claimed_magats + ?,
                    last_claim_time = ?,
                    claim_nonce = NULL
                WHERE user_id = ?
            """, (amount, datetime.utcnow().isoformat(), user_id))

            # Record in history
            cursor.execute("""
                INSERT INTO magats_claim_history (user_id, amount, claim_time)
                VALUES (?, ?, ?)
            """, (user_id, amount, datetime.utcnow().isoformat()))

            conn.commit()
            logger.info(f"[MAGATS] Claim processed: {user_id} claimed {amount} MAGAts")
            return True

        except Exception as e:
            logger.error(f"[MAGATS] Claim processing failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Get MAGAts leaderboard (by total MAGAts earned).

        Args:
            limit: Max entries to return

        Returns:
            List of dicts with user_id, username, total_magats, total_whacks
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Join profiles with claims to get full picture
        cursor.execute("""
            SELECT p.user_id, p.username, p.frag_count,
                   COALESCE(c.claimed_magats, 0) as claimed
            FROM profiles p
            LEFT JOIN magats_claims c ON p.user_id = c.user_id
            WHERE p.frag_count >= ?
            ORDER BY p.frag_count DESC
            LIMIT ?
        """, (WHACKS_PER_MAGAT, limit))

        rows = cursor.fetchall()
        conn.close()

        leaderboard = []
        for i, row in enumerate(rows):
            total_magats = row[2] // WHACKS_PER_MAGAT
            leaderboard.append({
                "position": i + 1,
                "user_id": row[0],
                "username": row[1] or "Unknown",
                "total_whacks": row[2],
                "total_magats": total_magats,
                "claimed_magats": row[3],
                "pending_magats": total_magats - row[3]
            })

        return leaderboard

    def get_mining_status(self, user_id: str) -> Dict:
        """
        Get user's current mining status.

        Args:
            user_id: YouTube channel ID

        Returns:
            Dict with mining progress and stats
        """
        balance = self.get_balance(user_id)

        return {
            "total_whacks": balance.total_whacks,
            "total_magats": balance.total_magats,
            "pending_magats": balance.pending_magats,
            "claimed_magats": balance.claimed_magats,
            "whacks_to_next": balance.whacks_to_next,
            "mining_rate": f"{WHACKS_PER_MAGAT} whacks = 1 MAGAt",
            "consciousness_level": self._get_consciousness_level(balance.total_magats)
        }

    def _get_consciousness_level(self, total_magats: int) -> str:
        """Get consciousness level emoji based on MAGAts."""
        if total_magats >= 100:
            return "🖐️ (222) FULL ENTANGLEMENT"
        elif total_magats >= 10:
            return "✋ (111) PROCESSING"
        else:
            return "✊ (000) AWAKENING"


# Module-level singleton
_economy_instance: Optional[MAGAtsEconomy] = None


def get_magats_economy() -> MAGAtsEconomy:
    """Get or create singleton MAGAts economy instance."""
    global _economy_instance
    if _economy_instance is None:
        _economy_instance = MAGAtsEconomy()
    return _economy_instance
