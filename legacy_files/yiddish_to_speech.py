#!/usr/bin/env python3
"""
Convert Any Yiddish Text to Speech
=================================
A simple tool to convert Yiddish text (Hebrew script) to speech
using phonetic transliteration + espeak TTS.
"""

import os
import subprocess
import sys

def yiddish_to_phonetic(text):
    """
    Convert Yiddish text to phonetic Latin script
    Enhanced mapping for better pronunciation
    """
    
    # Enhanced Yiddish to phonetic mapping
    mapping = {
        # Basic letters
        'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h',
        'ו': 'u', 'ז': 'z', 'ח': 'kh', 'ט': 't', 'י': 'i',
        'כ': 'k', 'ל': 'l', 'מ': 'm', 'נ': 'n', 'ס': 's',
        'ע': 'e', 'פ': 'p', 'צ': 'ts', 'ק': 'k', 'ר': 'r',
        'ש': 'sh', 'ת': 't',
        
        # Final forms
        'ך': 'kh', 'ם': 'm', 'ן': 'n', 'ף': 'f', 'ץ': 'ts',
        
        # Vowel combinations
        'אַ': 'a', 'אָ': 'o', 'עי': 'ay', 'וו': 'v', 'יי': 'ey',
        'וי': 'oy', 'אי': 'ay',
        
        # Common combinations
        'שׁ': 'sh', 'שׂ': 's', 'תּ': 't',
        
        # Numbers
        '4': 'four',
        
        # Punctuation and spaces
        ' ': ' ', '.': '.', ',': ',', '?': '?', '!': '!',
        '-': ' ', '־': ' '  # Hebrew maqaf
    }
    
    result = ""
    i = 0
    while i < len(text):
        # Try 2-character combinations first
        if i < len(text) - 1:
            two_char = text[i:i+2]
            if two_char in mapping:
                result += mapping[two_char]
                i += 2
                continue
        
        # Single character
        char = text[i]
        result += mapping.get(char, char)
        i += 1
    
    return result

def text_to_speech(text, output_file):
    """Generate speech from text using espeak"""
    
    try:
        # Use espeak with better voice settings
        cmd = [
            "espeak", 
            "-s", "130",        # Speed (words per minute)
            "-v", "en+m3",      # Voice (English male 3)
            "-p", "50",         # Pitch
            "-a", "150",        # Amplitude
            text, 
            "-w", output_file
        ]
        
        print(f"🔊 Generating speech...")
        subprocess.run(cmd, check=True, capture_output=True)
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Error generating speech: {e}")
        return False

def main():
    """Main function"""
    print("🎤 Yiddish Text-to-Speech Converter")
    print("=" * 40)
    
    # Your Yiddish text
    yiddish_text = "מעיאר עריק עדעמס איז באטראפן געווארן אין ארץ ישראל איינוואוינער טוען באגריסן א נייע 4-וועג סטאפ-סיין"
    
    print(f"📝 Original Yiddish text:")
    print(f"   {yiddish_text}")
    print()
    
    # Convert to phonetic
    phonetic_text = yiddish_to_phonetic(yiddish_text)
    print(f"🔤 Phonetic conversion:")
    print(f"   {phonetic_text}")
    print()
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Generate speech
    output_file = "output/yiddish_speech.wav"
    
    print(f"🎵 Converting to speech...")
    if text_to_speech(phonetic_text, output_file):
        print(f"✅ Success! Audio saved to: {output_file}")
        print(f"🎧 You can play it with: aplay {output_file}")
    else:
        print(f"❌ Failed to generate speech")
        print(f"💡 Make sure espeak is installed: sudo dnf install espeak")

def convert_custom_text(text):
    """Convert custom Yiddish text to speech"""
    print(f"📝 Converting: {text}")
    phonetic = yiddish_to_phonetic(text)
    print(f"🔤 Phonetic: {phonetic}")
    
    os.makedirs("output", exist_ok=True)
    output_file = "output/custom_yiddish.wav"
    
    if text_to_speech(phonetic, output_file):
        print(f"✅ Generated: {output_file}")
        return output_file
    else:
        print(f"❌ Failed to generate speech")
        return None

if __name__ == "__main__":
    # Check if custom text provided as argument
    if len(sys.argv) > 1:
        custom_text = " ".join(sys.argv[1:])
        convert_custom_text(custom_text)
    else:
        main() 