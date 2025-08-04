from openai import OpenAI
import json
import os
import re
import concurrent.futures
import threading
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()


# 用于线程安全的打印
print_lock = threading.Lock()


def safe_print(message):
    with print_lock:
        print(message)


prompt = """
StableDiffusion是一款利用深度学习的文生图模型，支持通过使用提示词来产生新的图像，描述要包含或省略的元素。
我在这里引入StableDiffusion算法中的Prompt概念，又被称为提示符。
下面的prompt是用来指导AI绘画模型创作图像的。它们包含了图像的各种细节，如人物的外观、背景、颜色和光线效果，以及图像的主题和风格。这些prompt的格式经常包含括号内的加权数字，用于指定某些细节的重要性或强调。例如，"(masterpiece:1.5)"表示作品质量是非常重要的，多个括号也有类似作用。此外，如果使用中括号，如"{blue hair:white hair:0.3}"，这代表将蓝发和白发加以融合，蓝发占比为0.3。
以下是用prompt帮助AI模型生成图像的例子：masterpiece,(bestquality),highlydetailed,ultra-detailed,cold,solo,(1girl),(detailedeyes),(shinegoldeneyes),(longliverhair),expressionless,(long sleeves),(puffy sleeves),(white wings),shinehalo,(heavymetal:1.2),(metaljewelry),cross-lacedfootwear (chain),(Whitedoves:1.2)
需要多增加一些漫画风格以及漫画的细节的关键词进来

仿照例子，给出一套详细描述以下内容的prompt。直接开始给出prompt不需要用自然语言描述不要出现人名不要使用中文：
"""

# prompt = """
# StableDiffusion是一款利用深度学习的文生图模型，支持通过使用提示词来产生新的图像，描述要包含或省略的元素。
# 一、核心结构框架（中英对照）：
#
# 画面质量设定：
# -(masterpiece, best quality, ultra-detailed, 8k resolution)
# -(杰作，最高品质，超精细，8K分辨率)
#
# 风格定位（关键部分）：
# a) 通用日系动漫：
# (anime style, official art, vibrant colors, cel-shading)
#
# b) 赛璐璐经典风：
# (90s anime, cel animation, hand-painted look, film grain)
#
# c) 现代二次元：
# (modern anime, Pixiv trend, semi-realistic eyes, soft lighting)
#
# 角色描述系统：
#
# 外貌：(slender body, asymmetrical hair, gradient eyes)
#
# 服装：(school uniform with sailor collar, pleated skirt)
#
# 动态：(dynamic pose, hair fluttering, flying petals)
#
# 场景增强系统：
#
# 背景：(cherry blossom park, bokeh lights, depth of field)
#
# 特效：(lens flare, light particles, glowing outline)
#
# 天气：(golden hour, sunbeam through leaves)
#
# 二、风格化参数建议：
#
# 新海诚风：
# (sky-blue palette, atmospheric perspective, hyper-detailed clouds, radiant lighting)
#
# 吉卜力风：
# (watercolor texture, pastoral landscape, European architecture, whimsical creatures)
#
# 赛博朋克：
# (neon lights, holographic UI, rain reflections, cybernetic implants)
#
# 三、进阶控制参数（Negative prompt示例）：
# lowres, bad anatomy, extra digits, blurry, ((duplicate)), (poorly drawn hands), mutation
#
# 四、完整示例模板：
# "(((masterpiece))), ((best quality)), anime key visual,
# character design sheet style,
# sakura pink hair with blue streaks,
# heterochromatic eyes (amber/emerald),
# futuristic kimono with led patterns,
# standing on floating shrine stairs,
# background of neon Tokyo skyline at dusk,
# volumetric light rays,
# Studio Trigger color palette,
# animated GIF style frame edges"
#
# 五、风格切换关键词库：
#
# 萌系：chibi proportion, sparkle eyes, pastel colors
#
# 热血系：speed lines, dramatic perspective, impact frames
#
# 黑暗系：gothic lolita, blood moon, ominous glow
#
# 六、专业建议：
#
# 使用权重控制：如 (sunset:1.3) 或 [clouds:0.8]
#
# 添加艺术媒介暗示：concept art, illustration board, matte painting
#
# 引用知名工作室风格：Ufotable shading, Kyoto Animation lighting
#
# 需要生成特定子风格时，可以提供以下信息：
#
# 期望的时代特征（80s/2000s等）
#
# 具体参考作品/画师
#
# 特殊材质需求（水彩/厚涂等）
#
# 画面情感基调（忧郁/欢快等）
#
# 必须为 2D 平面动画风格
#
# 仿照例子，给出一套详细描述以下内容的prompt。直接开始给出prompt不需要用自然语言描述不要出现人名不要使用中文：
# """

# prompt = """
# StableDiffusion is a text-to-image model that utilizes deep learning and supports generating new images by using prompt words to describe the elements to be included or omitted.
# Here I introduce the concept of Prompt in the StableDiffusion algorithm, which is also known as a prompt.
# The following prompt is used to guide the AI painting model in creating images. They contain various details of the image, such as the appearance of the characters, the background, colors and lighting effects, as well as the theme and style of the image. The format of these prompts often contains weighted numbers within parentheses to specify the importance or emphasis of certain details. For example, "(masterpiece:1.5)" indicates that the quality of the work is very important, and multiple parentheses have a similar function. Furthermore, if square brackets are used, such as "{blue hair:white hair:0.3}", this represents the fusion of blue hair and white hair, with the proportion of blue hair being 0.3.
# The following are examples of using prompts to help AI models generate images: masterpiece,(bestquality),highlydetailed,ultra-detailed,cold,solo,(1girl),(detailedeyes),(shinegoldeneyes),(longliverhai r),expressionless,(long sleeves),(puffy sleeves),(white  wings,shinehalo,(heavymetal:1.2),(metaljewelry), Cross-laced footwear (chain),(Whitedoves:1.2)
# More keywords related to comic styles and details need to be added
#
# Following the example, provide a set of prompts that describe the following content in detail. Start giving the prompt directly. No need to describe in natural language. Do not use names. Do not use Chinese
# """


