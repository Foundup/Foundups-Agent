"""
Vision Training Data Collector - Self-supervised learning from fixed coordinates

Collects training data from successful fixed coordinate clicks to train/fine-tune
the UI-TARS vision model. This enables continuous improvement of vision accuracy
by using the reliable fixed coordinate system as ground truth.

WSP Compliance:
    - WSP 48: Recursive pattern learning
    - WSP 77: AI Overseer integration
    - WSP 91: Observability

Architecture:
    Fixed Coordinate Click (success) → Screenshot + Coordinates → Training Dataset
    Training Dataset → Fine-tune UI-TARS LoRA → Improved Vision Model

Usage:
    collector = VisionTrainingCollector()
    
    # Record successful fixed coordinate click
    collector.record_successful_click(
        driver=selenium_driver,
        description="celebrate reaction emoji button",
        coordinates=(358, 669),
        viewport_size=(1920, 1080),
        action="click",
        platform="youtube_chat"
    )
    
    # Export to JSONL for training
    collector.export_to_jsonl("training_data.jsonl")
"""

import base64
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default storage paths
DATA_DIR = Path("modules/infrastructure/foundups_vision/data")
TRAINING_DIR = DATA_DIR / "training"
SCREENSHOTS_DIR = DATA_DIR / "training_screenshots"


@dataclass
class TrainingExample:
    """Single training example for vision model."""
    example_id: str
    screenshot_base64: str
    description: str
    coordinates_1000: Tuple[int, int]  # UI-TARS 1000x1000 format
    coordinates_pixel: Tuple[int, int]  # Original pixel coordinates
    viewport_size: Tuple[int, int]
    action: str  # click, type, scroll
    platform: str  # youtube_chat, youtube_studio, linkedin, etc.
    success: bool
    timestamp: str
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "screenshot_base64": self.screenshot_base64,
            "description": self.description,
            "coordinates_1000": self.coordinates_1000,
            "coordinates_pixel": self.coordinates_pixel,
            "viewport_size": self.viewport_size,
            "action": self.action,
            "platform": self.platform,
            "success": self.success,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    def to_ui_tars_format(self) -> Dict[str, Any]:
        """Convert to UI-TARS training format."""
        x, y = self.coordinates_1000
        return {
            "image": self.screenshot_base64,
            "conversations": [
                {
                    "role": "user",
                    "content": f"Click the {self.description}"
                },
                {
                    "role": "assistant", 
                    "content": f"Thought: I need to click the {self.description}.\nAction: click(start_box='<|box_start|>({x},{y})<|box_end|>')"
                }
            ],
            "metadata": {
                "platform": self.platform,
                "action": self.action,
                "success": self.success,
                "timestamp": self.timestamp,
            }
        }


