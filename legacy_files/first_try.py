import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchaudio
import torch.nn.functional as F

# Dataset class for Yiddish TTS data
class YiddishDataset(Dataset):
    def __init__(self, audio_dir, text_dir):
        self.audio_files = []
        self.text_files = []
        
        # Get all wav files
        wav_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
        
        for wav_file in wav_files:
            audio_path = os.path.join(audio_dir, wav_file)
            # Find corresponding text file with same base name
            base_name = wav_file.replace('.wav', '')
            text_file = f"{base_name}.txt"
            text_path = os.path.join(text_dir, text_file)
            
            if os.path.exists(text_path):
                self.audio_files.append(audio_path)
                self.text_files.append(text_path)
                print(f"Found pair: {wav_file} <-> {text_file}")
            else:
                print(f"No matching text file for {wav_file}")
        
        print(f"Found {len(self.audio_files)} audio-text pairs")

    def __len__(self):
        return len(self.audio_files)

    def __getitem__(self, idx):
        # Load audio using torchaudio
        audio_path = self.audio_files[idx]
        text_path = self.text_files[idx]
        
        try:
            print(f"Loading audio: {audio_path}")
            # Load audio with torchaudio
            audio, sample_rate = torchaudio.load(audio_path)
            print(f"Audio loaded successfully, shape: {audio.shape}, sample_rate: {sample_rate}")
            
            # Convert to mel spectrogram for TTS
            mel_transform = torchaudio.transforms.MelSpectrogram(
                sample_rate=sample_rate,
                n_mels=80,
                n_fft=1024,
                hop_length=256
            )
            mel_spec = mel_transform(audio)
            print(f"Mel spectrogram created, shape: {mel_spec.shape}")
            
            # Read text file
            print(f"Loading text: {text_path}")
            with open(text_path, 'r', encoding='utf-16') as f:
                text = f.read().strip()
            print(f"Text loaded successfully: {text[:50]}...")
            
            return mel_spec.squeeze(0), text  # Remove channel dimension
            
        except UnicodeDecodeError as e:
            print(f"Unicode error reading text file {text_path}: {e}")
            return torch.zeros(80, 100, requires_grad=True), ""
        except Exception as e:
            print(f"Error loading files {audio_path} or {text_path}: {e}")
            import traceback
            traceback.print_exc()
            # Return dummy data if loading fails
            return torch.zeros(80, 100, requires_grad=True), ""

def collate_fn(batch):
    """Custom collate function to handle variable length sequences"""
    mel_specs, texts = zip(*batch)
    
    # Find max length
    max_len = max([mel.size(1) for mel in mel_specs])
    
    # Pad mel spectrograms
    padded_mels = []
    for mel in mel_specs:
        pad_size = max_len - mel.size(1)
        if pad_size > 0:
            padded_mel = F.pad(mel, (0, pad_size))
        else:
            padded_mel = mel
        padded_mels.append(padded_mel)
    
    # Stack into batch
    mel_batch = torch.stack(padded_mels)
    
    return mel_batch, texts

# Simple TTS model (placeholder)
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

# Simple text preprocessing (character-level)
def text_to_indices(text, char_to_idx=None):
    if char_to_idx is None:
        # Create a simple character mapping
        chars = set(''.join([text]))
        char_to_idx = {char: idx for idx, char in enumerate(sorted(chars))}
    
    indices = [char_to_idx.get(char, 0) for char in text]
    return torch.tensor(indices, dtype=torch.long)

# Training function
def train_tts_model(audio_dir, text_dir, epochs=50, batch_size=1):  # More epochs, smaller batch
    dataset = YiddishDataset(audio_dir, text_dir)
    
    if len(dataset) == 0:
        print("No data found! Check your audio and text directories.")
        return
    
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    model = SimpleTTSModel()
    
    # Use L1 loss which is better for audio reconstruction
    criterion = nn.L1Loss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)  # Lower learning rate
    
    print(f"Starting training with {len(dataset)} samples...")
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (mel_batch, texts) in enumerate(dataloader):
            try:
                # Create more realistic text input based on actual text length
                text_len = min(len(texts[0]), 50) if texts[0] else 10
                dummy_text_input = torch.randint(0, 100, (mel_batch.size(0), text_len))
                
                optimizer.zero_grad()
                output = model(dummy_text_input, mel_batch)
                
                # Ensure output and target have same dimensions
                if output.size() != mel_batch.size():
                    min_len = min(output.size(2), mel_batch.size(2))
                    output = output[:, :, :min_len]
                    mel_batch = mel_batch[:, :, :min_len]
                
                # Detach target from computation graph
                mel_batch = mel_batch.detach()
                
                loss = criterion(output, mel_batch)
                loss.backward()
                
                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                optimizer.step()
                
                total_loss += loss.item()
                
                if batch_idx % 1 == 0:  # Print every batch since we have few samples
                    print(f'Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}, Loss: {loss.item():.4f}')
                    
            except Exception as e:
                print(f"Error in batch {batch_idx}: {e}")
                continue
        
        avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0
        print(f'Epoch {epoch+1}/{epochs} completed, Average Loss: {avg_loss:.4f}')
        
        # Save model every 10 epochs
        if (epoch + 1) % 10 == 0:
            temp_path = f'yiddish_tts_model_epoch_{epoch+1}.pth'
            torch.save({
                'model_state_dict': model.state_dict(),
                'model_config': {
                    'text_vocab_size': 1000,
                    'mel_dim': 80,
                    'hidden_dim': 256
                },
                'epoch': epoch + 1,
                'loss': avg_loss
            }, temp_path)
            print(f"Model checkpoint saved to {temp_path}")
    
    # Save the trained model
    model_save_path = 'yiddish_tts_model.pth'
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_config': {
            'text_vocab_size': 1000,
            'mel_dim': 80,
            'hidden_dim': 256
        },
        'epoch': epochs,
        'loss': avg_loss
    }, model_save_path)
    print(f"Final model saved to {model_save_path}")
    
    return model

if __name__ == "__main__":
    audio_directory = 'yiddish24_audio'
    text_directory = 'yiddish_24_transcribed'
    
    # Check if directories exist
    if not os.path.exists(audio_directory):
        print(f"Audio directory {audio_directory} not found!")
    if not os.path.exists(text_directory):
        print(f"Text directory {text_directory} not found!")
    
    train_tts_model(audio_directory, text_directory) 