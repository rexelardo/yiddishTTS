"""
LLM-Powered Yiddish Transliterator
==================================
Uses OpenAI's ChatGPT API to transliterate Yiddish text from Hebrew script to phonetic Latin script.

Setup:
1. Create a .env file in the project root with:
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   
2. Install dependencies:
   pip install openai python-dotenv
"""

import os
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv


class LLMTransliterator:
    """Transliterates Yiddish text using OpenAI's ChatGPT API."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM transliterator.
        
        Args:
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError(
                "Please set your OpenAI API key in .env file:\n"
                "OPENAI_API_KEY=your_actual_api_key_here"
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', model)
        
        # System prompt for consistent transliteration
        self.system_prompt = """You are an expert in Yiddish language and transliteration. Your task is to convert Yiddish text written in Hebrew script into phonetic Latin script suitable for text-to-speech synthesis.

Guidelines:
- Convert Hebrew letters to their Yiddish phonetic equivalents
- Use standard YIVO transliteration when possible
- Make the output pronounceable for English TTS engines
- Preserve the natural flow and rhythm of Yiddish speech
- Common conversions: ש=sh, ח=kh, צ=ts, ך=kh, ם=m, ן=n, ף=f, ץ=ts
- Handle vowels appropriately: א=a, ע=e, ו=u/o, י=i/y
- Convert װ to v, יי to ey, וו to u/v as appropriate

Example:
Hebrew: שלום עליכם
Phonetic: sholem aleykhem

Only return the transliterated text, no explanations."""

    def transliterate(self, text: str) -> str:
        """
        Transliterate Yiddish text using ChatGPT.
        
        Args:
            text: Yiddish text in Hebrew script
            
        Returns:
            Phonetic Latin script representation
        """
        if not text or not text.strip():
            return ""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Transliterate this Yiddish text: {text}"}
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent results
            )
            
            transliterated = response.choices[0].message.content
            return transliterated.strip() if transliterated else ""
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                print("❌ OpenAI API rate limit reached. Please try again later.")
            elif "authentication" in error_msg or "api key" in error_msg:
                print("❌ OpenAI API authentication failed. Check your API key.")
            elif "invalid" in error_msg:
                print(f"❌ Invalid OpenAI API request: {e}")
            else:
                print(f"❌ LLM transliteration error: {e}")
            return ""
    
    def transliterate_with_context(self, text: str, context: str = "") -> str:
        """
        Transliterate with additional context for better accuracy.
        
        Args:
            text: Yiddish text in Hebrew script
            context: Additional context about the text (topic, style, etc.)
            
        Returns:
            Phonetic Latin script representation
        """
        if not text or not text.strip():
            return ""
        
        user_message = f"Transliterate this Yiddish text: {text}"
        if context:
            user_message += f"\n\nContext: {context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            transliterated = response.choices[0].message.content
            return transliterated.strip() if transliterated else ""
            
        except Exception as e:
            print(f"❌ LLM transliteration error: {e}")
            return ""
    
    def batch_transliterate(self, texts: list) -> list:
        """
        Transliterate multiple texts in batch.
        
        Args:
            texts: List of Yiddish texts in Hebrew script
            
        Returns:
            List of transliterated texts
        """
        results = []
        for text in texts:
            result = self.transliterate(text)
            results.append(result)
        return results 