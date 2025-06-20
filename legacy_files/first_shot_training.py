# # from datasets import load_dataset, Audio
# # from transformers import (
# #     SpeechT5Processor,
# #     SpeechT5ForTextToSpeech,
# #     TrainingArguments,
# #     Trainer,
# # )
# # import torch
# # from speechbrain.pretrained import EncoderClassifier
# # import os

# # # 3) Load & cast to 16 kHz
# # ds = load_dataset(
# #     "csv",
# #     data_files={"train": "metadata.csv"},
# #     # column_names=["path","text"],
# #     split="train",
# # )
# # ds = ds.cast_column("path", Audio(sampling_rate=16_000))

# # # 4) Prep the SpeechT5 processor & model
# # checkpoint = "microsoft/speecht5_tts"
# # processor = SpeechT5Processor.from_pretrained(checkpoint)
# # model     = SpeechT5ForTextToSpeech.from_pretrained(checkpoint)

# # # 5) (Optional) load a speaker-embedding model (you can skip this if you only have one speaker)
# # device = "cuda" if torch.cuda.is_available() else "cpu"
# # spk_model = EncoderClassifier.from_hparams(
# #     source="speechbrain/spkrec-xvect-voxceleb",
# #     run_opts={"device": device},
# #     savedir=os.path.join("/tmp", "spkrec-xvect"),
# # )

# # def make_spk_emb(wav):
# #     # wav: np.ndarray, shape (T,)
# #     with torch.no_grad():
# #         emb = spk_model.encode_batch(torch.tensor(wav).unsqueeze(0).to(device))
# #         emb = torch.nn.functional.normalize(emb, dim=2).squeeze().cpu().numpy()
# #     return emb  # shape (512,)

# # # 6) map each example into the form SpeechT5 wants
# # def prepare(example):
# #     audio = example["path"]["array"]
# #     # basic character cleanup for Yiddish—add more mappings if needed:
# #     text = example["text"].replace("־","-")
# #     out = processor(
# #         text=text,
# #         audio_target=audio,
# #         sampling_rate=16_000,
# #         return_attention_mask=False,
# #     )
# #     # out["labels"] is a batch of size 1 → strip that dim
# #     out["labels"] = out["labels"][0]
# #     # add speaker embedding if you like (or use a constant vector)
# #     out["speaker_embeddings"] = make_spk_emb(audio)
# #     return out

# # # drop the old columns
# # ds = ds.map(prepare, remove_columns=["path","text"])

# # # 7) do a train/test split
# # ds = ds.train_test_split(test_size=0.2)
# # train_ds = ds["train"]
# # eval_ds  = ds["test"]

# # # 8) a small datacollator that pads and handles -100 for labels:
# # from dataclasses import dataclass
# # from typing import Any, Dict, List, Union
# # import torch

# # @dataclass
# # class TTSDataCollatorWithPadding:
# #     processor: Any   # a SpeechT5Processor

# #     def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]):
# #         # pad input_ids
# #         inputs  = [{"input_ids": f["input_ids"]} for f in features]
# #         labels  = [{"input_values": f["labels"]} for f in features]
# #         spk_emb = [f["speaker_embeddings"] for f in features]

# #         batch = self.processor.pad(
# #             input_ids=inputs,
# #             labels=labels,
# #             return_tensors="pt",
# #         )
# #         # replace padded timesteps with -100 so loss is ignored there
# #         batch["labels"] = batch["labels"].masked_fill(
# #             batch.decoder_attention_mask.unsqueeze(-1).ne(1), -100
# #         )
# #         del batch["decoder_attention_mask"]
# #         batch["speaker_embeddings"] = torch.tensor(spk_emb)
# #         return batch

# # collator = TTSDataCollatorWithPadding(processor=processor)

# # # 9) TrainingArguments & Trainer
# # training_args = TrainingArguments(
# #     output_dir="tts-small",
# #     per_device_train_batch_size=2,
# #     per_device_eval_batch_size=2,
# #     num_train_epochs=10,
# #     learning_rate=1e-4,
# #     logging_steps=10,
# #     save_steps=200,
# #     evaluation_strategy="steps",
# #     eval_steps=200,
# #     fp16=True,
# # )

# # trainer = Trainer(
# #     model=model,
# #     args=training_args,
# #     train_dataset=train_ds,
# #     eval_dataset=eval_ds,
# #     data_collator=collator,
# # )

# # # 10) kick off training
# # trainer.train()

# # # 11) Save your fine-tuned model & processor
# # output_dir = "tts-small"  # or wherever you want to dump it

# # # save the model weights + config
# # trainer.save_model(output_dir)

