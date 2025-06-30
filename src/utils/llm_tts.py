#!/usr/bin/env python3
"""
LLM-Powered Yiddish TTS Utility
===============================
Uses ChatGPT for transliteration, then TTS for speech generation.

Setup:
1. Create .env file in project root:
   OPENAI_API_KEY=your_openai_api_key_here
   
2. Install dependencies:
   pip install openai python-dotenv

Usage:
    1. Paste your text in the YIDDISH_TEXT variable
    2. Set your desired filename in OUTPUT_FILENAME
    3. Run: python src/utils/llm_tts.py
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_transliterator import LLMTransliterator
from core.synthesizer import SpeechSynthesizer


# ============================================================================
# PASTE YOUR TEXT HERE:
# ============================================================================

YIDDISH_TEXT = """מעיאר עריק עדעמס  איז באטראפן געווארן אין ארץ ישראל איינוואוינער טוען באגריסן א נייע 4-וועג סטאפ-סיין"""

# ============================================================================
# SET YOUR OUTPUT FILENAME HERE (without .wav extension):
# ============================================================================

OUTPUT_FILENAME = "llm_speech"

# ============================================================================
# Optional: Add context for better transliteration
# ============================================================================

CONTEXT = ""  # e.g., "news article", "poem", "conversation"

# ============================================================================
# That's it! Run this file to generate your speech using ChatGPT transliteration.
# ============================================================================


def main():
    """Generate speech using LLM transliteration."""
    print("🤖 LLM-Powered Yiddish TTS")
    print("=" * 30)
    
    # Check if text was provided
    if not YIDDISH_TEXT.strip():
        print("❌ No text provided! Please paste your Yiddish text in the YIDDISH_TEXT variable.")
        return
    
    try:
        # Initialize LLM transliterator
        print("🔤 Initializing ChatGPT transliterator...")
        llm_transliterator = LLMTransliterator()
        
        # Initialize speech synthesizer
        synthesizer = SpeechSynthesizer()
        
        print(f"📝 Original text: {YIDDISH_TEXT}")
        
        # Transliterate using ChatGPT
        print("🤖 Transliterating with ChatGPT...")
        if CONTEXT:
            phonetic_text = llm_transliterator.transliterate_with_context(YIDDISH_TEXT, CONTEXT)
        else:
            phonetic_text = llm_transliterator.transliterate(YIDDISH_TEXT)
        
        if not phonetic_text:
            print("❌ Transliteration failed!")
            return
        
        print(f"🔤 ChatGPT result: {phonetic_text}")
        
        # Generate speech from phonetic text
        output_file = f"output/{OUTPUT_FILENAME}.wav"
        print(f"🔊 Generating speech...")
        print(f"💾 Output: {output_file}")
        
        success = synthesizer.synthesize_phonetic_text(phonetic_text, output_file)
        
        if success:
            print(f"✅ Success! Generated: {output_file}")
            print("   You can now play the audio file.")
            print("\n🆚 Compare with rule-based transliteration:")
            
            # Show comparison with rule-based approach
            rule_based = synthesizer.transliterator.transliterate(YIDDISH_TEXT)
            print(f"   Rule-based: {rule_based}")
            print(f"   ChatGPT:    {phonetic_text}")
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