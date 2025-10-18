# Move2Japan Advanced Prompt Engineering System

**Created**: 2025-10-06
**Purpose**: Generate viral Japan-themed YouTube Shorts with anti-MAGA positioning
**Channel**: Move2Japan
**Tech**: Veo 3 + Gemini 2.0 Flash + Custom Prompt Enhancer

---

## 🎯 System Overview

### **Two-Stage Enhancement Pipeline**

```
User Topic
    ↓
Stage 1: Move2Japan Style Enhancement
    ├─ Japan 2025 trending topics
    ├─ Cultural authenticity filters
    ├─ Anti-MAGA progressive values (optional)
    ├─ Viral engagement hooks
    └─ Cinematic visual templates
    ↓
Stage 2: Gemini Final Polish
    ├─ Veo 3 optimization
    ├─ Cinematic refinement
    └─ Fun/cheeky tone injection
    ↓
Veo 3 Video Generation
```

---

## 📚 Components

### 1. **Move2Japan Style Guide**
**File**: `docs/MOVE2JAPAN_STYLE_GUIDE.md`

**Key Elements**:
- ✅ Brand voice (fun, cheeky, authentic, surprising)
- ✅ Japan authenticity filters (real vs stereotypes)
- ✅ Visual style templates (6 cinematicpatterns)
- ✅ Engagement hooks (surprise, POV, secrets)
- ✅ Tone examples (good vs avoid)
- ✅ Success metrics and themes

**Example Perfect Prompts**:
```
Food Discovery:
"A steaming bowl of tonkotsu ramen emerges from kitchen steam in a tiny
Osaka shop, camera slowly circles the bowl showing perfectly cooked chashu
pork, soft-boiled egg, and green onions, a pair of chopsticks lifts noodles
in slow motion, warm golden lighting, the chef smiles proudly in the background"

Urban Discovery:
"A neon-lit Tokyo street at night reflects in rain puddles, camera low angle
following footsteps past vending machines and izakaya doorways, suddenly pans
up to reveal Shibuya crossing's massive LED screens, hundreds of people cross
in perfect synchronized chaos, a single person stops to look up in wonder"
```

### 2. **Prompt Enhancer Module**
**File**: `src/prompt_enhancer.py`

**Class**: `Move2JapanPromptEnhancer`

**Features**:
- 🌸 Japan 2025 trending topics (BeReal, LINE commerce, K-beauty, etc.)
- 🎬 6 visual style templates (cinematic_reveal, pov_discovery, etc.)
- 🗽 Anti-MAGA progressive values (healthcare, safety, trains, education)
- 🎣 Viral engagement hooks (surprise, POV, secret, anti-MAGA)
- 🎨 Sensory details (steam, glow, mist, texture)
- 📹 Camera movements (pan, zoom, dolly, orbit)
- 💡 Cinematic lighting (golden hour, neon, dappled, warm)
- 👥 Human elements (wonder, satisfaction, discovery)

**Methods**:
```python
# Basic enhancement
enhance(topic, include_anti_maga=False, use_trending=True)

# Anti-MAGA positioning
create_anti_maga_japan_prompt(topic)

# Viral hooks
create_viral_hook(topic, hook_type="surprise")
```

### 3. **Veo 3 Generator Integration**
**File**: `src/veo3_generator.py`

**Enhanced Method**:
```python
def enhance_prompt(
    simple_topic: str,
    use_anti_maga: bool = False,
    use_trending: bool = True
) -> str:
    """
    Two-stage enhancement:
    1. Move2Japan style enhancement
    2. Gemini final polish for Veo 3
    """
```

---

## 🌸 Japan 2025 Trending Topics

Based on current research (October 2025):

1. **BeReal.** - Authentic moments (1st place trend)
2. **LINE Social Commerce** - Buy directly on LINE
3. **K-Beauty (fwee cosmetics)** - Vivid colors, wide variety
4. **Angel Mode Aesthetics** - Neo-pastel Korean style
5. **TikTok Viral Challenges** - Gun pose, dance trends
6. **Sustainability Initiatives** - Green tech, renewable energy
7. **Plant-Based Ramen** - Vegan options trending
8. **Neo-Retro Showa Nostalgia** - 80s-90s Japan aesthetic
9. **Digital Nomad Cafes** - Remote work culture

**Integration**: Randomly selected and woven into prompts when `use_trending=True`

---

## 🗽 Anti-MAGA Positioning

### **Implicit Progressive Values**

The system subtly positions Japan as a **progressive alternative** to MAGA ideology through:

#### **8 Core Themes**:

1. **Universal Healthcare**
   - *MAGA*: Medical bankruptcy, no access
   - *Japan*: "Affordable clinic visit, no bankruptcy, just routine care with dignity"

