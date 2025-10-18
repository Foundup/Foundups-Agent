# How To Test YouTube Shorts - Talking Baby Feature 👶🎥

## Quick Test (FREE - No Cost)

Test the talking baby prompt enhancement without generating videos:

```bash
cd O:\Foundups-Agent
PYTHONIOENCODING=utf-8 python modules/communication/youtube_shorts/tests/test_promo_generation.py
```

**What it does**:
- ✅ Tests talking baby is included in all prompts
- ✅ Generates META promotional prompt
- ✅ Initializes Veo3 generator
- ⏸️ Asks before actual video generation ($12 cost)

---

## Test Talking Baby Prompt Enhancement

Quick Python test to see prompts with talking baby:

```python
from modules.communication.youtube_shorts.src.prompt_enhancer import Move2JapanPromptEnhancer

enhancer = Move2JapanPromptEnhancer()

# Test any topic - talking baby is ALWAYS included now
topic = "Ramen shop in Tokyo"
enhanced = enhancer.enhance(topic)

print(enhanced)
# Output includes: "baby bouncing happily saying 'Move! Japan!' in adorable baby voice..."
```

---

## Generate Actual Video ($12 Cost)

### Option 1: Generate Promotional Short

This creates the META promo video about the feature itself:

```bash
cd O:\Foundups-Agent
PYTHONIOENCODING=utf-8 python modules/communication/youtube_shorts/tests/test_promo_generation.py
# When prompted, type "yes" to generate
```

**Prompt**: Baby in kimono explaining how to make videos via Super Chat
**Cost**: $12 (30 seconds)
**Time**: 1-2 minutes

### Option 2: Generate Any Topic with Talking Baby

```python
from modules.communication.youtube_shorts.src.veo3_generator import Veo3Generator

generator = Veo3Generator()

# Any topic will now have talking baby narrator
topic = "Cherry blossoms falling in Tokyo"

# Enhance with talking baby (automatic)
enhanced_prompt = generator.enhance_prompt(topic)

# Generate video
video_path = generator.generate_video(
    prompt=enhanced_prompt,
    duration=30,  # 30 seconds = $12
    fast_mode=True
)

print(f"Video: {video_path}")
```

---

## Test Live Chat Super Chat Integration

### 1. Mock Super Chat (FREE)

Test the $20 Super Chat workflow without actual donation:

```bash
cd O:\Foundups-Agent
PYTHONIOENCODING=utf-8 python modules/communication/youtube_shorts/tests/test_super_chat_integration.py
```

**Tests**:
- ✅ Super Chat event parsing
- ✅ $20 threshold check
- ✅ Topic extraction
- ✅ Handler routing
- ⚠️ Video generation (mocked - no cost)

### 2. Real Super Chat Test (COSTS $20+)

1. Start YouTube Live stream
2. Send $20+ Super Chat with topic: "Cherry blossoms in Tokyo"
3. Bot detects Super Chat event
4. Generates video with talking baby ($12 cost from $20 donation)
5. Uploads to YouTube as Short

**Net**: $20 donation - $12 generation = $8 profit

---

## Cost Breakdown

| Action | Cost | Time |
|--------|------|------|
| Prompt Enhancement Test | FREE | 5 seconds |
| Veo3 Initialization Test | FREE | 2 seconds |
| 5-second test video | $2 | 30 seconds |
| 30-second Short | $12 | 1-2 minutes |
| 60-second Short | $24 | 2-3 minutes |

---

## What Makes The Talking Baby Special? 👶

**Before (Generic)**:
```
Cherry blossoms in Tokyo, Meguro River, golden hour lighting
```

**After (With Talking Baby)** ✨:
```
Cherry blossoms in Tokyo, Meguro River, golden hour lighting,
baby bouncing happily saying 'Move! Japan!' in adorable baby voice with huge smile
```

**Result**: Every video has consistent Move2Japan branding with adorable baby narrator!

---

## Recommended Testing Flow

### Stage 1: Validation (FREE)
```bash
# Test prompts work
python modules/communication/youtube_shorts/tests/test_promo_generation.py
# All 3 tests should pass
```

### Stage 2: Small Test ($2)
```python
# Generate 5-second test video
generator = Veo3Generator()
topic = "Tokyo street at night"
enhanced = generator.enhance_prompt(topic)  # Includes talking baby
video = generator.generate_video(enhanced, duration=5)  # $2 cost
```

### Stage 3: Full Short ($12)
```python
# Generate 30-second promotional Short
# Use test_promo_generation.py and type "yes"
```

### Stage 4: Live Test ($20)
```
1. Start YouTube Live stream
2. Send $20 Super Chat: "Ramen shop in Osaka"
3. Wait 1-2 minutes
4. Video auto-posts with talking baby narrator
```

---

## Example Prompts Generated

**Topic**: "Cherry blossoms in Tokyo"

**Enhanced Prompt**:
```
Specific location: Meguro River, Tokyo,
perfectly arranged seasonal decorations,
trending style: BeReal-style authentic moments,
gentle breeze moving fabric/leaves,
slow smooth pan from left to right,
golden hour warm soft light,
a person pauses in genuine wonder,
baby bouncing happily saying 'Move! Japan!' in adorable baby voice with huge smile,
smooth pan revealing hidden details, golden hour lighting, cinematic composition
```

**Result**: 30-second video with:
- ✅ Cherry blossoms at Meguro River
- ✅ Golden hour cinematic lighting
- ✅ Smooth camera pan
- ✅ **Adorable baby saying "Move! Japan!"**
- ✅ Trending BeReal style
- ✅ Authentic Japan vibes

---

## Troubleshooting

**Error**: `GOOGLE_API_KEY not found`
- Check `.env` file has `GOOGLE_API_KEY=AIza...`

**Error**: `'GenerativeModel' object has no attribute 'predict_long_running'`
- Run: `pip install google-genai>=0.3.0`

**Issue**: Baby not in prompt
- Verify you're using latest `prompt_enhancer.py`
- Check `enhance()` method includes `_add_talking_baby()`

**Issue**: Video generation fails
- Check API quota/credits
- Verify `google-genai` SDK installed (not just `google-generativeai`)

---

## Ready to Generate?

```bash
# Quick validation test (FREE)
cd O:\Foundups-Agent
PYTHONIOENCODING=utf-8 python modules/communication/youtube_shorts/tests/test_promo_generation.py

# When ready for actual video, type "yes" when prompted
```

**Remember**: Every video now has a talking baby narrator! 👶✨
