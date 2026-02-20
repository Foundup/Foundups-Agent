"""
LoRA Training Data Converter for llama.cpp

Converts voice_sft.jsonl to llama.cpp finetune format.
Uses ChatML template compatible with Qwen.
"""
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ChatML template for Qwen
CHATML_TEMPLATE = """<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
{assistant}<|im_end|>"""


def convert_sft_to_chatml(input_path: str, output_path: str) -> int:
    """
    Convert SFT JSONL to ChatML format for llama.cpp finetune.
    
    Args:
        input_path: Path to voice_sft.jsonl
        output_path: Path to output train.txt
        
    Returns:
        Number of examples converted
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_path}")
        return 0
    
    examples = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
                # Extract fields
                system = data.get('system', 'You are a helpful assistant.')
                user = data.get('user', '')
                assistant = data.get('assistant', '')
                
                # Skip empty examples
                if not user or not assistant:
                    continue
                
                # Format as ChatML
                formatted = CHATML_TEMPLATE.format(
                    system=system,
                    user=user,
                    assistant=assistant
                )
                examples.append(formatted)
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse line: {e}")
                continue
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        # Separate examples with double newline
        f.write('\n\n'.join(examples))
    
    logger.info(f"Converted {len(examples)} examples to {output_path}")
    return len(examples)


def convert_all(training_dir: str = "training_data/nemo_test") -> dict:
    """
    Convert all training data to llama.cpp format.
    
    Returns:
        Summary of conversions
    """
    training_path = Path(training_dir)
    output_dir = training_path / "llama_cpp"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Convert voice SFT
    voice_sft = training_path / "voice_sft.jsonl"
    if voice_sft.exists():
        count = convert_sft_to_chatml(
            str(voice_sft),
            str(output_dir / "voice_train.txt")
        )
        results['voice_sft'] = count
    
    # Convert decision SFT (same format)
    decision_sft = training_path / "decision_sft.jsonl"
    if decision_sft.exists():
        count = convert_sft_to_chatml(
            str(decision_sft),
            str(output_dir / "decision_train.txt")
        )
        results['decision_sft'] = count
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = convert_all()
    print(f"Conversion complete: {results}")