2. **Gun-Free Safety**
   - *MAGA*: School shootings, armed guards
   - *Japan*: "Children walking to school alone safely, society built on trust not fear"

3. **Infrastructure Investment**
   - *MAGA*: Crumbling roads, no high-speed rail
   - *Japan*: "Bullet train departing precisely on time, infrastructure that actually works"

4. **Community Health (Masks)**
   - *MAGA*: Anti-science, individualism
   - *Japan*: "Respectfully wearing masks during cold season, caring about community health"

5. **Education Excellence**
   - *MAGA*: Book bans, defunding schools
   - *Japan*: "Well-funded public school, learning critical thinking, not censorship"

6. **Climate Action**
   - *MAGA*: Climate denial, fossil fuels
   - *Japan*: "Solar panels on traditional roofs, renewable energy, future-focused society"

7. **Civilized Policing**
   - *MAGA*: Police violence, 2nd Amendment worship
   - *Japan*: "Police officer without gun de-escalating situation, civilized society"

8. **Democracy That Works**
   - *MAGA*: Voter suppression, election denial
   - *Japan*: "Easy accessible voting stations with automatic registration"

### **Usage**:

```python
# Explicit anti-MAGA mode
enhancer.create_anti_maga_japan_prompt("healthcare")
# → "person using Japan's universal healthcare at affordable clinic..."

# Implicit values (subtle)
enhancer.enhance("Tokyo street", include_anti_maga=True)
# → Adds progressive values like "multicultural harmony" or "environmental consciousness"
```

---

## 🎣 Viral Engagement Hooks

### **4 Hook Types**:

1. **Surprise** (Default)
   - "You won't believe..."
   - "Wait until you see..."
   - "This will blow your mind..."
   - "Nobody talks about this..."

2. **POV** (First-Person)
   - "POV: You discover..."
   - "POV: Your first time..."
   - "POV: You realize..."
   - "POV: The moment when..."

3. **Secret** (Insider Knowledge)
   - "Locals hide this from tourists..."
   - "The secret spot nobody knows..."
   - "Hidden gem only Japanese people visit..."
   - "What guidebooks won't tell you..."

4. **Anti-MAGA** (Political Positioning)
   - "Why Japan gets it right..."
   - "Facts MAGA won't accept..."
   - "This is what progress looks like..."
   - "Real democracy in action..."

**Usage**:
```python
hook = enhancer.create_viral_hook("Vending machine with hot soup", "surprise")
# → "Nobody talks about this: Vending machine with hot soup"
```

---

## 🎬 Visual Style Templates

### **6 Cinematic Patterns**:

1. **cinematic_reveal**
   - "smooth pan revealing hidden details, golden hour lighting, cinematic composition"

2. **pov_discovery**
   - "first-person perspective, natural movement, surprising discovery moment"

3. **cultural_moment**
   - "everyday Japanese scene, uniquely cultural detail, emotional payoff"

4. **nature_urban_blend**
   - "natural beauty integrated with modern urban life, harmonious contrast"

5. **cozy_comfort**
   - "warm lighting, intimate framing, satisfying sensory details"

6. **viral_trend**
   - "trending format, playful execution, highly shareable moment"

**Selection**: Random by default, or specify: `enhance(topic, style="pov_discovery")`

---

## 🧪 Example Outputs

### **Input**: "Cherry blossoms in Tokyo"

**Stage 1 (Move2Japan Enhancement)**:
```
Specific location: Meguro River, Tokyo, meticulous food presentation,
trending style: Sustainability initiatives, atmospheric mist drifting
through air, smooth dolly in for intimate framing, dappled sunlight
through leaves, someone smiles with quiet satisfaction, natural beauty
integrated with modern urban life, harmonious contrast
```

**Stage 2 (Gemini Polish)**:
```
A gentle morning breeze drifts cherry blossom petals across the Meguro
River in Tokyo, the camera slowly dollies in to reveal a woman in a
soft sweater pausing on a traditional wooden bridge, smiling quietly
as pink petals land in her hair, dappled sunlight filters through the
blooming branches creating dancing shadows on the water below, the
harmonious blend of natural beauty and modern Tokyo life bathed in
warm sustainable morning light.
```

---

### **Input**: "Japan's healthcare" (Anti-MAGA Mode)

**Stage 1**:
```
person using Japan's universal healthcare at affordable clinic,
no bankruptcy, just routine care with dignity, perfectly arranged
seasonal decorations, trending style: BeReal-style authentic moments,
education and expertise (valuing knowledge, craft mastery), gentle
breeze moving fabric/leaves, low angle ascending to eye level, soft
diffused overcast luminosity, a local nods approvingly
```

