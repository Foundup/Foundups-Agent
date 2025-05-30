import logging
import os
import time
from datetime import datetime
import googleapiclient.errors
from dotenv import load_dotenv
from utils.throttling import calculate_dynamic_delay
from modules.token_manager import token_manager
from modules.banter_engine import BanterEngine
from utils.oauth_manager import get_authenticated_service
import asyncio

logger = logging.getLogger(__name__)

class LiveChatListener:
    """
    Connects to a YouTube livestream chat, listens for messages,
    logs them, and provides hooks for sending messages and AI interaction.
    """
    def __init__(self, youtube_service, video_id, live_chat_id=None):
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.next_page_token = None
        self.poll_interval_ms = 100000  # Default: 100 seconds
        self.error_backoff_seconds = 5  # Initial backoff for errors
        self.memory_dir = "memory"
        self.greeting_message = os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!")
        self.message_queue = []  # Queue for storing messages
        self.viewer_count = 0  # Track current viewer count
        self.banter_engine = BanterEngine()  # Initialize banter engine
        self.trigger_emojis = ["emoji1", "emoji2", "emoji3"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds
        self.is_running = False  # Flag to control the listening loop

