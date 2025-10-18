# Colab Training Upload Instructions

## What You Have

**File**: `colab_training_export.json`
**Size**: 3.11 MB
**Purpose**: Train Gemma on FoundUps-Agent system data

## Data Sources Included

This export contains training data from ALL system sources:

1. **012.txt**: 0102 operational decisions (PRIMARY)
2. **ModLog files**: Module change history
3. **WSP violations**: Violation -> Fix patterns
4. **Chat logs**: LiveChat conversation memory
5. **Git history**: Commits, renames, fixes
6. **Daemon logs**: DAE operational data

## Upload to Colab

### Step 1: Create New Colab Notebook

1. Go to https://colab.research.google.com/
2. Click "New Notebook"
3. Change runtime to GPU: Runtime -> Change runtime type -> GPU (T4)

### Step 2: Upload Training Data

```python
from google.colab import files
uploaded = files.upload()
# Select: colab_training_export.json
```

### Step 3: Follow Training Instructions

The JSON file contains complete training instructions in the `training_instructions` field.

Load it and follow the steps:

```python
import json

with open('colab_training_export.json', 'r') as f:
    data = json.load(f)

# View instructions
for step in data['training_instructions']['steps']:
    print(f"Step {step['step']}: {step['title']}")
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
