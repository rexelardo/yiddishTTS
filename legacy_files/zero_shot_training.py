from TTS.api import TTS
import soundfile as sf

# 1) Path to your 9 s, 16 kHz mono reference clip:
reference_wav = "small_16k_pcm16.wav"

# 2) Load a zero-shot multispeaker model (English-capable; you can whisper any Yiddish text here)
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/vits",
    progress_bar=False,
    gpu=torch.cuda.is_available()
)

# 3) The text you want to synthesize (Yiddish, for example):
text = "איך בין ChatGPT, אַ געקלאונטע קול."

# 4) Generate
wav, sr = tts.tts(text=text, speaker_wav=reference_wav)

# 5) Save out
sf.write("clone_output.wav", wav, sr)
print("Wrote clone_output.wav")
