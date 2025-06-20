#!/usr/bin/env python3
"""
Simple Yiddish TTS using command line interface
===============================================
Since there are compatibility issues with the Python API, 
let's use the command line interface instead.
"""

import os
import subprocess
import glob

def get_audio_files(directory):
    """Get all audio files from directory"""
    audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
    audio_files = []
    
    for ext in audio_extensions:
        files = glob.glob(os.path.join(directory, ext))
        audio_files.extend(files)
    
    return audio_files

def run_tts_command(text, speaker_wav, output_file, language="en"):
    """Run TTS using command line interface"""
    
    cmd = [
        "tts",
        "--model_name", "tts_models/multilingual/multi-dataset/xtts_v2",
        "--text", text,
        "--speaker_wav", speaker_wav,
        "--language_idx", language,
        "--out_path", output_file
    ]
    
    try:
        print(f"Running TTS command...")
        print(f"Text: {text[:50]}...")
        print(f"Speaker: {speaker_wav}")
        print(f"Output: {output_file}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Success! Generated: {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main function"""
    print("=== Simple Yiddish TTS using Command Line ===")
    
    # Configuration
    audio_dir = "TTS/audio"
    output_dir = "output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get audio files
    audio_files = get_audio_files(audio_dir)
    
    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}")
        return
    
    print(f"🎵 Found {len(audio_files)} audio files:")
    for audio in audio_files:
        print(f"  - {audio}")
    
    # Use the first audio file as reference
    reference_audio = audio_files[0]
    
    # Yiddish texts to synthesize
    yiddish_texts = [
        "שאלום עליכם, וויאזוי גייט עס?",
        "איך בין צופרידן מיט דעם רעזולטאט",
        "דאס איז א פרווו פון יידיש טעקסט צו רעדע"
    ]
    
    # Try different languages
    languages_to_try = ["ar", "de", "en"]  # Arabic, German, English
    
    for i, text in enumerate(yiddish_texts, 1):
        print(f"\n--- Processing text {i}/{len(yiddish_texts)} ---")
        
        success = False
        for lang in languages_to_try:
            output_file = os.path.join(output_dir, f"yiddish_simple_{i}_{lang}.wav")
            
            print(f"Trying language: {lang}")
            if run_tts_command(text, reference_audio, output_file, lang):
                success = True
                break
        
        if not success:
            print(f"❌ Failed to generate audio for text {i} with all languages")
        
        print("-" * 60)
    
    print("\n🎉 Simple Yiddish TTS generation complete!")
    print(f"📁 Check the '{output_dir}' folder for generated audio files")

if __name__ == "__main__":
    main() 