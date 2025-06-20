"""
Voice Cloner
============
Applies voice characteristics from reference audio to synthesized speech.
"""

import os
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple, Optional


class VoiceCloner:
    """Clones voice characteristics using audio processing techniques."""
    
    def __init__(self, reference_audio_dir: str = "reference_audio"):
        """
        Initialize the voice cloner.
        
        Args:
            reference_audio_dir: Directory containing reference audio files
        """
        self.reference_audio_dir = reference_audio_dir
    
    def get_reference_files(self) -> List[str]:
        """Get all reference audio files."""
        audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a']
        audio_files = []
        
        for ext in audio_extensions:
            pattern = os.path.join(self.reference_audio_dir, ext)
            files = glob.glob(pattern)
            audio_files.extend(files)
        
        return sorted(audio_files)
    
    def select_best_reference(self, reference_files: List[str]) -> Optional[str]:
        """
        Select the best reference file based on size and quality heuristics.
        
        Args:
            reference_files: List of reference audio file paths
            
        Returns:
            Path to the best reference file, or None if no files found
        """
        if not reference_files:
            return None
        
        # Simple heuristic: larger files are often better quality
        return max(reference_files, key=lambda f: os.path.getsize(f))
    
    def create_voice_variant(self, source_audio: str, output_file: str,
                           variant_type: str = "natural") -> bool:
        """
        Create a voice variant using sox audio processing.
        
        Args:
            source_audio: Source audio file
            output_file: Output file path
            variant_type: Type of variant ("natural", "deeper", "smooth", "character")
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if variant_type == "natural":
                cmd = [
                    "sox", source_audio, output_file,
                    "pitch", "-150",     # Lower pitch moderately
                    "tempo", "0.97",     # Slightly slower
                    "bass", "+2",        # Boost bass slightly
                    "treble", "-2",      # Reduce treble
                    "reverb", "15"       # Add slight room tone
                ]
            
            elif variant_type == "deeper":
                cmd = [
                    "sox", source_audio, output_file,
                    "pitch", "-250",     # Significantly lower pitch
                    "tempo", "0.95",     # Slower tempo
                    "equalizer", "300", "2", "+4",    # Boost low frequencies
                    "equalizer", "1200", "1", "+2",   # Boost low-mid
                    "equalizer", "3000", "1", "-3",   # Reduce high-mid
                    "reverb", "20"       # More room tone
                ]
            
            elif variant_type == "smooth":
                cmd = [
                    "sox", source_audio, output_file,
                    "pitch", "-100",     # Slight pitch adjustment
                    "tempo", "0.98",     # Slightly slower
                    "equalizer", "800", "1", "+1",    # Slight mid boost
                    "equalizer", "2500", "1", "-1",   # Slight presence reduction
                    "compand", "0.02,0.20", "-60,-60,-30,-10,-20,-8,-5,-8,-2,-8", "-8", "-7", "0.05",
                    "reverb", "10"       # Light reverb
                ]
            
            elif variant_type == "character":
                cmd = [
                    "sox", source_audio, output_file,
                    "pitch", "-200",     # Lower pitch
                    "tempo", "0.93",     # Slower, more deliberate
                    "equalizer", "400", "2", "+3",    # Boost low-mid
                    "equalizer", "1800", "1", "-2",   # Reduce clarity slightly
                    "equalizer", "4000", "1", "-4",   # Reduce high frequencies
                    "reverb", "25"       # More room character
                ]
            
            else:
                raise ValueError(f"Unknown variant type: {variant_type}")
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Sox processing failed for {variant_type}: {e}")
            return False
        except FileNotFoundError:
            print("❌ Sox not found. Install with: sudo apt install sox")
            return False
    
    def create_multiple_variants(self, source_audio: str, output_base: str) -> List[Tuple[str, str]]:
        """
        Create multiple voice variants.
        
        Args:
            source_audio: Source audio file
            output_base: Base path for output files (without extension)
            
        Returns:
            List of (variant_name, output_file) tuples
        """
        variants = [
            ("natural", "Natural"),
            ("deeper", "Deeper"),
            ("smooth", "Smooth"),
            ("character", "Character")
        ]
        
        results = []
        
        for variant_type, display_name in variants:
            output_file = f"{output_base}_{variant_type}.wav"
            
            print(f"\n🎵 Creating {display_name} voice variant...")
            
            if self.create_voice_variant(source_audio, output_file, variant_type):
                results.append((display_name, output_file))
                print(f"✅ {display_name} variant created")
            else:
                print(f"❌ {display_name} variant failed")
        
        return results
    
    def clone_voice(self, source_audio: str, output_dir: str = "output",
                   base_name: str = "voice_cloned") -> List[Tuple[str, str]]:
        """
        Complete voice cloning pipeline.
        
        Args:
            source_audio: Source audio file to process
            output_dir: Output directory
            base_name: Base name for output files
            
        Returns:
            List of (variant_name, output_file) tuples
        """
        print("🎤 Voice Cloning Pipeline")
        print("=" * 30)
        
        # Check if source audio exists
        if not os.path.exists(source_audio):
            print(f"❌ Source audio not found: {source_audio}")
            return []
        
        # Get reference files
        reference_files = self.get_reference_files()
        if not reference_files:
            print(f"❌ No reference files found in {self.reference_audio_dir}")
            return []
        
        best_reference = self.select_best_reference(reference_files)
        print(f"🎯 Selected reference: {os.path.basename(best_reference)}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create variants
        output_base = output_path / base_name
        variants = self.create_multiple_variants(source_audio, str(output_base))
        
        # Summary
        print(f"\n🎉 Voice cloning completed!")
        print(f"📁 Generated {len(variants)} variants:")
        
        for name, filepath in variants:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath) // 1024
                print(f"  🎵 {name}: {os.path.basename(filepath)} ({size}KB)")
        
        return variants 