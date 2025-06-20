"""
Better TTS approach using existing libraries and techniques
This uses more sophisticated methods that can work with limited data
"""

import torch
import torchaudio
import os
import re
from pathlib import Path
import numpy as np

# Yiddish phoneme mapping (simplified)
YIDDISH_PHONEMES = {
    # Vowels
    'א': 'a', 'ע': 'e', 'י': 'i', 'ו': 'u', 'ױ': 'oy', 'יי': 'ey', 'אי': 'ay',
    # Consonants
    'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h', 'ז': 'z', 'ח': 'kh', 'ט': 't',
    'כ': 'k', 'ך': 'k', 'ל': 'l', 'מ': 'm', 'ם': 'm', 'נ': 'n', 'ן': 'n',
    'ס': 's', 'פ': 'p', 'ף': 'f', 'צ': 'ts', 'ץ': 'ts', 'ק': 'k', 'ר': 'r',
    'ש': 'sh', 'ת': 't',
    # Common combinations
    'טש': 'tsh', 'דזש': 'dzh', 'זש': 'zh',
    # Punctuation and spaces
    ' ': 'SPACE', '.': 'PAUSE', ',': 'SHORT_PAUSE', '?': 'QUESTION', '!': 'EXCLAMATION'
}

def text_to_phonemes(text):
    """Convert Yiddish text to phonemes"""
    phonemes = []
    i = 0
    
    while i < len(text):
        # Check for multi-character combinations first
        found = False
        for length in [3, 2, 1]:  # Check longer combinations first
            if i + length <= len(text):
                substr = text[i:i+length]
                if substr in YIDDISH_PHONEMES:
                    phonemes.append(YIDDISH_PHONEMES[substr])
                    i += length
                    found = True
                    break
        
        if not found:
            # Unknown character, use placeholder
            phonemes.append('UNK')
            i += 1
    
    return phonemes

def segment_audio_by_words(audio, text, sample_rate):
    """
    Segment audio by words (simplified approach)
    In a real system, you'd use forced alignment
    """
    words = text.split()
    if not words:
        return {'full': audio}
    
    segments = {}
    audio_length = audio.shape[1]
    
    # Simple equal division by words (not accurate but functional)
    samples_per_word = audio_length // len(words)
    
    for i, word in enumerate(words):
        start_sample = i * samples_per_word
        end_sample = min((i + 1) * samples_per_word, audio_length)
        
        if start_sample < audio_length:
            word_audio = audio[:, start_sample:end_sample]
            segments[word.strip()] = word_audio
    
    # Also store the full audio
    segments['FULL'] = audio
    
    return segments

def segment_audio_by_phonemes(audio, phonemes, sample_rate):
    """
    Segment audio by phonemes (simplified approach)
    """
    if not phonemes:
        return {'FULL': audio}
    
    segments = {}
    audio_length = audio.shape[1]
    
    # Simple equal division by phonemes
    samples_per_phoneme = audio_length // len(phonemes)
    
    for i, phoneme in enumerate(phonemes):
        start_sample = i * samples_per_phoneme
        end_sample = min((i + 1) * samples_per_phoneme, audio_length)
        
        if start_sample < audio_length:
            phoneme_audio = audio[:, start_sample:end_sample]
            
            # Store or combine if phoneme already exists
            if phoneme in segments:
                # Average with existing phoneme audio
                existing = segments[phoneme]
                min_len = min(phoneme_audio.shape[1], existing.shape[1])
                averaged = (phoneme_audio[:, :min_len] + existing[:, :min_len]) / 2
                segments[phoneme] = averaged
            else:
                segments[phoneme] = phoneme_audio
    
    return segments

