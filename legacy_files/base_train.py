from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

from datasets import load_dataset, Audio
ds = load_dataset(
    "csv",
    data_files={"train": "metadata.csv"},
    split="train",
    column_names=["path","text"],    # if your CSV has headers, you can omit this
)

