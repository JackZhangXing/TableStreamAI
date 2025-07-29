import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# 选择适合您显存的模型大小，例如"medium"
model_id = "openai/whisper-small"

# 启用半精度以节省显存
processor = WhisperProcessor.from_pretrained(model_id)
model = WhisperForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 确保模型在GPU上运行
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)