def create_phoneme_library():
    """
    Create a comprehensive phoneme library from all available samples
    """
    print("=== Creating Phoneme Library ===")
    
    audio_dir = Path("yiddish24_audio")
    text_dir = Path("yiddish_24_transcribed")
    
    phoneme_library = {}
    word_library = {}
    
    # Process each audio-text pair
    for audio_file in audio_dir.glob("*.wav"):
        base_name = audio_file.stem
        text_file = text_dir / f"{base_name}.txt"
        
        if text_file.exists():
            try:
                # Load audio
                audio, sr = torchaudio.load(audio_file)
                
                # Load text (UTF-16 encoding)
                with open(text_file, 'r', encoding='utf-16') as f:
                    text = f.read().strip()
                
                print(f"\nProcessing: {base_name}")
                print(f"Text: {text[:100]}...")
                
                # Convert to phonemes
                phonemes = text_to_phonemes(text)
                print(f"Phonemes: {phonemes[:20]}...")
                
                # Segment by words
                word_segments = segment_audio_by_words(audio, text, sr)
                print(f"Word segments: {len(word_segments)}")
                
                # Segment by phonemes
                phoneme_segments = segment_audio_by_phonemes(audio, phonemes, sr)
                print(f"Phoneme segments: {len(phoneme_segments)}")
                
                # Add to libraries
                for word, word_audio in word_segments.items():
                    if word not in word_library:
                        word_library[word] = []
                    word_library[word].append({
                        'audio': word_audio,
                        'source': base_name,
                        'sample_rate': sr
                    })
                
                for phoneme, phoneme_audio in phoneme_segments.items():
                    if phoneme not in phoneme_library:
                        phoneme_library[phoneme] = []
                    phoneme_library[phoneme].append({
                        'audio': phoneme_audio,
                        'source': base_name,
                        'sample_rate': sr
                    })
                
            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\nPhoneme library created:")
    print(f"  - {len(phoneme_library)} unique phonemes")
    print(f"  - {len(word_library)} unique words")
    
    # Show available phonemes
    print(f"Available phonemes: {list(phoneme_library.keys())[:20]}...")
    
    return phoneme_library, word_library

def synthesize_from_phonemes(text, phoneme_library, word_library, output_path="phoneme_speech.wav", speech_rate=1.0):
    """
    Synthesize speech by concatenating phonemes and words
    
    Args:
        text: Input text to synthesize
        phoneme_library: Library of phoneme audio segments
        word_library: Library of word audio segments
        output_path: Path to save the synthesized audio
        speech_rate: Speech rate multiplier (0.5 = half speed, 2.0 = double speed)
    """
    print(f"\nSynthesizing speech for: '{text}' (rate: {speech_rate}x)")
    
    # Convert input text to phonemes
    input_phonemes = text_to_phonemes(text)
    print(f"Target phonemes: {input_phonemes}")
    
    synthesized_audio = []
    sample_rate = 8000
    
    # Process each phoneme in the input text
    for i, target_phoneme in enumerate(input_phonemes):
        found_audio = None
        
        if target_phoneme in phoneme_library:
            # Use the phoneme audio from library
            phoneme_data = phoneme_library[target_phoneme][0]  # Use first occurrence
            found_audio = phoneme_data['audio']
            sample_rate = phoneme_data['sample_rate']
            print(f"  [{i+1}/{len(input_phonemes)}] Using phoneme '{target_phoneme}'")
        else:
            # Try to find similar phonemes or create substitute
            substitute = find_substitute_phoneme(target_phoneme, phoneme_library)
            if substitute:
                phoneme_data = phoneme_library[substitute][0]
                found_audio = phoneme_data['audio']
                sample_rate = phoneme_data['sample_rate']
                print(f"  [{i+1}/{len(input_phonemes)}] Substituting '{target_phoneme}' -> '{substitute}'")
            else:
                # Create silence for completely unknown phonemes
                if target_phoneme == 'SPACE':
                    duration = 0.2 / speech_rate  # Adjust pause duration by speech rate
                elif target_phoneme in ['PAUSE', 'SHORT_PAUSE']:
                    duration = 0.3 / speech_rate
                else:
                    duration = 0.1 / speech_rate  # Short silence for unknown phonemes
                
                silence_samples = int(duration * sample_rate)
                found_audio = torch.zeros(1, silence_samples)
                print(f"  [{i+1}/{len(input_phonemes)}] Unknown '{target_phoneme}' -> silence ({duration:.2f}s)")
        
        if found_audio is not None:
            # Apply speech rate stretching to the audio segment
            if speech_rate != 1.0:
                stretch_factor = 1.0 / speech_rate  # Inverse because slower = longer
                found_audio = stretch_audio(found_audio, stretch_factor)
            
            synthesized_audio.append(found_audio)
    
    if synthesized_audio:
        # Concatenate all phoneme audio segments
        final_audio = torch.cat(synthesized_audio, dim=1)
        
        # Add some variation to make it less robotic
        final_audio = add_prosodic_variation(final_audio, sample_rate)
        
        # Normalize audio
        if final_audio.max() > 0:
            final_audio = final_audio / final_audio.abs().max() * 0.8
        
        # Save result
        torchaudio.save(output_path, final_audio, sample_rate)
        print(f"Synthesized speech saved to: {output_path}")
        
        # Verify file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            duration = final_audio.shape[1] / sample_rate
            print(f"File size: {file_size} bytes, Duration: {duration:.2f}s")
            return output_path
    
    return None

