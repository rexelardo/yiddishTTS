#!/usr/bin/env python3
"""
Yiddish Text-to-Speech CLI
==========================
Command-line interface for the Yiddish TTS system.

Usage:
    python yiddish_tts.py "שלום עליכם" --output hello.wav
    python yiddish_tts.py "שלום עליכם" --output hello.wav --voice-clone
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.synthesizer import SpeechSynthesizer
from src.voice_matching.voice_cloner import VoiceCloner


def main():
    parser = argparse.ArgumentParser(
        description="Convert Yiddish text to speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "שלום עליכם" --output hello.wav
  %(prog)s "שלום עליכם" --output hello.wav --voice-clone
  %(prog)s "שלום עליכם" --output hello.wav --speed 120 --pitch 40
        """
    )
    
    parser.add_argument(
        "text",
        help="Yiddish text to convert to speech (in Hebrew script)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output/yiddish_speech.wav",
        help="Output audio file path (default: output/yiddish_speech.wav)"
    )
    
    parser.add_argument(
        "--speed", "-s",
        type=int,
        default=150,
        help="Speech speed in words per minute (default: 150)"
    )
    
    parser.add_argument(
        "--pitch", "-p",
        type=int,
        default=50,
        help="Voice pitch 0-99 (default: 50)"
    )
    
    parser.add_argument(
        "--voice-clone", "-vc",
        action="store_true",
        help="Apply voice cloning using reference audio"
    )
    
    parser.add_argument(
        "--reference-dir", "-r",
        default="yiddish24_audio",
        help="Directory containing reference audio files (default: yiddish24_audio)"
    )
    
    parser.add_argument(
        "--voice", "-v",
        default="en",
        help="Voice to use for synthesis (default: en)"
    )
    
    args = parser.parse_args()
    
    print("🎤 Yiddish Text-to-Speech")
    print("=" * 25)
    
    # Initialize synthesizer
    synthesizer = SpeechSynthesizer(voice=args.voice)
    
    # Generate speech
    success = synthesizer.synthesize_yiddish_text(
        args.text,
        args.output,
        speed=args.speed,
        pitch=args.pitch
    )
    
    if not success:
        print("❌ Speech synthesis failed")
        return 1
    
    # Apply voice cloning if requested
    if args.voice_clone:
        print("\n🎭 Applying voice cloning...")
        
        cloner = VoiceCloner(reference_audio_dir=args.reference_dir)
        variants = cloner.clone_voice(
            args.output,
            output_dir=str(Path(args.output).parent),
            base_name=Path(args.output).stem
        )
        
        if variants:
            print(f"\n🎧 Listen to variants:")
            print(f"   Original: {args.output}")
            for name, filepath in variants:
                print(f"   {name}: {filepath}")
        else:
            print("❌ Voice cloning failed")
    
    print(f"\n✅ Complete! Generated: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 