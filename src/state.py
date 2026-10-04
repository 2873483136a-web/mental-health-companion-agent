"""LangGraph 状态定义。"""
from typing import List, Literal, TypedDict
from typing_extensions import Annotated

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    # 完整对话历史（HumanMessage / AIMessage），使用 add_messages 累加
    messages: Annotated[list, add_messages]
    # 用户最新输入
    user_input: str
    # 分析结果
    risk_level: Literal["none", "low", "medium", "high"]
    risk_reason: str
    emotion: str
    intensity: int
    strategy: str          # 策略 key
    strategy_reason: str
    # 生成的回应
    response: str
    # 本轮走的路径（normal / crisis），便于可视化与评测
    route: str
