"""
QLoRA Voice Training for Digital Twin

Fine-tunes a small LLM (Qwen 1.5B or similar) on 012's voice patterns
using 4-bit quantization for 6GB VRAM compatibility.

Requirements:
    pip install transformers accelerate bitsandbytes peft

Usage:
    python lora_trainer.py --data training_data/nemo_test/voice_sft.jsonl
"""
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

logger = logging.getLogger(__name__)


@dataclass
class VoiceTrainingConfig:
    """Configuration for voice LoRA training."""
    
    # Model
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct"  # Small, fits 6GB
    
    # Data
    data_path: str = "training_data/nemo_test/voice_sft.jsonl"
    max_seq_length: int = 512  # Keep short for VRAM
    
    # LoRA
    lora_r: int = 8  # Low rank for efficiency
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: list = field(default_factory=lambda: ["q_proj", "v_proj"])
    
    # Training
    output_dir: str = "training_output/voice_lora"
    epochs: int = 3
    batch_size: int = 1  # Small for 6GB VRAM
    gradient_accumulation: int = 8
    learning_rate: float = 2e-4
    
    # 4-bit quantization
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"


class VoiceLoRATrainer:
    """Trains LoRA adapter for 012's voice patterns."""
    
    def __init__(self, config: VoiceTrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.dataset = None
        
    def load_model(self):
        """Load base model with 4-bit quantization."""
        logger.info(f"[TRAINER] Loading {self.config.base_model}")
        
        # 4-bit config for 6GB VRAM
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=self.config.use_4bit,
            bnb_4bit_compute_dtype=getattr(torch, self.config.bnb_4bit_compute_dtype),
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        logger.info("[TRAINER] Model loaded with LoRA")
        
    def load_data(self):
        """Load and tokenize training data."""
        logger.info(f"[TRAINER] Loading data from {self.config.data_path}")
        
        data_path = Path(self.config.data_path)
        if not data_path.exists():
            raise FileNotFoundError(f"Data not found: {data_path}")
        
        examples = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        logger.info(f"[TRAINER] Loaded {len(examples)} examples")
        
        # Format as ChatML
        formatted = []
        for ex in examples:
            messages = [
                {"role": "system", "content": ex.get("system", "You are 012's Digital Twin.")},
                {"role": "user", "content": ex.get("user", "")},
                {"role": "assistant", "content": ex.get("assistant", "")},
            ]
            
            # Tokenize
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
            
            tokens = self.tokenizer(
                text,
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length",
                return_tensors="pt"
            )
            
            formatted.append({
                "input_ids": tokens["input_ids"].squeeze(),
                "attention_mask": tokens["attention_mask"].squeeze(),
                "labels": tokens["input_ids"].squeeze(),
            })
        
        # Create dataset
        from torch.utils.data import Dataset
        
        class VoiceDataset(Dataset):
            def __init__(self, data):
                self.data = data
            def __len__(self):
                return len(self.data)
            def __getitem__(self, idx):
                return self.data[idx]
        
        self.dataset = VoiceDataset(formatted)
        logger.info(f"[TRAINER] Dataset ready: {len(self.dataset)} examples")
        
    def train(self):
        """Run training."""
        if self.model is None:
            self.load_model()
        if self.dataset is None:
            self.load_data()
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation,
            learning_rate=self.config.learning_rate,
            logging_steps=10,
            save_strategy="epoch",
            fp16=True,
            optim="paged_adamw_8bit",
            warmup_ratio=0.03,
            report_to="none",
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset,
        )
        
        logger.info("[TRAINER] Starting training...")
        trainer.train()
        
        # Save LoRA adapter
        adapter_path = output_dir / "voice_lora"
        self.model.save_pretrained(str(adapter_path))
        self.tokenizer.save_pretrained(str(adapter_path))
        
        logger.info(f"[TRAINER] LoRA adapter saved to {adapter_path}")
        return str(adapter_path)


def main():
    """Run voice LoRA training."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train LoRA for 012's voice")
    parser.add_argument("--data", default="training_data/nemo_test/voice_sft.jsonl")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--output", default="training_output/voice_lora")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    config = VoiceTrainingConfig(
        base_model=args.model,
        data_path=args.data,
        output_dir=args.output,
        epochs=args.epochs,
    )
    
    trainer = VoiceLoRATrainer(config)
    adapter_path = trainer.train()
    
    print(f"\n✅ Training complete!")
    print(f"   LoRA adapter: {adapter_path}")


if __name__ == "__main__":
    main()
