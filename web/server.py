"""网页版可视化界面后端（FastAPI）。

复用 src.agent.CompanionAgent，为每个会话(thread_id)保留一个带记忆的智能体实例。
提供：
    GET  /            → 返回单页前端
    POST /api/chat    → {message, thread_id?} -> 完整结构化结果（回应+本轮分析）
    POST /api/reset   → 开启新会话

启动：
    python -m web.server        （默认 http://127.0.0.1:8000）
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI                       # noqa: E402
from fastapi.responses import FileResponse         # noqa: E402
from fastapi.staticfiles import StaticFiles        # noqa: E402
from pydantic import BaseModel                     # noqa: E402

from src.agent import CompanionAgent               # noqa: E402
from src.strategies import STRATEGIES              # noqa: E402

app = FastAPI(title="心理陪伴智能体「小屿」")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# thread_id -> CompanionAgent（进程内会话记忆）
_AGENTS: dict = {}


def _get_agent(thread_id: str) -> CompanionAgent:
    if thread_id not in _AGENTS:
        _AGENTS[thread_id] = CompanionAgent(thread_id=thread_id)
    return _AGENTS[thread_id]


class ChatIn(BaseModel):
    message: str
    thread_id: str = ""


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/strategies")
def strategies():
    """给前端展示策略图例。"""
    return [{"key": s.key, "name": s.name, "when": s.when}
            for s in STRATEGIES.values()]


@app.post("/api/chat")
def chat(inp: ChatIn):
    thread_id = inp.thread_id or f"web-{uuid.uuid4().hex[:8]}"
    agent = _get_agent(thread_id)
    rec = agent.chat(inp.message)
    rec["thread_id"] = thread_id
    return rec


@app.post("/api/reset")
def reset():
    return {"thread_id": f"web-{uuid.uuid4().hex[:8]}"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n  心理陪伴智能体「小屿」网页界面： http://{host}:{port}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
