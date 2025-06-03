"""
Enhanced BanterEngine class for processing chat messages and generating responses.

Integrates improvements from test coverage analysis:
- Enhanced error handling and validation
- Better caching and performance optimization
- Improved emoji sequence detection
- More robust response generation
- Better logging and monitoring

Following WSP 3: Enterprise Domain Architecture
"""

import logging
import random
import time
from typing import Optional, Dict, Tuple, List, Any
from datetime import datetime, timedelta

# Import the SEQUENCE_MAP from sequence_responses
from ..sequence_responses import SEQUENCE_MAP
# Import the emoji action map
from .emoji_sequence_map import get_emoji_sequence

class BanterEngineError(Exception):
    """Base exception for Banter Engine errors."""
    pass

class EmojiSequenceError(Exception):
    """Exception for emoji sequence processing errors."""
    pass

class ResponseGenerationError(Exception):
    """Exception for response generation errors."""
    pass

class BanterEngineConfig:
    """Configuration class for Banter Engine settings."""
    
    def __init__(self):
        # Response caching settings
        self.CACHE_EXPIRY_MINUTES = 30
        self.MAX_CACHE_SIZE = 1000
        
        # Performance settings
        self.MAX_INPUT_LENGTH = 1000
        self.MAX_RESPONSE_LENGTH = 500
        
        # Emoji processing settings
        self.MAX_EMOJI_SEQUENCE_LENGTH = 10
        self.REQUIRED_SEQUENCE_LENGTH = 3
        
        # Response generation settings
        self.FALLBACK_ENABLED = True
        self.RESPONSE_VALIDATION_ENABLED = True
        
        # Logging settings
        self.DEBUG_MODE = False

# Global configuration instance
config = BanterEngineConfig()