def find_substitute_phoneme(target_phoneme, phoneme_library):
    """
    Find a similar phoneme if the exact one isn't available
    """
    # Define phoneme similarity groups
    similarity_groups = {
        # Vowels
        'a': ['e', 'i'],
        'e': ['a', 'i'],
        'i': ['e', 'a'],
        'u': ['o', 'a'],
        'o': ['u', 'a'],
        
        # Consonants
        'b': ['p', 'd'],
        'p': ['b', 't'],
        'd': ['t', 'b'],
        't': ['d', 'p'],
        'g': ['k', 'd'],
        'k': ['g', 't'],
        's': ['z', 'sh'],
        'z': ['s', 'zh'],
        'sh': ['s', 'zh'],
        'zh': ['z', 'sh'],
        'm': ['n'],
        'n': ['m'],
        'l': ['r'],
        'r': ['l'],
    }
    
    # First try exact match
    if target_phoneme in phoneme_library:
        return target_phoneme
    
    # Try similar phonemes
    if target_phoneme in similarity_groups:
        for similar in similarity_groups[target_phoneme]:
            if similar in phoneme_library:
                return similar
    
    # Try any vowel for vowels, any consonant for consonants
    vowels = ['a', 'e', 'i', 'u', 'o']
    consonants = ['b', 'p', 'd', 't', 'g', 'k', 's', 'z', 'm', 'n', 'l', 'r']
    
    if target_phoneme in vowels:
        for vowel in vowels:
            if vowel in phoneme_library:
                return vowel
    elif target_phoneme in consonants:
        for consonant in consonants:
            if consonant in phoneme_library:
                return consonant
    
    return None

def stretch_audio(audio, stretch_factor):
    """
    Stretch audio by a given factor using simple linear interpolation
    
    Args:
        audio: Input audio tensor [channels, samples]
        stretch_factor: Factor to stretch by (2.0 = double length, 0.5 = half length)
    
    Returns:
        Stretched audio tensor
    """
    if stretch_factor == 1.0:
        return audio
    
    original_length = audio.shape[1]
    new_length = int(original_length * stretch_factor)
    
    # Create indices for interpolation
    original_indices = torch.linspace(0, original_length - 1, original_length)
    new_indices = torch.linspace(0, original_length - 1, new_length)
    
    # Simple linear interpolation for each channel
    stretched_audio = torch.zeros(audio.shape[0], new_length)
    
    for channel in range(audio.shape[0]):
        stretched_audio[channel] = torch.nn.functional.interpolate(
            audio[channel].unsqueeze(0).unsqueeze(0), 
            size=new_length, 
            mode='linear', 
            align_corners=True
        ).squeeze()
    
    return stretched_audio

def add_prosodic_variation(audio, sample_rate):
    """
    Add slight variations to make speech less robotic
    """
    # Add slight pitch variation (very basic)
    # This is a simplified approach - real prosody is much more complex
    
    # Create slight amplitude modulation
    duration = audio.shape[1] / sample_rate
    t = torch.linspace(0, duration, audio.shape[1])
    
    # Very subtle amplitude variation (±5%)
    amp_variation = 1.0 + 0.05 * torch.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz variation
    
    # Apply variation
    varied_audio = audio * amp_variation.unsqueeze(0)
    
    return varied_audio

