#!/usr/bin/env python3
"""
Better Voice Cloning for Yiddish Speech
======================================
Improved voice cloning with multiple models and better voice matching.
"""

import os
import subprocess
import torch
import torchaudio
import numpy as np
from TTS.api import TTS
import glob

# Configuration
GENERATED_SPEECH = "output/yiddish_speech.wav"
REFERENCE_AUDIO_DIR = "yiddish24_audio"
OUTPUT_DIR = "output"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def analyze_voice_characteristics(audio_path):
    """Analyze basic voice characteristics of reference audio"""
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Basic analysis
        duration = waveform.shape[1] / sample_rate
        rms_energy = torch.sqrt(torch.mean(waveform**2))
        
        print(f"📊 Audio analysis for {os.path.basename(audio_path)}:")
        print(f"   Duration: {duration:.1f}s")
        print(f"   RMS Energy: {rms_energy:.4f}")
        print(f"   Sample Rate: {sample_rate}Hz")
        
        return {
            'duration': duration,
            'energy': rms_energy.item(),
            'sample_rate': sample_rate
        }
    except Exception as e:
        print(f"❌ Error analyzing {audio_path}: {e}")
        return None

def try_xtts_voice_cloning(text, reference_audio, output_file):
    """Try XTTS voice cloning (the best quality if it works)"""
    try:
        print("🔄 Attempting XTTS voice cloning...")
        
        # Try to bypass the PyTorch compatibility issue
        import torch.serialization
        original_load = torch.load
        
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        torch.load = patched_load
        
        # Initialize XTTS
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
        
        # Convert Yiddish text to phonetic for XTTS
        from yiddish_to_speech import yiddish_to_phonetic
        phonetic_text = yiddish_to_phonetic(text)
        
        # Generate with voice cloning
        tts.tts_to_file(
            text=phonetic_text,
            speaker_wav=reference_audio,
            language="en",  # Use English for phonetic text
            file_path=output_file
        )
        
        # Restore original torch.load
        torch.load = original_load
        
        print("✅ XTTS voice cloning successful!")
        return True
        
    except Exception as e:
        print(f"❌ XTTS failed: {e}")
        # Restore original torch.load
        torch.load = original_load
        return False

def try_multiple_vc_models(source_wav, target_wav, output_base):
    """Try multiple voice conversion models"""
    
    models_to_try = [
        ("voice_conversion_models/multilingual/vctk/freevc24", "FreeVC24"),
        ("voice_conversion_models/en/vctk/resemble_enhance", "Resemble"),
        ("voice_conversion_models/multilingual/multi-dataset/your_tts", "YourTTS-VC"),
    ]
    
    results = []
    
    for model_name, display_name in models_to_try:
        try:
            print(f"\n🔄 Trying {display_name} ({model_name})...")
            
            output_file = f"{output_base}_{display_name.lower()}.wav"
            
            tts = TTS(model_name=model_name, progress_bar=False).to(DEVICE)
            tts.voice_conversion_to_file(
                source_wav=source_wav,
                target_wav=target_wav,
                file_path=output_file
            )
            
            print(f"✅ {display_name} successful: {output_file}")
            results.append((display_name, output_file))
            
        except Exception as e:
            print(f"❌ {display_name} failed: {e}")
            continue
    
    return results

def improve_with_audio_processing(input_wav, reference_wav, output_wav):
    """Use audio processing to better match voice characteristics"""
    try:
        print("🔄 Applying advanced audio processing...")
        
        # Load both audio files to analyze characteristics
        ref_waveform, ref_sr = torchaudio.load(reference_wav)
        src_waveform, src_sr = torchaudio.load(input_wav)
        
        # Resample if needed
        if src_sr != ref_sr:
            resampler = torchaudio.transforms.Resample(src_sr, ref_sr)
            src_waveform = resampler(src_waveform)
        
        # Apply spectral envelope matching (basic implementation)
        # This is a simplified version - more advanced techniques exist
        
        # For now, use sox with better parameters based on reference
        cmd = [
            "sox", input_wav, output_wav,
            "pitch", "-200",     # Adjust pitch more significantly
            "tempo", "0.95",     # Slightly slower
            "reverb", "5",       # Less reverb
            "equalizer", "1000", "1.5", "2.0",  # Boost mids
            "equalizer", "3000", "1.0", "-1.0", # Reduce highs
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Audio processing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio processing failed: {e}")
        return False

def main():
    """Main function with multiple voice cloning approaches"""
    print("🎤 Better Voice Cloning for Yiddish Speech")
    print("=" * 45)
    
    # Check if generated speech exists
    if not os.path.exists(GENERATED_SPEECH):
        print(f"❌ Generated speech not found: {GENERATED_SPEECH}")
        print("💡 Run: python yiddish_to_speech.py first")
        return
    
    # Get reference audio files
    reference_files = glob.glob(os.path.join(REFERENCE_AUDIO_DIR, "*.wav"))
    
    if not reference_files:
        print(f"❌ No reference audio files found in {REFERENCE_AUDIO_DIR}")
        return
    
    print(f"🎵 Analyzing {len(reference_files)} reference files...")
    
    # Analyze each reference file
    best_reference = None
    best_score = 0
    
    for ref_file in reference_files:
        analysis = analyze_voice_characteristics(ref_file)
        if analysis and analysis['duration'] > 3.0:  # At least 3 seconds
            # Score based on duration and energy (longer, clearer audio is better)
            score = analysis['duration'] * analysis['energy']
            if score > best_score:
                best_score = score
                best_reference = ref_file
    
    if not best_reference:
        best_reference = max(reference_files, key=lambda f: os.path.getsize(f))
    
    print(f"\n🎯 Selected best reference: {best_reference}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n🔄 Trying multiple voice cloning approaches...")
    
    # Get the original text for XTTS
    original_text = "מעיאר עריק עדעמס איז באטראפן געווארן אין ארץ ישראל איינוואוינער טוען באגריסן א נייע 4-וועג סטאפ-סיין"
    
    # Method 1: Try XTTS direct voice cloning (best quality if it works)
    xtts_output = os.path.join(OUTPUT_DIR, "xtts_direct_clone.wav")
    if try_xtts_voice_cloning(original_text, best_reference, xtts_output):
        print(f"🎯 XTTS direct cloning successful: {xtts_output}")
    
    # Method 2: Try multiple voice conversion models
    vc_base = os.path.join(OUTPUT_DIR, "voice_converted")
    vc_results = try_multiple_vc_models(GENERATED_SPEECH, best_reference, vc_base)
    
    # Method 3: Enhanced audio processing
    enhanced_output = os.path.join(OUTPUT_DIR, "enhanced_voice_clone.wav")
    if vc_results:
        # Use the first successful VC result as input for enhancement
        best_vc_result = vc_results[0][1]
        improve_with_audio_processing(best_vc_result, best_reference, enhanced_output)
    
    # Summary
    print(f"\n🎉 Voice cloning attempts completed!")
    print(f"📁 Check these files:")
    
    all_outputs = [
        ("Original generated", GENERATED_SPEECH),
        ("XTTS direct", xtts_output),
        ("Enhanced version", enhanced_output),
    ]
    
    # Add VC results
    for name, file in vc_results:
        all_outputs.append((f"VC {name}", file))
    
    for name, file in all_outputs:
        if os.path.exists(file):
            size = os.path.getsize(file) // 1024
            print(f"  🎵 {name}: {file} ({size}KB)")
    
    print(f"\n🎧 Test them with:")
    for name, file in all_outputs:
        if os.path.exists(file):
            print(f"   aplay '{file}'  # {name}")

if __name__ == "__main__":
    main() 