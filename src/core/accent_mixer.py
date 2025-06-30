"""
Accent Mixer for Yiddish TTS
============================
Blends multiple accents to create hybrid Yiddish pronunciations.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .enhanced_synthesizer import EnhancedYiddishSynthesizer


class AccentMixer:
    """Mixes multiple accents to create hybrid Yiddish speech."""
    
    # Predefined accent combinations
    ACCENT_BLENDS = {
        'yiddish_authentic': {
            'name': 'Authentic Yiddish Blend',
            'description': 'German + Hungarian (historical Yiddish regions)',
            'accents': ['german', 'hungarian'],
            'weights': [0.7, 0.3],  # German dominant
            'speed_adjust': -5,  # Slightly slower
            'pitch_adjust': -3   # Slightly lower
        },
        'eastern_european': {
            'name': 'Eastern European Blend', 
            'description': 'Polish + Russian + Hungarian',
            'accents': ['polish', 'russian', 'hungarian'],
            'weights': [0.4, 0.4, 0.2],
            'speed_adjust': -8,
            'pitch_adjust': -2
        },
        'germanic_yiddish': {
            'name': 'Germanic Yiddish',
            'description': 'German + Dutch (Germanic languages)',
            'accents': ['german', 'dutch'],
            'weights': [0.8, 0.2],
            'speed_adjust': -3,
            'pitch_adjust': -5
        },
        'austro_hungarian': {
            'name': 'Austro-Hungarian',
            'description': 'German + Hungarian (Habsburg Empire)',
            'accents': ['german', 'hungarian'],
            'weights': [0.6, 0.4],
            'speed_adjust': -10,
            'pitch_adjust': 0
        }
    }
    
    def __init__(self):
        """Initialize the accent mixer."""
        pass
    
    def list_available_blends(self):
        """Display available accent blend presets."""
        print("🎭 Available Accent Blends:")
        print("=" * 40)
        for key, config in self.ACCENT_BLENDS.items():
            print(f"  {key:<18} - {config['name']}")
            print(f"  {' ' * 20} {config['description']}")
            accents_str = " + ".join([f"{acc} ({w:.0%})" for acc, w in zip(config['accents'], config['weights'])])
            print(f"  {' ' * 20} Mix: {accents_str}")
            print()
    
    def generate_accent_samples(self, text: str, accents: List[str], 
                               output_dir: str = "temp") -> List[str]:
        """
        Generate the same text with different accents.
        
        Args:
            text: Phonetic text to synthesize
            accents: List of accent names
            output_dir: Temporary output directory
            
        Returns:
            List of generated audio file paths
        """
        Path(output_dir).mkdir(exist_ok=True)
        sample_files = []
        
        for accent in accents:
            synthesizer = EnhancedYiddishSynthesizer(accent=accent)
            output_file = f"{output_dir}/sample_{accent}.wav"
            
            success = synthesizer.synthesize_phonetic_text(text, output_file)
            if success:
                sample_files.append(output_file)
            else:
                print(f"⚠️ Failed to generate {accent} sample")
        
        return sample_files
    
    def blend_audio_files(self, audio_files: List[str], weights: List[float], 
                         output_file: str, speed_adjust: int = 0, 
                         pitch_adjust: int = 0) -> bool:
        """
        Blend multiple audio files with specified weights.
        
        Args:
            audio_files: List of audio file paths
            weights: List of weights (should sum to 1.0)
            output_file: Output blended file
            speed_adjust: Speed adjustment (-10 to +10)
            pitch_adjust: Pitch adjustment (-10 to +10)
            
        Returns:
            True if successful
        """
        if len(audio_files) != len(weights):
            print("❌ Number of audio files must match number of weights")
            return False
        
        if not audio_files:
            print("❌ No audio files to blend")
            return False
        
        try:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Create sox command for blending
            cmd = ["sox", "-m"]
            
            # Add each file with its weight
            for audio_file, weight in zip(audio_files, normalized_weights):
                cmd.extend(["-v", str(weight), audio_file])
            
            # Temporary file for blend
            temp_blend = output_file.replace('.wav', '_temp_blend.wav')
            cmd.append(temp_blend)
            
            # Blend files
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Apply speed and pitch adjustments
            if speed_adjust != 0 or pitch_adjust != 0:
                final_cmd = ["sox", temp_blend, output_file]
                
                if speed_adjust != 0:
                    # Convert speed adjustment to tempo ratio
                    tempo_ratio = 1.0 + (speed_adjust / 100.0)
                    final_cmd.extend(["tempo", str(tempo_ratio)])
                
                if pitch_adjust != 0:
                    # Convert pitch adjustment to pitch shift
                    pitch_shift = pitch_adjust * 20  # Scale for audible difference
                    final_cmd.extend(["pitch", str(pitch_shift)])
                
                subprocess.run(final_cmd, check=True, capture_output=True)
                
                # Clean up temp file
                os.remove(temp_blend)
            else:
                # Just rename temp file to final
                os.rename(temp_blend, output_file)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Audio blending failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Blending error: {e}")
            return False
    
    def create_accent_blend(self, phonetic_text: str, blend_name: str, 
                           output_file: str) -> bool:
        """
        Create a predefined accent blend.
        
        Args:
            phonetic_text: Text to synthesize with blend
            blend_name: Name of predefined blend
            output_file: Output file path
            
        Returns:
            True if successful
        """
        if blend_name not in self.ACCENT_BLENDS:
            print(f"❌ Unknown blend '{blend_name}'. Available: {list(self.ACCENT_BLENDS.keys())}")
            return False
        
        blend_config = self.ACCENT_BLENDS[blend_name]
        
        print(f"🎭 Creating {blend_config['name']} blend...")
        print(f"   {blend_config['description']}")
        
        # Generate samples for each accent
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_files = self.generate_accent_samples(
                phonetic_text, 
                blend_config['accents'], 
                temp_dir
            )
            
            if len(sample_files) != len(blend_config['accents']):
                print("❌ Failed to generate all accent samples")
                return False
            
            # Blend the samples
            success = self.blend_audio_files(
                sample_files,
                blend_config['weights'],
                output_file,
                blend_config.get('speed_adjust', 0),
                blend_config.get('pitch_adjust', 0)
            )
            
            return success
    
    def create_custom_blend(self, phonetic_text: str, accents: List[str], 
                           weights: List[float], output_file: str,
                           speed_adjust: int = 0, pitch_adjust: int = 0) -> bool:
        """
        Create a custom accent blend.
        
        Args:
            phonetic_text: Text to synthesize
            accents: List of accent names to blend
            weights: List of weights for each accent
            output_file: Output file path
            speed_adjust: Speed adjustment (-10 to +10)
            pitch_adjust: Pitch adjustment (-10 to +10)
            
        Returns:
            True if successful
        """
        print(f"🎭 Creating custom blend: {' + '.join(accents)}")
        
        # Generate samples for each accent
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_files = self.generate_accent_samples(
                phonetic_text, accents, temp_dir
            )
            
            if len(sample_files) != len(accents):
                print("❌ Failed to generate all accent samples")
                return False
            
            # Blend the samples
            success = self.blend_audio_files(
                sample_files, weights, output_file, speed_adjust, pitch_adjust
            )
            
            return success 