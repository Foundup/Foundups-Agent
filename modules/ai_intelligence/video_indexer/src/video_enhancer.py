# -*- coding: utf-8 -*-
"""
Video Enhancer - Enhance existing video JSON for Digital Twin training.

WSP Compliance:
    WSP 77: Agent Coordination (Digital Twin training)
    WSP 84: Code Reuse (uses LLMConnector for multi-provider support)

Purpose:
    Run 8 enhancement questions on existing video JSON to extract:
    - Verbatim quotes (Q1)
    - Intent labels (Q2)
    - Quotable moments (Q3)
    - Comment triggers (Q4)
    - Q&A moments (Q5)
    - Reply signals (Q6)
    - Teaching moments (Q7)
    - Style fingerprint (Q8)
    
Supported LLM Providers:
    - Grok (xAI) - GROK_API_KEY
    - Gemini (Google) - GOOGLE_API_KEY
    - Claude (Anthropic) - ANTHROPIC_API_KEY
    - GPT (OpenAI) - OPENAI_API_KEY
"""

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load .env file for API keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, keys must be in environment

logger = logging.getLogger(__name__)

# Import LLMConnector for multi-provider support (WSP 84)
try:
    from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
    LLM_AVAILABLE = True
except ImportError:
    LLMConnector = None
    LLM_AVAILABLE = False
    logger.warning("[ENHANCER] LLMConnector not available")


@dataclass
class VoicePatterns:
    """012's speaking patterns."""
    signature_phrases: List[str] = field(default_factory=list)
    filler_words: List[str] = field(default_factory=list)
    sentence_starters: List[str] = field(default_factory=list)
    emphatic_words: List[str] = field(default_factory=list)
    speaking_pace: str = "medium"


@dataclass
class StyleFingerprint:
    """Style metrics for the speaker."""
    formality: float = 0.5
    energy: float = 0.5
    humor: float = 0.3
    personal_sharing: float = 0.5
    technical_depth: float = 0.5
    analogy_usage: float = 0.5
    sentence_length: str = "medium"


@dataclass
class TrainingEnhancements:
    """All training data enhancements for a video."""
    is_012_content: bool = True
    quality_tier: int = 1  # 0=LOW, 1=MED, 2=HIGH
    voice_patterns: Optional[VoicePatterns] = None
    style_fingerprint: Optional[StyleFingerprint] = None
    intent_labels: List[Dict[str, Any]] = field(default_factory=list)
    quotable_moments: List[Dict[str, Any]] = field(default_factory=list)
    comment_triggers: List[Dict[str, Any]] = field(default_factory=list)
    qa_moments: List[Dict[str, Any]] = field(default_factory=list)
    teaching_moments: List[Dict[str, Any]] = field(default_factory=list)
    verbatim_quotes: List[Dict[str, Any]] = field(default_factory=list)


