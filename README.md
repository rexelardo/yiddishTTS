# Yiddish Text-to-Speech (TTS) System

A Python-based text-to-speech system for converting Yiddish text (written in Hebrew script) to natural-sounding speech with voice cloning capabilities.

![Yiddish TTS Demo](https://img.shields.io/badge/Status-Working-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Features

- **📝 Text Transliteration**: Converts Yiddish text from Hebrew script to phonetic Latin script
- **🔊 Speech Synthesis**: Generates speech using espeak TTS engine
- **🎭 Voice Cloning**: Applies voice characteristics from reference audio
- **🎵 Multiple Variants**: Creates different voice styles (natural, deeper, smooth, character)
- **⚡ Batch Processing**: Process multiple texts at once
- **🖥️ CLI Interface**: Easy-to-use command-line interface

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/yiddish-tts.git
   cd yiddish-tts
   ```

2. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt install espeak espeak-data sox

   # Fedora/RHEL
   sudo dnf install espeak sox

   # macOS
   brew install espeak sox
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

**Simple text-to-speech**:
```bash
python yiddish_tts.py "שלום עליכם" --output hello.wav
```

**With voice cloning**:
```bash
python yiddish_tts.py "שלום עליכם" --output hello.wav --voice-clone
```

**Custom settings**:
```bash
python yiddish_tts.py "שלום עליכם" --output hello.wav --speed 120 --pitch 40
```

## 📁 Project Structure

```
yiddish-tts/
├── src/                          # Main source code
│   ├── core/                     # Core TTS functionality
│   │   ├── transliterator.py     # Hebrew to phonetic conversion
│   │   └── synthesizer.py        # Speech synthesis
│   └── voice_matching/           # Voice cloning and processing
│       └── voice_cloner.py       # Voice characteristic matching
├── examples/                     # Usage examples
│   └── basic_usage.py           # Basic usage demonstrations
├── docs/                        # Documentation
├── yiddish_tts.py              # Main CLI interface
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎵 How It Works

### 1. Text Transliteration
The system converts Yiddish text from Hebrew script to phonetic Latin script:

```python
from src.core.transliterator import YiddishTransliterator

transliterator = YiddishTransliterator()
phonetic = transliterator.transliterate("שלום עליכם")
# Output: "shalum elikm"
```

### 2. Speech Synthesis
Converts phonetic text to speech using espeak:

```python
from src.core.synthesizer import SpeechSynthesizer

synthesizer = SpeechSynthesizer()
synthesizer.synthesize_yiddish_text("שלום עליכם", "output.wav")
```

### 3. Voice Cloning
Applies voice characteristics from reference audio:

```python
from src.voice_matching.voice_cloner import VoiceCloner

cloner = VoiceCloner(reference_audio_dir="reference_audio")
variants = cloner.clone_voice("input.wav", "output_dir")
```

## 🎛️ Voice Variants

The system can generate multiple voice variants:

- **Natural**: Subtle adjustments for more natural speech
- **Deeper**: Lower pitch with enhanced bass frequencies
- **Smooth**: Professional-sounding with gentle compression
- **Character**: Aged voice with distinctive character

## 📖 Examples

### Python API Usage

```python
from src.core.synthesizer import SpeechSynthesizer
from src.voice_matching.voice_cloner import VoiceCloner

# Basic synthesis
synthesizer = SpeechSynthesizer()
synthesizer.synthesize_yiddish_text(
    "די בריוו איז אינטערגעשריבן", 
    "output/speech.wav"
)

# Voice cloning
cloner = VoiceCloner(reference_audio_dir="reference_audio")
variants = cloner.clone_voice("output/speech.wav")

# Batch processing
texts = ["שלום עליכם", "גוטן מארגן", "א גוטן טאג"]
files = synthesizer.batch_synthesize(texts, "output/")
```

### CLI Usage

```bash
# Basic usage
python yiddish_tts.py "שלום עליכם"

# With custom output
python yiddish_tts.py "שלום עליכם" --output greetings.wav

# With voice cloning
python yiddish_tts.py "שלום עליכם" --voice-clone --reference-dir my_audio/

# Custom voice settings
python yiddish_tts.py "שלום עליכם" --speed 120 --pitch 60
```

## 🔧 Configuration

### Reference Audio Setup

1. Create a directory for reference audio files:
   ```bash
   mkdir reference_audio
   ```

2. Add your reference audio files (WAV, MP3, FLAC, M4A):
   ```
   reference_audio/
   ├── speaker1.wav
   ├── speaker2.wav
   └── speaker3.wav
   ```

3. The system automatically selects the best reference file based on quality heuristics.

### Customizing Transliteration

You can customize the transliteration by adding word or character mappings:

```python
from src.core.transliterator import YiddishTransliterator

transliterator = YiddishTransliterator()

# Add custom word mapping
transliterator.add_word_mapping("וואונדער", "vunder")

# Add custom character mapping
transliterator.add_char_mapping("ח", "ch")
```

## 🛠️ Development

### Running Examples

```bash
# Run basic usage examples
python examples/basic_usage.py

# Test the CLI
python yiddish_tts.py "דאס איז א טעסט" --output test.wav
```

### Adding New Voice Variants

To add a new voice variant, modify the `create_voice_variant` method in `src/voice_matching/voice_cloner.py`:

```python
elif variant_type == "my_variant":
    cmd = [
        "sox", source_audio, output_file,
        "pitch", "-100",     # Your pitch adjustment
        "tempo", "0.98",     # Your tempo adjustment
        # Add more sox effects...
    ]
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- espeak (text-to-speech engine)
- sox (audio processing)

### Python Dependencies
- pathlib (built-in)
- subprocess (built-in)
- argparse (built-in)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **espeak** - Text-to-speech synthesis engine
- **sox** - Audio processing toolkit  
- **Yiddish language community** - For preserving this beautiful language

## 📞 Support

If you encounter issues or have questions:

1. Check the [Issues](https://github.com/your-username/yiddish-tts/issues) page
2. Create a new issue with:
   - Your operating system
   - Python version
   - Full error message
   - Steps to reproduce

## 🔮 Future Improvements

- [ ] Support for more TTS engines (Festival, SAPI)
- [ ] Neural voice cloning with XTTS
- [ ] Web interface
- [ ] Mobile app
- [ ] Better phonetic mapping
- [ ] Yiddish language model integration
- [ ] SSML support for advanced speech control

---

**Made with ❤️ for the Yiddish language community** 