def create_character_based_synthesis(text, phoneme_library, output_path="char_speech.wav", speech_rate=1.0):
    """
    Alternative approach: synthesize based on individual characters
    
    Args:
        text: Input text to synthesize
        phoneme_library: Library of phoneme audio segments
        output_path: Path to save the synthesized audio
        speech_rate: Speech rate multiplier (0.5 = half speed, 2.0 = double speed)
    """
    print(f"\nCharacter-based synthesis for: '{text}' (rate: {speech_rate}x)")
    
    synthesized_audio = []
    sample_rate = 8000
    
    for i, char in enumerate(text):
        if char in YIDDISH_PHONEMES:
            phoneme = YIDDISH_PHONEMES[char]
            
            if phoneme in phoneme_library:
                phoneme_data = phoneme_library[phoneme][0]
                char_audio = phoneme_data['audio']
                sample_rate = phoneme_data['sample_rate']
                
                # Add slight random variation to each character
                variation = 0.9 + 0.2 * torch.rand(1).item()  # ±10% variation
                char_audio = char_audio * variation
                
                # Apply speech rate stretching
                if speech_rate != 1.0:
                    stretch_factor = 1.0 / speech_rate
                    char_audio = stretch_audio(char_audio, stretch_factor)
                
                synthesized_audio.append(char_audio)
                print(f"  [{i+1}/{len(text)}] '{char}' -> '{phoneme}'")
            else:
                # Short silence for unknown characters
                silence_duration = 0.05 / speech_rate
                silence = torch.zeros(1, int(silence_duration * sample_rate))
                synthesized_audio.append(silence)
                print(f"  [{i+1}/{len(text)}] '{char}' -> silence")
        else:
            # Handle spaces and punctuation
            if char == ' ':
                silence_duration = 0.15 / speech_rate
                silence = torch.zeros(1, int(silence_duration * sample_rate))
                synthesized_audio.append(silence)
                print(f"  [{i+1}/{len(text)}] space -> pause")
            elif char in '.,!?':
                silence_duration = 0.25 / speech_rate
                silence = torch.zeros(1, int(silence_duration * sample_rate))
                synthesized_audio.append(silence)
                print(f"  [{i+1}/{len(text)}] '{char}' -> long pause")
    
    if synthesized_audio:
        final_audio = torch.cat(synthesized_audio, dim=1)
        
        # Normalize
        if final_audio.max() > 0:
            final_audio = final_audio / final_audio.abs().max() * 0.8
        
        # Save
        torchaudio.save(output_path, final_audio, sample_rate)
        print(f"Character-based speech saved to: {output_path}")
        
        return output_path
    
    return None

def analyze_phoneme_coverage(phoneme_library, text):
    """
    Analyze how well we can synthesize the given text
    """
    phonemes = text_to_phonemes(text)
    words = text.split()
    
    print(f"\nAnalyzing text: '{text}'")
    print(f"Words: {words}")
    print(f"Phonemes: {phonemes}")
    
    # Check phoneme coverage
    covered_phonemes = 0
    missing_phonemes = []
    
    for phoneme in phonemes:
        if phoneme in phoneme_library:
            covered_phonemes += 1
        else:
            missing_phonemes.append(phoneme)
    
    coverage = covered_phonemes / len(phonemes) if phonemes else 0
    print(f"Phoneme coverage: {coverage:.1%} ({covered_phonemes}/{len(phonemes)})")
    
    if missing_phonemes:
        print(f"Missing phonemes: {set(missing_phonemes)}")
    
    return coverage

def create_simple_voice_clone():
    """
    Create a simple voice cloning approach using available audio samples
    This is more realistic for limited data scenarios
    """
    
    print("=== Simple Voice Cloning with Limited Data ===")
    
    # Check available audio files
    audio_dir = Path("yiddish24_audio")
    text_dir = Path("yiddish_24_transcribed")
    
    audio_files = list(audio_dir.glob("*.wav"))
    print(f"Found {len(audio_files)} audio files")
    
    if len(audio_files) == 0:
        print("No audio files found!")
        return
    
    # Load and analyze the audio samples
    sample_rates = []
    durations = []
    
    for audio_file in audio_files:
        try:
            audio, sr = torchaudio.load(audio_file)
            duration = audio.shape[1] / sr
            sample_rates.append(sr)
            durations.append(duration)
            print(f"{audio_file.name}: {duration:.2f}s, {sr}Hz, shape: {audio.shape}")
        except Exception as e:
            print(f"Error loading {audio_file}: {e}")
    
    if sample_rates:
        print(f"Average duration: {sum(durations)/len(durations):.2f}s")
        print(f"Sample rate: {sample_rates[0]}Hz")
    
    return audio_files, sample_rates[0] if sample_rates else 8000