class VideoEnhancer:
    """
    Enhance video JSON with training data using Gemini.
    
    Runs 8 enhancement prompts to extract training-relevant data
    from existing indexed videos.
    
    Example:
        >>> enhancer = VideoEnhancer()
        >>> result = enhancer.enhance_video("path/to/video.json")
    """
    
    # Enhancement prompts - NOTE: Double braces {{ }} escape for .format()
    PROMPTS = {
        "style_fingerprint": """Analyze the speaker's style in this video content.
Return JSON:
{{
  "formality": 0.3,
  "energy": 0.7,
  "humor": 0.4,
  "personal_sharing": 0.8,
  "technical_depth": 0.5,
  "analogy_usage": 0.9,
  "sentence_length": "medium",
  "speaking_pace": "medium"
}}

Video content:
{content}""",

        "voice_patterns": """Extract the speaker's vocabulary patterns from this video.
Return JSON:
{{
  "signature_phrases": ["phrase1", "phrase2"],
  "filler_words": ["uh", "you know"],
  "sentence_starters": ["So", "The thing is"],
  "emphatic_words": ["awesome", "important"]
}}

Video content:
{content}""",

        "intent_labels": """Classify the TOP 5 most important segment intents only.
Return JSON with exactly this format:
{{
  "intents": [
    {{"segment_idx": 0, "intent": "personal_disclosure", "confidence": 0.9}},
    {{"segment_idx": 2, "intent": "analogy", "confidence": 0.85}},
    {{"segment_idx": 5, "intent": "call_to_action", "confidence": 0.95}}
  ]
}}

Intent options: inform, persuade, joke, story, question, call_to_action, personal_disclosure, technical_explanation, opinion, analogy

Only return TOP 5 most distinctive intents. Keep response short.

Segments:
{segments}""",

        "quotable_moments": """Identify the most memorable/quotable moments.
Return JSON:
{{
  "quotables": [
    {{"segment_idx": 0, "text": "exact quote", "category": "philosophical", "shareability": 0.9}}
  ]
}}

Segments:
{segments}""",

        "comment_triggers": """Which parts would likely generate viewer comments?
Return JSON:
{{
  "triggers": [
    {{"segment_idx": 0, "trigger_type": "controversial_opinion", "engagement_score": 0.8}}
  ]
}}

Segments:
{segments}""",

        "qa_moments": """Identify questions asked or answered in this video.
Return JSON:
{{
  "questions": [
    {{"segment_idx": 0, "question": "the question", "question_type": "rhetorical", "answered": true, "answer_segment_idx": 1}}
  ]
}}

Segments:
{segments}""",

        "teaching_moments": """Identify moments where the speaker teaches or explains concepts.
Return JSON:
{{
  "teachings": [
    {{"segment_idx": 0, "concept": "what is taught", "complexity": "beginner", "uses_analogy": true, "key_terms": ["term1"]}}
  ]
}}

Segments:
{segments}""",

        "verbatim_quotes": """Extract EXACT memorable quotes from this content.
Return JSON:
{{
  "quotes": [
    {{"segment_idx": 0, "exact_text": "the exact words spoken", "intent": "opinion"}}
  ]
}}

Focus on impactful statements, not summaries.

Segments:
{segments}"""
    }

    def __init__(
        self,
        model: str = "grok-3-latest",  # Default to Grok, also supports: gemini-2.0-flash, claude-3-sonnet, gpt-4
        max_tokens: int = 2048,
        temperature: float = 0.3
    ):
        """
        Initialize enhancer with multi-provider LLM support.
        
        Args:
            model: Model identifier. Supported:
                   - grok-3-latest (xAI) - uses GROK_API_KEY
                   - gemini-2.0-flash-exp (Google) - uses GOOGLE_API_KEY
                   - claude-3-sonnet-20240229 (Anthropic) - uses ANTHROPIC_API_KEY
                   - gpt-4 (OpenAI) - uses OPENAI_API_KEY
            max_tokens: Maximum response tokens
            temperature: Response temperature (0.0-1.0)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm = None
        
        if LLM_AVAILABLE and LLMConnector:
            self.llm = LLMConnector(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            if not getattr(self.llm, 'simulation_mode', True):
                logger.info(f"[ENHANCER] LLM initialized: {self.llm.provider}/{model}")
            else:
                logger.warning(f"[ENHANCER] LLM in simulation mode: {model}")
        else:
            logger.error("[ENHANCER] LLMConnector not available")
    
    def enhance_video(
        self,
        video_json_path: str,
        save: bool = True
    ) -> Optional[TrainingEnhancements]:
        """
        Enhance a single video JSON.
        
        Args:
            video_json_path: Path to video JSON file
            save: Whether to save enhanced JSON
            
        Returns:
            TrainingEnhancements dataclass
        """
        path = Path(video_json_path)
        if not path.exists():
            logger.error(f"[ENHANCER] File not found: {path}")
            return None
        
        # Load existing JSON
        with open(path, "r", encoding="utf-8") as f:
            video_data = json.load(f)
        
        video_id = video_data.get("video_id", path.stem)
        logger.info(f"[ENHANCER] Enhancing {video_id}")
        
        # Extract content for prompts
        segments = video_data.get("audio", {}).get("segments", [])
        content = self._build_content_string(video_data)
        segments_text = self._build_segments_string(segments)
        
        # Run enhancement prompts
        enhancements = TrainingEnhancements()
        
        # Q8: Style Fingerprint (most important)
        style = self._run_prompt("style_fingerprint", content=content)
        if style:
            enhancements.style_fingerprint = StyleFingerprint(
                formality=style.get("formality", 0.5),
                energy=style.get("energy", 0.5),
                humor=style.get("humor", 0.3),
                personal_sharing=style.get("personal_sharing", 0.5),
                technical_depth=style.get("technical_depth", 0.5),
                analogy_usage=style.get("analogy_usage", 0.5),
                sentence_length=style.get("sentence_length", "medium"),
            )
        
        # Q1: Voice Patterns
        patterns = self._run_prompt("voice_patterns", content=content)
        if patterns:
            enhancements.voice_patterns = VoicePatterns(
                signature_phrases=patterns.get("signature_phrases", []),
                filler_words=patterns.get("filler_words", []),
                sentence_starters=patterns.get("sentence_starters", []),
                emphatic_words=patterns.get("emphatic_words", []),
                speaking_pace=style.get("speaking_pace", "medium") if style else "medium"
            )
        
        # Q2: Intent Labels
        intents = self._run_prompt("intent_labels", segments=segments_text)
        if intents:
            enhancements.intent_labels = intents.get("intents", [])
        
        # Q3: Quotable Moments
        quotables = self._run_prompt("quotable_moments", segments=segments_text)
        if quotables:
            enhancements.quotable_moments = quotables.get("quotables", [])
        
        # Q4: Comment Triggers
        triggers = self._run_prompt("comment_triggers", segments=segments_text)
        if triggers:
            enhancements.comment_triggers = triggers.get("triggers", [])
        
        # Q5: Q&A Moments
        qa = self._run_prompt("qa_moments", segments=segments_text)
        if qa:
            enhancements.qa_moments = qa.get("questions", [])
        
        # Q7: Teaching Moments
        teachings = self._run_prompt("teaching_moments", segments=segments_text)
        if teachings:
            enhancements.teaching_moments = teachings.get("teachings", [])
        
        # Q1 (detailed): Verbatim Quotes
        quotes = self._run_prompt("verbatim_quotes", segments=segments_text)
        if quotes:
            enhancements.verbatim_quotes = quotes.get("quotes", [])
        
        # Determine quality tier based on enhancement richness
        enhancements.quality_tier = self._calculate_quality_tier(enhancements)
        
        # Save if requested
        if save:
            video_data["training_data"] = asdict(enhancements)
            video_data["enhanced_at"] = datetime.now().isoformat()
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[ENHANCER] Saved enhanced JSON for {video_id}")
        
        return enhancements
    
    def _run_prompt(self, prompt_key: str, **kwargs) -> Optional[Dict]:
        """Run a single enhancement prompt using LLMConnector."""
        if not self.llm:
            logger.warning("[ENHANCER] No LLM client available")
            return None
        
        prompt_template = self.PROMPTS.get(prompt_key)
        if not prompt_template:
            return None
        
        prompt = prompt_template.format(**kwargs)
        
        # Add system prompt for JSON output
        system_prompt = "You are a video content analyzer. Always respond with valid JSON only, no markdown."
        
        try:
            response = self.llm.get_response(prompt, system_prompt=system_prompt)
            
            if not response:
                logger.warning(f"[ENHANCER] Empty response for {prompt_key}")
                return None
            
            # Clean up response for JSON parsing
            text = response.strip()
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            
            # Find JSON object in response (handle extra text before/after)
            brace_match = re.search(r'\{.*\}', text, re.DOTALL)
            if brace_match:
                text = brace_match.group(0)
            
            # Clean common issues
            text = text.replace('\n', ' ')  # Remove newlines that break JSON
            text = re.sub(r',\s*}', '}', text)  # Remove trailing commas
            text = re.sub(r',\s*]', ']', text)  # Remove trailing commas in arrays
            
            # Try to parse JSON
            return json.loads(text)
            
        except json.JSONDecodeError as je:
            logger.debug(f"[ENHANCER] JSON parse failed for {prompt_key}: {je}")
            return None
        except Exception as e:
            logger.warning(f"[ENHANCER] Prompt {prompt_key} failed: {e}")
            return None
    
    def _build_content_string(self, video_data: Dict) -> str:
        """Build content string for prompts."""
        parts = []
        
        title = video_data.get("title", "")
        if title:
            parts.append(f"Title: {title}")
        
        summary = video_data.get("metadata", {}).get("summary", "")
        if summary:
            parts.append(f"Summary: {summary}")
        
        transcript = video_data.get("audio", {}).get("transcript_summary", "")
        if transcript:
            parts.append(f"Transcript: {transcript}")
        
        topics = video_data.get("metadata", {}).get("topics", [])
        if topics:
            parts.append(f"Topics: {', '.join(topics)}")
        
        return "\n\n".join(parts)
    
    def _build_segments_string(self, segments: List[Dict]) -> str:
        """Build segments string for prompts."""
        lines = []
        for i, seg in enumerate(segments):
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "")
            speaker = seg.get("speaker", "")
            
            lines.append(f"[{i}] {start}-{end}s ({speaker}): {text}")
        
        return "\n".join(lines)
    
    def _calculate_quality_tier(self, enhancements: TrainingEnhancements) -> int:
        """Calculate quality tier based on enhancement richness."""
        score = 0
        
        if enhancements.style_fingerprint:
            score += 2
        if enhancements.voice_patterns and enhancements.voice_patterns.signature_phrases:
            score += 2
        if len(enhancements.intent_labels) > 0:
            score += 1
        if len(enhancements.quotable_moments) > 0:
            score += 2
        if len(enhancements.verbatim_quotes) > 0:
            score += 2
        
        if score >= 7:
            return 2  # HIGH
        elif score >= 3:
            return 1  # MEDIUM
        else:
            return 0  # LOW
    
    def batch_enhance(
        self,
        video_dir: str,
        max_videos: Optional[int] = None,
        delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Enhance multiple video JSONs.
        
        Args:
            video_dir: Directory containing video JSON files
            max_videos: Maximum videos to process
            delay: Delay between API calls
            
        Returns:
            Summary of results
        """
        video_path = Path(video_dir)
        json_files = list(video_path.glob("*.json"))
        
        # Filter out already-enhanced videos
        unenhanaced = []
        for jf in json_files:
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                if not data.get("training_data"):
                    unenhanaced.append(jf)
            except:
                unenhanaced.append(jf)  # Try to enhance if can't read
        
        logger.info(f"[ENHANCER] {len(unenhanaced)}/{len(json_files)} videos need enhancement")
        
        if max_videos:
            unenhanaced = unenhanaced[:max_videos]
        
        results = {"enhanced": 0, "failed": 0, "tiers": {0: 0, 1: 0, 2: 0}}
        
        for i, json_file in enumerate(unenhanaced):
            logger.info(f"[ENHANCER] Processing {i+1}/{len(unenhanaced)}: {json_file.name}")
            
            try:
                enhancements = self.enhance_video(str(json_file), save=True)
                if enhancements:
                    results["enhanced"] += 1
                    results["tiers"][enhancements.quality_tier] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"[ENHANCER] Failed {json_file.name}: {e}")
                results["failed"] += 1
            
            if i < len(unenhanaced) - 1:
                time.sleep(delay)
        
        return results


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Video Enhancer Test")
    print("=" * 60)
    
    enhancer = VideoEnhancer()
    
    # Test with one video
    test_path = "memory/video_index/undaodu/-EpadSzhyCE.json"
    if Path(test_path).exists():
        result = enhancer.enhance_video(test_path, save=False)
        if result:
            print(f"Quality Tier: {result.quality_tier}")
            print(f"Style: {result.style_fingerprint}")
            print(f"Patterns: {result.voice_patterns}")
            print(f"Quotables: {len(result.quotable_moments)}")
    else:
        print(f"Test file not found: {test_path}")
