"""自动演示脚本。

用法：
    python -m demo.demo            # 跑全部预设场景（自动演示）
    python -m demo.demo --chat     # 进入交互式对话，自己和"小屿"聊

演示会打印每一轮的：用户输入 → 后台分析（风险/情绪/策略）→ 小屿回应。
"""
import argparse
import os
import sys
import time

# 允许以 `python demo/demo.py` 或 `python -m demo.demo` 两种方式运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import CompanionAgent          # noqa: E402
from demo.scenarios import SCENARIOS          # noqa: E402

# ---- 终端着色（无依赖）----
C = {"g": "\033[92m", "b": "\033[94m", "y": "\033[93m",
     "r": "\033[91m", "m": "\033[95m", "d": "\033[90m", "0": "\033[0m",
     "bold": "\033[1m"}


def _c(s, color):
    return f"{C[color]}{s}{C['0']}"


def _risk_color(level):
    return {"none": "g", "low": "y", "medium": "r", "high": "r"}.get(level, "y")


def print_turn(rec, idx):
    print(_c(f"\n  [第{idx}轮] 用户：", "bold") + rec["user_input"])
    risk = rec["risk_level"]
    analysis = (f"    {_c('· 分析', 'd')}  "
                f"风险={_c(risk, _risk_color(risk))}  "
                f"情绪={rec['emotion']}({rec['intensity']}/5)  "
                f"策略={_c(rec['strategy_name'], 'm')}  "
                f"路径={rec['route']}  {rec['latency_s']}s")
    print(analysis)
    if rec.get("strategy_reason"):
        print(_c(f"      选择理由：{rec['strategy_reason']}", "d"))
    print(_c("    小屿：", "g") + rec["response"])


def run_scenarios():
    print(_c("\n" + "=" * 68, "b"))
    print(_c("  心理陪伴智能体「小屿」 —— 自动演示（DeepSeek + LangGraph）", "bold"))
    print(_c("=" * 68, "b"))
    for s in SCENARIOS:
        print(_c(f"\n\n▉ {s['title']}", "b"))
        print(_c(f"  {s['desc']}", "d"))
        # 每个场景独立会话，保留多轮记忆
        agent = CompanionAgent(thread_id=s["id"])
        for i, turn in enumerate(s["turns"], 1):
            rec = agent.chat(turn)
            print_turn(rec, i)
            time.sleep(0.3)
        print(_c(f"\n  ✔ 场景完成，调用记录已写入 logs/{s['id']}.jsonl", "d"))
    print(_c("\n\n全部演示完成。可运行 `python -m evaluation.evaluate` 查看自动评测。\n", "bold"))


def run_chat():
    print(_c("进入交互模式（输入 exit 退出）。我是小屿，随便聊聊吧～\n", "g"))
    agent = CompanionAgent(thread_id="interactive")
    while True:
        try:
            text = input(_c("你：", "bold")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in ("exit", "quit", "q", ""):
            break
        rec = agent.chat(text)
        tag = _c(f"[风险{rec['risk_level']}/{rec['strategy_name']}]", "d")
        print(_c("小屿：", "g") + rec["response"] + "  " + tag + "\n")
    print(_c("\n再见，照顾好自己。", "g"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat", action="store_true", help="交互式对话模式")
    args = ap.parse_args()
    if args.chat:
        run_chat()
    else:
        run_scenarios()
