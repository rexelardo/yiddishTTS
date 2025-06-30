#!/usr/bin/env python3
"""
Simple Yiddish TTS Utility
===========================
Copy and paste your Yiddish text below, set your filename, and run!

Usage:
    1. Paste your text in the YIDDISH_TEXT variable
    2. Set your desired filename in OUTPUT_FILENAME
    3. Run: python src/utils/simple_tts.py
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.synthesizer import SpeechSynthesizer


# ============================================================================
# PASTE YOUR TEXT HERE:
# ============================================================================

YIDDISH_TEXT = """מעיאר עריק עדעמס  איז באטראפן געווארן אין ארץ ישראל איינוואוינער טוען באגריסן א נייע 4-וועג סטאפ-סיין"""

# ============================================================================
# SET YOUR OUTPUT FILENAME HERE (without .wav extension):
# ============================================================================

OUTPUT_FILENAME = "my_speech"

# ============================================================================
# That's it! Run this file to generate your speech.
# ============================================================================


def main():
    """Generate speech from the text above."""
    print("🎤 Simple Yiddish TTS")
    print("=" * 25)
    
    # Check if text was provided
    if not YIDDISH_TEXT.strip():
        print("❌ No text provided! Please paste your Yiddish text in the YIDDISH_TEXT variable.")
        return
    
    # Initialize synthesizer
    synthesizer = SpeechSynthesizer()
    
    # Generate output path
    output_file = f"output/{OUTPUT_FILENAME}.wav"
    
    print(f"📝 Text: {YIDDISH_TEXT}")
    print(f"💾 Output: {output_file}")
    print(f"🔊 Generating speech...")
    
    # Generate speech
    success = synthesizer.synthesize_yiddish_text(YIDDISH_TEXT, output_file)
    
    if success:
        print(f"✅ Success! Generated: {output_file}")
        print("   You can now play the audio file.")
    else:
        print(f"❌ Failed to generate speech.")


if __name__ == "__main__":
    main() 