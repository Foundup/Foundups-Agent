#!/usr/bin/env python3
"""
Export Training Corpus for Google Colab

Prepares comprehensive training corpus for Colab upload:
1. Collects ALL system data (012.txt, ModLogs, violations, chats, git, logs)
2. Formats for Colab consumption (JSON + instructions)
3. Creates lightweight export package (<50MB)

Usage:
    python export_for_colab.py --output colab_training_export.json

WSP Compliance: WSP 90 (UTF-8), WSP 49 (Module Structure)
"""

import argparse
import json
import logging
from pathlib import Path
from .comprehensive_training_corpus import ComprehensiveTrainingCorpus

logger = logging.getLogger(__name__)


class ColabExporter:
    """
    Exports training corpus for Google Colab.

    Output format optimized for Colab notebooks:
    - Single JSON file
    - Compressed patterns
    - Colab-ready instructions
    """

    def __init__(self):
        self.collector = ComprehensiveTrainingCorpus()

    def export(self, output_file: str):
        """
        Create Colab-ready training export.

        Returns path to export file.
        """
        logger.info("[COLAB-EXPORT] Starting comprehensive data collection...")

        # Collect all training data
        corpus = self.collector.collect_all()

        # Create Colab-ready format
        colab_package = self._format_for_colab(corpus)

        # Export to JSON
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(colab_package, f, indent=2, ensure_ascii=False)

        file_size_mb = output_path.stat().st_size / (1024 * 1024)

        logger.info(f"[COLAB-EXPORT] Export complete: {output_path}")
        logger.info(f"[COLAB-EXPORT] File size: {file_size_mb:.2f} MB")
        logger.info(f"[COLAB-EXPORT] Total patterns: {colab_package['metadata']['total_patterns']}")

        # Create upload instructions
        self._create_upload_instructions(output_path)

        return output_path

    def _format_for_colab(self, corpus: dict) -> dict:
        """
        Format corpus for Colab consumption.

        Colab format:
        - Flattened patterns (easier for ChromaDB ingestion)
        - Metadata for each pattern
        - Training instructions
        """
        patterns = []

        # Flatten all patterns from all sources
        for source_type, source_patterns in corpus.items():
            for pattern in source_patterns:
                # Add source type to pattern
                pattern['source_type'] = source_type

                # Determine training category
                pattern['training_category'] = self._categorize_pattern(pattern)

                patterns.append(pattern)

        # Calculate statistics
        stats = self._calculate_stats(patterns)

        return {
            "format_version": "1.0",
            "exported_for": "Google Colab",
            "metadata": {
                "total_patterns": len(patterns),
                "source_breakdown": stats['source_breakdown'],
                "training_categories": stats['training_categories'],
                "export_date": self.collector.stats.get('export_date', 'unknown')
            },
            "patterns": patterns,
            "training_instructions": self._generate_training_instructions(),
            "colab_setup": self._generate_colab_setup()
        }

    def _categorize_pattern(self, pattern: dict) -> str:
        """
        Categorize pattern for training.

        Categories match Gemma's role:
        - classification: Simple yes/no decisions
        - routing: Which module/WSP applies
        - error_solution: Error → Fix mappings
        - priority_scoring: Urgency/importance decisions
        """
        source_type = pattern.get('source_type', '')
        decision_type = pattern.get('decision_type', '')

        if source_type == '012_operations':
            if decision_type == 'priority_scoring':
                return 'priority_scoring'
            elif decision_type == 'routing_decision':
                return 'routing'
            else:
                return 'operational_decision'

        elif source_type == 'wsp_violations':
            return 'error_solution'

        elif source_type == 'modlogs':
            return 'change_history'

        elif source_type == 'chat_logs':
            return 'interaction_pattern'

        elif source_type == 'git_history':
            return 'evolution_pattern'

        else:
            return 'general'

    def _calculate_stats(self, patterns: list) -> dict:
        """Calculate statistics for patterns."""
        source_breakdown = {}
        training_categories = {}

        for pattern in patterns:
            # Count by source
            source = pattern.get('source_type', 'unknown')
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

            # Count by training category
            category = pattern.get('training_category', 'unknown')
            training_categories[category] = training_categories.get(category, 0) + 1

        return {
            'source_breakdown': source_breakdown,
            'training_categories': training_categories
        }

    def _generate_training_instructions(self) -> dict:
        """
        Generate Colab training instructions.

        Returns step-by-step guide for training in Colab.
        """
        return {
            "overview": "Train Gemma 270M/2B on FoundUps-Agent system data",
            "steps": [
                {
                    "step": 1,
                    "title": "Upload this JSON to Colab",
                    "code": "from google.colab import files\nuploaded = files.upload()  # Select colab_training_export.json"
                },
                {
                    "step": 2,
                    "title": "Install dependencies",
                    "code": "!pip install transformers peft datasets accelerate bitsandbytes chromadb -q"
                },
                {
                    "step": 3,
                    "title": "Load patterns into ChromaDB",
                    "code": "import chromadb\nimport json\n\n# Load patterns\nwith open('colab_training_export.json', 'r') as f:\n    data = json.load(f)\n\n# Create ChromaDB collection\nclient = chromadb.Client()\ncollection = client.create_collection('foundups_patterns')\n\n# Add patterns\nfor pattern in data['patterns']:\n    collection.add(\n        ids=[pattern['id']],\n        documents=[pattern.get('content', pattern.get('context', ''))],\n        metadatas=[{'category': pattern['training_category']}]\n    )"
                },
                {
                    "step": 4,
                    "title": "Load Gemma model with LoRA",
                    "code": "from transformers import AutoModelForCausalLM, AutoTokenizer\nfrom peft import LoraConfig, get_peft_model\n\nmodel = AutoModelForCausalLM.from_pretrained('google/gemma-2b')\ntokenizer = AutoTokenizer.from_pretrained('google/gemma-2b')\n\nlora_config = LoraConfig(\n    r=8,\n    lora_alpha=16,\n    target_modules=['q_proj', 'v_proj'],\n    lora_dropout=0.05\n)\n\nmodel = get_peft_model(model, lora_config)"
                },
                {
                    "step": 5,
                    "title": "Train with RAG (few-shot learning)",
                    "code": "# Query ChromaDB for similar patterns\nresults = collection.query(\n    query_texts=['your query here'],\n    n_results=5\n)\n\n# Build few-shot prompt\nprompt = 'Based on these examples:\\n'\nfor doc in results['documents'][0]:\n    prompt += f'- {doc}\\n'\nprompt += '\\nAnswer: '\n\n# Gemma inference\nresponse = model.generate(prompt)"
                },
                {
                    "step": 6,
                    "title": "Export LoRA adapter",
                    "code": "model.save_pretrained('./gemma-foundups-lora')\nfiles.download('./gemma-foundups-lora')  # Download to local"
                }
            ],
            "expected_results": {
                "training_time": "30-60 minutes on Colab T4 GPU",
                "model_size": "Gemma 2B + LoRA adapter (~4MB)",
                "accuracy_target": "85%+ on classification tasks"
            }
        }

    def _generate_colab_setup(self) -> dict:
        """
        Generate Colab environment setup instructions.
        """
        return {
            "runtime": "GPU (T4 recommended for Gemma 2B)",
            "python_version": "3.10+",
            "required_packages": [
                "transformers>=4.38.0",
                "peft>=0.8.0",
                "datasets>=2.16.0",
                "accelerate>=0.26.0",
                "bitsandbytes>=0.42.0",
                "chromadb>=0.4.22"
            ],
            "memory_requirements": {
                "gemma_270m": "~4GB RAM + 4GB VRAM",
                "gemma_2b": "~8GB RAM + 8GB VRAM (LoRA)",
                "gemma_7b": "~16GB RAM + 16GB VRAM (QLoRA required)"
            },
            "colab_free_tier": {
                "works_with": ["gemma_270m", "gemma_2b"],
                "requires_pro": ["gemma_7b"]
            }
        }

    def _create_upload_instructions(self, export_path: Path):
        """
        Create README with upload instructions.
        """
        instructions_file = export_path.parent / "COLAB_UPLOAD_INSTRUCTIONS.md"

        instructions = f"""# Colab Training Upload Instructions

## What You Have

**File**: `{export_path.name}`
**Size**: {export_path.stat().st_size / (1024 * 1024):.2f} MB
**Purpose**: Train Gemma on FoundUps-Agent system data

## Data Sources Included

This export contains training data from ALL system sources:

1. **012.txt**: 0102 operational decisions (PRIMARY)
2. **ModLog files**: Module change history
3. **WSP violations**: Violation → Fix patterns
4. **Chat logs**: LiveChat conversation memory
5. **Git history**: Commits, renames, fixes
6. **Daemon logs**: DAE operational data

## Upload to Colab

### Step 1: Create New Colab Notebook

1. Go to https://colab.research.google.com/
2. Click "New Notebook"
3. Change runtime to GPU: Runtime → Change runtime type → GPU (T4)

### Step 2: Upload Training Data

```python
from google.colab import files
uploaded = files.upload()
# Select: {export_path.name}
```

### Step 3: Follow Training Instructions

The JSON file contains complete training instructions in the `training_instructions` field.

Load it and follow the steps:

```python
import json

with open('{export_path.name}', 'r') as f:
    data = json.load(f)

# View instructions
for step in data['training_instructions']['steps']:
    print(f"Step {{step['step']}}: {{step['title']}}")
    print(step['code'])
    print()
```

### Step 4: Train Gemma

Follow the 6-step training process in the JSON.

Expected time: 30-60 minutes on Colab T4 GPU

### Step 5: Download LoRA Adapter

After training, download the LoRA adapter and integrate with local system.

## Integration Back to Local System

1. Download LoRA adapter from Colab
2. Place in: `O:/Foundups-Agent/holo_index/models/gemma-foundups-lora/`
3. Load in local Gemma inference:

```python
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("google/gemma-2b")
model = PeftModel.from_pretrained(base_model, "./models/gemma-foundups-lora")
```

## Expected Results

- **Gemma 270M**: 85%+ accuracy on classification tasks
- **Gemma 2B**: 90%+ accuracy, better context understanding
- **Training time**: 30-60 minutes
- **Adapter size**: ~4MB (easy to download)

## Support

See complete architecture in:
- `docs/Qwen_Gemma_Training_Architecture_From_WRE_Pattern.md`
- `docs/Gemma3_Training_Strategy_HoloIndex.md`
"""

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        logger.info(f"[COLAB-EXPORT] Upload instructions created: {instructions_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Export training corpus for Google Colab")
    parser.add_argument(
        '--output',
        default='O:/Foundups-Agent/holo_index/training/colab_training_export.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    # Export
    exporter = ColabExporter()
    output_path = exporter.export(args.output)

    print("\n" + "="*60)
    print("[SUCCESS] Colab export complete!")
    print("="*60)
    print(f"\nExport file: {output_path}")
    print(f"Upload instructions: {output_path.parent / 'COLAB_UPLOAD_INSTRUCTIONS.md'}")
    print("\nNext steps:")
    print("1. Upload JSON to Google Colab")
    print("2. Follow training instructions in JSON")
    print("3. Download LoRA adapter")
    print("4. Integrate with local system")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
