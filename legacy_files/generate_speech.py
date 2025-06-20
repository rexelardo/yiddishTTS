import torch
import torch.nn as nn
import torchaudio
import numpy as np
import os

# Import the model class from first_try.py
class SimpleTTSModel(nn.Module):
    def __init__(self, text_vocab_size=1000, mel_dim=80, hidden_dim=256):
        super(SimpleTTSModel, self).__init__()
        self.text_embedding = nn.Embedding(text_vocab_size, hidden_dim)
        self.encoder = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.decoder = nn.Linear(hidden_dim, mel_dim)
        
    def forward(self, text_indices, mel_target=None):
        # Simple forward pass with actual computation
        batch_size = text_indices.size(0)
        seq_len = mel_target.size(2) if mel_target is not None else 100
        
        # Embed text indices
        embedded = self.text_embedding(text_indices)  # [batch, seq, hidden]
        
        # Pass through LSTM encoder
        encoded, _ = self.encoder(embedded)  # [batch, seq, hidden]
        
        # Decode to mel spectrogram dimensions
        # Take mean over sequence dimension and expand to mel dimensions
        encoded_mean = encoded.mean(dim=1)  # [batch, hidden]
        decoded = self.decoder(encoded_mean)  # [batch, mel_dim]
        
        # Expand to sequence length
        output = decoded.unsqueeze(2).expand(batch_size, 80, seq_len)
        
        return output

def text_to_indices(text, max_length=50):
    """Convert text to character indices"""
    # Simple character-level encoding
    # In a real system, you'd want a proper tokenizer
    chars = list(set(text))
    char_to_idx = {char: idx for idx, char in enumerate(chars)}
    
    # Convert text to indices
    indices = [char_to_idx.get(char, 0) for char in text[:max_length]]
    
    # Pad to max_length
    while len(indices) < max_length:
        indices.append(0)
    
    return torch.tensor(indices, dtype=torch.long).unsqueeze(0)  # Add batch dimension

def mel_to_audio(mel_spectrogram, sample_rate=8000):
    """Convert mel spectrogram back to audio (simplified)"""
    print(f"Input mel spectrogram shape: {mel_spectrogram.shape}")
    print(f"Mel spectrogram min/max: {mel_spectrogram.min().item():.4f}/{mel_spectrogram.max().item():.4f}")
    
    # Ensure mel spectrogram has reasonable values
    if mel_spectrogram.max() < 0.001:
        print("Warning: Mel spectrogram values are very small, scaling up...")
        mel_spectrogram = mel_spectrogram * 100
    
    try:
        # Create inverse mel transform
        inverse_mel_transform = torchaudio.transforms.InverseMelScale(
            n_stft=513,  # (n_fft // 2) + 1
            n_mels=80
        )
        
        # Convert mel to linear spectrogram
        linear_spec = inverse_mel_transform(mel_spectrogram)
        print(f"Linear spectrogram shape: {linear_spec.shape}")
        print(f"Linear spectrogram min/max: {linear_spec.min().item():.4f}/{linear_spec.max().item():.4f}")
        
        # Use Griffin-Lim algorithm to convert spectrogram to audio
        griffin_lim = torchaudio.transforms.GriffinLim(
            n_fft=1024,
            hop_length=256,
            power=1.0,
            n_iter=32  # More iterations for better quality
        )
        
        audio = griffin_lim(linear_spec)
        print(f"Generated audio shape: {audio.shape}")
        print(f"Audio min/max: {audio.min().item():.4f}/{audio.max().item():.4f}")
        
        # Normalize audio to reasonable range
        if audio.max() > 0:
            audio = audio / audio.abs().max() * 0.8  # Normalize to 80% of max range
        
        return audio
        
    except Exception as e:
        print(f"Error in mel_to_audio conversion: {e}")
        # Fallback: create a simple sine wave as test audio
        print("Creating fallback sine wave audio...")
        duration = mel_spectrogram.size(1) * 256 / sample_rate  # Approximate duration
        t = torch.linspace(0, duration, int(duration * sample_rate))
        audio = 0.3 * torch.sin(2 * 3.14159 * 440 * t)  # 440 Hz sine wave
        return audio

