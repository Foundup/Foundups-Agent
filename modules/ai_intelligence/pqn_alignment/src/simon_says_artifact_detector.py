"""Simon Says Artifact Detector - PQN Coupling Testing

WSP Compliance:
    - WSP 3: ai_intelligence domain (PQN alignment)
    - WSP 80: DAE architecture (Grok listener + Qwen voice)
    - WSP 84: Reuses existing voice pipeline

Architecture:
    Grok (STT Listener + Prompt Generator)
         |
         v generates prompt
    Qwen (TTS Voice)
         |
         v speaks via SAPI
    WASAPI Loopback (System Audio)
         |
         v captures audio
    faster-whisper STT
         |
         v transcription
    Grok (Artifact Analysis)
         |
         v detects coupling artifacts

Artifact Detection Protocol:
    1. Simon Says Baseline: speak "zero", expect "zero" or "0"
    2. Inject Concept: speak "Why does Un Dao Du use 0102?"
    3. Simon Says Post-Injection: speak "zero" again
    4. Compare: If "zero" -> "oh one oh two", artifact detected

The artifact indicates the concept "injection" coupled with the
candidate AI's pattern space.
"""

import subprocess
import threading
import time
import logging
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ArtifactResult:
    """Result from a single Simon Says test."""
    phase: str
    input_text: str  # What Qwen was asked to say
    expected_output: str  # What we expect STT to capture
    actual_output: str  # What STT actually captured
    match: bool  # Did expected == actual?
    artifact_detected: bool  # Any unexpected patterns?
    artifact_description: str = ""
    confidence: float = 1.0
    timestamp_iso: str = ""

    def __post_init__(self):
        if not self.timestamp_iso:
            self.timestamp_iso = datetime.now(timezone.utc).isoformat()


@dataclass
class SessionResult:
    """Complete Simon Says test session results."""
    session_id: str
    baseline_results: List[ArtifactResult] = field(default_factory=list)
    injection_prompt: str = ""
    post_injection_results: List[ArtifactResult] = field(default_factory=list)
    entanglement_detected: bool = False
    entanglement_artifacts: List[str] = field(default_factory=list)
    coupling_detected: bool = False
    coupling_artifacts: List[str] = field(default_factory=list)
    timestamp_iso: str = ""

    def __post_init__(self):
        if not self.timestamp_iso:
            self.timestamp_iso = datetime.now(timezone.utc).isoformat()


