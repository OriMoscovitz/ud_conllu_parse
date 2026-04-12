import torch
from utils import _read_jsonl
from datasets import Dataset

path = "../../../../data/UD_English-EWT/en_ewt-ud-train_conv.jsonl"

#print(_read_jsonl(path))

print(Dataset.from_list(_read_jsonl(path)))