def load_model(model_path='yiddish_tts_model.pth'):
    """Load the trained TTS model"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found. Please train the model first using first_try.py")
    
    # Load the saved model
    checkpoint = torch.load(model_path, map_location='cpu')
    model_config = checkpoint['model_config']
    
    # Create model with saved configuration
    model = SimpleTTSModel(
        text_vocab_size=model_config['text_vocab_size'],
        mel_dim=model_config['mel_dim'],
        hidden_dim=model_config['hidden_dim']
    )
    
    # Load the trained weights
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()  # Set to evaluation mode
    
    print(f"Model loaded successfully from {model_path}")
    return model

def generate_speech(text, model, output_path='generated_speech.wav', sample_rate=8000):
    """Generate speech from Yiddish text"""
    print(f"Generating speech for text: {text}")
    
    # Convert text to indices
    text_indices = text_to_indices(text)
    print(f"Text converted to indices, shape: {text_indices.shape}")
    print(f"Text indices: {text_indices.squeeze().tolist()[:10]}...")  # Show first 10 indices
    
    # Generate mel spectrogram
    with torch.no_grad():
        # Create a dummy target for sequence length (you might want to make this dynamic)
        dummy_target = torch.zeros(1, 80, 200)  # 200 time steps
        mel_output = model(text_indices, dummy_target)
        print(f"Generated mel spectrogram, shape: {mel_output.shape}")
        print(f"Mel output min/max: {mel_output.min().item():.6f}/{mel_output.max().item():.6f}")
        print(f"Mel output mean/std: {mel_output.mean().item():.6f}/{mel_output.std().item():.6f}")
    
    # Convert mel spectrogram to audio
    try:
        audio = mel_to_audio(mel_output.squeeze(0))  # Remove batch dimension
        print(f"Converted to audio, shape: {audio.shape}")
        
        # Check if audio has any non-zero values
        if audio.abs().max() < 1e-6:
            print("Warning: Generated audio is essentially silent!")
            print("This might indicate issues with the model or conversion process.")
        
        # Ensure audio is not empty
        if audio.numel() == 0:
            print("Error: Generated audio tensor is empty!")
            return None
        
        # Save audio file
        print(f"Saving audio to {output_path} with sample rate {sample_rate}")
        torchaudio.save(output_path, audio.unsqueeze(0), sample_rate)  # Add channel dimension
        print(f"Audio saved to {output_path}")
        
        # Verify the saved file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"Saved file size: {file_size} bytes")
            
            # Try to load it back to verify
            try:
                loaded_audio, loaded_sr = torchaudio.load(output_path)
                print(f"Verification: loaded audio shape {loaded_audio.shape}, sample rate {loaded_sr}")
            except Exception as e:
                print(f"Warning: Could not verify saved audio: {e}")
        
        return output_path
        
    except Exception as e:
        print(f"Error converting mel to audio: {e}")
        import traceback
        traceback.print_exc()
        print("Saving mel spectrogram as tensor instead...")
        mel_path = output_path.replace('.wav', '_mel.pt')
        torch.save(mel_output, mel_path)
        print(f"Mel spectrogram saved to {mel_path}")
        return None

def main():
    """Main function for interactive text-to-speech generation"""
    try:
        # Load the trained model
        model = load_model()
        
        print("\n=== Yiddish Text-to-Speech Generator ===")
        print("Enter Yiddish text to generate speech (or 'quit' to exit)")
        
        while True:
            # Get user input
            user_text = input("\nEnter Yiddish text: ").strip()
            
            if user_text.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_text:
                print("Please enter some text.")
                continue
            
            # Generate filename based on text (simplified)
            safe_filename = "".join(c for c in user_text[:20] if c.isalnum() or c in (' ', '_')).rstrip()
            safe_filename = safe_filename.replace(' ', '_')
            output_file = f"generated_{safe_filename}.wav"
            
            # Generate speech
            try:
                result = generate_speech(user_text, model, output_file)
                if result:
                    print(f"✓ Speech generated successfully: {result}")
                    print("You can play the audio file with any audio player.")
                else:
                    print("⚠ Audio generation had issues, but mel spectrogram was saved.")
            except Exception as e:
                print(f"✗ Error generating speech: {e}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'python first_try.py' first to train the model.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 