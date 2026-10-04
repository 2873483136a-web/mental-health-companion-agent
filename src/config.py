"""LLM 与全局配置。

统一从 .env 读取 DeepSeek 配置，提供两种温度的 LLM 实例：
- analysis_llm: 低温度，用于风险/情绪/策略等结构化分析（要求稳定、确定）
- chat_llm:     较高温度，用于生成有温度的自然回应

关于 SSL：
macOS 自带/Xcode 的 Python 常常找不到 CA 证书（报 CERTIFICATE_VERIFY_FAILED），
这里统一用 certifi 的证书包解决。若身处会做 TLS 拦截的公司代理网络，可：
  · 在 .env 里设 DEEPSEEK_CA_BUNDLE=/path/to/公司根证书.pem  （推荐）
  · 或临时设 DEEPSEEK_VERIFY_SSL=false 关闭校验（仅本地调试用，不安全）
"""
import os
from functools import lru_cache

import certifi
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_CA_BUNDLE = os.getenv("DEEPSEEK_CA_BUNDLE", "").strip()
DEEPSEEK_VERIFY_SSL = os.getenv("DEEPSEEK_VERIFY_SSL", "true").strip().lower()


def _resolve_verify():
    """决定 httpx 的 verify 取值：自定义 CA > 关闭校验 > certifi 默认。"""
    if DEEPSEEK_CA_BUNDLE and os.path.exists(DEEPSEEK_CA_BUNDLE):
        return DEEPSEEK_CA_BUNDLE
    if DEEPSEEK_VERIFY_SSL in ("false", "0", "no"):
        return False
    return certifi.where()


# 让底层 requests/urllib 等也能找到证书
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())


@lru_cache(maxsize=None)
def _http_client() -> httpx.Client:
    verify = _resolve_verify()
    if verify is False:
        # 关闭校验时消掉 httpx 的告警噪音
        import warnings
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    return httpx.Client(verify=verify, timeout=60)


@lru_cache(maxsize=None)
def get_llm(temperature: float = 0.7, json_mode: bool = False) -> ChatOpenAI:
    """返回一个 DeepSeek(OpenAI 兼容) LLM 实例。

    json_mode=True 时强制模型输出 JSON 对象，用于结构化分析节点。
    """
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未检测到 DEEPSEEK_API_KEY，请在 .env 中配置。")
    kwargs = {
        "model": DEEPSEEK_MODEL,
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_BASE_URL,
        "temperature": temperature,
        "timeout": 60,
        "max_retries": 2,
        "http_client": _http_client(),
    }
    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
    return ChatOpenAI(**kwargs)


def analysis_llm() -> ChatOpenAI:
    """结构化分析用：低温度 + JSON 输出。"""
    return get_llm(temperature=0.0, json_mode=True)


def chat_llm() -> ChatOpenAI:
    """对话生成用：保留温度以获得自然、有共情感的语言。"""
    return get_llm(temperature=0.7, json_mode=False)
