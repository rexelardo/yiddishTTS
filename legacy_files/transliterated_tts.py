#!/usr/bin/env python3
"""
Transliterated Yiddish TTS
=========================
This approach converts Yiddish text to phonetic Latin script,
then uses standard TTS models which work more reliably.
"""

import os
import subprocess

# Create output directory
os.makedirs("output", exist_ok=True)

def yiddish_to_phonetic(text):
    """
    Convert Yiddish text to phonetic Latin script
    This is a simple mapping - you can improve it based on your needs
    """
    
    # Basic Yiddish to phonetic mapping
    mapping = {
        'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h',
        'ו': 'u', 'ז': 'z', 'ח': 'kh', 'ט': 't', 'י': 'i',
        'כ': 'k', 'ל': 'l', 'מ': 'm', 'נ': 'n', 'ס': 's',
        'ע': 'e', 'פ': 'p', 'צ': 'ts', 'ק': 'k', 'ר': 'r',
        'ש': 'sh', 'ת': 't',
        # Final forms
        'ך': 'kh', 'ם': 'm', 'ן': 'n', 'ף': 'f', 'ץ': 'ts',
        # Vowels
        'אַ': 'a', 'אָ': 'o', 'עי': 'ei', 'וו': 'v', 'יי': 'ei',
        # Common combinations
        'שׁ': 'sh', 'שׂ': 's', 'תּ': 't',
        # Spaces and punctuation remain the same
        ' ': ' ', '.': '.', ',': ',', '?': '?', '!': '!'
    }
    
    result = ""
    for char in text:
        result += mapping.get(char, char)
    
    return result

def run_simple_tts(text, output_file):
    """Run TTS with espeak (should be available on most Linux systems)"""
    
    try:
        # Try espeak first (simple but reliable)
        cmd = ["espeak", "-s", "120", "-v", "en+m3", text, "-w", output_file]
        subprocess.run(cmd, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try festival as backup
            cmd = ["festival", "--tts", "--text", text, "--output", output_file]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def main():
    """Main function"""
    print("=== Transliterated Yiddish TTS ===")
    
    # Your Yiddish texts
    yiddish_texts = [
        "שאלום עליכם, וויאזוי גייט עס?",
        "איך בין צופרידן מיט דעם רעזולטאט", 
        "דאס איז א פרווו פון יידיש טעקסט צו רעדע"
    ]
    
    for i, yiddish_text in enumerate(yiddish_texts, 1):
        print(f"\n--- Processing text {i} ---")
        print(f"Original: {yiddish_text}")
        
        # Convert to phonetic
        phonetic_text = yiddish_to_phonetic(yiddish_text)
        print(f"Phonetic: {phonetic_text}")
        
        # Generate speech
        output_file = f"output/yiddish_phonetic_{i}.wav"
        
        if run_simple_tts(phonetic_text, output_file):
            print(f"✅ Generated: {output_file}")
        else:
            print(f"❌ Failed to generate audio for text {i}")
            print("💡 Install espeak: sudo dnf install espeak espeak-devel")
    
    print("\n🎉 Phonetic TTS generation complete!")
    print("📝 Note: This is a basic phonetic conversion.")
    print("📝 For better results, refine the phonetic mapping.")

if __name__ == "__main__":
    main() 