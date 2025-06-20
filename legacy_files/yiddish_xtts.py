#!/usr/bin/env python3
"""
Yiddish Text-to-Speech using XTTS Voice Cloning
================================================
This script uses Coqui XTTS to generate speech from Yiddish text (in Hebrew script)
by cloning the voice from your existing audio files.

Requirements:
- Your virtual environment should already have TTS installed
- Audio files should be at least 3 seconds long for good cloning results
"""

import os
import torch
from TTS.api import TTS

# Configuration
SPEAKER_AUDIO_PATH = "TTS/audio/1749769413.wav"  # Path to your reference audio
OUTPUT_DIR = "output"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def initialize_xtts():
    """Initialize XTTS model"""
    print("🐸 Initializing XTTS model...")
    print(f"Using device: {DEVICE}")
    
    # Initialize XTTS v2 - the latest version with best voice cloning
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
    
    # Check supported languages
    print(f"Supported languages: {tts.languages}")
    
    return tts

def synthesize_yiddish_text(tts, text, output_filename, speaker_audio=SPEAKER_AUDIO_PATH):
    """
    Synthesize Yiddish text to speech
    
    Args:
        tts: TTS model instance
        text: Yiddish text in Hebrew script
        output_filename: Output audio file name
        speaker_audio: Path to reference audio for voice cloning
    """
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print(f"🎤 Generating speech for: {text[:50]}...")
    print(f"📁 Output file: {output_path}")
    
    # Since XTTS doesn't have direct Yiddish support, we'll try different approaches:
    # 1. First try Hebrew (closest language)
    # 2. If that fails, try German (Germanic language family)
    # 3. As fallback, use English (most robust)
    
    languages_to_try = ["ar", "de", "en"]  # Arabic has Hebrew-like script, German is Germanic, English as fallback
    
    for lang in languages_to_try:
        try:
            print(f"Trying language code: {lang}")
            
            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_audio,
                language=lang,
                file_path=output_path,
                split_sentences=True  # This helps with longer texts
            )
            
            print(f"✅ Success! Audio generated with language: {lang}")
            return output_path
            
        except Exception as e:
            print(f"❌ Failed with {lang}: {str(e)}")
            continue
    
    print("❌ Failed to generate audio with all language attempts")
    return None

def main():
    """Main function to demonstrate Yiddish TTS"""
    
    # Check if reference audio exists
    if not os.path.exists(SPEAKER_AUDIO_PATH):
        print(f"❌ Reference audio not found: {SPEAKER_AUDIO_PATH}")
        print("Please make sure your audio file exists!")
        return
    
    # Initialize XTTS
    tts = initialize_xtts()
    
    # Example Yiddish texts from your files
    yiddish_texts = [
        "די ניו יארק סטעיט סענאט האט געשטימט",
        "אין לעיקוואוד חברים איינגעשפאנט ציצושטעלן עלעקטאריק",
        "שאלום עליכם, וויאזוי גייט עס?"
    ]
    
    print("🎯 Starting Yiddish TTS generation...")
    
    for i, text in enumerate(yiddish_texts, 1):
        output_file = f"yiddish_output_{i}.wav"
        result = synthesize_yiddish_text(tts, text, output_file)
        
        if result:
            print(f"✅ Generated: {result}")
        else:
            print(f"❌ Failed to generate audio for text {i}")
        
        print("-" * 50)
    
    print("🎉 Yiddish TTS generation complete!")
    print(f"📁 Check the '{OUTPUT_DIR}' folder for generated audio files")

if __name__ == "__main__":
    main() 