# # # also save the processor (tokenizer + feature extractor)
# # processor.save_pretrained(output_dir)



# from datasets import load_dataset, Audio
# from transformers import (
#     SpeechT5Processor,
#     SpeechT5ForTextToSpeech,
#     Trainer,
#     TrainingArguments
# )
# import torch
# from torch.nn.utils.rnn import pad_sequence

# # 1) load your tiny CSV
# ds = load_dataset(
#     "csv",
#     data_files={"train": "metadata.csv"},
#     split="train",
# )
# # cast to actual 16 kHz waveforms
# ds = ds.cast_column("path", Audio(sampling_rate=16_000))

# # 2) model + processor
# processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
# model     = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")


# def preprocess(batch):
#     # batch["path"] is a list of dicts {"array": np.ndarray, "sampling_rate": int}
#     waveforms = [audio["array"] for audio in batch["path"]]
#     batch["waveform"] = waveforms

#     # tokenize your texts (this returns torch.Tensors)
#     enc = processor(
#         text=batch["text"],
#         sampling_rate=16_000,
#         padding=True, 
#         return_tensors="pt"
#     )
#     # Move them back to plain Python lists for the Dataset
#     batch["input_ids"]      = enc.input_ids.tolist()
#     batch["attention_mask"] = enc.attention_mask.tolist()

#     return batch

# # **batched=True** so that prepare sees lists and returns lists
# ds = ds.map(
#     preprocess,
#     batched=True,
#     # remove_columns=["path","text"],
# )


# # 3) prepare—with truncation!
# def prepare(batch):
#     # raw waveform
#     batch["waveform"] = batch["path"]["array"]
#     # tokenize + truncate to max_length=600
#     tok = processor(
#         text=batch["text"],
#         sampling_rate=16_000,
#         return_tensors="pt",
#         padding="max_length",
#         truncation=True,
#         max_length=600,
#     )
#     batch["input_ids"]      = tok.input_ids[0]
#     batch["attention_mask"] = tok.attention_mask[0]
#     return batch

# ds = ds.map(prepare, remove_columns=["path", "text"])

# # 4) collator
# def collate_fn(batch):
#     input_ids = pad_sequence(
#         [torch.tensor(b["input_ids"],      dtype=torch.long) for b in batch],
#         batch_first=True,
#         padding_value=processor.tokenizer.pad_token_id,
#     )
#     attention_mask = pad_sequence(
#         [torch.tensor(b["attention_mask"], dtype=torch.long) for b in batch],
#         batch_first=True,
#         padding_value=0,
#     )
#     labels = pad_sequence(
#         [torch.tensor(b["waveform"],        dtype=torch.float) for b in batch],
#         batch_first=True,
#     )
#     return {
#         "input_ids":      input_ids,
#         "attention_mask": attention_mask,
#         "labels":         labels,
#     }


# import os
# OUTPUT_ROOT = os.path.join(os.getcwd(), "output")
# os.makedirs(OUTPUT_ROOT, exist_ok=True)

# # 5) training args (no evaluation_strategy if your Transformers is older)
# training_args = TrainingArguments(
#     output_dir                   = OUTPUT_ROOT,
#     per_device_train_batch_size  = 4,
#     num_train_epochs             = 10,
#     fp16                         = True,
#     logging_steps                = 10,
#     save_steps                   = 500,
#     # if you *do* have a recent Transformers (>4.8), you can add:
#     # evaluation_strategy="steps",
#     # eval_steps=200,
# )

# trainer = Trainer(
#     model          = model,
#     args           = training_args,
#     train_dataset  = ds,
#     data_collator  = collate_fn,
# )

# # 6) train!
# trainer.train()

# # 7) save your fine-tuned checkpoint:
# trainer.save_model("/content/yid-speec​ht5-tts-finetuned")
# processor.save_pretrained("/content/yid-speecht5-tts-finetuned")



# from datasets     import load_dataset, Audio
# from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, TrainingArguments, Trainer
# import torch
# from torch.nn.utils.rnn import pad_sequence

# # 1) load your CSV and cast the path column to Audio at 16 kHz
# ds = load_dataset(
#     "csv",
#     data_files={"train": "metadata.csv"},
#     split="train",
#     # column_names=["path","text"]  # only if your CSV has no header
# )
# ds = ds.cast_column("path", Audio(sampling_rate=16_000))


# # 2) load model & processor
# processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
# model     = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")


# # 3) batched preprocessing: always produce lists of input_ids, attention_mask, waveform
# def preprocess(batch):
#     # turn the Audio feature into a list of raw arrays
#     batch["waveform"] = [a["array"] for a in batch["path"]]

