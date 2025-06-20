#!/usr/bin/env python3
"""
Precise Voice Matching for Yiddish Speech
=========================================
Analyzes the original voice characteristics and applies precise adjustments
to make the generated speech sound more like the original speaker.
"""

import os
import subprocess
import torch
import torchaudio
import numpy as np
from scipy import signal
import librosa

# Configuration
GENERATED_SPEECH = "output/yiddish_speech.wav"
REFERENCE_AUDIO_DIR = "yiddish24_audio"
OUTPUT_DIR = "output"

def analyze_voice_prosody(audio_path):
    """Analyze voice characteristics in detail"""
    try:
        # Load audio with librosa for better analysis
        y, sr = librosa.load(audio_path)
        
        # Extract key voice characteristics
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Get fundamental frequency (F0)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        avg_pitch = np.mean(pitch_values) if pitch_values else 0
        
        # Get spectral characteristics
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        characteristics = {
            'avg_pitch': avg_pitch,
            'pitch_std': np.std(pitch_values) if pitch_values else 0,
            'spectral_centroid_mean': np.mean(spectral_centroid),
            'mfcc_mean': np.mean(mfccs, axis=1),
            'tempo': tempo,
            'duration': len(y) / sr,
            'rms_energy': np.sqrt(np.mean(y**2))
        }
        
        print(f"📊 Voice analysis for {os.path.basename(audio_path)}:")
        print(f"   Average Pitch: {avg_pitch:.1f} Hz")
        print(f"   Pitch Variation: {characteristics['pitch_std']:.1f} Hz")
        print(f"   Spectral Centroid: {characteristics['spectral_centroid_mean']:.1f} Hz")
        print(f"   Tempo: {tempo:.1f} BPM")
        print(f"   Energy: {characteristics['rms_energy']:.4f}")
        
        return characteristics
        
    except Exception as e:
        print(f"❌ Error analyzing {audio_path}: {e}")
        return None

def create_voice_matched_version(source_audio, reference_audio, output_audio):
    """Create a voice-matched version using detailed analysis"""
    
    print("🔍 Analyzing reference voice characteristics...")
    ref_chars = analyze_voice_prosody(reference_audio)
    
    if not ref_chars:
        print("❌ Could not analyze reference audio")
        return False
    
    print("\n🔍 Analyzing generated speech...")
    src_chars = analyze_voice_prosody(source_audio)
    
    if not src_chars:
        print("❌ Could not analyze source audio")
        return False
    
    print("\n🎛️ Calculating voice adjustments...")
    
    # Calculate required adjustments
    pitch_ratio = ref_chars['avg_pitch'] / src_chars['avg_pitch'] if src_chars['avg_pitch'] > 0 else 1.0
    pitch_adjustment = 1200 * np.log2(pitch_ratio)  # Convert to cents
    
    # Energy adjustment
    energy_ratio = ref_chars['rms_energy'] / src_chars['rms_energy'] if src_chars['rms_energy'] > 0 else 1.0
    
    # Spectral adjustment
    spectral_ratio = ref_chars['spectral_centroid_mean'] / src_chars['spectral_centroid_mean'] if src_chars['spectral_centroid_mean'] > 0 else 1.0
    
    print(f"   Pitch adjustment: {pitch_adjustment:.0f} cents")
    print(f"   Energy ratio: {energy_ratio:.2f}")
    print(f"   Spectral ratio: {spectral_ratio:.2f}")
    
    # Apply adjustments with sox
    try:
        print("\n🎵 Applying voice matching adjustments...")
        
        cmd = [
            "sox", source_audio, output_audio,
            "pitch", str(int(pitch_adjustment)),  # Pitch adjustment in cents
            "gain", str(20 * np.log10(energy_ratio)),  # Energy adjustment in dB
            "equalizer", "1000", "2", str(2 * (spectral_ratio - 1)),  # Spectral adjustment
            "reverb", "20", "50", "100"  # Add slight reverb to match room tone
        ]
        
        # Limit extreme adjustments
        if abs(pitch_adjustment) > 500:  # Limit to ±500 cents
            cmd[3] = str(int(np.sign(pitch_adjustment) * 500))
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Voice matching completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Sox processing failed: {e}")
        return False

