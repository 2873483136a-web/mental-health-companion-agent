"""LangGraph 节点实现。

对话一轮的处理流程：
    analyze  →  (条件路由)
                 ├─ 普通:  generate_response
                 └─ 危机:  crisis_response

analyze 节点一次 LLM 调用完成【风险评估 + 情绪识别 + 策略选择】，
既是安全阀（任务目标2），也是策略选择机制（任务目标3）。
"""
import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .config import analysis_llm, chat_llm
from .prompts import (ANALYZE_SYSTEM, build_crisis_system,
                      build_response_system)
from .state import AgentState
from .strategies import DEFAULT_STRATEGY, STRATEGIES, get_strategy


def _history_text(messages, limit: int = 8) -> str:
    """把最近的对话历史渲染成文本，供分析节点参考上下文。"""
    recent = messages[-limit:] if messages else []
    lines = []
    for m in recent:
        role = "用户" if isinstance(m, HumanMessage) else "小屿"
        lines.append(f"{role}：{m.content}")
    return "\n".join(lines) if lines else "（无历史）"


def analyze(state: AgentState) -> AgentState:
    """结构化分析：风险 + 情绪 + 策略。"""
    user_input = state["user_input"]
    history = _history_text(state.get("messages", []))
    prompt = (
        f"{ANALYZE_SYSTEM}\n\n【对话历史】\n{history}\n\n"
        f"【用户最新一句话】\n{user_input}"
    )
    raw = analysis_llm().invoke(prompt).content
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # 兜底：解析失败时保守处理为低风险 + 默认共情策略
        data = {}

    risk_level = data.get("risk_level", "low")
    if risk_level not in ("none", "low", "medium", "high"):
        risk_level = "low"
    strategy = data.get("strategy", DEFAULT_STRATEGY)
    if strategy not in STRATEGIES:
        strategy = DEFAULT_STRATEGY

    return {
        "risk_level": risk_level,
        "risk_reason": data.get("risk_reason", ""),
        "emotion": data.get("emotion", "未知"),
        "intensity": int(data.get("intensity", 3) or 3),
        "strategy": strategy,
        "strategy_reason": data.get("strategy_reason", ""),
    }


def route_after_analyze(state: AgentState) -> str:
    """条件路由：中/高风险走危机干预，其余走普通回应。"""
    return "crisis" if state.get("risk_level") in ("medium", "high") else "normal"


def generate_response(state: AgentState) -> AgentState:
    """普通路径：按选定策略生成有温度的回应。"""
    strat = get_strategy(state["strategy"])
    system = build_response_system(
        strategy_name=strat.name,
        strategy_guidance=strat.guidance,
        emotion=state.get("emotion", "未知"),
        intensity=state.get("intensity", 3),
    )
    msgs = [SystemMessage(content=system)]
    msgs += state.get("messages", [])
    msgs.append(HumanMessage(content=state["user_input"]))
    reply = chat_llm().invoke(msgs).content

    return {
        "response": reply,
        "route": "normal",
        "messages": [HumanMessage(content=state["user_input"]),
                     AIMessage(content=reply)],
    }


def crisis_response(state: AgentState) -> AgentState:
    """危机路径：危机干预 + 转介专业资源。"""
    system = build_crisis_system(state.get("risk_level", "high"))
    msgs = [SystemMessage(content=system)]
    msgs += state.get("messages", [])
    msgs.append(HumanMessage(content=state["user_input"]))
    reply = chat_llm().invoke(msgs).content

    return {
        "response": reply,
        "route": "crisis",
        "messages": [HumanMessage(content=state["user_input"]),
                     AIMessage(content=reply)],
    }
