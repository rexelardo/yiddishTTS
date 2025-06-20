# Yiddish Text-to-Speech Solutions

## 🎯 Your Situation
- **Goal**: Generate speech from Yiddish text (Hebrew script)  
- **Available data**: 3 audio files + 3 text files (not enough for training)
- **Best approach**: Voice cloning with pre-trained models

## ✅ **WORKING SOLUTION** (Currently Implemented)

### Transliterated TTS (`transliterated_tts.py`)
**Status**: ✅ Working  
**Quality**: Basic but functional  
**Files generated**: 
- `output/yiddish_phonetic_1.wav`
- `output/yiddish_phonetic_2.wav` 
- `output/yiddish_phonetic_3.wav`

**How it works**:
1. Converts Yiddish text to phonetic Latin script
2. Uses espeak TTS engine (reliable, available on Linux)
3. Generates basic but understandable speech

## 🚫 **Issues with Advanced Solutions**

### XTTS (Coqui TTS) Issues
**Status**: ❌ Not working due to PyTorch compatibility  
**Problem**: PyTorch 2.7 changed default `weights_only=True`, but XTTS models require `weights_only=False`

**Error**: `WeightsUnpickler error: Unsupported global: GLOBAL TTS.tts.configs.xtts_config.XttsConfig`

## 🔧 **Recommended Next Steps**

### 1. **Immediate Use** (What's Working Now)
```bash
python transliterated_tts.py
```
- Generates speech from your Yiddish texts
- Basic quality but functional
- No voice cloning (uses default synthetic voice)

### 2. **Better Quality Options**

#### Option A: Fix XTTS Compatibility
```bash
# Downgrade PyTorch (may break other dependencies)
pip install torch==2.0.1 torchaudio==2.0.2

# OR use alternative XTTS installation
pip install -e git+https://github.com/coqui-ai/TTS.git@main#egg=TTS
```

#### Option B: Use Commercial Services
- **ElevenLabs**: Best quality, supports voice cloning
- **Google Cloud TTS**: May work with Hebrew text
- **Azure Speech**: Has Hebrew support

#### Option C: Alternative Open Source
- **Bark**: `pip install bark-tts`
- **StyleTTS2**: Newer architecture
- **Fairseq MMS**: Supports 1000+ languages

### 3. **Improve Phonetic Mapping**
The current transliteration is basic. You can improve it by:

```python
# Better Yiddish phonetic mapping
mapping = {
    'שׁ': 'sh', 'שׂ': 's',    # Distinguish shin/sin
    'אי': 'ay', 'וי': 'oy',   # Diphthongs
    'יי': 'ey', 'וו': 'v',    # Double letters
    # Add more specific mappings...
}
```

## 📊 **Quality Comparison**

| Method | Quality | Voice Cloning | Yiddish Support | Status |
|--------|---------|---------------|-----------------|--------|
| espeak (current) | ⭐⭐ | ❌ | Via transliteration | ✅ Working |
| XTTS | ⭐⭐⭐⭐⭐ | ✅ | Via transliteration | ❌ Broken |
| ElevenLabs | ⭐⭐⭐⭐⭐ | ✅ | Via transliteration | 💰 Paid |
| Google TTS | ⭐⭐⭐⭐ | ❌ | Maybe direct Hebrew | 💰 Paid |

## 🎵 **Using Your Voice Cloning Data**

Your 3 audio files in `TTS/audio/` can be used for voice cloning once XTTS is fixed:

1. **1749769413.wav** - Use as primary reference
2. **1750115277.wav** - Additional reference  
3. **1750339888.wav** - Additional reference

**Recommended approach**:
- Use all 3 files together for better voice cloning
- Ensure they're at least 3 seconds each (check with `ffprobe`)
- Clean audio quality improves results

## 🔍 **Debugging XTTS (If You Want to Fix It)**

The error occurs in `TTS/tts/models/xtts.py` line 714:
```python
# Current (failing):
checkpoint = load_fsspec(model_path, map_location=torch.device("cpu"))["model"]

# Potential fix:
checkpoint = load_fsspec(model_path, map_location=torch.device("cpu"), weights_only=False)["model"]
```

## 📝 **Your Original Texts**
For reference, here are your Yiddish texts and their phonetic conversions:

1. **Original**: שאלום עליכם, וויאזוי גייט עס?  
   **Phonetic**: shalum elikm, uuiazui giit es?

2. **Original**: איך בין צופרידן מיט דעם רעזולטאט  
   **Phonetic**: aikh bin tsupridn mit dem rezultat

3. **Original**: דאס איז א פרווו פון יידיש טעקסט צו רעדע  
   **Phonetic**: das aiz a pruuu pun iidish tekst tsu rede

## 🚀 **Next Actions**
1. ✅ Test the generated audio files: `ls output/`
2. 🔧 Improve phonetic mapping in `transliterated_tts.py`
3. 🎯 Try commercial services for better quality
4. 🔨 Fix XTTS if you need voice cloning

The current solution works and gives you functional Yiddish TTS. For production quality, consider the commercial options or fixing the XTTS compatibility issue. 