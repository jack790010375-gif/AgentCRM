"""大模型配置（第7步）：从 .env 读取密钥，初始化模型，绑定工具。"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 读取 .env 文件
load_dotenv()


def get_llm() -> ChatOpenAI:
    """初始化大模型。"""
    return ChatOpenAI(
        api_key=os.getenv("MODEL_API_KEY"),
        model=os.getenv("MODEL_NAME"),
        base_url=os.getenv("MODEL_BASE_URL"),
        temperature=0,  # 温度设为0，让模型尽量稳定、不胡说
    )


def get_llm_with_tools(tools: list) -> ChatOpenAI:
    """初始化大模型并绑定工具。"""
    llm = get_llm()
    return llm.bind_tools(tools)
