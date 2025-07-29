import os
from pathlib import Path


# os.getcwd()
# print(os.getcwd())

# audio_path = "/data/book/1043294775/audio/0/1.mp3"
# windows_path = Path(audio_path)
# print(windows_path)



audio_path = '/data/book/1043294775/audio/0/1.mp3'
base_path = 'E:\\code\\TaleStreamAI\\app'  # 或 r'E:\code\TaleStreamAI\app'

# # 移除audio_path开头的斜杠，确保它是相对路径
# relative_audio_path = audio_path.lstrip('/')
# # 拼接路径
# full_path = os.path.join(base_path, relative_audio_path)
# print(full_path)

# 移除audio_path开头的斜杠
relative_audio_path = audio_path.lstrip('/')

# 使用Path对象拼接路径
full_path = Path(base_path) / relative_audio_path

print(full_path)