class VisionTrainingCollector:
    """
    Collects training data from successful fixed coordinate clicks.
    
    This enables self-supervised learning where the reliable fixed coordinate
    system provides ground truth labels for training the vision model.
    """

    def __init__(self, db_path: str = None) -> None:
        """
        Initialize training data collector.
        
        Args:
            db_path: Path to SQLite database for storing training examples
        """
        # Ensure directories exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        if db_path is None:
            db_path = str(DATA_DIR / "vision_training.db")
        
        self.db_path = db_path
        self._init_db()
        
        # Statistics
        self._session_examples = 0
        self._session_start = datetime.utcnow().isoformat()
        
        logger.info(f"[VISION-TRAIN] Collector initialized, db={db_path}")

    def _init_db(self) -> None:
        """Initialize SQLite database for training examples."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_examples (
                    example_id TEXT PRIMARY KEY,
                    screenshot_path TEXT,
                    description TEXT,
                    coordinates_1000_x INTEGER,
                    coordinates_1000_y INTEGER,
                    coordinates_pixel_x INTEGER,
                    coordinates_pixel_y INTEGER,
                    viewport_width INTEGER,
                    viewport_height INTEGER,
                    action TEXT,
                    platform TEXT,
                    success INTEGER,
                    timestamp TEXT,
                    duration_ms INTEGER,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform ON training_examples(platform)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_success ON training_examples(success)
            """)
            conn.commit()

    def pixel_to_1000(
        self,
        pixel_x: int,
        pixel_y: int,
        viewport_width: int,
        viewport_height: int,
    ) -> Tuple[int, int]:
        """
        Convert pixel coordinates to UI-TARS 1000x1000 format.
        
        Args:
            pixel_x: X coordinate in pixels
            pixel_y: Y coordinate in pixels
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
            
        Returns:
            Tuple of (x, y) in 1000x1000 coordinate space
        """
        x_1000 = int((pixel_x / viewport_width) * 1000)
        y_1000 = int((pixel_y / viewport_height) * 1000)
        return (x_1000, y_1000)

    def record_successful_click(
        self,
        driver,
        description: str,
        coordinates: Tuple[int, int],
        viewport_size: Tuple[int, int] = None,
        action: str = "click",
        platform: str = "youtube_chat",
        duration_ms: int = 0,
        metadata: Dict[str, Any] = None,
    ) -> Optional[str]:
        """
        Record a successful fixed coordinate click for training.
        
        Args:
            driver: Selenium WebDriver instance
            description: Human-readable description of clicked element
            coordinates: (x, y) pixel coordinates that were clicked
            viewport_size: (width, height) of viewport (auto-detected if None)
            action: Action type (click, type, scroll)
            platform: Platform name (youtube_chat, linkedin, etc.)
            duration_ms: Time taken for the action
            metadata: Additional metadata
            
        Returns:
            example_id if successful, None if failed
        """
        try:
            # Generate unique ID
            example_id = f"{platform}_{int(time.time() * 1000)}"
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Capture screenshot
            screenshot_bytes = driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Save screenshot to disk for reference
            screenshot_path = SCREENSHOTS_DIR / f"{example_id}.png"
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
            
            # Get viewport size if not provided
            if viewport_size is None:
                try:
                    viewport = driver.execute_script(
                        "return {w: window.innerWidth, h: window.innerHeight}"
                    )
                    viewport_size = (viewport['w'], viewport['h'])
                except Exception:
                    viewport_size = (1920, 1080)  # Default
            
            # Convert to UI-TARS 1000x1000 format
            pixel_x, pixel_y = coordinates
            coords_1000 = self.pixel_to_1000(
                pixel_x, pixel_y,
                viewport_size[0], viewport_size[1]
            )
            
            # Create training example
            example = TrainingExample(
                example_id=example_id,
                screenshot_base64=screenshot_base64,
                description=description,
                coordinates_1000=coords_1000,
                coordinates_pixel=coordinates,
                viewport_size=viewport_size,
                action=action,
                platform=platform,
                success=True,
                timestamp=timestamp,
                duration_ms=duration_ms,
                metadata=metadata or {},
            )
            
            # Store in database (without base64 - reference screenshot file)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO training_examples
                    (example_id, screenshot_path, description, 
                     coordinates_1000_x, coordinates_1000_y,
                     coordinates_pixel_x, coordinates_pixel_y,
                     viewport_width, viewport_height,
                     action, platform, success, timestamp, duration_ms, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    example_id,
                    str(screenshot_path),
                    description,
                    coords_1000[0], coords_1000[1],
                    pixel_x, pixel_y,
                    viewport_size[0], viewport_size[1],
                    action, platform, 1, timestamp, duration_ms,
                    json.dumps(metadata or {})
                ))
                conn.commit()
            
            self._session_examples += 1
            logger.info(
                f"[VISION-TRAIN] Recorded training example: {example_id} "
                f"({description}, coords_1000={coords_1000})"
            )
            
            return example_id
            
        except Exception as e:
            logger.error(f"[VISION-TRAIN] Failed to record training example: {e}")
            return None

    def get_example_count(self, platform: str = None) -> int:
        """Get count of training examples."""
        with sqlite3.connect(self.db_path) as conn:
            if platform:
                result = conn.execute(
                    "SELECT COUNT(*) FROM training_examples WHERE platform = ?",
                    (platform,)
                ).fetchone()
            else:
                result = conn.execute(
                    "SELECT COUNT(*) FROM training_examples"
                ).fetchone()
            return result[0] if result else 0

    def export_to_jsonl(
        self,
        output_path: str = None,
        platform: str = None,
        limit: int = None,
        include_screenshots: bool = True,
    ) -> str:
        """
        Export training examples to JSONL format for UI-TARS fine-tuning.
        
        Args:
            output_path: Path to output JSONL file
            platform: Filter by platform (None for all)
            limit: Maximum number of examples to export
            include_screenshots: Include base64 screenshots (large file!)
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = str(TRAINING_DIR / f"training_export_{timestamp}.jsonl")
        
        query = "SELECT * FROM training_examples WHERE success = 1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        
        exported_count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for row in rows:
                # Load screenshot if including
                screenshot_base64 = ""
                if include_screenshots and row['screenshot_path']:
                    try:
                        with open(row['screenshot_path'], 'rb') as img:
                            screenshot_base64 = base64.b64encode(img.read()).decode('utf-8')
                    except Exception as e:
                        logger.warning(f"[VISION-TRAIN] Could not load screenshot: {e}")
                
                # Create UI-TARS format
                x, y = row['coordinates_1000_x'], row['coordinates_1000_y']
                example = {
                    "image": screenshot_base64,
                    "conversations": [
                        {
                            "role": "user",
                            "content": f"Click the {row['description']}"
                        },
                        {
                            "role": "assistant",
                            "content": f"Thought: I need to click the {row['description']}.\nAction: click(start_box='<|box_start|>({x},{y})<|box_end|>')"
                        }
                    ],
                    "metadata": {
                        "example_id": row['example_id'],
                        "platform": row['platform'],
                        "action": row['action'],
                        "coordinates_pixel": [row['coordinates_pixel_x'], row['coordinates_pixel_y']],
                        "viewport": [row['viewport_width'], row['viewport_height']],
                        "timestamp": row['timestamp'],
                    }
                }
                f.write(json.dumps(example) + "\n")
                exported_count += 1
        
        logger.info(f"[VISION-TRAIN] Exported {exported_count} examples to {output_path}")
        return output_path

    def get_stats(self) -> Dict[str, Any]:
        """Get training collection statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM training_examples").fetchone()[0]
            
            # Count by platform
            platform_counts = {}
            for row in conn.execute(
                "SELECT platform, COUNT(*) FROM training_examples GROUP BY platform"
            ).fetchall():
                platform_counts[row[0]] = row[1]
        
        return {
            "total_examples": total,
            "session_examples": self._session_examples,
            "session_start": self._session_start,
            "by_platform": platform_counts,
            "db_path": self.db_path,
        }


# Global singleton
_collector = None


def get_training_collector() -> VisionTrainingCollector:
    """Get or create global training collector instance."""
    global _collector
    if _collector is None:
        _collector = VisionTrainingCollector()
    return _collector


# Convenience functions
def record_click(
    driver,
    description: str,
    coordinates: Tuple[int, int],
    platform: str = "youtube_chat",
    **kwargs
) -> Optional[str]:
    """Record a successful click for training."""
    collector = get_training_collector()
    return collector.record_successful_click(
        driver=driver,
        description=description,
        coordinates=coordinates,
        platform=platform,
        **kwargs
    )


def export_training_data(output_path: str = None, **kwargs) -> str:
    """Export training data to JSONL."""
    collector = get_training_collector()
    return collector.export_to_jsonl(output_path=output_path, **kwargs)


if __name__ == "__main__":
    # Test the collector
    collector = VisionTrainingCollector()
    print(f"Stats: {collector.get_stats()}")




