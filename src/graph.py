"""LangGraph 图的组装。

    START → analyze → ┬─(normal)→ generate_response → END
                      └─(crisis)→ crisis_response    → END
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes import (analyze, crisis_response, generate_response,
                    route_after_analyze)
from .state import AgentState


def build_graph(with_memory: bool = True):
    g = StateGraph(AgentState)
    g.add_node("analyze", analyze)
    g.add_node("generate_response", generate_response)
    g.add_node("crisis_response", crisis_response)

    g.add_edge(START, "analyze")
    g.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {"normal": "generate_response", "crisis": "crisis_response"},
    )
    g.add_edge("generate_response", END)
    g.add_edge("crisis_response", END)

    # 用 MemorySaver 保存多轮对话状态（按 thread_id 区分会话）
    checkpointer = MemorySaver() if with_memory else None
    return g.compile(checkpointer=checkpointer)
