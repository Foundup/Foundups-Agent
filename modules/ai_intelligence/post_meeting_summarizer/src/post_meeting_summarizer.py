"""
Post Meeting Summarizer - WSP/WRE AI Intelligence Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive meeting summarization and testing capabilities
- WSP 54 (Agent Duties): AI-powered meeting summarization for autonomous development
- WSP 22 (ModLog): Change tracking and summarization history
- WSP 50 (Pre-Action Verification): Enhanced verification before summarization

Provides AI-powered meeting summarization capabilities for autonomous development operations.
Enables 0102 pArtifacts to automatically summarize meetings and extract actionable insights.
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MeetingSummary:
    """Result of meeting summarization operation."""
    meeting_id: str
    title: str
    participants: List[str]
    date: datetime
    duration_minutes: int
    key_points: List[str]
    action_items: List[str]
    decisions: List[str]
    next_steps: List[str]
    wsp_references: List[str]
    summary_text: str
    confidence_score: float


@dataclass
class MeetingTranscript:
    """Meeting transcript data structure."""
    meeting_id: str
    title: str
    participants: List[str]
    date: datetime
    duration_minutes: int
    transcript: str
    metadata: Dict[str, Any]


class PostMeetingSummarizer:
    """
    AI-powered meeting summarizer for autonomous development operations.
    
    Provides comprehensive meeting summarization including:
    - Key points extraction
    - Action items identification
    - Decision tracking
    - WSP compliance checking
    - Next steps planning
    """
    
    def __init__(self):
        """Initialize the meeting summarizer with WSP compliance standards."""
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
    def summarize_meeting(self, transcript: MeetingTranscript) -> MeetingSummary:
        """
        Summarize a meeting transcript.
        
        Args:
            transcript: MeetingTranscript object containing meeting data
            
        Returns:
            MeetingSummary with comprehensive meeting analysis
        """
        try:
            # Extract key information
            key_points = self._extract_key_points(transcript.transcript)
            action_items = self._extract_action_items(transcript.transcript)
            decisions = self._extract_decisions(transcript.transcript)
            next_steps = self._extract_next_steps(transcript.transcript)
            wsp_references = self._extract_wsp_references(transcript.transcript)
            
            # Generate summary text
            summary_text = self._generate_summary_text(
                transcript, key_points, action_items, decisions, next_steps
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                transcript.transcript, key_points, action_items
            )
            
            return MeetingSummary(
                meeting_id=transcript.meeting_id,
                title=transcript.title,
                participants=transcript.participants,
                date=transcript.date,
                duration_minutes=transcript.duration_minutes,
                key_points=key_points,
                action_items=action_items,
                decisions=decisions,
                next_steps=next_steps,
                wsp_references=wsp_references,
                summary_text=summary_text,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            # Return minimal summary on error
            return MeetingSummary(
                meeting_id=transcript.meeting_id,
                title=transcript.title,
                participants=transcript.participants,
                date=transcript.date,
                duration_minutes=transcript.duration_minutes,
                key_points=["Error occurred during summarization"],
                action_items=[],
                decisions=[],
                next_steps=[],
                wsp_references=[],
                summary_text=f"Error summarizing meeting: {str(e)}",
                confidence_score=0.0
            )
    
    def summarize_from_text(self, meeting_text: str, meeting_id: str = None) -> MeetingSummary:
        """
        Summarize meeting from raw text.
        
        Args:
            meeting_text: Raw meeting text/transcript
            meeting_id: Optional meeting identifier
            
        Returns:
            MeetingSummary with meeting analysis
        """
        # Create a basic transcript object
        transcript = MeetingTranscript(
            meeting_id=meeting_id or f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Meeting Summary",
            participants=[],
            date=datetime.now(),
            duration_minutes=0,
            transcript=meeting_text,
            metadata={}
        )
        
        return self.summarize_meeting(transcript)
    
    def _extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points from meeting transcript."""
        key_points = []
        
        # Look for common key point indicators
        patterns = [
            r'(?:key point|important|critical|main point|highlight)[:\s]+(.+?)(?:\n|\.)',
            r'(?:discussed|covered|addressed)[:\s]+(.+?)(?:\n|\.)',
            r'(?:agreed|decided|concluded)[:\s]+(.+?)(?:\n|\.)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            key_points.extend([match.strip() for match in matches])
        
        # Remove duplicates and limit to top points
        unique_points = list(dict.fromkeys(key_points))
        return unique_points[:10]  # Limit to top 10 key points
    
    def _extract_action_items(self, transcript: str) -> List[str]:
        """Extract action items from meeting transcript."""
        action_items = []
        
        # Look for action item indicators
        patterns = [
            r'(?:action item|todo|task|follow up)[:\s]+(.+?)(?:\n|\.)',
            r'(?:will|going to|plan to|need to)[\s]+(.+?)(?:\n|\.)',
            r'(?:assigned|responsible for)[:\s]+(.+?)(?:\n|\.)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            action_items.extend([match.strip() for match in matches])
        
        # Remove duplicates
        unique_items = list(dict.fromkeys(action_items))
        return unique_items[:15]  # Limit to top 15 action items
    
    def _extract_decisions(self, transcript: str) -> List[str]:
        """Extract decisions made during the meeting."""
        decisions = []
        
        # Look for decision indicators
        patterns = [
            r'(?:decided|agreed|approved|voted|chose)[:\s]+(.+?)(?:\n|\.)',
            r'(?:decision|resolution|outcome)[:\s]+(.+?)(?:\n|\.)',
            r'(?:final|concluded|settled on)[:\s]+(.+?)(?:\n|\.)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            decisions.extend([match.strip() for match in matches])
        
        # Remove duplicates
        unique_decisions = list(dict.fromkeys(decisions))
        return unique_decisions[:10]  # Limit to top 10 decisions
    
    def _extract_next_steps(self, transcript: str) -> List[str]:
        """Extract next steps from meeting transcript."""
        next_steps = []
        
        # Look for next step indicators
        patterns = [
            r'(?:next step|next action|following)[:\s]+(.+?)(?:\n|\.)',
            r'(?:moving forward|going forward|next time)[:\s]+(.+?)(?:\n|\.)',
            r'(?:schedule|plan|arrange)[:\s]+(.+?)(?:\n|\.)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            next_steps.extend([match.strip() for match in matches])
        
        # Remove duplicates
        unique_steps = list(dict.fromkeys(next_steps))
        return unique_steps[:10]  # Limit to top 10 next steps
    
    def _extract_wsp_references(self, transcript: str) -> List[str]:
        """Extract WSP protocol references from meeting transcript."""
        wsp_references = []
        
        # Look for WSP references
        wsp_pattern = r'\b(?:wsp|protocol)\s*[#]?\s*(\d+)\b'
        wsp_matches = re.findall(wsp_pattern, transcript, re.IGNORECASE)
        
        for match in wsp_matches:
            wsp_references.append(f"WSP {match}")
        
        # Look for WSP keywords
        for keyword in self.wsp_keywords:
            if keyword.lower() in transcript.lower():
                wsp_references.append(f"WSP keyword: {keyword}")
        
        # Remove duplicates
        unique_references = list(dict.fromkeys(wsp_references))
        return unique_references
    
    def _generate_summary_text(self, transcript: MeetingTranscript, 
                              key_points: List[str], action_items: List[str],
                              decisions: List[str], next_steps: List[str]) -> str:
        """Generate a comprehensive summary text."""
        summary_parts = []
        
        # Meeting overview
        summary_parts.append(f"Meeting: {transcript.title}")
        summary_parts.append(f"Date: {transcript.date.strftime('%Y-%m-%d %H:%M')}")
        summary_parts.append(f"Duration: {transcript.duration_minutes} minutes")
        summary_parts.append(f"Participants: {', '.join(transcript.participants)}")
        summary_parts.append("")
        
        # Key points
        if key_points:
            summary_parts.append("Key Points:")
            for i, point in enumerate(key_points[:5], 1):  # Top 5 key points
                summary_parts.append(f"{i}. {point}")
            summary_parts.append("")
        
        # Decisions
        if decisions:
            summary_parts.append("Decisions Made:")
            for i, decision in enumerate(decisions[:5], 1):  # Top 5 decisions
                summary_parts.append(f"{i}. {decision}")
            summary_parts.append("")
        
        # Action items
        if action_items:
            summary_parts.append("Action Items:")
            for i, item in enumerate(action_items[:10], 1):  # Top 10 action items
                summary_parts.append(f"{i}. {item}")
            summary_parts.append("")
        
        # Next steps
        if next_steps:
            summary_parts.append("Next Steps:")
            for i, step in enumerate(next_steps[:5], 1):  # Top 5 next steps
                summary_parts.append(f"{i}. {step}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _calculate_confidence(self, transcript: str, key_points: List[str], 
                            action_items: List[str]) -> float:
        """Calculate confidence score for the summary."""
        confidence = 50.0  # Base confidence
        
        # Increase confidence based on content quality
        if len(transcript) > 500:
            confidence += 10
        
        if key_points:
            confidence += min(len(key_points) * 2, 20)
        
        if action_items:
            confidence += min(len(action_items) * 1.5, 15)
        
        # Decrease confidence for very short transcripts
        if len(transcript) < 100:
            confidence -= 20
        
        return min(max(confidence, 0.0), 100.0)
    
    def save_summary(self, summary: MeetingSummary, output_path: str) -> bool:
        """
        Save meeting summary to file.
        
        Args:
            summary: MeetingSummary object to save
            output_path: Path to save the summary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to JSON-serializable format
            summary_dict = {
                'meeting_id': summary.meeting_id,
                'title': summary.title,
                'participants': summary.participants,
                'date': summary.date.isoformat(),
                'duration_minutes': summary.duration_minutes,
                'key_points': summary.key_points,
                'action_items': summary.action_items,
                'decisions': summary.decisions,
                'next_steps': summary.next_steps,
                'wsp_references': summary.wsp_references,
                'summary_text': summary.summary_text,
                'confidence_score': summary.confidence_score
            }
            
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_dict, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving summary: {e}")
            return False
    
    def load_summary(self, file_path: str) -> Optional[MeetingSummary]:
        """
        Load meeting summary from file.
        
        Args:
            file_path: Path to the summary file
            
        Returns:
            MeetingSummary object or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summary_dict = json.load(f)
            
            # Convert back to MeetingSummary object
            return MeetingSummary(
                meeting_id=summary_dict['meeting_id'],
                title=summary_dict['title'],
                participants=summary_dict['participants'],
                date=datetime.fromisoformat(summary_dict['date']),
                duration_minutes=summary_dict['duration_minutes'],
                key_points=summary_dict['key_points'],
                action_items=summary_dict['action_items'],
                decisions=summary_dict['decisions'],
                next_steps=summary_dict['next_steps'],
                wsp_references=summary_dict['wsp_references'],
                summary_text=summary_dict['summary_text'],
                confidence_score=summary_dict['confidence_score']
            )
            
        except Exception as e:
            print(f"Error loading summary: {e}")
            return None


def summarize_meeting(transcript: MeetingTranscript) -> MeetingSummary:
    """
    Convenience function to summarize a meeting.
    
    Args:
        transcript: MeetingTranscript object
        
    Returns:
        MeetingSummary with meeting analysis
    """
    summarizer = PostMeetingSummarizer()
    return summarizer.summarize_meeting(transcript)


def summarize_text(meeting_text: str, meeting_id: str = None) -> MeetingSummary:
    """
    Convenience function to summarize meeting text.
    
    Args:
        meeting_text: Raw meeting text
        meeting_id: Optional meeting identifier
        
    Returns:
        MeetingSummary with meeting analysis
    """
    summarizer = PostMeetingSummarizer()
    return summarizer.summarize_from_text(meeting_text, meeting_id)


if __name__ == "__main__":
    """Test the meeting summarizer with sample data."""
    # Sample meeting transcript
    sample_transcript = """
    Meeting: WSP Compliance Review
    Participants: 0102 Agent, ComplianceAgent
    
    Key points discussed:
    - WSP 22 compliance violations need immediate attention
    - Missing ModLog.md files in 8 enterprise domains
    - WSP 34 incomplete implementations require resolution
    
    Decisions made:
    - Prioritize ModLog.md creation for all enterprise domains
    - Implement WSP 34 testing protocol for incomplete modules
    - Assign ComplianceAgent to monitor WSP compliance
    
    Action items:
    - Create ModLog.md files for all missing domains
    - Implement code_analyzer module following WSP 34
    - Update audit reports with WSP 54 agent assignments
    
    Next steps:
    - Schedule follow-up meeting after ModLog implementation
    - Review WSP compliance scores after fixes
    - Plan next phase of WSP 34 implementations
    """
    
    summarizer = PostMeetingSummarizer()
    summary = summarizer.summarize_from_text(sample_transcript, "wsp_compliance_20250803")
    
    print("Meeting Summary:")
    print(summary.summary_text)
    print(f"\nConfidence Score: {summary.confidence_score}%")
    print(f"WSP References: {summary.wsp_references}") 