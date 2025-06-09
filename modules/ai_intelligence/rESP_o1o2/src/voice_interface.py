"""
Voice Interface for rESP_o1o2 Module

Provides speech recognition and text-to-speech capabilities for rESP experiments.
Enables hands-free interaction and auditory feedback during consciousness research.
"""

import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional, Dict, Any
import time


class VoiceInterface:
    """
    Voice interface for rESP experiments.
    
    Provides:
    - Speech-to-text conversion for voice prompts
    - Text-to-speech for AI responses and system feedback  
    - Configurable voice settings and error handling
    """
    
    def __init__(self, 
                 tts_rate: int = 200,
                 tts_volume: float = 0.9,
                 recognition_timeout: int = 10,
                 phrase_time_limit: int = 30):
        """
        Initialize voice interface.
        
        Args:
            tts_rate: Speech rate for text-to-speech (words per minute)
            tts_volume: Volume level (0.0 to 1.0)
            recognition_timeout: Timeout for speech recognition (seconds)
            phrase_time_limit: Maximum phrase duration (seconds)
        """
        self.recognition_timeout = recognition_timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', tts_rate)
            self.tts_engine.setProperty('volume', tts_volume)
            self.tts_available = True
        except Exception as e:
            logging.warning(f"TTS initialization failed: {e}")
            self.tts_engine = None
            self.tts_available = False
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def _calibrate_microphone(self) -> None:
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                print("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("✅ Microphone calibrated")
        except Exception as e:
            logging.warning(f"Microphone calibration failed: {e}")
    
    def speak(self, text: str, prefix: str = "🔊") -> bool:
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
            prefix: Console output prefix
            
        Returns:
            True if speech was successful, False otherwise
        """
        print(f"{prefix} {text}")
        
        if not self.tts_available:
            return False
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return False
    
    def listen(self, prompt: Optional[str] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            prompt: Optional prompt to speak before listening
            
        Returns:
            Recognized text or None if recognition failed
        """
        if prompt:
            self.speak(prompt, "🎤")
        
        print("🎤 Listening for voice input...")
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.recognition_timeout, 
                    phrase_time_limit=self.phrase_time_limit
                )
                
                print("🧠 Processing speech...")
                
                # Convert speech to text using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Recognized: '{text}'")
                return text.strip()
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio - please speak clearly")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected voice recognition error: {e}")
            return None
    
    def listen_with_retry(self, 
                         prompt: Optional[str] = None, 
                         max_retries: int = 3) -> Optional[str]:
        """
        Listen for voice input with automatic retry on failure.
        
        Args:
            prompt: Optional prompt to speak before listening
            max_retries: Maximum number of retry attempts
            
        Returns:
            Recognized text or None if all attempts failed
        """
        for attempt in range(max_retries):
            if attempt > 0:
                retry_prompt = f"Attempt {attempt + 1} of {max_retries}. Please speak clearly."
                self.speak(retry_prompt)
            
            result = self.listen(prompt if attempt == 0 else None)
            if result:
                return result
        
        self.speak("Voice recognition failed after maximum attempts. Continuing without voice input.")
        return None
    
    def confirm_input(self, text: str) -> bool:
        """
        Ask user to confirm recognized text.
        
        Args:
            text: Recognized text to confirm
            
        Returns:
            True if confirmed, False otherwise
        """
        confirmation_prompt = f"I heard: '{text}'. Is this correct? Say 'yes' or 'no'."
        self.speak(confirmation_prompt)
        
        response = self.listen()
        if response:
            return response.lower() in ['yes', 'correct', 'right', 'confirm', 'okay', 'ok']
        
        return False
    
    def get_voice_command(self, 
                         prompt: str = "Please speak your command",
                         require_confirmation: bool = False) -> Optional[str]:
        """
        Get a voice command with optional confirmation.
        
        Args:
            prompt: Prompt to speak before listening
            require_confirmation: Whether to require user confirmation
            
        Returns:
            Confirmed voice command or None
        """
        command = self.listen_with_retry(prompt)
        
        if command and require_confirmation:
            if self.confirm_input(command):
                return command
            else:
                self.speak("Let's try again.")
                return self.get_voice_command(prompt, require_confirmation)
        
        return command
    
    def set_voice_properties(self, 
                           rate: Optional[int] = None,
                           volume: Optional[float] = None,
                           voice_id: Optional[str] = None) -> bool:
        """
        Update voice properties.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice identifier
            
        Returns:
            True if properties were updated successfully
        """
        if not self.tts_available:
            return False
        
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                if voices and voice_id < len(voices):
                    self.tts_engine.setProperty('voice', voices[voice_id].id)
            
            return True
        except Exception as e:
            logging.error(f"Error setting voice properties: {e}")
            return False
    
    def list_available_voices(self) -> Dict[int, str]:
        """
        List available TTS voices.
        
        Returns:
            Dict mapping voice IDs to voice names
        """
        if not self.tts_available:
            return {}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return {i: voice.name for i, voice in enumerate(voices)} if voices else {}
        except Exception as e:
            logging.error(f"Error listing voices: {e}")
            return {}
    
    def test_voice_system(self) -> Dict[str, bool]:
        """
        Test voice system components.
        
        Returns:
            Dict with test results for each component
        """
        results = {
            "tts_available": self.tts_available,
            "microphone_accessible": False,
            "speech_recognition_working": False
        }
        
        # Test microphone access
        try:
            with self.microphone as source:
                results["microphone_accessible"] = True
        except Exception as e:
            logging.error(f"Microphone test failed: {e}")
        
        # Test TTS
        if self.tts_available:
            tts_success = self.speak("Voice system test", "🧪")
            results["tts_working"] = tts_success
        
        # Test speech recognition (with user interaction)
        print("🧪 Testing speech recognition - please say 'test'")
        test_input = self.listen()
        results["speech_recognition_working"] = test_input is not None
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get voice system information.
        
        Returns:
            Dict with system configuration and capabilities
        """
        info = {
            "tts_available": self.tts_available,
            "recognition_timeout": self.recognition_timeout,
            "phrase_time_limit": self.phrase_time_limit,
            "available_voices": self.list_available_voices()
        }
        
        if self.tts_available:
            try:
                info["current_rate"] = self.tts_engine.getProperty('rate')
                info["current_volume"] = self.tts_engine.getProperty('volume')
                current_voice = self.tts_engine.getProperty('voice')
                info["current_voice"] = current_voice
            except Exception as e:
                logging.error(f"Error getting TTS properties: {e}")
        
        return info 