class BanterEngine:
    """Enhanced BanterEngine with improved error handling and performance."""
    
    def __init__(self):
        """Initialize the enhanced BanterEngine."""
        try:
            # Use the imported SEQUENCE_MAP directly
            self.sequence_map_data = SEQUENCE_MAP
            self.logger = logging.getLogger(__name__)
            
            # Enhanced caching system
            self._response_cache = {}
            self._cache_timestamps = {}
            self._cache_hits = 0
            self._cache_misses = 0
            
            # Performance tracking
            self._total_requests = 0
            self._successful_responses = 0
            self._failed_responses = 0
            
            # Store themes derived from tones with validation
            self._themes = {}
            self._initialize_themes()
            self._populate_themed_responses()
            
            # Validate initialization
            self._validate_initialization()
            
            self.logger.info("✅ Enhanced BanterEngine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize BanterEngine: {e}")
            raise BanterEngineError(f"Initialization failed: {e}")

    def _initialize_themes(self):
        """Initialize themes with proper validation."""
        try:
            # Extract unique tones from sequence map
            tones = set()
            for info in self.sequence_map_data.values():
                tone = info.get("tone")
                if tone and isinstance(tone, str):
                    tones.add(tone)
            
            # Initialize theme dictionary
            self._themes = {tone: [] for tone in tones}
            self._themes["default"] = []
            self._themes["greeting"] = []
            
            self.logger.debug(f"Initialized {len(self._themes)} themes: {list(self._themes.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize themes: {e}")
            raise BanterEngineError(f"Theme initialization failed: {e}")

    def _populate_themed_responses(self):
        """Enhanced themed response population with validation."""
        try:
            # Default responses with validation
            default_responses = [
                "Interesting sequence! 🤔",
                "Your emoji game is strong! 💪", 
                "I see what you did there! 👀",
                "That's a unique combination! ✨",
                "Nice emoji work! 🎯"
            ]
            
            greeting_responses = [
                "Hey there! 👋",
                "Hello! How's it going? 😊",
                "Welcome! Great to see you! 🌟",
                "Hi! Ready for some fun? 🎉",
                "Greetings! What brings you here? 🤗"
            ]

            # Validate and set default responses
            self._themes["default"] = self._validate_responses(default_responses)
            self._themes["greeting"] = self._validate_responses(greeting_responses)
            
            # Populate from sequence map with enhanced validation
            for seq, info in self.sequence_map_data.items():
                if not isinstance(info, dict):
                    continue
                    
                tone = info.get("tone")
                example = info.get("example")
                
                if tone and isinstance(tone, str) and example and isinstance(example, str):
                    if tone not in self._themes:
                        self._themes[tone] = []
                    
                    # Validate and add example
                    validated_example = self._validate_response(example)
                    if validated_example and validated_example not in self._themes[tone]:
                        self._themes[tone].append(validated_example)
                
                # Add contextual responses for each tone
                if tone and tone not in ["default", "greeting"]:
                    contextual_responses = [
                        f"Feeling the {tone} vibes! 🌊",
                        f"That's some {tone} energy! ⚡",
                        f"Perfect {tone} moment! 🎭"
                    ]
                    
                    for response in contextual_responses:
                        validated_response = self._validate_response(response)
                        if validated_response and validated_response not in self._themes[tone]:
                            self._themes[tone].append(validated_response)
            
            # Ensure all themes have at least one response
            for theme, responses in self._themes.items():
                if not responses:
                    fallback_response = f"Exploring {theme} vibes! ✨"
                    self._themes[theme] = [fallback_response]
            
            total_responses = sum(len(responses) for responses in self._themes.values())
            self.logger.info(f"✅ Populated {total_responses} responses across {len(self._themes)} themes")
            
        except Exception as e:
            self.logger.error(f"Failed to populate themed responses: {e}")
            raise BanterEngineError(f"Response population failed: {e}")

    def _validate_responses(self, responses: List[str]) -> List[str]:
        """Validate a list of responses."""
        validated = []
        for response in responses:
            validated_response = self._validate_response(response)
            if validated_response:
                validated.append(validated_response)
        return validated

    def _validate_response(self, response: str) -> Optional[str]:
        """Enhanced response validation."""
        if not response or not isinstance(response, str):
            return None
        
        # Clean and validate
        cleaned = response.strip()
        if not cleaned:
            return None
        
        # Length validation
        if len(cleaned) > config.MAX_RESPONSE_LENGTH:
            self.logger.warning(f"Response too long, truncating: {cleaned[:50]}...")
            cleaned = cleaned[:config.MAX_RESPONSE_LENGTH].strip()
        
        return cleaned

    def _validate_initialization(self):
        """Validate that initialization was successful."""
        if not self.sequence_map_data:
            raise BanterEngineError("Sequence map data is empty")
        
        if not self._themes:
            raise BanterEngineError("No themes initialized")
        
        if "default" not in self._themes:
            raise BanterEngineError("Default theme missing")
        
        total_responses = sum(len(responses) for responses in self._themes.values())
        if total_responses == 0:
            raise BanterEngineError("No responses available")
        
        self.logger.debug(f"✅ Validation passed: {len(self.sequence_map_data)} sequences, {len(self._themes)} themes, {total_responses} responses")

    def _extract_emoji_sequence_enhanced(self, input_text: str) -> Optional[Tuple[int, int, int]]:
        """Enhanced emoji sequence extraction with better error handling."""
        if not input_text or not isinstance(input_text, str):
            return None
        
        try:
            # Import the correct emoji mapping with error handling
            from ..emoji_sequence_map import EMOJI_TO_NUMBER as EMOJI_TO_NUM
            
            if not EMOJI_TO_NUM:
                self.logger.error("Emoji mapping is empty")
                return None
            
            sequence = []
            i = 0
            max_length = min(len(input_text), config.MAX_INPUT_LENGTH)
            
            while i < max_length and len(sequence) < config.MAX_EMOJI_SEQUENCE_LENGTH:
                # Check for multi-character emoji first (🖐️)
                if i + 1 < max_length:
                    two_char = input_text[i:i+2]
                    if two_char in EMOJI_TO_NUM:
                        sequence.append(EMOJI_TO_NUM[two_char])
                        if len(sequence) == config.REQUIRED_SEQUENCE_LENGTH:
                            return tuple(sequence)
                        i += 2
                        continue
                
                # Check for single-character emoji
                char = input_text[i]
                if char in EMOJI_TO_NUM:
                    sequence.append(EMOJI_TO_NUM[char])
                    if len(sequence) == config.REQUIRED_SEQUENCE_LENGTH:
                        return tuple(sequence)
                i += 1
            
            # Log partial sequences for debugging
            if sequence and config.DEBUG_MODE:
                self.logger.debug(f"Partial sequence found: {sequence} (need {config.REQUIRED_SEQUENCE_LENGTH})")
            
            return None
            
        except ImportError as e:
            self.logger.error(f"Failed to import emoji mapping: {e}")
            raise EmojiSequenceError(f"Emoji mapping import failed: {e}")
        except Exception as e:
            self.logger.error(f"Error extracting emoji sequence: {e}")
            return None

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if valid."""
        if cache_key not in self._response_cache:
            return None
        
        # Check if cache entry is expired
        timestamp = self._cache_timestamps.get(cache_key)
        if timestamp:
            age = datetime.now() - timestamp
            if age > timedelta(minutes=config.CACHE_EXPIRY_MINUTES):
                # Remove expired entry
                del self._response_cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None
        
        self._cache_hits += 1
        return self._response_cache[cache_key]

    def _cache_response(self, cache_key: str, response: str):
        """Cache a response with timestamp."""
        # Implement simple LRU by removing oldest entries if cache is full
        if len(self._response_cache) >= config.MAX_CACHE_SIZE:
            # Remove oldest entry
            oldest_key = min(self._cache_timestamps.keys(), 
                           key=lambda k: self._cache_timestamps[k])
            del self._response_cache[oldest_key]
            del self._cache_timestamps[oldest_key]
        
        self._response_cache[cache_key] = response
        self._cache_timestamps[cache_key] = datetime.now()
        self._cache_misses += 1

    def process_input_enhanced(self, input_text: str) -> Tuple[str, Optional[str]]:
        """
        Enhanced input processing with caching, validation, and error handling.
        
        Args:
            input_text: Input text to process
            
        Returns:
            Tuple of (state/tone string, response message or None)
        """
        self._total_requests += 1
        
        try:
            # Input validation
            if not input_text:
                return "Empty input", None
            
            if not isinstance(input_text, str):
                self.logger.warning(f"Invalid input type: {type(input_text)}")
                return "Invalid input type", None
            
            # Check for whitespace-only input (backward compatibility)
            if input_text.isspace():
                return "Empty input", None
            
            # Length validation
            if len(input_text) > config.MAX_INPUT_LENGTH:
                self.logger.warning(f"Input too long, truncating: {len(input_text)} chars")
                input_text = input_text[:config.MAX_INPUT_LENGTH]
            
            # Check cache first
            cache_key = f"input:{hash(input_text)}"
            cached_result = self._get_cached_response(cache_key)
            if cached_result:
                self.logger.debug(f"Cache hit for input: {input_text[:50]}...")
                # cached_result here is just the (state, tone) string.
                # The actual response needs to be regenerated or also cached.
                # For simplicity, let's assume tone is part of cached_result or extractable
                # This part might need refinement if we cache the full (state_str, response_text) tuple
                # For now, let's assume the cached_result is the (state, tone) and we fetch a fresh random banter
                # based on an assumed tone, or default.
                # Let's parse tone from cached_result if possible.
                tone_from_cache = "default"
                if cached_result and "Tone: " in cached_result:
                    try:
                        tone_from_cache = cached_result.split("Tone: ")[1].split(",")[0].strip()
                    except IndexError:
                        pass # Stick to default
                return cached_result, self.get_random_banter_enhanced(theme=tone_from_cache)
            
            # Enhanced emoji sequence detection
            sequence_tuple = self._extract_emoji_sequence_enhanced(input_text)
            
            # Fallback pattern matching with enhanced validation
            if not sequence_tuple and config.FALLBACK_ENABLED:
                sequence_tuple = self._fallback_pattern_matching(input_text)
            
            if sequence_tuple and sequence_tuple in self.sequence_map_data:
                sequence_info = self.sequence_map_data[sequence_tuple]
                state = sequence_info.get("state", "Unknown State")
                tone = sequence_info.get("tone", "default")
                
                # Validate state and tone
                if not isinstance(state, str) or not isinstance(tone, str):
                    self.logger.warning(f"Invalid sequence data for {sequence_tuple}")
                    state = "Unknown State"
                    tone = "default"
                
                result_str = f"State: {state}, Tone: {tone}"
                
                # Get response with fallback
                response = sequence_info.get("example")
                if not response or not isinstance(response, str):
                    self.logger.warning(f"No valid example for sequence {sequence_tuple}, using random banter with tone: {tone}")
                    response = self.get_random_banter_enhanced(theme=tone)
                else:
                    response = self._validate_response(response)
                    if not response:
                        response = self.get_random_banter_enhanced(theme=tone)
                    else:
                        # Append emoji sequence based on tone (action-tag)
                        action_tag_emojis = get_emoji_sequence(tone)
                        response = f"{response} {action_tag_emojis}".strip()
                
                # Cache the result
                self._cache_response(cache_key, result_str) # Consider caching (result_str, response) tuple
                self._successful_responses += 1
                
                return result_str, response
            else:
                result = "No sequence detected"
                self._cache_response(cache_key, result)
                # For "No sequence detected", we might still want a themed random banter
                # For now, it returns None, but could call get_random_banter_enhanced() with a default/neutral theme
                return result, self.get_random_banter_enhanced(theme="default") # Or return None if no response for "No sequence"
                
        except Exception as e:
            self.logger.error(f"Error processing input '{input_text[:50]}...': {e}")
            self._failed_responses += 1
            # Return a default themed response on error
            return "Processing error", self.get_random_banter_enhanced(theme="default")

    def _fallback_pattern_matching(self, input_text: str) -> Optional[Tuple[int, int, int]]:
        """Enhanced fallback pattern matching."""
        try:
            # More sophisticated pattern matching
            patterns = {
                "✊✋🖐️": (0, 1, 2),
                "✊✊✊": (0, 0, 0),
                "✋✋✋": (1, 1, 1),
                "🖐️🖐️🖐️": (2, 2, 2),
                "✊✊✋": (0, 0, 1),
                "✊✋✋": (0, 1, 1),
                "✋✊✊": (1, 0, 0),
            }
            
            for pattern, sequence in patterns.items():
                if pattern in input_text:
                    self.logger.debug(f"Fallback pattern matched: {pattern} -> {sequence}")
                    return sequence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in fallback pattern matching: {e}")
            return None

    def get_random_banter_enhanced(self, theme: str = "default") -> str:
        """
        Enhanced random banter generation with validation and fallback.
        
        Args:
            theme: Theme to get banter for
            
        Returns:
            Random banter message with action-tag emoji appended
        """
        final_response = "Thanks for the interaction! 😊" # Ultimate fallback
        try:
            # Validate theme
            if not theme or not isinstance(theme, str):
                theme = "default"
            
            # Get responses for theme with fallback
            responses = self._themes.get(theme)
            if not responses:
                self.logger.warning(f"No responses for theme '{theme}', using default")
                responses = self._themes.get("default", [])
            
            selected_response = None
            if responses:
                # Select random response with validation
                selected_response_candidate = random.choice(responses)
                validated_response_candidate = self._validate_response(selected_response_candidate)
                
                if validated_response_candidate:
                    selected_response = validated_response_candidate
                else:
                    # Fallback to first available valid response in the theme
                    for response_item in responses:
                        validated_item = self._validate_response(response_item)
                        if validated_item:
                            selected_response = validated_item
                            break
            
            if selected_response:
                final_response = selected_response
            else:
                self.logger.warning(f"No valid responses found for theme '{theme}' or default, using ultimate fallback.")
                # final_response remains the ultimate fallback
            
            # Append emoji sequence based on the theme (action-tag)
            action_tag_emojis = get_emoji_sequence(theme)
            return f"{final_response} {action_tag_emojis}".strip()
            
        except Exception as e:
            self.logger.error(f"Error generating random banter for theme '{theme}': {e}")
            # Return ultimate fallback with default emoji sequence on error
            action_tag_emojis = get_emoji_sequence("default")
            return f"{final_response} {action_tag_emojis}".strip()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_hit_rate = (self._cache_hits / (self._cache_hits + self._cache_misses)) * 100 if (self._cache_hits + self._cache_misses) > 0 else 0
        success_rate = (self._successful_responses / self._total_requests) * 100 if self._total_requests > 0 else 0
        
        return {
            "total_requests": self._total_requests,
            "successful_responses": self._successful_responses,
            "failed_responses": self._failed_responses,
            "success_rate_percent": round(success_rate, 2),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "cache_size": len(self._response_cache),
            "themes_count": len(self._themes),
            "total_responses": sum(len(responses) for responses in self._themes.values())
        }

    def clear_cache(self):
        """Clear the response cache."""
        self._response_cache.clear()
        self._cache_timestamps.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.logger.info("✅ Response cache cleared")

    def list_themes_enhanced(self) -> List[str]:
        """
        Get a list of available themes with validation.
        
        Returns:
            List of available theme names
        """
        try:
            themes = list(self._themes.keys())
            themes.sort()  # Sort for consistent output
            return themes
        except Exception as e:
            self.logger.error(f"Error listing themes: {e}")
            return ["default"]

    # Backward compatibility aliases
    process_input = process_input_enhanced
    get_random_banter = get_random_banter_enhanced
    list_themes = list_themes_enhanced
    _extract_emoji_sequence = _extract_emoji_sequence_enhanced 