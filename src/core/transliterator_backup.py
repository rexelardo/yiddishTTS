"""
Yiddish Text Transliterator
===========================
Converts Yiddish text (Hebrew script) to phonetic Latin script for TTS.
"""

import re
from typing import Dict, Optional


class YiddishTransliterator:
    """Transliterates Yiddish text from Hebrew script to phonetic Latin script."""
    
    def __init__(self):
        """Initialize the transliterator with character mappings."""
        self.char_mapping = self._create_character_mapping()
        self.word_replacements = self._create_word_replacements()
    
    def _create_character_mapping(self) -> Dict[str, str]:
        """Create the Hebrew to Latin character mapping."""
        return {
            # Basic letters
            'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h',
            'ו': 'u', 'ז': 'z', 'ח': 'kh', 'ט': 't', 'י': 'i',
            'כ': 'k', 'ל': 'l', 'מ': 'm', 'נ': 'n', 'ס': 's',
            'ע': 'e', 'פ': 'p', 'צ': 'ts', 'ק': 'k', 'ר': 'r',
            'ש': 'sh', 'ת': 't',
            
            # Final forms
            'ך': 'k', 'ם': 'm', 'ן': 'n', 'ף': 'f', 'ץ': 'ts',
            
            # Vowels and diacritics
            'ַ': 'a', 'ָ': 'o', 'ֶ': 'e', 'ֵ': 'e', 'ִ': 'i',
            'ֹ': 'o', 'ֻ': 'u', 'ְ': '', 'ּ': '',
            
            # Punctuation
            '׳': '', '״': '', '־': '-',
            
            # Numbers (keep as is for now)
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '.': '.', ',': ',', '!': '!', '?': '?',
            
            # Spaces and common punctuation
            ' ': ' ', '\n': ' ', '\t': ' '
        }
    
    def _create_word_replacements(self) -> Dict[str, str]:
        """Create common word replacements for better pronunciation."""
        return {
            # Common words that need special handling
            'און': 'un',
            'אין': 'in', 
            'איז': 'iz',  # Fixed: was 'ayz', now 'iz'
            'דאס': 'das',
            'דער': 'der',
            'די': 'di',
            'פון': 'fun',  # More accurate: was 'pun', now 'fun'
            'מיט': 'mit',
            'אויף': 'oyf',  # Simplified: was 'aoyf', now 'oyf'
            'צו': 'tsu',
            'פאר': 'far',  # More accurate: was 'par', now 'far'
            'נאך': 'nokh',
            'אלע': 'ale',
            'וואס': 'vas',
            'ווען': 'ven',
            'וואו': 'vu',  # More accurate: was 'vau', now 'vu'
            'ווי': 'vi',
            'וועט': 'vet',
            'האט': 'hot',  # More accurate: was 'hat', now 'hot'
            'זיין': 'zayn',
            'איר': 'ir',
            'זי': 'zi',
            'ער': 'er',
            'מיר': 'mir',
            'איך': 'ikh',
            'דו': 'du',
            # Additional common words for better pronunciation
            'באטראפן': 'betrofn',  # Your word from the example
            'געווארן': 'gevorn',   # Your word from the example
            'וועלן': 'veln',
            'קענען': 'kenen',
            'גיין': 'geyn',
            'קומען': 'kumen',
            'זאגן': 'zogn',
            'טון': 'tun',
            'געבן': 'gebn',
            'נעמען': 'nemen',
            'טשאלנט': 'tshalnt',
            'פאר': 'far'
        }
    
    def transliterate_char(self, char: str) -> str:
        """Transliterate a single character."""
        return self.char_mapping.get(char, char)
    
    def transliterate_word(self, word: str) -> str:
        """Transliterate a single word with special word handling."""
        # Check for direct word replacements first
        word_clean = word.strip('.,!?;:"()[]{}')
        if word_clean in self.word_replacements:
            return self.word_replacements[word_clean]
        
        # Character-by-character transliteration
        result = ''.join(self.transliterate_char(char) for char in word)
        
        # Clean up multiple spaces and common issues
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()
        
        return result
    
    def transliterate(self, text: str) -> str:
        """
        Transliterate Yiddish text to phonetic Latin script.
        
        Args:
            text: Yiddish text in Hebrew script
            
        Returns:
            Phonetic Latin script representation
        """
        if not text:
            return ""
        
        # Split into words and process each
        words = text.split()
        transliterated_words = []
        
        for word in words:
            transliterated_word = self.transliterate_word(word)
            if transliterated_word:  # Only add non-empty words
                transliterated_words.append(transliterated_word)
        
        result = ' '.join(transliterated_words)
        
        # Final cleanup
        result = re.sub(r'\s+', ' ', result)  # Multiple spaces to single
        result = re.sub(r'^\s+|\s+$', '', result)  # Trim
        
        return result
    
    def add_word_mapping(self, yiddish_word: str, phonetic_word: str) -> None:
        """Add a custom word mapping."""
        self.word_replacements[yiddish_word] = phonetic_word
    
    def add_char_mapping(self, yiddish_char: str, phonetic_char: str) -> None:
        """Add a custom character mapping."""
        self.char_mapping[yiddish_char] = phonetic_char 