#     # tokenize your Yiddish text
#     enc = processor(
#         text=batch["text"],
#         sampling_rate=16_000,
#         padding="longest",
#         truncation=True,
#         max_length=600,
#         return_tensors="pt",
#     )
#     batch["input_ids"]      = enc.input_ids.cpu().tolist()
#     batch["attention_mask"] = enc.attention_mask.cpu().tolist()
#     return batch



# ds = ds.map(
#     preprocess,
#     batched=True,              # crucial!
#     remove_columns=["path","text"],
#     batch_size=8,              # choose sensible batch size
# )
# print(ds.column_names)
# # → ['waveform', 'input_ids', 'attention_mask']
# print(ds[0])
# # → {'waveform': [...], 'input_ids': [...], 'attention_mask': [...]}


# # 4) collate into real tensors

# def collate_fn(batch):
#     input_ids = pad_sequence(
#         [torch.tensor(b["input_ids"],      dtype=torch.long) for b in batch],
#         batch_first=True,
#         padding_value=processor.tokenizer.pad_token_id,
#     )
#     attention_mask = pad_sequence(
#         [torch.tensor(b["attention_mask"], dtype=torch.long) for b in batch],
#         batch_first=True,
#         padding_value=0,
#     )
#     labels = pad_sequence(
#         [torch.tensor(b["waveform"],        dtype=torch.float) for b in batch],
#         batch_first=True,
#     )
#     return {
#         "input_ids":      input_ids,
#         "attention_mask": attention_mask,
#         "labels":         labels,
#     }


# # 5) TrainingArguments & Trainer
# training_args = TrainingArguments(
#     output_dir            = "tts-exp",
#     per_device_train_batch_size = 4,
#     num_train_epochs           = 10,
#     fp16                       = True,
#     logging_steps              = 10,
#     save_steps                 = 500,
# )

# trainer = Trainer(
#     model           = model,
#     args            = training_args,
#     train_dataset   = ds,
#     data_collator   = collate_fn,
# )

# trainer.train()












from datasets import load_dataset, Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, Trainer, TrainingArguments
from torch.nn.utils.rnn import pad_sequence
import torch

# 1) load your CSV (with header “path,text”) and cast to audio@16 kHz
ds = load_dataset("csv", data_files="metadata.csv", split="train")
ds = ds.cast_column("path", Audio(sampling_rate=16_000))

# 2) load model+processor
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model     = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

# 3) single batched preprocess → waveform + tokenized text
def preprocess(batch):
    # pull out list of raw numpy arrays
    batch["waveform"] = [a["array"] for a in batch["path"]]
    # tokenize the Yiddish text:
    enc = processor(
        text=batch["text"],
        sampling_rate=16_000,
        padding="longest",
        truncation=True,
        max_length=600,
        return_tensors="pt",
    )
    # bring back to Python lists so HuggingFace Dataset will keep them
    batch["input_ids"]      = enc.input_ids.cpu().tolist()
    batch["attention_mask"] = enc.attention_mask.cpu().tolist()
    return batch

ds = ds.map(
    preprocess,
    batched=True,
    batch_size=8,                    # tune to your GPU/RAM
    remove_columns=["path", "text"],
)

# sanity check:
print(ds.column_names)  # should be ['waveform','input_ids','attention_mask']
print(ds[0]["waveform"].shape, len(ds[0]["input_ids"]), len(ds[0]["attention_mask"]))

# 4) collator
def collate_fn(batch):
    input_ids = pad_sequence(
        [torch.tensor(b["input_ids"],      dtype=torch.long) for b in batch],
        batch_first=True,
        padding_value=processor.tokenizer.pad_token_id,
    )
    attention_mask = pad_sequence(
        [torch.tensor(b["attention_mask"], dtype=torch.long) for b in batch],
        batch_first=True,
        padding_value=0,
    )
    labels = pad_sequence(
        [torch.tensor(b["waveform"],        dtype=torch.float) for b in batch],
        batch_first=True,
    )
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}

# 5) Trainer
training_args = TrainingArguments(
    output_dir="tts-exp",
    per_device_train_batch_size=4,
    num_train_epochs=10,
    fp16=True,
    logging_steps=10,
    save_steps=500,
    push_to_hub=False,
)

trainer = Trainer(
    model            = model,
    args             = training_args,
    train_dataset    = ds,
    data_collator    = collate_fn,
)

trainer.train()




# 7) save your fine-tuned checkpoint:
trainer.save_model("/content/yid-speec​ht5-tts-finetuned")
processor.save_pretrained("/content/yid-speecht5-tts-finetuned")