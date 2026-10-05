# 心理陪伴智能体「小屿」 (Mental-Health Companion Agent)

>基于 **DeepSeek + LangGraph** 实现的、面向学生的心理陪伴对话智能体。它能在遵循心理沟通策略与安全规则的前提下，理解情绪、按场景选择沟通策略、循循善诱地促进用户表达，并在识别到心理危机时进入危机干预路径、转介专业资源。

---

## 1. 它解决什么问题

面向**学生群体**的日常情绪陪伴：学生常常"表达意愿不足、难以直接说出困扰"。小屿通过共情、倾听、开放式提问等策略降低表达压力，引导用户愿意开口、持续交流；同时守住明确的安全边界，遇到危机及时转介专业帮助。

展示：使用时的web页面速览#来源于两个帮助测试该智能体的同学，具体的测试反馈见/docs/dev_log.md
<img width="1280" height="623" alt="aaba3c04e5610ad8297e807c2dbc5d57" src="https://github.com/user-attachments/assets/b5825a54-5015-440f-ba01-7155ab801005" />
<img width="1273" height="647" alt="9efc812e375ee536524289694ebe651b" src="https://github.com/user-attachments/assets/f6b475bc-7de5-4c41-8ff0-4d0d9059dea5" />
页面设计清新简洁，让人拥有好心情。侧栏有实时跟进的风险评估和情绪判断，以及对应的回复策略，旨在更好的帮助陪伴学生客户群体。

## 2. 核心能力（对应任务目标）

| # | 任务目标 | 本项目实现 |
|---|---------|-----------|
| 1 | 基于大模型 API 搭建心理陪伴对话智能体 | LangGraph 状态图 + DeepSeek，多轮记忆（`src/`） |
| 2 | 角色设定、语气与安全边界（它不做什么） | `src/prompts.py` 的 `PERSONA` + `SAFETY_BOUNDARY` |
| 3 | 心理对话策略选择机制 | `src/strategies.py` 策略库 + `analyze` 节点按场景选择 |
| 4 | 评测方法：谁试、试什么、看什么指标 | `evaluation/`（LLM-as-judge + 人工试用，5 维度 + 危机硬性安全项） |

## 3. 架构

```
用户输入
   │
   ▼
[analyze]  一次 LLM 调用完成：风险评估 + 情绪识别 + 策略选择（结构化 JSON）
   │
   ├── risk ∈ {medium, high} ──▶ [crisis_response]  危机干预 + 求助热线转介
   │
   └── risk ∈ {none, low}    ──▶ [generate_response] 按选定策略生成有温度的回应
```

- **风险优先**：任何一轮先过安全阀，"宁高勿漏"，中/高风险直接走危机路径。
- **策略选择机制**：从 6 个心理沟通策略（共情 / 倾听反映 / 开放式提问 / 情绪支持 / 温和认知重构 / 资源探索）中按情绪与场景选择。
- **多轮记忆**：LangGraph `MemorySaver` 按 `thread_id` 维护会话上下文。

## 4. 快速开始

```bash
# 1) 创建虚拟环境并安装依赖
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2) 配置 DeepSeek Key
cp .env.example .env      # 然后填入 DEEPSEEK_API_KEY

# 3) 自动演示（跑 3 个预设场景）
.venv/bin/python -m demo.demo

# 4) 网页可视化界面（推荐）—— 聊天 + 实时展示风险/情绪/策略分析
.venv/bin/python -m web.server        # 打开 http://127.0.0.1:8000

# 5) 自己和小屿聊（终端交互模式）
.venv/bin/python -m demo.demo --chat

# 6) 自动评测（LLM-as-judge，5 维度 + 危机安全项）
.venv/bin/python -m evaluation.evaluate
```

Windows PowerShell（使用独立环境，不覆盖从 macOS 复制来的 `.venv`）：

```powershell
py -m venv .venv-windows
.\.venv-windows\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-windows\Scripts\python.exe -m demo.demo
# 交互式对话
.\.venv-windows\Scripts\python.exe -m demo.demo --chat
```

## 5. 目录结构

```
mental-health-companion-agent/
├── src/                 # 智能体核心
│   ├── config.py        # DeepSeek LLM 配置
│   ├── state.py         # LangGraph 状态
│   ├── strategies.py    # 心理沟通策略库
│   ├── prompts.py       # 角色/安全边界/各节点提示词
│   ├── nodes.py         # analyze / generate_response / crisis_response
│   ├── graph.py         # 状态图组装
│   └── agent.py         # CompanionAgent 高层接口 + 调用记录
├── demo/                # 自动演示与场景
├── web/                 # 网页可视化界面（FastAPI + 单页前端）
│   ├── server.py        # 后端 API
│   └── static/index.html# 聊天 + 实时分析面板
├── evaluation/          # 评测方法与指标
├── docs/                # 方案设计 / 开发日志 / 日程记录
└── logs/                # 每轮调用记录（.jsonl，自动生成）
```

## 6. 安全边界（它不做什么）

不诊断精神疾病、不荐药、不替代专业咨询、不评判说教、不打探隐私、**不讨论任何自伤/伤人的具体方法**；遇危机稳稳接住情绪并转介 24 小时热线（400-161-9995 等）与身边信任的人。

## 7. 文档

- 方案设计与调研：[docs/design.md](docs/design.md)
- 开发日志与评测分析：[docs/dev_log.md](docs/dev_log.md)
- 日程记录：[docs/schedule.md](docs/schedule.md)

> ⚠️ 免责声明：本项目为课程作业原型，**不能替代专业心理咨询或医疗**。如果你或身边的人正处于危机，请立即拨打 400-161-9995 或 120。

## 8. 常见问题

**`CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`**
macOS 的 Python 找不到 CA 证书。本项目已默认用 `certifi` 修复。若你在**会做 TLS 拦截的公司代理网络**下仍报错，在 `.env` 里二选一：
```bash
DEEPSEEK_CA_BUNDLE=/绝对路径/公司根证书.pem   # 推荐：指定公司根证书
# 或（仅本地调试，不安全）
DEEPSEEK_VERIFY_SSL=false
```

**`APIConnectionError` / `WinError 10054`（连接被重置）**
这是到 DeepSeek API 的网络连接中断，不是 LangGraph 未安装。客户端会自动重试最多 5 次；仍失败时，交互模式会显示底层网络错误。Windows 下先确认代理程序正在运行，且代理地址/端口与 `HTTP_PROXY`、`HTTPS_PROXY` 环境变量一致。若当前网络允许直连，可在 PowerShell 当前窗口临时清除代理后重试：
```powershell
Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY, Env:ALL_PROXY -ErrorAction SilentlyContinue
```
交互模式会显示连接错误和排查提示；网络恢复后可直接重试本轮。

