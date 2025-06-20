#!/usr/bin/env python3
"""
Pipeline Voice Matching for Custom Yiddish Text
===============================================
Applies voice matching to the newly generated custom_yiddish.wav
"""

import os
import subprocess
import glob

# Configuration
CUSTOM_SPEECH = "output/custom_yiddish.wav"
REFERENCE_AUDIO_DIR = "yiddish24_audio"
OUTPUT_DIR = "output"

def create_voice_variants(source_audio, reference_audio, output_base):
    """Create multiple voice variants with different matching approaches"""
    
    variants = []
    
    print(f"🎯 Using reference: {os.path.basename(reference_audio)}")
    print(f"🎵 Source: {os.path.basename(source_audio)}")
    
    # Variant 1: Natural/Conservative
    print("\n🎵 Creating natural voice variant...")
    natural_output = f"{output_base}_natural.wav"
    try:
        cmd = [
            "sox", source_audio, natural_output,
            "pitch", "-150",     # Lower pitch moderately
            "tempo", "0.97",     # Slightly slower
            "bass", "+2",        # Boost bass slightly
            "treble", "-2",      # Reduce treble
            "reverb", "15"       # Add slight room tone
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Natural", natural_output))
        print("✅ Natural variant created")
    except Exception as e:
        print(f"❌ Natural variant failed: {e}")
    
    # Variant 2: Deeper/Warmer
    print("\n🎵 Creating deeper voice variant...")
    deeper_output = f"{output_base}_deeper.wav"
    try:
        cmd = [
            "sox", source_audio, deeper_output,
            "pitch", "-250",     # Significantly lower pitch
            "tempo", "0.95",     # Slower tempo
            "equalizer", "300", "2", "+4",    # Boost low frequencies
            "equalizer", "1200", "1", "+2",   # Boost low-mid
            "equalizer", "3000", "1", "-3",   # Reduce high-mid
            "reverb", "20"       # More room tone
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Deeper", deeper_output))
        print("✅ Deeper variant created")
    except Exception as e:
        print(f"❌ Deeper variant failed: {e}")
    
    # Variant 3: Smooth/Professional
    print("\n🎵 Creating smooth voice variant...")
    smooth_output = f"{output_base}_smooth.wav"
    try:
        cmd = [
            "sox", source_audio, smooth_output,
            "pitch", "-100",     # Slight pitch adjustment
            "tempo", "0.98",     # Slightly slower
            "equalizer", "800", "1", "+1",    # Slight mid boost
            "equalizer", "2500", "1", "-1",   # Slight presence reduction
            "compand", "0.02,0.20", "-60,-60,-30,-10,-20,-8,-5,-8,-2,-8", "-8", "-7", "0.05",  # Gentle compression
            "reverb", "10"       # Light reverb
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Smooth", smooth_output))
        print("✅ Smooth variant created")
    except Exception as e:
        print(f"❌ Smooth variant failed: {e}")
    
    # Variant 4: Aged/Character voice
    print("\n🎵 Creating character voice variant...")
    character_output = f"{output_base}_character.wav"
    try:
        cmd = [
            "sox", source_audio, character_output,
            "pitch", "-200",     # Lower pitch
            "tempo", "0.93",     # Slower, more deliberate
            "equalizer", "400", "2", "+3",    # Boost low-mid
            "equalizer", "1800", "1", "-2",   # Reduce clarity slightly
            "equalizer", "4000", "1", "-4",   # Reduce high frequencies
            "reverb", "25"       # More room character
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variants.append(("Character", character_output))
        print("✅ Character variant created")
    except Exception as e:
        print(f"❌ Character variant failed: {e}")
    
    return variants

def main():
    """Main function"""
    print("🎤 Pipeline Voice Matching for Custom Yiddish Text")
    print("=" * 50)
    
    # Check if custom speech exists
    if not os.path.exists(CUSTOM_SPEECH):
        print(f"❌ Custom speech not found: {CUSTOM_SPEECH}")
        print("💡 Run the yiddish_to_speech.py script first")
        return
    
    # Get reference audio files
    reference_files = glob.glob(os.path.join(REFERENCE_AUDIO_DIR, "*.wav"))
    if not reference_files:
        print(f"❌ No reference files found in {REFERENCE_AUDIO_DIR}")
        return
    
    # Select best reference (largest file, likely best quality)
    best_reference = max(reference_files, key=lambda f: os.path.getsize(f))
    
    print(f"📊 Custom speech: {os.path.getsize(CUSTOM_SPEECH) // 1024}KB")
    print(f"📊 Reference: {os.path.getsize(best_reference) // 1024}KB")
    
    # Create voice variants
    variant_base = os.path.join(OUTPUT_DIR, "custom_voice")
    variants = create_voice_variants(CUSTOM_SPEECH, best_reference, variant_base)
    
    # Summary
    print(f"\n🎉 Voice matching completed!")
    print(f"📁 Generated files:")
    
    all_files = [
        ("Original custom", CUSTOM_SPEECH),
        ("Reference speaker", best_reference)
    ] + variants
    
    for name, filepath in all_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) // 1024
            print(f"  🎵 {name}: {os.path.basename(filepath)} ({size}KB)")
    
    print(f"\n🎧 Listen and compare:")
    print(f"   aplay '{best_reference}'  # Original speaker")
    print(f"   aplay '{CUSTOM_SPEECH}'  # Generated speech")
    
    for name, filepath in variants:
        if os.path.exists(filepath):
            print(f"   aplay '{filepath}'  # {name} variant")
    
    print(f"\n💡 The longer text should provide better voice matching results!")

if __name__ == "__main__":
    main() 