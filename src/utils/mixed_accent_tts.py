#!/usr/bin/env python3
"""
Mixed Accent Yiddish TTS Utility
================================
Creates blended accents for ultra-authentic Yiddish pronunciation.

Usage:
    1. Paste your text in the YIDDISH_TEXT variable
    2. Set your desired filename in OUTPUT_FILENAME
    3. Choose your blend in ACCENT_BLEND
    4. Run: python src/utils/mixed_accent_tts.py
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.accent_mixer import AccentMixer
from core.llm_transliterator import LLMTransliterator
from core.transliterator import YiddishTransliterator


# ============================================================================
# PASTE YOUR TEXT HERE:
# ============================================================================

YIDDISH_TEXT = """אַן אוקראַינישע "עף 16" מיליטערישע פּילאָט איז געשטאָרבן אין א קראַך, אינמיטן אַרבעטן אָפּצושטעלן א רוסישע לופט אַטאַקע, וואָס האָט אַריינגענומען הונדערטער דראָונס, קרוז מיסילס און באַליסטישע מיסיל • די איראַנער רעגירונג זאָגט אַז מדינת ישראל'ס באָמבאַרדירונג אויף די גרויסע עווין טורמע אין די איראַנער הויפּטשטאָט טעהראַן, האָט געקאָסט די לעבנס פון 71 מענטשן • די קאָנגרעס בודזשעט אָפיס זאָגט אַז די סענאַט ווערסיע פון פּרעזידענט טראָמפּ'ס גרויסע שטייער שניטן און שפּענדונג ביל, וועט צולייגן 3.3 טריליאָן דאָלער צו די פעדעראַלע בודזשעט דעפיציט אין די קומענדיגע צען יאָר • פּרעזידענט טראָמפּ זאָגט אַז די געשפּרעכן מיט קאַנאַדע זענען דערווייל איינגעפרוירן, ביז ווילאַנג קאַנאַדע וועט נישט אַראָפּנעמען געוויסע שטייערן פון אַמעריקאַנער קאָמפּאַניס • קאָנגרעסמאַן דאָן בעיקען, וועלכער איז פון די געציילטע רעפּובליקאַנער וואָס שטעלן זיך אָפט אַרויס קעגן פּרעזידענט טראָמפּ, האָט געמאָלדן אַז ער וועט נישט לויפן פאַר ווידערוויילונג • דער לינקער ליבעראַלער מעיאָר קאַנדידאַט זאראן מאמדאני האָט ווידערהאָלט זיין פּלאַן אַז ער וועט צילן געגנטער וואו עס וואוינען מער ווייסע אין ניו יאָרק סיטי, צו שטעלן דאָרטן העכערע שטייערן און רעגירונג רעגולאַציעס"""

# ============================================================================
# SET YOUR OUTPUT FILENAME HERE (without .wav extension):
# ============================================================================

OUTPUT_FILENAME = "yiddish_mixed_accent"

# ============================================================================
# CHOOSE YOUR ACCENT BLEND:
# Options: 'yiddish_authentic', 'eastern_european', 'germanic_yiddish', 'austro_hungarian'
# Or set to 'custom' to define your own mix below
# ============================================================================

ACCENT_BLEND = "yiddish_authentic"  # German + Hungarian blend

# ============================================================================
# CUSTOM BLEND SETTINGS (only used if ACCENT_BLEND = 'custom'):
# ============================================================================

CUSTOM_ACCENTS = ['german', 'hungarian', 'polish']
CUSTOM_WEIGHTS = [0.5, 0.3, 0.2]  # Must sum to 1.0
CUSTOM_SPEED_ADJUST = -5  # -10 to +10
CUSTOM_PITCH_ADJUST = -2  # -10 to +10

# ============================================================================
# TRANSLITERATION METHOD:
# Options: 'chatgpt' (needs .env with API key) or 'rule_based'
# ============================================================================

TRANSLITERATION_METHOD = "rule_based"  # or "chatgpt"

# ============================================================================
# Optional: Context for ChatGPT transliteration
# ============================================================================

CONTEXT = ""  # e.g., "news article", "conversation"

# ============================================================================
# That's it! Run this file to generate blended accent speech.
# ============================================================================


def main():
    """Generate speech with blended accents."""
    print("🎭🎶 Mixed Accent Yiddish TTS")
    print("=" * 35)
    
    # Check if text was provided
    if not YIDDISH_TEXT.strip():
        print("❌ No text provided! Please paste your Yiddish text in the YIDDISH_TEXT variable.")
        return
    
    # Initialize accent mixer
    mixer = AccentMixer()
    
    # Show available blends
    print("\n🎭 Available accent blends:")
    mixer.list_available_blends()
    
    print(f"📝 Original text: {YIDDISH_TEXT}")
    
    # Transliterate text
    try:
        if TRANSLITERATION_METHOD == "chatgpt":
            print("🤖 Using ChatGPT transliteration...")
            llm_transliterator = LLMTransliterator()
            if CONTEXT:
                phonetic_text = llm_transliterator.transliterate_with_context(YIDDISH_TEXT, CONTEXT)
            else:
                phonetic_text = llm_transliterator.transliterate(YIDDISH_TEXT)
        else:
            print("📖 Using rule-based transliteration...")
            rule_transliterator = YiddishTransliterator()
            phonetic_text = rule_transliterator.transliterate(YIDDISH_TEXT)
        
        if not phonetic_text:
            print("❌ Transliteration failed!")
            return
        
        print(f"🔤 Phonetic text: {phonetic_text}")
        
    except Exception as e:
        print(f"❌ Transliteration error: {e}")
        if TRANSLITERATION_METHOD == "chatgpt":
            print("💡 Try setting TRANSLITERATION_METHOD = 'rule_based' or set up your .env file")
        return
    
    # Generate output path
    output_file = f"output/{OUTPUT_FILENAME}.wav"
    print(f"💾 Output: {output_file}")
    
    # Create accent blend
    try:
        if ACCENT_BLEND == 'custom':
            print(f"🎨 Creating custom blend...")
            success = mixer.create_custom_blend(
                phonetic_text,
                CUSTOM_ACCENTS,
                CUSTOM_WEIGHTS,
                output_file,
                CUSTOM_SPEED_ADJUST,
                CUSTOM_PITCH_ADJUST
            )
        else:
            print(f"🎭 Creating {ACCENT_BLEND} blend...")
            success = mixer.create_accent_blend(
                phonetic_text,
                ACCENT_BLEND,
                output_file
            )
        
        if success:
            print(f"\n✅ Success! Generated blended accent: {output_file}")
            print("   This should sound incredibly authentic!")
            print(f"\n🎭 Blend details:")
            if ACCENT_BLEND != 'custom':
                blend_config = mixer.ACCENT_BLENDS[ACCENT_BLEND]
                print(f"   Name: {blend_config['name']}")
                print(f"   Mix: {blend_config['description']}")
                accents_str = " + ".join([f"{acc} ({w:.0%})" for acc, w in zip(blend_config['accents'], blend_config['weights'])])
                print(f"   Accents: {accents_str}")
            else:
                accents_str = " + ".join([f"{acc} ({w:.0%})" for acc, w in zip(CUSTOM_ACCENTS, CUSTOM_WEIGHTS)])
                print(f"   Custom mix: {accents_str}")
        else:
            print(f"❌ Failed to generate blended accent.")
            
    except Exception as e:
        print(f"❌ Accent blending error: {e}")
        print("💡 Make sure sox is installed: sudo apt install sox")


if __name__ == "__main__":
    main() 