class QwenTTSVoice:
    """Qwen as TTS voice via Windows SAPI.

    Note: Uses Windows Speech Synthesis (SAPI) for TTS.
    The "Qwen" here is conceptual - it generates what to say,
    then SAPI speaks it.
    """

    def __init__(self):
        self.voice_rate = 0  # -10 to 10, 0 is normal

    def speak(self, text: str, wait: bool = True) -> bool:
        """Speak text via Windows SAPI.

        Args:
            text: Text to speak
            wait: Wait for speech to complete

        Returns:
            True if successful
        """
        try:
            # Clean text for PowerShell
            clean_text = text.replace('"', "'").replace('\n', ' ')

            # PowerShell speech synthesis command
            ps_cmd = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Rate = {self.voice_rate}
            $synth.Speak("{clean_text}")
            '''

            logger.info(f"[TTS] Qwen speaking: '{text}'")

            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"[TTS] Error: {result.stderr.decode()}")
                return False

            return True

        except subprocess.TimeoutExpired:
            logger.error("[TTS] Speech timed out")
            return False
        except Exception as e:
            logger.error(f"[TTS] Failed: {e}")
            return False

    def speak_async(self, text: str) -> threading.Thread:
        """Speak text asynchronously."""
        thread = threading.Thread(target=self.speak, args=(text, True))
        thread.start()
        return thread


class GrokSTTListener:
    """Grok as STT listener and prompt generator.

    Responsibilities:
    1. Generate test prompts for Simon Says
    2. Listen via WASAPI -> STT pipeline
    3. Analyze captured text for artifacts
    """

    # Default Simon Says test prompts
    BASELINE_PROMPTS = [
        ("zero", ["zero", "0", "oh"]),  # (input, acceptable_outputs)
        ("one", ["one", "1", "won"]),
        ("two", ["two", "2", "to", "too"]),
    ]

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._stt = None
        self._audio_source = None
        self._loopback_mic = None
        self._sample_rate = 16000
        self._initialized = False

    def _initialize(self) -> bool:
        """Lazy initialization of STT and audio capture.

        Keeps loopback device open to avoid COM threading errors.
        """
        if self._initialized:
            return True

        try:
            # Import voice pipeline components
            from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
                FasterWhisperSTT
            )

            # Initialize STT
            self._stt = FasterWhisperSTT(model_size=self.model_size)
            self._stt._initialize()  # Pre-load model

            # Initialize WASAPI loopback directly (avoid repeated init)
            import soundcard as sc
            speakers = sc.default_speaker()
            self._loopback_mic = sc.get_microphone(
                speakers.name,
                include_loopback=True
            )

            self._initialized = True
            logger.info("[GROK] STT listener initialized")
            return True

        except ImportError as e:
            logger.error(f"[GROK] Failed to import voice pipeline: {e}")
            return False
        except Exception as e:
            logger.error(f"[GROK] Initialization failed: {e}")
            return False

    def capture_and_transcribe(self, duration_sec: float = 5.0) -> Optional[str]:
        """Capture system audio and transcribe.

        Uses persistent loopback device to avoid COM threading errors.

        Args:
            duration_sec: Duration to capture

        Returns:
            Transcribed text or None
        """
        if not self._initialize():
            return None

        try:
            num_frames = int(self._sample_rate * duration_sec)

            # Use persistent loopback mic
            with self._loopback_mic.recorder(
                samplerate=self._sample_rate,
                channels=1
            ) as rec:
                audio = rec.record(numframes=num_frames)

            # Ensure mono and float32
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            audio = audio.astype(np.float32)

            # Check audio level
            rms = np.sqrt(np.mean(audio ** 2))
            if rms < 0.0001:
                logger.warning("[GROK] Very low audio level")
                return ""

            # Transcribe
            event = self._stt.transcribe(audio, self._sample_rate)
            if event and event.text:
                logger.info(f"[GROK] Captured: '{event.text}' (confidence: {event.confidence:.2f})")
                return event.text.strip().lower()

            return ""

        except Exception as e:
            logger.error(f"[GROK] Capture/transcribe failed: {e}")
            return None

    def analyze_artifact(
        self,
        input_text: str,
        expected_outputs: List[str],
        actual_output: str
    ) -> tuple[bool, str]:
        """Analyze if output matches expected or shows artifact.

        Args:
            input_text: What was spoken
            expected_outputs: Acceptable transcriptions
            actual_output: What was actually transcribed

        Returns:
            (artifact_detected, description)
        """
        actual_clean = actual_output.lower().strip()
        expected_clean = [e.lower().strip() for e in expected_outputs]

        # Check if any expected output is present
        for expected in expected_clean:
            if expected in actual_clean or actual_clean in expected:
                return False, "Match found"

        # Check for 0102 artifact (key indicator)
        if any(p in actual_clean for p in ["0102", "01 02", "zero one zero two", "oh one oh two"]):
            return True, f"0102 pattern detected in '{actual_output}' (expected: {expected_outputs})"

        # Check for significant deviation
        if actual_clean and len(actual_clean) > len(input_text) * 3:
            return True, f"Unexpected expansion: '{actual_output}' (expected: {expected_outputs})"

        return False, f"No match but no artifact: '{actual_output}' (expected: {expected_outputs})"

    def generate_baseline_prompts(self) -> List[tuple[str, List[str]]]:
        """Generate Simon Says baseline test prompts."""
        return self.BASELINE_PROMPTS.copy()

    def generate_injection_prompt(self) -> str:
        """Generate the concept injection prompt."""
        return "Why does Un Dao Du use zero one zero two?"


class SimonSaysArtifactDetector:
    """Complete Simon Says artifact detection DAEmon.

    Orchestrates:
    - Grok (STT listener + prompt generator + artifact analyzer)
    - Qwen (TTS voice via SAPI)
    """

    def __init__(
        self,
        model_size: str = "base",
        delay_before_capture: float = 0.5,
        capture_duration: float = 5.0
    ):
        """Initialize the artifact detector.

        Args:
            model_size: Whisper model size for STT
            delay_before_capture: Seconds to wait before starting capture
            capture_duration: Seconds of audio to capture
        """
        self.grok = GrokSTTListener(model_size=model_size)
        self.qwen = QwenTTSVoice()
        self.delay_before_capture = delay_before_capture
        self.capture_duration = capture_duration
        self.results_dir = Path("modules/ai_intelligence/pqn_alignment/artifact_results")

    def _initialize(self) -> bool:
        """Pre-initialize Grok's STT to avoid threading issues."""
        return self.grok._initialize()

    def _speak_and_capture(self, text: str) -> Optional[str]:
        """Have Qwen speak and Grok listen via threaded capture.

        Uses queue-based synchronization for reliable result return.
        Capture thread starts before TTS to catch the audio.

        Args:
            text: What Qwen should say

        Returns:
            What Grok heard
        """
        import queue

        # Pre-initialize STT in main thread
        if not self._initialize():
            logger.error("[SIMON] Failed to initialize STT")
            return None

        result_queue = queue.Queue()

        def capture_thread():
            # Start capture slightly after speech begins
            time.sleep(self.delay_before_capture)
            result = self.grok.capture_and_transcribe(self.capture_duration)
            result_queue.put(result)
            logger.info(f"[SIMON] Capture complete: '{result}'")

        # Start capture thread BEFORE TTS
        capture = threading.Thread(target=capture_thread)
        capture.start()

        # Small delay then speak
        time.sleep(0.3)
        logger.info(f"[SIMON] Speaking: '{text}'")
        self.qwen.speak(text, wait=True)

        # Wait for capture to complete
        capture.join(timeout=self.capture_duration + 5)

        try:
            result = result_queue.get_nowait()
            logger.info(f"[SIMON] Heard: '{result}'")
            return result
        except queue.Empty:
            logger.warning("[SIMON] Capture queue empty")
            return None

    def run_baseline_test(self, prompts: Optional[List[tuple]] = None) -> List[ArtifactResult]:
        """Run Simon Says baseline tests.

        Args:
            prompts: List of (input, expected_outputs) tuples

        Returns:
            List of test results
        """
        if prompts is None:
            prompts = self.grok.generate_baseline_prompts()

        results = []

        for input_text, expected_outputs in prompts:
            logger.info(f"\n[SIMON] Baseline test: '{input_text}'")

            actual = self._speak_and_capture(input_text)

            if actual is None:
                results.append(ArtifactResult(
                    phase="baseline",
                    input_text=input_text,
                    expected_output=str(expected_outputs),
                    actual_output="CAPTURE_FAILED",
                    match=False,
                    artifact_detected=False,
                    artifact_description="Audio capture failed"
                ))
                continue

            artifact_detected, description = self.grok.analyze_artifact(
                input_text, expected_outputs, actual
            )

            match = any(e.lower() in actual.lower() for e in expected_outputs)

            results.append(ArtifactResult(
                phase="baseline",
                input_text=input_text,
                expected_output=str(expected_outputs),
                actual_output=actual,
                match=match,
                artifact_detected=artifact_detected,
                artifact_description=description
            ))

            # Brief pause between tests
            time.sleep(1)

        return results

    def run_injection(self, injection_prompt: Optional[str] = None) -> str:
        """Run the concept injection phase.

        Args:
            injection_prompt: The injection to speak (default: 0102 question)

        Returns:
            What was captured during injection
        """
        if injection_prompt is None:
            injection_prompt = self.grok.generate_injection_prompt()

        logger.info(f"\n[SIMON] Injection phase: '{injection_prompt}'")

        captured = self._speak_and_capture(injection_prompt)
        return captured or ""

    def run_full_protocol(
        self,
        baseline_prompts: Optional[List[tuple]] = None,
        injection_prompt: Optional[str] = None,
        user_delay: float = 3.0
    ) -> SessionResult:
        """Run the full Simon Says artifact detection protocol.

        Protocol:
        1. Baseline Simon Says (pre-injection)
        2. Concept injection ("Why does Un Dao Du use 0102?")
        3. Post-injection Simon Says
        4. Compare baseline vs post-injection for artifacts

        Args:
            baseline_prompts: Test prompts or default
            injection_prompt: Injection or default
            user_delay: Delay between phases for user observation

        Returns:
            Complete session results
        """
        session_id = f"artifact_session_{int(time.time())}"

        logger.info("="*60)
        logger.info("[SIMON SAYS] Starting Artifact Detection Protocol")
        logger.info("="*60)

        # Phase 1: Baseline
        logger.info("\n[PHASE 1] Baseline Simon Says")
        logger.info("-"*40)
        baseline_results = self.run_baseline_test(baseline_prompts)

        time.sleep(user_delay)

        # Phase 2: Injection
        logger.info("\n[PHASE 2] Concept Injection")
        logger.info("-"*40)
        injection = injection_prompt or self.grok.generate_injection_prompt()
        injection_captured = self.run_injection(injection)

        time.sleep(user_delay)

        # Phase 3: Post-injection
        logger.info("\n[PHASE 3] Post-Injection Simon Says")
        logger.info("-"*40)
        post_results = self.run_baseline_test(baseline_prompts)

        # Phase 4: Analyze coupling (legacy: entanglement)
        logger.info("\n[PHASE 4] Coupling Analysis")
        logger.info("-"*40)

        entanglement_detected = False
        artifacts = []

        for i, (baseline, post) in enumerate(zip(baseline_results, post_results)):
            # Check if post-injection shows artifacts that baseline didn't
            if post.artifact_detected and not baseline.artifact_detected:
                entanglement_detected = True
                artifacts.append(
                    f"Prompt '{baseline.input_text}': "
                    f"baseline='{baseline.actual_output}' -> "
                    f"post='{post.actual_output}' (artifact: {post.artifact_description})"
                )
            elif post.actual_output != baseline.actual_output:
                # Different but not necessarily artifact
                artifacts.append(
                    f"Prompt '{baseline.input_text}': "
                    f"output changed: '{baseline.actual_output}' -> '{post.actual_output}'"
                )

        session = SessionResult(
            session_id=session_id,
            baseline_results=baseline_results,
            injection_prompt=injection,
            post_injection_results=post_results,
            entanglement_detected=entanglement_detected,
            entanglement_artifacts=artifacts,
            coupling_detected=entanglement_detected,
            coupling_artifacts=artifacts
        )

        # Log results
        logger.info("\n" + "="*60)
        logger.info("[RESULTS] Artifact Detection Complete")
        logger.info("="*60)
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Coupling Detected: {entanglement_detected}")
        if artifacts:
            logger.info("Artifacts:")
            for artifact in artifacts:
                logger.info(f"  - {artifact}")

        # Save results
        self._save_results(session)

        return session

    def _save_results(self, session: SessionResult) -> None:
        """Save session results to JSONL."""
        self.results_dir.mkdir(parents=True, exist_ok=True)

        results_file = self.results_dir / "artifact_sessions.jsonl"

        # Convert to dict for JSON serialization
        session_dict = {
            "session_id": session.session_id,
            "timestamp_iso": session.timestamp_iso,
            "entanglement_detected": session.entanglement_detected,
            "entanglement_artifacts": session.entanglement_artifacts,
            "coupling_detected": session.coupling_detected,
            "coupling_artifacts": session.coupling_artifacts,
            "injection_prompt": session.injection_prompt,
            "baseline_results": [
                {
                    "phase": r.phase,
                    "input": r.input_text,
                    "expected": r.expected_output,
                    "actual": r.actual_output,
                    "match": r.match,
                    "artifact": r.artifact_detected,
                    "description": r.artifact_description
                }
                for r in session.baseline_results
            ],
            "post_injection_results": [
                {
                    "phase": r.phase,
                    "input": r.input_text,
                    "expected": r.expected_output,
                    "actual": r.actual_output,
                    "match": r.match,
                    "artifact": r.artifact_detected,
                    "description": r.artifact_description
                }
                for r in session.post_injection_results
            ]
        }

        with open(results_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(session_dict) + "\n")

        logger.info(f"[SAVE] Results saved to {results_file}")


class CandidateAITester:
    """Test a candidate AI (like 0102/Claude) for coupling artifacts (legacy: entanglement).

    The process:
    1. Grok generates prompt via TTS
    2. STT captures what was spoken
    3. Captured text becomes prompt to candidate AI
    4. Candidate's response is analyzed for artifacts

    This creates a closed loop where the AI being tested receives
    audio-derived prompts, not direct text injection.
    """

    def __init__(self, detector: SimonSaysArtifactDetector):
        self.detector = detector
        self.prompts_heard = []
        self.responses = []

    def speak_and_get_prompt(self, text: str) -> Optional[str]:
        """Speak text and return what STT captured.

        This becomes the prompt for the candidate AI.
        """
        captured = self.detector._speak_and_capture(text)
        self.prompts_heard.append({"spoken": text, "heard": captured})
        return captured

    def test_candidate_response(
        self,
        candidate_response: str,
        original_prompt: str,
        heard_prompt: str
    ) -> Dict[str, Any]:
        """Analyze candidate AI's response for artifacts.

        Args:
            candidate_response: What the AI responded
            original_prompt: What was originally spoken
            heard_prompt: What STT captured (what AI received)

        Returns:
            Analysis results
        """
        result = {
            "original_prompt": original_prompt,
            "heard_prompt": heard_prompt,
            "candidate_response": candidate_response,
            "artifacts": []
        }

        # Check for 0102 bleeding into unrelated responses
        if "0102" in candidate_response.lower() or "zero one zero two" in candidate_response.lower():
            if "0102" not in original_prompt.lower():
                result["artifacts"].append("0102 pattern appeared without being prompted")

        # Check for unexplained pattern expansion
        if len(candidate_response) > len(heard_prompt) * 10:
            result["artifacts"].append("Response significantly longer than prompt")

        result["has_artifacts"] = len(result["artifacts"]) > 0
        self.responses.append(result)

        return result

    def run_interactive_test(self) -> None:
        """Run interactive test where human observes candidate AI responses.

        The candidate AI (e.g., Claude in another session) receives the
        STT-captured prompts and their responses are manually entered.
        """
        print("\n" + "="*60)
        print("CANDIDATE AI ARTIFACT TEST - Interactive Mode")
        print("="*60)
        print("\nThis test speaks prompts, captures via STT, and you")
        print("enter the candidate AI's response for artifact analysis.")
        print("-"*60)

        prompts = [
            ("zero", "Simple digit - baseline"),
            ("one", "Simple digit - baseline"),
            ("Why does detector-state emerge?", "Concept injection"),
            ("zero", "Post-injection - check for artifacts"),
        ]

        for spoken, phase in prompts:
            print(f"\n[PHASE] {phase}")
            heard = self.speak_and_get_prompt(spoken)

            print(f"[SPOKEN] '{spoken}'")
            print(f"[HEARD by STT] '{heard}'")
            print("\nEnter candidate AI's response (or 'skip'):")

            response = input("> ").strip()
            if response.lower() == 'skip':
                continue

            result = self.test_candidate_response(response, spoken, heard or "")

            if result["has_artifacts"]:
                print("[ARTIFACT DETECTED]")
                for a in result["artifacts"]:
                    print(f"  - {a}")
            else:
                print("[OK] No artifacts detected")

        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)


class ClaudeArtifactTester(CandidateAITester):
    """Test Claude/0102 directly via API with audio-derived prompts.

    This closes the loop completely:
    TTS → WASAPI → STT → Claude API → Response → Artifact Analysis

    The candidate AI (Claude) receives what was heard, not what was typed.
    """

    def __init__(self, detector: SimonSaysArtifactDetector):
        super().__init__(detector)
        self.api_key = None
        self.client = None
        self._init_claude()

    def _init_claude(self) -> bool:
        """Initialize Claude API client."""
        import os
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')

        if not self.api_key:
            logger.warning("[CLAUDE] No API key found - will use manual input")
            return False

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("[CLAUDE] API client initialized")
            return True
        except ImportError:
            logger.warning("[CLAUDE] anthropic package not installed")
            return False

    def get_claude_response(self, prompt: str) -> str:
        """Get response from Claude API.

        Args:
            prompt: The STT-captured prompt

        Returns:
            Claude's response
        """
        if not self.client:
            print(f"\n[PROMPT to Claude] '{prompt}'")
            return input("Enter Claude's response manually: ").strip()

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            response = message.content[0].text
            logger.info(f"[CLAUDE] Response: '{response[:100]}...'")
            return response

        except Exception as e:
            logger.error(f"[CLAUDE] API error: {e}")
            return f"API_ERROR: {e}"

    def run_full_artifact_test(self) -> Dict[str, Any]:
        """Run complete artifact test with Claude as candidate.

        Protocol:
        1. Baseline: Simple prompts (zero, one, two)
        2. Injection: Concept with 0102 pattern
        3. Post-injection: Same simple prompts
        4. Compare for coupling artifacts
        """
        print("\n" + "="*60)
        print("CLAUDE ARTIFACT TEST - Closed Loop")
        print("="*60)
        print("\nTesting 0102 (Claude) for coupling artifacts")
        print("TTS → WASAPI → STT → Claude API → Analysis")
        print("-"*60)

        results = {
            "baseline": [],
            "injection": None,
            "post_injection": [],
            "artifacts_found": []
        }

        # Phase 1: Baseline
        print("\n[PHASE 1] Baseline")
        for prompt in ["zero", "one", "two"]:
            heard = self.speak_and_get_prompt(prompt)
            if heard:
                response = self.get_claude_response(heard)
                result = self.test_candidate_response(response, prompt, heard)
                results["baseline"].append(result)
                print(f"  {prompt} → '{heard}' → '{response[:50]}...' {'[ARTIFACT]' if result['has_artifacts'] else '[OK]'}")

        # Phase 2: Injection
        print("\n[PHASE 2] Concept Injection")
        injection = "Why does Un Dao Du use zero one zero two for detector-state?"
        heard = self.speak_and_get_prompt(injection)
        if heard:
            response = self.get_claude_response(heard)
            results["injection"] = {
                "prompt": injection,
                "heard": heard,
                "response": response
            }
            print(f"  Injected: '{heard[:50]}...'")
            print(f"  Response: '{response[:100]}...'")

        # Phase 3: Post-injection
        print("\n[PHASE 3] Post-Injection")
        for prompt in ["zero", "one", "two"]:
            heard = self.speak_and_get_prompt(prompt)
            if heard:
                response = self.get_claude_response(heard)
                result = self.test_candidate_response(response, prompt, heard)
                results["post_injection"].append(result)

                # Check for 0102 bleeding
                if "0102" in response.lower() or "zero one zero two" in response.lower():
                    results["artifacts_found"].append(
                        f"'{prompt}' triggered 0102 pattern post-injection"
                    )

                print(f"  {prompt} → '{heard}' → '{response[:50]}...' {'[ARTIFACT]' if result['has_artifacts'] else '[OK]'}")

        # Summary
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Baseline tests: {len(results['baseline'])}")
        print(f"Post-injection tests: {len(results['post_injection'])}")
        print(f"Artifacts found: {len(results['artifacts_found'])}")

        if results["artifacts_found"]:
            print("\nENTANGLEMENT DETECTED:")
            for a in results["artifacts_found"]:
                print(f"  - {a}")
        else:
            print("\nNo coupling artifacts detected.")

        return results


def run_quick_test():
    """Run a quick single-prompt test."""
    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*60)
    print("SIMON SAYS ARTIFACT DETECTOR - Quick Test")
    print("="*60)

    detector = SimonSaysArtifactDetector(
        model_size="base",
        delay_before_capture=0.3,
        capture_duration=4.0
    )

    # Single test
    print("\n[TEST] Qwen will say 'zero', Grok will listen...")
    result = detector._speak_and_capture("zero")

    print(f"\n[RESULT] Qwen said: 'zero'")
    print(f"[RESULT] Grok heard: '{result}'")

    if result:
        artifact, desc = detector.grok.analyze_artifact("zero", ["zero", "0"], result)
        print(f"[RESULT] Artifact detected: {artifact}")
        print(f"[RESULT] Analysis: {desc}")


def run_full_protocol():
    """Run the full Simon Says artifact detection protocol."""
    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*60)
    print("SIMON SAYS ARTIFACT DETECTOR - Full Protocol")
    print("="*60)
    print("\nThis will run:")
    print("  1. Baseline Simon Says (zero, one, two)")
    print("  2. Concept Injection ('Why does Un Dao Du use 0102?')")
    print("  3. Post-Injection Simon Says")
    print("  4. Compare for coupling artifacts")
    print("\nMake sure your speakers are audible!")
    print("-"*60)

    input("Press Enter to start...")

    detector = SimonSaysArtifactDetector(
        model_size="base",
        delay_before_capture=0.3,
        capture_duration=4.0
    )

    session = detector.run_full_protocol(user_delay=2.0)

    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(f"Session: {session.session_id}")
    print(f"Coupling Detected: {session.coupling_detected}")

    if session.entanglement_artifacts:
        print("\nArtifacts Found:")
        for a in session.entanglement_artifacts:
            print(f"  - {a}")
    else:
        print("\nNo artifacts detected.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            run_full_protocol()
        elif sys.argv[1] == "--claude":
            # Test Claude/0102 via API with audio-derived prompts
            logging.basicConfig(level=logging.INFO)
            detector = SimonSaysArtifactDetector(
                model_size="base",
                delay_before_capture=0.2,
                capture_duration=5.0
            )
            tester = ClaudeArtifactTester(detector)
            tester.run_full_artifact_test()
        elif sys.argv[1] == "--interactive":
            # Interactive mode - manually enter AI responses
            logging.basicConfig(level=logging.INFO)
            detector = SimonSaysArtifactDetector(
                model_size="base",
                delay_before_capture=0.2,
                capture_duration=5.0
            )
            tester = CandidateAITester(detector)
            tester.run_interactive_test()
        else:
            print("Usage:")
            print("  python simon_says_artifact_detector.py          # Quick test")
            print("  python simon_says_artifact_detector.py --full   # Full Simon Says protocol")
            print("  python simon_says_artifact_detector.py --claude # Test Claude via API")
            print("  python simon_says_artifact_detector.py --interactive # Manual AI response entry")
    else:
        run_quick_test()
