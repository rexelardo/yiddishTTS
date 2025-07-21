#!/usr/bin/env python3
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
        "--config_path", "yiddish_tts_training/config.json",
        "--restore_path", "",  # Leave empty for training from scratch
        "--group_id", "yiddish_tts",
        "--model_name", "yiddish_vits",
        "--continue_path", "",  # Use this to resume training if needed
    ]
    
    print("🎯 Starting Yiddish TTS training...")
    print("📊 Monitor training with TensorBoard:")
    print(f"   tensorboard --logdir yiddish_tts_output")
    print()
    
    main()