def create_multiple_variants(source_audio, reference_audio, output_base):
    """Create multiple variants with different voice matching approaches"""
    
    variants = []
    
    # Variant 1: Conservative matching
    print("\n🎵 Creating conservative voice match...")
    conservative_output = f"{output_base}_conservative.wav"
    try:
        cmd = [
            "sox", source_audio, conservative_output,
            "pitch", "-100",     # Slight pitch lowering
            "tempo", "0.98",     # Slightly slower
            "bass", "+3",        # Boost bass
            "treble", "-1"       # Reduce treble
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Conservative", conservative_output))
        print("✅ Conservative variant created")
    except:
        print("❌ Conservative variant failed")
    
    # Variant 2: Aggressive matching
    print("\n🎵 Creating aggressive voice match...")
    aggressive_output = f"{output_base}_aggressive.wav"
    try:
        cmd = [
            "sox", source_audio, aggressive_output,
            "pitch", "-300",     # More pitch adjustment
            "tempo", "0.95",     # Slower tempo
            "equalizer", "500", "1", "+4",    # Boost low mids
            "equalizer", "2000", "1", "-2",   # Reduce high mids
            "reverb", "10"       # Add room tone
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Aggressive", aggressive_output))
        print("✅ Aggressive variant created")
    except:
        print("❌ Aggressive variant failed")
    
    # Variant 3: Warm/deeper voice
    print("\n🎵 Creating warm voice variant...")
    warm_output = f"{output_base}_warm.wav"
    try:
        cmd = [
            "sox", source_audio, warm_output,
            "pitch", "-200",     # Lower pitch
            "equalizer", "200", "2", "+5",    # Boost very low frequencies
            "equalizer", "800", "1", "+3",    # Boost low-mid
            "equalizer", "4000", "1", "-3",   # Reduce presence
            "compand", "0.02,0.20", "-60,-60,-30,-15,-20,-10,-5,-8,-2,-8", "-8", "-7", "0.05"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Warm", warm_output))
        print("✅ Warm variant created")
    except:
        print("❌ Warm variant failed")
    
    return variants

def main():
    """Main function"""
    print("🎯 Precise Voice Matching for Yiddish Speech")
    print("=" * 45)
    
    # Check files
    if not os.path.exists(GENERATED_SPEECH):
        print(f"❌ Generated speech not found: {GENERATED_SPEECH}")
        return
    
    reference_files = [f for f in os.listdir(REFERENCE_AUDIO_DIR) if f.endswith('.wav')]
    if not reference_files:
        print(f"❌ No reference files found in {REFERENCE_AUDIO_DIR}")
        return
    
    # Select best reference
    best_reference = max([os.path.join(REFERENCE_AUDIO_DIR, f) for f in reference_files], 
                        key=lambda f: os.path.getsize(f))
    
    print(f"🎯 Using reference: {best_reference}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Method 1: Precise analysis-based matching
    precise_output = os.path.join(OUTPUT_DIR, "precise_voice_match.wav")
    print("\n🔬 Attempting precise voice matching...")
    create_voice_matched_version(GENERATED_SPEECH, best_reference, precise_output)
    
    # Method 2: Multiple variants
    print("\n🎨 Creating multiple voice variants...")
    variant_base = os.path.join(OUTPUT_DIR, "voice_variant")
    variants = create_multiple_variants(GENERATED_SPEECH, best_reference, variant_base)
    
    # Summary
    print(f"\n🎉 Voice matching completed!")
    print(f"📁 Generated files:")
    
    all_files = [
        ("Original", GENERATED_SPEECH),
        ("Original reference", best_reference),
        ("Precise match", precise_output)
    ] + variants
    
    for name, filepath in all_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) // 1024
            print(f"  🎵 {name}: {os.path.basename(filepath)} ({size}KB)")
    
    print(f"\n🎧 Test different versions:")
    print(f"   aplay '{best_reference}'  # Original speaker")
    print(f"   aplay '{GENERATED_SPEECH}'  # Synthetic voice")
    if os.path.exists(precise_output):
        print(f"   aplay '{precise_output}'  # Precise match")
    for name, filepath in variants:
        if os.path.exists(filepath):
            print(f"   aplay '{filepath}'  # {name} variant")

if __name__ == "__main__":
    main() 