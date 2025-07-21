#!/usr/bin/env python3
"""
Yiddish TTS Training Script
===========================

High-quality training setup for authentic Yiddish text-to-speech
using CoquiTTS with best practices for capturing language essence.
"""

import os
import json
import shutil
from pathlib import Path
from TTS.tts.configs.vits_config import VitsConfig

def create_coqui_metadata(segments_dir: Path, output_file: Path):
    """Create CoquiTTS-compatible metadata from our segments."""
    
    audio_dir = segments_dir / "audio"
    text_dir = segments_dir / "text"
    metadata_json = segments_dir / "segments_metadata.json"
    
    # Load our metadata
    with open(metadata_json, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    # Create LJSpeech format: filename|text
    metadata_lines = []
    
    for segment in segments:
        audio_file = Path(segment['audio_file']).name  # Just filename without extension
        audio_file = audio_file.replace('.wav', '')  # Remove extension for LJSpeech format
        text_path = segment['text_file']
        
        # Read the text
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        # Clean text for TTS (remove special characters that might confuse)
        text = clean_text_for_tts(text)
        
        # Format: filename|normalized_text|original_text (LJSpeech format)
        line = f"{audio_file}|{text}|{text}"
        metadata_lines.append(line)
    
    # Save metadata in LJSpeech format
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(metadata_lines))
    
    print(f"Created CoquiTTS metadata: {output_file}")
    print(f"Total training samples: {len(metadata_lines)}")
    
    return len(metadata_lines)

def clean_text_for_tts(text: str) -> str:
    """Clean text for TTS training while preserving Yiddish characters."""
    import re
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove quotation marks that might confuse training
    text = text.replace('"', '').replace('"', '').replace('"', '')
    
    # Remove parenthetical expressions that might be inconsistent
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove extra punctuation but keep basic sentence structure
    text = re.sub(r'[^\w\s\.\,\!\?\'\-\u0590-\u05FF]+', '', text)
    
    # Clean up spacing
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_vits_config(dataset_path: Path, output_path: Path, num_samples: int):
    """Get optimized VITS config for Yiddish single-speaker training."""
    
    # Create a minimal working config - we'll add more settings as needed
    config = VitsConfig()
    
    # Essential settings
    config.model = "vits"
    config.num_speakers = 1
    config.batch_size = 16
    config.epochs = 1000
    config.save_step = 500
    config.print_step = 50
    config.run_eval = True
    config.output_path = str(output_path)
    
    # Dataset configuration - using ljspeech formatter for custom Yiddish dataset
    config.datasets = [{"formatter": "ljspeech", "meta_file_train": "metadata.txt", "meta_file_val": "metadata.txt", "path": str(dataset_path)}]
    config.use_phonemes = False
    config.phoneme_language = "yi"
    
    # Audio settings
    config.audio.sample_rate = 24000
    config.audio.num_mels = 80
    config.audio.fft_size = 1024
    config.audio.hop_length = 256
    config.audio.win_length = 1024
    config.audio.mel_fmin = 0
    config.audio.mel_fmax = 12000
    
    # Test sentences for validation
    config.test_sentences = [
        "שלום עליכם, ווי גייט עס?",
        "דאס איז א טעסט פון אונזער יידיש מאדעל.",
        "מיר וועלן זען ווי גוט עס ארבעט."
    ]
    
    return config

def setup_training_environment(segments_dir: Path):
    """Set up the complete training environment."""
    
    print("🚀 Setting up Yiddish TTS training environment...")
    
    # Create training directory structure
    train_dir = Path("yiddish_tts_training")
    train_dir.mkdir(exist_ok=True)
    
    # Create metadata
    metadata_file = train_dir / "metadata.txt"
    num_samples = create_coqui_metadata(segments_dir, metadata_file)
    
    # Copy audio files to training directory
    audio_train_dir = train_dir / "wavs"
    audio_train_dir.mkdir(exist_ok=True)
    
    print("📁 Copying audio files...")
    for audio_file in (segments_dir / "audio").glob("*.wav"):
        shutil.copy2(audio_file, audio_train_dir / audio_file.name)
    
    # Create config
    output_dir = Path("yiddish_tts_output")
    config = get_vits_config(train_dir, output_dir, num_samples)
    
    # Save config
    config_file = train_dir / "config.json"
    config.save_json(str(config_file))
    
    print(f"✅ Training environment ready!")
    print(f"   - Dataset: {train_dir}")
    print(f"   - Samples: {num_samples}")
    print(f"   - Config: {config_file}")
    print(f"   - Output: {output_dir}")
    
    return train_dir, config_file, output_dir

def create_training_script(train_dir: Path, config_file: Path, output_dir: Path):
    """Create the actual training script."""
    
    script_content = f'''#!/usr/bin/env python3
"""
Yiddish TTS Training - Execution Script
"""

import os
import sys
from TTS.bin.train_tts import main

if __name__ == "__main__":
    # Set environment variables for better performance
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Adjust if you have multiple GPUs
    
    # Override sys.argv for the training script
    sys.argv = [
        "train_tts.py",
        "--config_path", "{config_file}",
        "--restore_path", "",  # Leave empty for training from scratch
        "--group_id", "yiddish_tts",
        "--model_name", "yiddish_vits",
        "--continue_path", "",  # Use this to resume training if needed
    ]
    
    print("🎯 Starting Yiddish TTS training...")
    print("📊 Monitor training with TensorBoard:")
    print(f"   tensorboard --logdir {output_dir}")
    print()
    
    main()
'''
    
    script_file = Path("train_yiddish.py")
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    
    print(f"📝 Created training script: {script_file}")
    return script_file

def main():
    """Main setup function."""
    
    # Check if segments exist
    segments_dir = Path("tts_segments")
    if not segments_dir.exists():
        print("❌ Error: tts_segments directory not found!")
        print("   Please run the audio splitting script first.")
        return
    
    # Setup training
    train_dir, config_file, output_dir = setup_training_environment(segments_dir)
    
    # Create training script
    script_file = create_training_script(train_dir, config_file, output_dir)
    
    print()
    print("🎉 Yiddish TTS training setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Start training:")
    print(f"   python {script_file}")
    print()
    print("2. Monitor with TensorBoard:")
    print(f"   tensorboard --logdir {output_dir}")
    print()
    print("💡 Training tips:")
    print("   - Training will take several hours")
    print("   - Monitor loss curves in TensorBoard")
    print("   - Best models saved every 500 steps")
    print("   - Stop when loss plateaus (usually 20k-50k steps)")
    print("   - Training quality is MORE IMPORTANT than multilingual compatibility")

if __name__ == "__main__":
    main() 