"""
Speech Synthesizer
==================
Converts phonetic text to speech using various TTS engines.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union
from .transliterator import YiddishTransliterator


class SpeechSynthesizer:
    """Synthesizes speech from phonetic text using espeak or other TTS engines."""
    
    def __init__(self, engine: str = "espeak", voice: str = "en"):
        """
        Initialize the speech synthesizer.
        
        Args:
            engine: TTS engine to use ("espeak", "festival", etc.)
            voice: Voice to use for synthesis
        """
        self.engine = engine
        self.voice = voice
        self.transliterator = YiddishTransliterator()
    
    def _check_engine_available(self) -> bool:
        """Check if the TTS engine is available."""
        try:
            subprocess.run([self.engine, "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def synthesize_with_espeak(self, text: str, output_file: str, 
                              speed: int = 150, pitch: int = 50) -> bool:
        """
        Synthesize speech using espeak.
        
        Args:
            text: Text to synthesize
            output_file: Output audio file path
            speed: Speech speed (words per minute)
            pitch: Voice pitch (0-99)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                "espeak",
                "-v", self.voice,
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
                               speed: int = 150, pitch: int = 50) -> bool:
        """
        Convert Yiddish text to speech (full pipeline).
        
        Args:
            yiddish_text: Yiddish text in Hebrew script
            output_file: Output audio file path
            speed: Speech speed
            pitch: Voice pitch
            
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
        
        # Synthesize speech
        print("🔊 Generating speech...")
        success = self.synthesize_with_espeak(
            phonetic_text, output_file, speed, pitch
        )
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate: {output_file}")
        
        return success
    
    def synthesize_phonetic_text(self, phonetic_text: str, output_file: str,
                                speed: int = 150, pitch: int = 50) -> bool:
        """
        Synthesize speech from already transliterated phonetic text.
        
        Args:
            phonetic_text: Phonetic text in Latin script
            output_file: Output audio file path
            speed: Speech speed
            pitch: Voice pitch
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🔤 Synthesizing: {phonetic_text}")
        
        success = self.synthesize_with_espeak(
            phonetic_text, output_file, speed, pitch
        )
        
        if success:
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate: {output_file}")
        
        return success
    
    def batch_synthesize(self, text_list: list, output_dir: str,
                        prefix: str = "yiddish_") -> list:
        """
        Synthesize multiple texts in batch.
        
        Args:
            text_list: List of Yiddish texts
            output_dir: Output directory
            prefix: Filename prefix
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, text in enumerate(text_list, 1):
            output_file = output_path / f"{prefix}{i:03d}.wav"
            
            if self.synthesize_yiddish_text(text, str(output_file)):
                generated_files.append(str(output_file))
        
        return generated_files 