import requests
import json
import time
import os
import glob

# 配置参数
API_KEY = "sk-b9fb0bfdb44e4d51a174c61365f18724"  # 在 https://platform.deepseek.com 获取
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"  # 或 "deepseek-coder"（若需代码相关翻译）


# 读取小说章节（假设是 txt 文件）
def read_chapter(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# 智能分段翻译（避免超出 token 限制）
def translate_text(text, max_chunk_length=10000):
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    translated_chunks = []

    for chunk in chunks:
        prompt = f"""
        你是一位专业文学翻译家。请将以下中文小说章节精准翻译为英文，要求：
        1. 保留原文风格（如古风、口语化等）
        2. 人名/地名保持拼音或约定俗成的英文名
        3. 对话部分使用自然英语口语
        4. 文化专有词适当意译
        5. 章节标题单独翻译并标注

        待翻译内容：
        {chunk}
        """

        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3  # 降低随机性，提高一致性
            }
        )

        if response.status_code == 200:
            result = response.json()
            translated = result['choices'][0]['message']['content']
            translated_chunks.append(translated)
            print(f"✅ 已翻译 {len(chunk)} 字符")
        else:
            print(f"❌ 翻译失败: {response.text}")

        time.sleep(1.2)  # 避免请求过快被限流

    return "\n\n".join(translated_chunks)




# 主流程
if __name__ == "__main__":
    # book_id = "1043294775"
    # chapter_text = read_chapter(f"data/book/{book_id}/list/0.txt")  # 你的小说章节文件
    # translated_text = translate_text(chapter_text)
    #
    #
    #
    # # 保存翻译结果
    # with open(f"data/book/{book_id}/list2/0.txt", "w", encoding="utf-8") as f:
    #     f.write(translated_text)
    #
    # print("🎉 章节翻译完成！已保存至 0.txt")

    book_id = "1043294775"
    # 转换前中文目录
    list_dir = f"data/book/{book_id}/list"
    # 转换后英文目录
    list2_dir = f"data/book/{book_id}/list2"

    # 确保输出目录存在
    os.makedirs(list2_dir, exist_ok=True)

    # 获取所有txt文件
    txt_files = glob.glob(os.path.join(list_dir, "*.txt"))

    if not txt_files:
        print("未找到任何txt文件")
        exit()

    # 遍历并翻译所有文件
    for file_path in txt_files:
        file_name = os.path.basename(file_path)
        print(f"正在处理文件: {file_name}")

        # 读取章节内容
        try:
            chapter_text = read_chapter(file_path)
        except Exception as e:
            print(f"读取文件 {file_name} 失败: {e}")
            continue

        # 翻译文本
        translated_text = translate_text(chapter_text)

        if translated_text is not None:
            # 保存翻译结果
            output_path = os.path.join(list2_dir, file_name)
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(translated_text)
                print(f"🎉 文件 {file_name} 翻译完成！已保存至 {output_path}")
            except Exception as e:
                print(f"保存文件 {file_name} 失败: {e}")
        else:
            print(f"❌ 文件 {file_name} 翻译失败")