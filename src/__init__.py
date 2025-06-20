"""
Yiddish Text-to-Speech (Yiddish TTS)
===================================

A Python package for converting Yiddish text (Hebrew script) to speech
using transliteration and voice cloning techniques.

Main Components:
- Text transliteration (Hebrew script to phonetic)
- Speech synthesis using espeak/TTS
- Voice cloning and matching
- Audio processing and enhancement

Author: Bob Charish Project
"""

__version__ = "1.0.0"
__author__ = "Bob Charish Project"

from .core.transliterator import YiddishTransliterator
from .core.synthesizer import SpeechSynthesizer
from .voice_matching.voice_cloner import VoiceCloner

__all__ = [
    'YiddishTransliterator',
    'SpeechSynthesizer', 
    'VoiceCloner'
] 