import whisper

model = whisper.load_model("turbo")
result = model.transcribe("yiddish24_audio/130837_אקטועלע נייעס  פרייזן פון האלץ פאר קאנסטראקשען איז.mp3", language="yi")
print(result["text"])
