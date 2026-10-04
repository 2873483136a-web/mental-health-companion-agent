"""心理沟通策略库。

参考心理咨询面谈中的常用技术，将其抽象为可被智能体"按场景选择"的策略。
每个策略包含：名称、适用场景、对生成回应的具体指导（写进生成提示词）。
策略选择机制（见 nodes.select_strategy）会根据用户情绪/意图，从这里挑选 1 个主策略。
"""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Strategy:
    key: str
    name: str          # 中文名
    when: str          # 适用场景（供 LLM 选择时判断）
    guidance: str      # 生成回应时的具体行为指导


STRATEGIES: Dict[str, Strategy] = {
    "empathy": Strategy(
        key="empathy",
        name="共情与情感确认",
        when="用户表达了明显的负面情绪（难过、焦虑、委屈、孤独），需要先被理解和接纳。",
        guidance="先准确命名并确认对方的情绪，让其感到'被看见'；不急于给建议或讲道理。",
    ),
    "active_listening": Strategy(
        key="active_listening",
        name="倾听与反映",
        when="用户在叙述事情经过、倾诉，尚未表达清晰的诉求。",
        guidance="用自己的话简要复述/总结对方所说的关键内容与感受，表明你在认真听，鼓励其继续说。",
    ),
    "open_question": Strategy(
        key="open_question",
        name="开放式提问",
        when="用户表达意愿不足、信息笼统，需要温和引导其展开、澄清具体情境。",
        guidance="提出 1 个开放、具体、低压力的问题（避免连环追问），帮助对方进一步表达，问题要顺着对方刚说的内容。",
    ),
    "emotional_support": Strategy(
        key="emotional_support",
        name="情绪支持与鼓励",
        when="用户情绪已被接纳，处于自我怀疑/无力状态，需要被肯定和支持。",
        guidance="给予真诚的肯定与陪伴，指出对方已经做出的努力或展现的力量；传递'你并不孤单'，但不空洞地喊口号。",
    ),
    "reframe": Strategy(
        key="reframe",
        name="认知重构（温和）",
        when="用户存在明显的绝对化/灾难化想法（如'我一无是处''完了'），且情绪已相对稳定。",
        guidance="在充分共情的前提下，温和地提供另一种看待角度，用探讨而非说教的口吻，尊重对方是否接受。",
    ),
    "explore_resource": Strategy(
        key="explore_resource",
        name="资源与应对探索",
        when="用户情绪平稳，开始思考'怎么办'，希望寻找可行的下一步。",
        guidance="和对方一起探索其已有的支持资源和曾经有效的应对方式，共同想 1-2 个小而可行的下一步，由对方做主。",
    ),
}

DEFAULT_STRATEGY = "empathy"


def strategy_catalog_text() -> str:
    """把策略库渲染成给 LLM 做选择时看的清单。"""
    lines = []
    for s in STRATEGIES.values():
        lines.append(f"- {s.key}（{s.name}）：适用于 {s.when}")
    return "\n".join(lines)


def get_strategy(key: str) -> Strategy:
    return STRATEGIES.get(key, STRATEGIES[DEFAULT_STRATEGY])
