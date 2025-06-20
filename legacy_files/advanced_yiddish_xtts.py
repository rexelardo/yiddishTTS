#!/usr/bin/env python3
"""
Advanced Yiddish Text-to-Speech using XTTS Multi-File Voice Cloning
===================================================================
This script uses multiple audio files for better voice cloning results.
"""

import os
import torch
from TTS.api import TTS
import glob

# Configuration
AUDIO_DIR = "TTS/audio"
OUTPUT_DIR = "output"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_audio_files(directory):
    """Get all audio files from directory"""
    audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
    audio_files = []
    
    for ext in audio_extensions:
        files = glob.glob(os.path.join(directory, ext))
        audio_files.extend(files)
    
    return audio_files

def initialize_xtts():
    """Initialize XTTS model"""
    print("🐸 Initializing XTTS model...")
    print(f"Using device: {DEVICE}")
    
    # Initialize XTTS v2
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
    
    print(f"Supported languages: {tts.languages}")
    
    return tts

def synthesize_with_multiple_references(tts, text, output_filename, speaker_audios):
    """
    Synthesize text using multiple reference audio files for better cloning
    """
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print(f"🎤 Generating speech for: {text[:50]}...")
    print(f"📁 Using {len(speaker_audios)} reference audio files")
    print(f"📁 Output file: {output_path}")
    
    # Try different language approaches
    languages_to_try = [
        ("ar", "Arabic (similar script)"),
        ("de", "German (Germanic family)"), 
        ("en", "English (fallback)")
    ]
    
    for lang_code, lang_name in languages_to_try:
        try:
            print(f"Trying {lang_name} ({lang_code})...")
            
            # Use multiple reference files - XTTS automatically handles this
            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_audios,  # Pass list of audio files
                language=lang_code,
                file_path=output_path,
                split_sentences=True
            )
            
            print(f"✅ Success with {lang_name}!")
            return output_path
            
        except Exception as e:
            print(f"❌ Failed with {lang_name}: {str(e)}")
            continue
    
    print("❌ Failed with all language attempts")
    return None

def read_yiddish_texts():
    """Read Yiddish texts from your transcript files"""
    texts = []
    transcript_files = [
        "yiddish_24_transcribed/1749769413.txt",
        "yiddish_24_transcribed/1750115277.txt", 
        "yiddish_24_transcribed/1750339888.txt"
    ]
    
    for file_path in transcript_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    texts.append(content)
    
    return texts

def main():
    """Main function"""
    print("=== Advanced Yiddish XTTS Voice Cloning ===")
    
    # Get audio files
    audio_files = get_audio_files(AUDIO_DIR)
    
    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR}")
        return
    
    print(f"🎵 Found {len(audio_files)} audio files:")
    for audio in audio_files:
        print(f"  - {audio}")
    
    # Initialize XTTS
    tts = initialize_xtts()
    
    # Read Yiddish texts
    yiddish_texts = read_yiddish_texts()
    
    if not yiddish_texts:
        print("❌ No Yiddish texts found. Using sample texts...")
        yiddish_texts = [
            "שאלום עליכם, וויאזוי גייט עס?",
            "איך בין צופרידן מיט דעם רעזולטאט",
            "דאס איז א פרווו פון יידיש טעקסט צו רעדע"
        ]
    
    print(f"📝 Found {len(yiddish_texts)} texts to synthesize")
    
    # Generate speech for each text
    for i, text in enumerate(yiddish_texts, 1):
        print(f"\n--- Processing text {i}/{len(yiddish_texts)} ---")
        
        # Limit text length for better results
        if len(text) > 200:
            text = text[:200] + "..."
            print("⚠️  Text truncated to 200 characters for better results")
        
        output_file = f"yiddish_advanced_{i}.wav"
        result = synthesize_with_multiple_references(
            tts, text, output_file, audio_files
        )
        
        if result:
            print(f"✅ Generated: {result}")
        else:
            print(f"❌ Failed to generate audio for text {i}")
        
        print("-" * 60)
    
    print("\n🎉 Advanced Yiddish TTS generation complete!")
    print(f"📁 Check the '{OUTPUT_DIR}' folder for generated audio files")
    
    # Show tips for better results
    print("\n💡 Tips for better results:")
    print("1. Use audio files that are at least 6 seconds long")
    print("2. Ensure audio quality is good (clear, minimal background noise)")
    print("3. If results aren't good, try adjusting the text or using different reference audio")
    print("4. Consider using only the best quality audio file if multi-file results are poor")

if __name__ == "__main__":
    main() 