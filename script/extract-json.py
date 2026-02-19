#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史事件提取脚本
功能：将文本切片后发送给DeepSeek API，按指定JSON格式整理历史事件
"""

import json
import time
import requests
from typing import List, Dict, Optional
import os

# ==================== 配置区域 ====================
# 请在此处填写您的 DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"  # 或 deepseek-reasoner

# 文本切片配置
CHUNK_SIZE = 2000  # 每片文本的最大字符数
CHUNK_OVERLAP = 200  # 切片重叠字符数（避免信息被切断）

# API请求配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试等待时间（秒）
REQUEST_TIMEOUT = 60  # 请求超时时间（秒）


# ==================================================


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    将长文本切片，保留重叠部分避免信息丢失

    Args:
        text: 输入文本
        chunk_size: 每片最大字符数
        overlap: 重叠字符数

    Returns:
        切片后的文本列表
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # 如果不是最后一片，尝试在句子边界处切分
        if end < text_length:
            # 寻找最近的句号、换行等作为切分点
            split_point = -1
            for sep in ['。\n', '。\n\n', '\n\n', '。\n-', '\n-']:
                pos = text.rfind(sep, start, end)
                if pos > start + chunk_size // 2:
                    split_point = pos + len(sep)
                    break

            if split_point == -1:
                for sep in ['。', '！', '？', '\n']:
                    pos = text.rfind(sep, start, end)
                    if pos > start + chunk_size // 2:
                        split_point = pos + 1
                        break

            if split_point > -1:
                end = split_point

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # 移动起始位置，保留重叠部分
        start = end - overlap if end < text_length else text_length

    return chunks


def call_deepseek_api(messages: List[Dict], api_key: str = DEEPSEEK_API_KEY) -> Optional[str]:
    """
    调用 DeepSeek API

    Args:
        messages: 消息列表
        api_key: API密钥

    Returns:
        API返回的文本内容，失败则返回None
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,  # 较低温度使输出更稳定
        "max_tokens": 4096,
        "response_format": {"type": "json_object"}  # 强制JSON格式输出
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if content:
                return content

            print(f"⚠️  第{attempt + 1}次请求返回空内容")

        except requests.exceptions.RequestException as e:
            print(f"⚠️  第{attempt + 1}次请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"⚠️  第{attempt + 1}次响应解析失败: {str(e)}")
        except Exception as e:
            print(f"⚠️  第{attempt + 1}次请求异常: {str(e)}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避

    return None


def build_system_prompt() -> str:
    """构建系统提示词"""
    return """你是一个专业的历史事件整理助手。请仔细阅读输入文本，提取其中的历史事件信息，并严格按照以下JSON格式输出：

输出格式要求：
- 必须输出有效的JSON数组
- 每个事件对象包含以下字段：
  - date: 日期，格式为 "YYYY-MM-DD"，如果日期不完整则尽量推断
  - time: 24小时制时间，整数（0-23），如果不明确则填12
  - event: 事件简写，简洁明了
  - description: 具体描述，详细说明事件经过
  - mood: 心情，描述当时人物的情绪状态，多个情绪用顿号分隔
  - impact: 影响力，只能是"低"、"中"、"高"之一
  - historical_context: 历史背景，说明事件发生的历史环境

注意事项：
1. 只输出JSON数组，不要有任何其他文字说明
2. 如果文本中没有明确的历史事件，返回空数组 []
3. 确保所有字段都存在且格式正确
4. 日期格式必须统一为 YYYY-MM-DD
5. 描述要客观准确，基于文本内容"""


def build_user_prompt(chunk: str, chunk_index: int, total_chunks: int) -> str:
    """构建用户提示词"""
    return f"""请分析以下文本片段（第{chunk_index + 1}/{total_chunks}片），提取其中的历史事件：

---文本开始---
{chunk}
---文本结束---

请严格按照JSON数组格式输出提取的事件信息。"""


def parse_json_response(response_text: str) -> List[Dict]:
    """
    解析API返回的JSON响应

    Args:
        response_text: API返回的文本

    Returns:
        解析后的事件列表
    """
    # 尝试直接解析
    try:
        # 清理可能的markdown标记
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        # 确保是列表
        if isinstance(data, dict):
            # 尝试从常见键名获取列表
            for key in ["events", "data", "result", "items"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []

    except json.JSONDecodeError as e:
        print(f"⚠️  JSON解析失败: {str(e)}")
        return []


def process_text(text: str, api_key: str = DEEPSEEK_API_KEY) -> List[Dict]:
    """
    处理完整文本，提取所有历史事件

    Args:
        text: 输入文本
        api_key: API密钥

    Returns:
        所有提取的事件列表
    """
    # 切片
    chunks = split_text(text)
    print(f"📄 文本已切分为 {len(chunks)} 片")

    all_events = []
    system_prompt = build_system_prompt()

    for i, chunk in enumerate(chunks):
        print(f"🔄 处理第 {i + 1}/{len(chunks)} 片...")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_prompt(chunk, i, len(chunks))}
        ]

        response = call_deepseek_api(messages, api_key)

        if response:
            events = parse_json_response(response)
            all_events.extend(events)
            print(f"✅ 提取到 {len(events)} 个事件")
        else:
            print(f"❌ 第 {i + 1} 片处理失败")

        # 避免API限流
        if i < len(chunks) - 1:
            time.sleep(1)

    # 去重（基于date和event）
    seen = set()
    unique_events = []
    for event in all_events:
        key = (event.get("date", ""), event.get("event", ""))
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    print(f"📊 去重后共 {len(unique_events)} 个事件")
    return unique_events


def save_results(events: List[Dict], output_file: str = "events_output.json"):
    """保存结果到文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"💾 结果已保存到 {output_file}")


def main():
    """主函数"""
    # 检查API Key
    if DEEPSEEK_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 错误：请设置 DEEPSEEK_API_KEY 环境变量或在脚本中填写您的API Key")
        print("   获取API Key: https://platform.deepseek.com/")
        return

    # 示例文本（可替换为从文件读取）
    # sample_text = """
    # 1949年10月1日下午3点整，毛泽东在天安门城楼上向全世界庄严宣告：
    # "中华人民共和国中央人民政府今天成立了！"这一刻标志着中国人民从此站起来了。
    #
    # 1948年9月12日，辽沈战役发起，这是解放战争中三大战役的第一场。
    #
    # 1945年8月15日，日本宣布无条件投降，抗日战争取得胜利。
    # """

    # 或者从文件读取
    with open("D:/what-was-he-doing-in-the-past/script/book/maozedong.txt", "r", encoding="utf-8") as f:
        sample_text = f.read()

    print("🚀 开始处理文本...")
    events = process_text(sample_text)

    if events:
        save_results(events)
        print("\n📋 提取的事件预览:")
        print(json.dumps(events[:2], ensure_ascii=False, indent=2))
    else:
        print("⚠️  未提取到任何事件")


if __name__ == "__main__":
    main()