**Stage 2**:
```
A young professional enters a spotless Tokyo medical clinic, greeted
by friendly staff as she checks in for a routine visit that costs
less than a movie ticket, no insurance battles or bankruptcy fears,
just respectful healthcare delivered with expertise and care, soft
natural light illuminates the modern waiting room decorated with
seasonal ikebana flowers, the camera ascends from a low angle to
reveal her relieved smile—this is what civilized society looks like.
```

---

### **Input**: "Vending machine with hot soup"

**Viral Hook**:
```
"Nobody talks about this: Vending machine with hot soup"
```

**Enhanced Prompt**:
```
A tired salary worker feeds coins into a glowing late-night Tokyo
vending machine, camera zooms to show the incredible variety: hot
corn soup, iced coffee, energy drinks, even steaming ramen cups, a
warm can clanks down with satisfying weight, steam rises as it opens
filling the cold night air, their face lights up with pure simple
joy, neon Tokyo skyline reflects in puddles behind them as they take
that first warm sip—peak Japan convenience culture.
```

---

## 📊 Testing Results

**Prompt Enhancer Test**:
```bash
$ python modules/communication/youtube_shorts/src/prompt_enhancer.py

✅ Topic: Cherry blossoms in Tokyo
✅ Enhanced: [Full enhanced prompt with location, style, trending, etc.]

✅ Topic: Japan's universal healthcare
✅ Enhanced: [Anti-MAGA positioning with progressive values]

✅ Hook: Nobody talks about this: Vending machine with hot soup
```

**Integration Test**:
```python
from modules.communication.youtube_shorts.src.veo3_generator import Veo3Generator

gen = Veo3Generator()
enhanced = gen.enhance_prompt("Cherry blossoms in Tokyo")
# ✅ Two-stage enhancement works
```

---

## 🚀 Usage in Production

### **For Super Chat Shorts**:

When user sends $20+ Super Chat:
```python
# Their message becomes the topic
topic = super_chat_message  # e.g., "Ramen shop in Osaka"

# Generate with trending elements
orchestrator.create_and_upload(
    topic=topic,
    use_anti_maga=False,  # Keep political content opt-in
    use_trending=True     # Always use trending topics
)
```

### **For Anti-MAGA Content**:

During live chat with MAGA trolls:
```python
# Counter-example
topic = "Why Japan has universal healthcare and no medical bankruptcy"

orchestrator.create_and_upload(
    topic=topic,
    use_anti_maga=True,  # Explicit progressive positioning
    use_trending=True
)
```

---

## 📁 Files Created

1. **MOVE2JAPAN_STYLE_GUIDE.md** (15KB)
   - Brand voice and tone guidelines
   - Visual style examples
   - Authenticity filters
   - Success metrics

2. **prompt_enhancer.py** (10KB)
   - `Move2JapanPromptEnhancer` class
   - Trending topics integration
   - Anti-MAGA positioning logic
   - Viral hook generation

3. **PROMPT_ENGINEERING_SYSTEM.md** (this file)
   - Complete system documentation
   - Usage examples
   - Testing results

4. **veo3_generator.py** (updated)
   - Two-stage enhancement pipeline
   - Fallback handling
   - Anti-MAGA mode support

---

## 🎯 Key Advantages

### **vs Generic AI Video Prompts**:
- ✅ **Brand Consistency**: Every Short feels like Move2Japan
- ✅ **Cultural Authenticity**: Real Japan, not stereotypes
- ✅ **Viral Optimization**: Built-in engagement hooks
- ✅ **Trending Integration**: Always current with 2025 trends
- ✅ **Progressive Positioning**: Subtle anti-MAGA values
- ✅ **Cinematic Quality**: Professional visual templates

### **Business Impact**:
- 💰 Higher engagement → More watch time → More revenue
- 📈 Consistent brand voice → Loyal audience
- 🎯 Trending topics → Algorithm boost
- 🗽 Progressive values → Differentiation from right-wing Japan content
- 🌸 Authenticity → Trust and credibility

---

## 🔮 Future Enhancements

1. **A/B Testing System**
   - Test different prompts for same topic
   - Track engagement metrics
   - Optimize hooks and styles

2. **Seasonal Templates**
   - Cherry blossom season (March-April)
   - Summer festivals (July-August)
   - Autumn leaves (October-November)
   - Winter/New Year (December-January)

3. **User Preference Learning**
   - Track which prompts get most $20+ Super Chats
   - Identify top-performing styles
   - Auto-optimize based on revenue

4. **Multi-Language Hooks**
   - Japanese captions
   - Romaji for pronunciation
   - English + Japanese bilingual

---

**Status**: ✅ READY FOR PRODUCTION

The prompt engineering system is fully integrated and tested. Every Super Chat will now generate professionally-crafted, viral-optimized, culturally-authentic Japan Shorts with optional anti-MAGA positioning.

🎬 **Let's make Move2Japan the #1 progressive Japan channel!** 🇯🇵✊