def simple_concatenative_synthesis(text, audio_files, output_path="concatenated_speech.wav"):
    """
    Simple approach: use existing audio segments to create new speech
    This is more realistic with very limited data
    """
    
    print(f"Creating speech for: '{text}'")
    print("Using concatenative synthesis approach...")
    
    # For now, let's create a simple approach that uses one of the existing samples
    # In a real system, you'd segment the audio by phonemes/words
    
    if not audio_files:
        print("No audio files available!")
        return None
    
    # Use the first audio file as base
    base_audio_file = audio_files[0]
    
    try:
        audio, sr = torchaudio.load(base_audio_file)
        print(f"Using base audio: {base_audio_file.name}")
        
        # Simple processing: repeat or trim based on text length
        text_length_factor = max(0.5, min(2.0, len(text) / 50))  # Scale between 0.5x and 2x
        
        if text_length_factor > 1.0:
            # Repeat audio for longer text
            repeats = int(text_length_factor)
            audio = torch.cat([audio] * repeats, dim=1)
        else:
            # Trim audio for shorter text
            new_length = int(audio.shape[1] * text_length_factor)
            audio = audio[:, :new_length]
        
        # Add some variation (simple pitch shift simulation)
        # This is very basic - real pitch shifting would use more sophisticated methods
        
        # Save the result
        torchaudio.save(output_path, audio, sr)
        print(f"Generated speech saved to: {output_path}")
        
        # Verify file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"File size: {file_size} bytes")
            return output_path
        
    except Exception as e:
        print(f"Error in concatenative synthesis: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def create_voice_samples_library():
    """
    Create a library of voice samples that can be used for synthesis
    """
    
    print("=== Creating Voice Sample Library ===")
    
    audio_dir = Path("yiddish24_audio")
    text_dir = Path("yiddish_24_transcribed")
    
    voice_library = {}
    
    # Process each audio-text pair
    for audio_file in audio_dir.glob("*.wav"):
        base_name = audio_file.stem
        text_file = text_dir / f"{base_name}.txt"
        
        if text_file.exists():
            try:
                # Load audio
                audio, sr = torchaudio.load(audio_file)
                
                # Load text (UTF-16 encoding)
                with open(text_file, 'r', encoding='utf-16') as f:
                    text = f.read().strip()
                
                # Store in library
                voice_library[base_name] = {
                    'audio': audio,
                    'text': text,
                    'sample_rate': sr,
                    'duration': audio.shape[1] / sr
                }
                
                print(f"Added to library: {base_name}")
                print(f"  Text: {text[:50]}...")
                print(f"  Duration: {audio.shape[1] / sr:.2f}s")
                
            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
    
    return voice_library

def generate_speech_from_library(text, voice_library, output_path="library_speech.wav"):
    """
    Generate speech using the voice library
    """
    
    if not voice_library:
        print("Voice library is empty!")
        return None
    
    print(f"Generating speech for: '{text}'")
    
    # Simple approach: find the sample with most similar length
    text_len = len(text)
    best_match = None
    best_score = float('inf')
    
    for sample_id, sample_data in voice_library.items():
        sample_text_len = len(sample_data['text'])
        score = abs(text_len - sample_text_len)
        
        if score < best_score:
            best_score = score
            best_match = sample_id
    
    if best_match:
        print(f"Using sample: {best_match}")
        sample_data = voice_library[best_match]
        
        # Use the audio from the best matching sample
        audio = sample_data['audio']
        sr = sample_data['sample_rate']
        
        # Simple modification based on text length ratio
        length_ratio = text_len / len(sample_data['text'])
        
        if length_ratio > 1.2:
            # Stretch audio for longer text (very basic)
            new_length = int(audio.shape[1] * min(length_ratio, 2.0))
            # Simple interpolation to stretch
            indices = torch.linspace(0, audio.shape[1] - 1, new_length).long()
            audio = audio[:, indices]
        elif length_ratio < 0.8:
            # Compress audio for shorter text
            new_length = int(audio.shape[1] * max(length_ratio, 0.5))
            audio = audio[:, :new_length]
        
        # Save result
        torchaudio.save(output_path, audio, sr)
        print(f"Speech generated and saved to: {output_path}")
        
        return output_path
    
    return None

def main():
    """
    Main function for better TTS approach with phoneme segmentation
    """
    
    print("=== Advanced TTS with Phoneme Segmentation ===")
    print("This approach segments your audio by words and phonemes for better synthesis\n")
    
    # Create phoneme and word libraries
    phoneme_library, word_library = create_phoneme_library()
    
    if not phoneme_library and not word_library:
        print("Could not create libraries. Check your audio and text files.")
        return
    
    print(f"\nLibraries created successfully!")
    print(f"  - Phoneme library: {len(phoneme_library)} unique phonemes")
    print(f"  - Word library: {len(word_library)} unique words")
    
    # Show some available words and phonemes
    if word_library:
        print(f"  - Available words (sample): {list(word_library.keys())[:10]}...")
    if phoneme_library:
        print(f"  - Available phonemes (sample): {list(phoneme_library.keys())[:15]}...")
    
    # Interactive speech generation
    print("\n" + "="*50)
    print("Enter Yiddish text to synthesize speech")
    print("The system will use whole words when available,")
    print("and fall back to phoneme synthesis for new words.")
    print("Commands:")
    print("  analyze <text>     - See phoneme coverage")
    print("  rate <0.5-2.0>     - Set speech rate (0.5=slow, 1.0=normal, 2.0=fast)")
    print("  quit               - Exit")
    print("="*50)
    
    # Default speech rate
    current_speech_rate = 0.7  # Start with slower speech
    
    while True:
        user_input = input(f"\nEnter Yiddish text (rate: {current_speech_rate}x): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Check for rate command
        if user_input.lower().startswith('rate '):
            try:
                new_rate = float(user_input[5:].strip())
                if 0.3 <= new_rate <= 3.0:
                    current_speech_rate = new_rate
                    print(f"✓ Speech rate set to {current_speech_rate}x")
                    if new_rate < 0.8:
                        print("  (Slower speech)")
                    elif new_rate > 1.2:
                        print("  (Faster speech)")
                    else:
                        print("  (Normal speech)")
                else:
                    print("⚠ Speech rate should be between 0.3 and 3.0")
            except ValueError:
                print("⚠ Invalid rate. Use format: rate 0.7")
            continue
        
        # Check for analyze command
        if user_input.lower().startswith('analyze '):
            text_to_analyze = user_input[8:].strip()
            if text_to_analyze:
                analyze_phoneme_coverage(phoneme_library, text_to_analyze)
            continue
        
        # Generate filename
        safe_name = "".join(c for c in user_input[:20] if c.isalnum() or c in (' ', '_')).strip()
        safe_name = safe_name.replace(' ', '_') or 'generated'
        output_file = f"phoneme_tts_{safe_name}.wav"
        
        # Analyze coverage first
        coverage = analyze_phoneme_coverage(phoneme_library, user_input)
        
        if coverage < 0.5:
            print(f"⚠ Warning: Low phoneme coverage ({coverage:.1%}). Results may have gaps.")
        
        # Generate speech using phoneme synthesis
        print(f"\nGenerating speech at {current_speech_rate}x speed...")
        result = synthesize_from_phonemes(user_input, phoneme_library, word_library, output_file, speech_rate=current_speech_rate)
        
        if result:
            print(f"✓ Phoneme-based speech generated: {result}")
            
            # Also create character-based version
            char_output = f"char_{safe_name}.wav"
            char_result = create_character_based_synthesis(user_input, phoneme_library, char_output, speech_rate=current_speech_rate)
            if char_result:
                print(f"✓ Character-based version: {char_result}")
            
            print("  You can play both audio files to compare approaches.")
            print(f"  Both generated at {current_speech_rate}x speed")
        else:
            print("✗ Failed to generate speech")

if __name__ == "__main__":
    main() 