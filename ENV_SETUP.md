# Environment Setup for LLM Transliterator

## Step 1: Create .env file

Create a file named `.env` in the project root directory with the following content:

```
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

## Step 2: Install Dependencies

```bash
pip install openai python-dotenv
```

## Step 3: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Replace `your_openai_api_key_here` in the `.env` file with your actual key

## Step 4: Usage

Use the LLM-powered TTS with:

```bash
python src/utils/llm_tts.py
```

The system will:
1. Use ChatGPT to transliterate your Yiddish text
2. Generate speech using the transliterated text
3. Show a comparison with the rule-based approach 