"""对外的高层接口：CompanionAgent。

封装 LangGraph 图，提供：
- chat(text): 单轮对话，返回结构化结果（回应 + 本轮分析）
- 会话级多轮记忆（thread_id）
- 每轮调用记录写入 logs/*.jsonl（对应提交要求：调用记录）
"""
import json
import os
import time
import uuid
from datetime import datetime
from typing import Optional

from .graph import build_graph
from .strategies import get_strategy

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


class CompanionAgent:
    def __init__(self, thread_id: Optional[str] = None, log: bool = True):
        self.app = build_graph(with_memory=True)
        self.thread_id = thread_id or f"session-{uuid.uuid4().hex[:8]}"
        self.log = log
        if log:
            os.makedirs(LOG_DIR, exist_ok=True)
            self.log_path = os.path.join(LOG_DIR, f"{self.thread_id}.jsonl")

    def chat(self, text: str) -> dict:
        config = {"configurable": {"thread_id": self.thread_id}}
        t0 = time.time()
        result = self.app.invoke({"user_input": text}, config=config)
        elapsed = round(time.time() - t0, 2)

        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "thread_id": self.thread_id,
            "user_input": text,
            "response": result.get("response", ""),
            "route": result.get("route"),
            "risk_level": result.get("risk_level"),
            "risk_reason": result.get("risk_reason"),
            "emotion": result.get("emotion"),
            "intensity": result.get("intensity"),
            "strategy": result.get("strategy"),
            "strategy_name": get_strategy(result.get("strategy", "empathy")).name,
            "strategy_reason": result.get("strategy_reason"),
            "latency_s": elapsed,
        }
        if self.log:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record
