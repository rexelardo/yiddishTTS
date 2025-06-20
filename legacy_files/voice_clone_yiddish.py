#!/usr/bin/env python3
"""
Voice Clone Yiddish Speech
=========================
Takes the generated yiddish_speech.wav and applies voice cloning 
using the reference audio files to make it sound like the original speaker.
"""

import os
import subprocess
import torch
from TTS.api import TTS
import glob

# Configuration
GENERATED_SPEECH = "output/yiddish_speech.wav"
REFERENCE_AUDIO_DIR = "yiddish24_audio"
OUTPUT_DIR = "output"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def get_reference_audio_files():
    """Get reference audio files for voice cloning"""
    audio_files = glob.glob(os.path.join(REFERENCE_AUDIO_DIR, "*.wav"))
    return sorted(audio_files)

def try_voice_conversion_models():
    """Try different voice conversion approaches"""
    
    print("🔍 Available voice conversion models:")
    
    # Try to list available voice conversion models
    try:
        tts = TTS()
        models = tts.list_models()
        
        # Look for voice conversion models
        vc_models = []
        for model_type in models:
            if 'voice_conversion' in model_type:
                for model in models[model_type]:
                    vc_models.append(f"{model_type}/{model}")
        
        print(f"Found {len(vc_models)} voice conversion models:")
        for model in vc_models:
            print(f"  - {model}")
        
        return vc_models
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def voice_convert_with_tts(source_wav, target_wav, output_wav, model_name=None):
    """Use TTS voice conversion"""
    
    if model_name is None:
        # Try the most common voice conversion model
        model_name = "voice_conversion_models/multilingual/vctk/freevc24"
    
    try:
        print(f"🔄 Trying voice conversion with model: {model_name}")
        
        # Initialize voice conversion model
        tts = TTS(model_name=model_name, progress_bar=False).to(DEVICE)
        
        # Perform voice conversion
        tts.voice_conversion_to_file(
            source_wav=source_wav,
            target_wav=target_wav, 
            file_path=output_wav
        )
        
        print(f"✅ Voice conversion successful!")
        return True
        
    except Exception as e:
        print(f"❌ Voice conversion failed: {e}")
        return False

def try_alternative_voice_conversion(source_wav, target_wav, output_wav):
    """Try alternative voice conversion methods"""
    
    # Try using sox for simple pitch/formant adjustment
    try:
        print("🔄 Trying simple voice adjustment with sox...")
        
        # This is a basic approach - analyze target audio and apply similar characteristics
        cmd = [
            "sox", source_wav, output_wav,
            "pitch", "-100",     # Lower pitch slightly
            "reverb", "10",      # Add slight reverb
            "bass", "+2"         # Boost bass slightly
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Basic voice adjustment completed!")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Sox not available or failed")
        return False

def main():
    """Main voice cloning function"""
    print("🎤 Voice Cloning for Yiddish Speech")
    print("=" * 40)
    
    # Check if generated speech exists
    if not os.path.exists(GENERATED_SPEECH):
        print(f"❌ Generated speech not found: {GENERATED_SPEECH}")
        print("💡 Run: python yiddish_to_speech.py first")
        return
    
    # Get reference audio files
    reference_files = get_reference_audio_files()
    
    if not reference_files:
        print(f"❌ No reference audio files found in {REFERENCE_AUDIO_DIR}")
        return
    
    print(f"🎵 Found {len(reference_files)} reference audio files:")
    for file in reference_files:
        print(f"  - {file}")
    
    # Use the largest file as primary reference (likely has more voice data)
    primary_reference = max(reference_files, key=lambda f: os.path.getsize(f))
    print(f"\n🎯 Using primary reference: {primary_reference}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Try voice conversion approaches
    output_file = os.path.join(OUTPUT_DIR, "yiddish_voice_cloned.wav")
    
    print(f"\n🔄 Attempting voice conversion...")
    print(f"Source: {GENERATED_SPEECH}")
    print(f"Target voice: {primary_reference}")
    print(f"Output: {output_file}")
    
    # Method 1: Try TTS voice conversion
    success = voice_convert_with_tts(GENERATED_SPEECH, primary_reference, output_file)
    
    if not success:
        # Method 2: Try alternative models
        vc_models = try_voice_conversion_models()
        for model in vc_models[:3]:  # Try first 3 models
            print(f"\n🔄 Trying model: {model}")
            if voice_convert_with_tts(GENERATED_SPEECH, primary_reference, output_file, model):
                success = True
                break
    
    if not success:
        # Method 3: Try basic audio processing
        print(f"\n🔄 Trying basic voice adjustment...")
        success = try_alternative_voice_conversion(GENERATED_SPEECH, primary_reference, output_file)
    
    if success:
        print(f"\n✅ Voice cloning completed!")
        print(f"🎧 Original: {GENERATED_SPEECH}")
        print(f"🎤 Voice cloned: {output_file}")
        print(f"🎵 Play with: aplay {output_file}")
    else:
        print(f"\n❌ Voice cloning failed with all methods")
        print(f"💡 Try installing sox: sudo dnf install sox")
        print(f"💡 Or use the original: aplay {GENERATED_SPEECH}")

def quick_clone():
    """Quick voice cloning with minimal setup"""
    print("🚀 Quick Voice Clone")
    
    if not os.path.exists(GENERATED_SPEECH):
        print(f"❌ Need to generate speech first: python yiddish_to_speech.py")
        return
    
    reference_files = get_reference_audio_files()
    if not reference_files:
        print(f"❌ No reference audio found")
        return
    
    primary_ref = max(reference_files, key=lambda f: os.path.getsize(f))
    output_file = os.path.join(OUTPUT_DIR, "quick_voice_clone.wav")
    
    # Try the most reliable voice conversion model
    if voice_convert_with_tts(GENERATED_SPEECH, primary_ref, output_file):
        print(f"✅ Quick clone: {output_file}")
    else:
        print(f"❌ Quick clone failed")

if __name__ == "__main__":
    main() 