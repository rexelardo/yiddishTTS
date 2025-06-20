#!/usr/bin/env python3
"""
Basic Usage Example
===================
Demonstrates basic usage of the Yiddish TTS system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.synthesizer import SpeechSynthesizer
from src.voice_matching.voice_cloner import VoiceCloner


def basic_synthesis_example():
    """Basic text-to-speech synthesis."""
    print("🎤 Basic Synthesis Example")
    print("=" * 30)
    
    # Initialize synthesizer
    synthesizer = SpeechSynthesizer()
    
    # Yiddish texts to synthesize
    texts = [
        "שלום עליכם",
        "איך בין צופרידן מיט דעם רעזולטאט",
        "דאס איז א פרובע פון יידיש טעקסט צו רעדע"
    ]
    
    # Generate speech for each text
    for i, text in enumerate(texts, 1):
        output_file = f"output/example_{i}.wav"
        
        print(f"\n📝 Text {i}: {text}")
        success = synthesizer.synthesize_yiddish_text(text, output_file)
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate: {output_file}")


def voice_cloning_example():
    """Voice cloning example."""
    print("\n🎭 Voice Cloning Example")
    print("=" * 30)
    
    # First generate base speech
    synthesizer = SpeechSynthesizer()
    base_text = "די בריוו איז אינטערגעשריבן דורך די אויסערן מיניסטארן"
    base_output = "output/base_speech.wav"
    
    print(f"📝 Generating base speech...")
    if not synthesizer.synthesize_yiddish_text(base_text, base_output):
        print("❌ Failed to generate base speech")
        return
    
    # Apply voice cloning
    cloner = VoiceCloner(reference_audio_dir="yiddish24_audio")
    variants = cloner.clone_voice(
        base_output,
        output_dir="output",
        base_name="voice_cloned_example"
    )
    
    if variants:
        print("\n🎧 Play the results:")
        print(f"   Base: {base_output}")
        for name, filepath in variants:
            print(f"   {name}: {filepath}")


def batch_processing_example():
    """Batch processing example."""
    print("\n📦 Batch Processing Example")
    print("=" * 30)
    
    synthesizer = SpeechSynthesizer()
    
    # List of texts to process
    yiddish_texts = [
        "גוטן מארגן",
        "וואס מאכסטו?",
        "איך בין זייער פרייליך",
        "א גוטן טאג צו אלע",
        "מיר זענען דא צו העלפן"
    ]
    
    # Batch synthesize
    generated_files = synthesizer.batch_synthesize(
        yiddish_texts,
        output_dir="output",
        prefix="batch_"
    )
    
    print(f"\n✅ Generated {len(generated_files)} files:")
    for file in generated_files:
        print(f"   {file}")


def main():
    """Run all examples."""
    print("🎯 Yiddish TTS Examples")
    print("=" * 40)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Run examples
    basic_synthesis_example()
    voice_cloning_example()
    batch_processing_example()
    
    print("\n🎉 All examples completed!")
    print("Check the 'output' directory for generated audio files.")


if __name__ == "__main__":
    main() 