# 创建OpenAI客户端
def create_client():
    return OpenAI(
        api_key=os.getenv("AL_API_KEY"),
        base_url=os.getenv("AL_API_URL"),
    )


# 润色提示词
def refine_prompt(text: str, board_info: str, client=None) -> str:
    global prompt
    if client is None:
        client = create_client()

    # _text = f"""
    #     以下是小说分镜音频文案：{text}
    #     以下是小说分镜关键字：{board_info}
    #     这是一本漫画小说
    # """

    _text = f"""
            The following is the audio copy for the storyboard of the novel:{text}
            The following are the key words for the storyboard of the novel:{board_info}
            This is a comic novel
        """

    try:
        response = client.chat.completions.create(
            model="deepseek-v3",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": _text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        safe_print(f"API调用失败: {e}")
        raise


# 处理分镜文本的异常
def handle_board_text_exception(text: str) -> str:
    # 如果text中包含\n，则将\n替换为空
    text = text.replace("\n", "")
    # 如果text中包含\r，则将\r替换为空
    text = text.replace("\r", "")
    # 如果text中包含\t，则将\t替换为空
    text = text.replace("\t", "")
    # 如果text中包含多个连续空格，则将多个空格替换为空
    text = re.sub(r"\s+", " ", text)
    return text


# 处理单个分镜对象
def process_single_item(item, client):
    item_id = item.get("id", "未知")


    # 检查是否已处理过（已有lensLanguage_end字段）  ai优化后图形生成提示词
    if "lensLanguage_end" in item and item["lensLanguage_end"]:
        safe_print(f"跳过已处理的ID: {item_id}")
        return item, "skipped"

    # 预处理文本
    original_text = item.get("text", "")
    processed_text = handle_board_text_exception(original_text)
    item["text"] = processed_text

    # 生成优化的提示词
    try:
        lens_language = refine_prompt(processed_text, processed_text, client)
        item["lensLanguage_end"] = lens_language
        return item, "success"
    except Exception as e:
        # 处理失败时，使用lensLanguage_en的值作为备选
        if "lensLanguage_en" in item and item["lensLanguage_en"]:
            item["lensLanguage_end"] = item["lensLanguage_en"]
            safe_print(f"处理ID: {item_id} 时出错，使用lensLanguage_en作为备选")
            return item, "fallback"
        else:
            safe_print(f"处理ID: {item_id} 时出错，且无可用的lensLanguage_en: {e}")
            return item, "error"


# 处理单个章节文件
def process_chapter_file(chapter_file_path, max_workers=10):
    try:
        # 读取文件内容
        with open(chapter_file_path, "r", encoding="utf-8") as f:
            board_info = json.load(f)

        # 创建客户端
        client = create_client()

        # 使用线程池处理每个对象
        processed_items = []
        result_stats = {"success": 0, "fallback": 0, "error": 0, "skipped": 0}
        total_items = len(board_info)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(process_single_item, item, client): item
                for item in board_info
            }

            # 处理结果，使用tqdm显示进度
            for future in tqdm(
                concurrent.futures.as_completed(future_to_item),
                total=total_items,
                desc=f"处理 {os.path.basename(chapter_file_path)}",
            ):
                item_result, status = future.result()
                processed_items.append(item_result)
                result_stats[status] += 1

        # 写回文件
        with open(chapter_file_path, "w", encoding="utf-8") as f:
            json.dump(processed_items, f, ensure_ascii=False, indent=2)

        safe_print(f"已完成文件 {os.path.basename(chapter_file_path)} 的处理")
        safe_print(
            f"统计: 成功={result_stats['success']}, 使用备选={result_stats['fallback']}, 错误={result_stats['error']}, 跳过={result_stats['skipped']}"
        )
        return True
    except Exception as e:
        safe_print(f"处理文件 {os.path.basename(chapter_file_path)} 时出错: {e}")
        return False


# 多线程处理所有分镜文件
def process_board_files(book_id: str, file_threads=5, item_threads=10) -> None:
    # 读取 data/book/{book_id}/storyboard/*.json
    storyboard_dir = f"data/book/{book_id}/storyboard"
    if not os.path.exists(storyboard_dir):
        print(f"目录不存在: {storyboard_dir}")
        return

    # 按文件名排序
    chapter_files = os.listdir(storyboard_dir)
    chapter_files.sort(key=lambda x: int(x.split(".")[0]))
    chapter_file_paths = [os.path.join(storyboard_dir, f) for f in chapter_files]

    # 使用线程池处理文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=file_threads) as executor:
        # 提交所有任务
        futures = [
            executor.submit(process_chapter_file, path, item_threads)
            for path in chapter_file_paths
        ]

        # 处理结果
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                result = future.result()
                if result:
                    safe_print(f"成功处理文件 {i+1}/{len(chapter_files)}")
                else:
                    safe_print(f"处理文件失败 {i+1}/{len(chapter_files)}")
            except Exception as e:
                safe_print(f"处理文件时发生异常: {e}")


if __name__ == "__main__":
    book_id = "1043294775"  # 可以作为参数传入
    # 设置文件级别的线程数和处理每个文件内分镜的线程数
    file_threads = 2  # 同时处理的文件数
    item_threads = 10  # 每个文件内同时处理的分镜对象数
    process_board_files(book_id, file_threads, item_threads)
