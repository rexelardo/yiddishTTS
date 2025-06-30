#!/usr/bin/env python3
"""
Accent-Enhanced Yiddish TTS Utility with ChatGPT Transliteration
================================================================
Uses ChatGPT for transliteration + German accent for authentic pronunciation.

Setup:
1. Create .env file in project root:
   OPENAI_API_KEY=your_openai_api_key_here
   
2. Install dependencies:
   pip install openai python-dotenv

Usage:
    1. Paste your text in the YIDDISH_TEXT variable
    2. Set your desired filename in OUTPUT_FILENAME
    3. Choose your accent in ACCENT (default: 'german')
    4. Run: python src/utils/accent_tts.py
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.enhanced_synthesizer import EnhancedYiddishSynthesizer
from core.llm_transliterator import LLMTransliterator


# ============================================================================
# PASTE YOUR TEXT HERE:
# ============================================================================

YIDDISH_TEXT = """אַן אוקראַינישע "עף 16" מיליטערישע פּילאָט איז געשטאָרבן אין א קראַך, אינמיטן אַרבעטן אָפּצושטעלן א רוסישע לופט אַטאַקע, וואָס האָט אַריינגענומען הונדערטער דראָונס, קרוז מיסילס און באַליסטישע מיסיל • די איראַנער רעגירונג זאָגט אַז מדינת ישראל'ס באָמבאַרדירונג אויף די גרויסע עווין טורמע אין די איראַנער הויפּטשטאָט טעהראַן, האָט געקאָסט די לעבנס פון 71 מענטשן • די קאָנגרעס בודזשעט אָפיס זאָגט אַז די סענאַט ווערסיע פון פּרעזידענט טראָמפּ'ס גרויסע שטייער שניטן און שפּענדונג ביל, וועט צולייגן 3.3 טריליאָן דאָלער צו די פעדעראַלע בודזשעט דעפיציט אין די קומענדיגע צען יאָר • פּרעזידענט טראָמפּ זאָגט אַז די געשפּרעכן מיט קאַנאַדע זענען דערווייל איינגעפרוירן, ביז ווילאַנג קאַנאַדע וועט נישט אַראָפּנעמען געוויסע שטייערן פון אַמעריקאַנער קאָמפּאַניס • קאָנגרעסמאַן דאָן בעיקען, וועלכער איז פון די געציילטע רעפּובליקאַנער וואָס שטעלן זיך אָפט אַרויס קעגן פּרעזידענט טראָמפּ, האָט געמאָלדן אַז ער וועט נישט לויפן פאַר ווידערוויילונג • דער לינקער ליבעראַלער מעיאָר קאַנדידאַט זאראן מאמדאני האָט ווידערהאָלט זיין פּלאַן אַז ער וועט צילן געגנטער וואו עס וואוינען מער ווייסע אין ניו יאָרק סיטי, צו שטעלן דאָרטן העכערע שטייערן און רעגירונג רעגולאַציעס"""

# ============================================================================
# SET YOUR OUTPUT FILENAME HERE (without .wav extension):
# ============================================================================

OUTPUT_FILENAME = "yiddish_accent_speech"

# ============================================================================
# CHOOSE YOUR ACCENT:
# Options: 'german', 'polish', 'russian', 'hungarian', 'dutch', 'english'
# ============================================================================

ACCENT = "polish"  # German accent is most authentic for Yiddish

# ============================================================================
# Optional: Add context for better ChatGPT transliteration
# ============================================================================

CONTEXT = ""  # e.g., "news article", "poem", "conversation"

# ============================================================================
# Optional: Customize voice settings (leave None to use accent defaults)
# ============================================================================

CUSTOM_SPEED = None  # e.g., 140 (words per minute)
CUSTOM_PITCH = None  # e.g., 45 (0-99)

# ============================================================================
# That's it! Run this file for ChatGPT transliteration + authentic accent.
# ============================================================================


def main():
    """Generate speech with ChatGPT transliteration and authentic accent."""
    print("🤖🎭 ChatGPT + Accent-Enhanced Yiddish TTS")
    print("=" * 45)
    
    # Check if text was provided
    if not YIDDISH_TEXT.strip():
        print("❌ No text provided! Please paste your Yiddish text in the YIDDISH_TEXT variable.")
        return
    
    try:
        # Initialize ChatGPT transliterator
        print("🔤 Initializing ChatGPT transliterator...")
        llm_transliterator = LLMTransliterator()
        
        # Initialize enhanced synthesizer with chosen accent
        synthesizer = EnhancedYiddishSynthesizer(accent=ACCENT)
        
        print(f"📝 Original text: {YIDDISH_TEXT}")
        
        # Transliterate using ChatGPT
        print("🤖 Transliterating with ChatGPT...")
        if CONTEXT:
            phonetic_text = llm_transliterator.transliterate_with_context(YIDDISH_TEXT, CONTEXT)
        else:
            phonetic_text = llm_transliterator.transliterate(YIDDISH_TEXT)
        
        if not phonetic_text:
            print("❌ ChatGPT transliteration failed!")
            return
        
        print(f"🔤 ChatGPT result: {phonetic_text}")
        
        # Generate output path
        output_file = f"output/{OUTPUT_FILENAME}.wav"
        print(f"💾 Output: {output_file}")
        
        # Generate speech with accent using ChatGPT transliteration
        print(f"🎭 Generating speech with {synthesizer.voice_config['name']} accent...")
        success = synthesizer.synthesize_phonetic_text(
            phonetic_text, 
            output_file,
            speed=CUSTOM_SPEED,
            pitch=CUSTOM_PITCH
        )
        
        if success:
            print(f"\n✅ Success! Generated: {output_file}")
            print("   You can now play the audio file.")
            print(f"\n🆚 Comparison:")
            
            # Show comparison with rule-based approach
            rule_based = synthesizer.transliterator.transliterate(YIDDISH_TEXT)
            print(f"   Rule-based: {rule_based}")
            print(f"   ChatGPT:    {phonetic_text}")
            print(f"\n🎭 Generated with {synthesizer.voice_config['name']} accent")
            print("   Best of both: ChatGPT transliteration + authentic German accent!")
        else:
            print(f"❌ Failed to generate speech.")
            
    except ValueError as e:
        print(f"❌ Setup error: {e}")
        print("\nSetup instructions:")
        print("1. Create a .env file in the project root")
        print("2. Add your OpenAI API key: OPENAI_API_KEY=your_key_here")
        print("3. Install dependencies: pip install openai python-dotenv")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 