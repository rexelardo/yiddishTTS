"""
Enhanced Yiddish Speech Synthesizer
===================================
Synthesizer with accent support for authentic Yiddish pronunciation.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union
from .transliterator import YiddishTransliterator


class EnhancedYiddishSynthesizer:
    """Enhanced synthesizer with accent support for Yiddish TTS."""
    
    # Voice options with their characteristics
    ACCENT_VOICES = {
        'german': {
            'voice': 'de',
            'name': 'German (Most Authentic)',
            'description': 'German accent - closest to historical Yiddish',
            'speed': 140,
            'pitch': 45
        },
        'polish': {
            'voice': 'pl', 
            'name': 'Polish (Eastern European)',
            'description': 'Polish accent - Eastern European Yiddish communities',
            'speed': 125,
            'pitch': 48
        },
        'russian': {
            'voice': 'ru',
            'name': 'Russian (Eastern European)', 
            'description': 'Russian accent - Slavic influence',
            'speed': 130,
            'pitch': 42
        },
        'hungarian': {
            'voice': 'hu',
            'name': 'Hungarian (Central European)',
            'description': 'Hungarian accent - Central European communities',
            'speed': 145,
            'pitch': 50
        },
        'dutch': {
            'voice': 'nl',
            'name': 'Dutch (Germanic)',
            'description': 'Dutch accent - Germanic language family',
            'speed': 150,
            'pitch': 47
        },
        'english': {
            'voice': 'en',
            'name': 'English (Fallback)',
            'description': 'English accent - less authentic but widely supported',
            'speed': 150,
            'pitch': 50
        }
    }
    
    def __init__(self, accent: str = "german", engine: str = "espeak"):
        """
        Initialize the enhanced synthesizer.
        
        Args:
            accent: Accent to use ('german', 'polish', 'russian', 'hungarian', 'dutch', 'english')
            engine: TTS engine to use (default: espeak)
        """
        self.engine = engine
        self.accent = accent
        self.transliterator = YiddishTransliterator()
        
        # Validate accent
        if accent not in self.ACCENT_VOICES:
            print(f"⚠️ Unknown accent '{accent}'. Using 'german' instead.")
            self.accent = "german"
        
        # Get voice settings
        self.voice_config = self.ACCENT_VOICES[self.accent]
        print(f"🎭 Using {self.voice_config['name']}: {self.voice_config['description']}")
    
    def list_available_accents(self):
        """Display available accent options."""
        print("🎭 Available Yiddish Accents:")
        print("=" * 40)
        for key, config in self.ACCENT_VOICES.items():
            print(f"  {key:10} - {config['name']}")
            print(f"           {config['description']}")
            print()
    
    def synthesize_with_accent(self, text: str, output_file: str, 
                              speed: Optional[int] = None, 
                              pitch: Optional[int] = None) -> bool:
        """
        Synthesize speech with the selected accent.
        
        Args:
            text: Text to synthesize
            output_file: Output audio file path
            speed: Speech speed (uses accent default if None)
            pitch: Voice pitch (uses accent default if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Use accent defaults if not specified
        if speed is None:
            speed = self.voice_config['speed']
        if pitch is None:
            pitch = self.voice_config['pitch']
        
        try:
            cmd = [
                "espeak",
                "-v", self.voice_config['voice'],
                "-s", str(speed),
                "-p", str(pitch),
                "-w", output_file,
                text
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Espeak synthesis failed: {e}")
            return False
        except FileNotFoundError:
            print("❌ Espeak not found. Install with: sudo apt install espeak")
            return False
    
    def synthesize_yiddish_text(self, yiddish_text: str, output_file: str,
                               speed: Optional[int] = None, 
                               pitch: Optional[int] = None) -> bool:
        """
        Convert Yiddish text to speech (full pipeline with accent).
        
        Args:
            yiddish_text: Yiddish text in Hebrew script
            output_file: Output audio file path
            speed: Speech speed (uses accent default if None)
            pitch: Voice pitch (uses accent default if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Transliterate to phonetic text
        print(f"📝 Converting: {yiddish_text}")
        phonetic_text = self.transliterator.transliterate(yiddish_text)
        print(f"🔤 Phonetic: {phonetic_text}")
        print(f"🎭 Accent: {self.voice_config['name']}")
        
        # Synthesize speech with accent
        print("🔊 Generating speech...")
        success = self.synthesize_with_accent(
            phonetic_text, output_file, speed, pitch
        )
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate: {output_file}")
        
        return success
    
    def synthesize_phonetic_text(self, phonetic_text: str, output_file: str,
                                speed: Optional[int] = None, 
                                pitch: Optional[int] = None) -> bool:
        """
        Synthesize speech from already transliterated phonetic text.
        
        Args:
            phonetic_text: Phonetic text in Latin script
            output_file: Output audio file path
            speed: Speech speed (uses accent default if None)
            pitch: Voice pitch (uses accent default if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🔤 Synthesizing: {phonetic_text}")
        print(f"🎭 Accent: {self.voice_config['name']}")
        
        success = self.synthesize_with_accent(
            phonetic_text, output_file, speed, pitch
        )
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate: {output_file}")
        
        return success
    
    def compare_accents(self, text: str, output_dir: str = "output") -> list:
        """
        Generate the same text with different accents for comparison.
        
        Args:
            text: Yiddish text to synthesize
            output_dir: Output directory for comparison files
            
        Returns:
            List of generated files
        """
        phonetic_text = self.transliterator.transliterate(text)
        print(f"🔤 Phonetic: {phonetic_text}")
        print(f"🎭 Generating comparison across accents...")
        
        generated_files = []
        
        for accent_key, config in self.ACCENT_VOICES.items():
            output_file = f"{output_dir}/accent_comparison_{accent_key}.wav"
            
            # Temporarily switch to this accent
            old_accent = self.accent
            old_config = self.voice_config
            self.accent = accent_key
            self.voice_config = config
            
            print(f"  🎯 {config['name']}...")
            success = self.synthesize_with_accent(phonetic_text, output_file)
            
            if success:
                generated_files.append((accent_key, config['name'], output_file))
            
            # Restore original accent
            self.accent = old_accent
            self.voice_config = old_config
        
        return generated_files 