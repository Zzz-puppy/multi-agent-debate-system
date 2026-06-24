<div align="center">

# 多智能体课堂辩论系统 🎭

**基于 LangGraph 的多智能体辩论模拟系统**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3+-green.svg)](https://www.langchain.com/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 项目简介

本项目实现了一个**多智能体课堂辩论系统**，模拟真实的课堂辩论场景。系统包含三个智能体角色：

- **正方学生** — 持正方观点，构建论点链，反驳反方
- **反方学生** — 持反方观点，构建论点链，反驳正方
- **教师** — 主持辩论流程、点评双方表现、评估论点质量、总结评分

每个智能体采用 **ReAct（推理→行动→复盘→回答）** 推理循环，结合联网搜索、历史知识检索、论点质量评估等工具，生成有逻辑、有依据的辩论内容。

## 系统架构

```
用户输入辩题 → 辩论管理器 → 多轮辩论循环 → 输出辩论记录
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    正方学生     反方学生      教师
   (ReAct Agent) (ReAct Agent) (ReAct Agent)
        │           │           │
        └───────────┼───────────┘
                    ▼
            工具层 & 记忆层
```

### 项目结构

```
├── agents/                  # 智能体定义
│   ├── student_agent.py     # 学生辩手（正方/反方）
│   ├── teacher_agent.py     # 教师（主持/点评/总结）
│   └── prompts.py           # 系统提示词
├── graph/                   # 辩论工作流
│   ├── debate_graph.py      # 辩论编排器
│   └── state.py             # 状态定义
├── tools/                   # 工具层
│   ├── web_search.py        # 网络搜索（DuckDuckGo）
│   ├── argument_evaluator.py # 论点质量评估（LLM-as-a-Judge）
│   └── strategy_recommender.py # 辩论策略推荐
├── memory/                  # 记忆层
│   ├── short_term.py        # 短期记忆（会话上下文）
│   ├── long_term_rag.py     # 长期记忆（ChromaDB 向量存储）
│   └── personal_profile.py  # 个人档案（JSON持久化）
├── utils/                   # 工具模块
│   ├── llm_manager.py       # LLM 实例管理器
│   ├── scoring.py           # 评分系统
│   └── formatter.py         # 辩论记录格式化输出
├── data/                    # 数据
│   ├── preset_topics.py     # 预设辩题
│   └── chroma_db/           # ChromaDB 持久化目录
├── main.py                  # 主入口
├── requirements.txt         # 依赖
└── .env.example             # 环境变量示例
```

## 技术栈

| 技术 | 用途 |
|------|------|
| [LangGraph](https://www.langchain.com/langgraph) | 智能体编排与状态管理 |
| [LangChain](https://www.langchain.com/) | LLM 调用与工具集成 |
| [ChromaDB](https://www.trychroma.com/) | 向量数据库（长期记忆） |
| [DeepSeek](https://platform.deepseek.com/) | 大语言模型 |
| [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) | 免费联网搜索 |
| [pytest](https://docs.pytest.org/) | 单元测试 |

## 快速开始

### 前置条件

- Python 3.12+
- DeepSeek API Key（[免费注册](https://platform.deepseek.com/)）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/Zzz-puppy/multi-agent-debate-system.git
cd multi-agent-debate-system

# 2. 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key
```

### 运行

```bash
python main.py
```

支持两种模式：
1. **自定义辩题** — 直接输入任意辩题，AI 会自动验证是否有效
2. **预设辩题** — 输入 `preset` 选择内置辩题

### 示例输出

辩论结束后会生成：
- 控制台实时输出辩论过程
- 详细的评分报告（逻辑性、论据质量、反驳能力、语言表达）
- Markdown 格式辩论记录（`output/debate_YYYYMMDD_HHMMSS.md`）

## 评分系统

评分独立于教师总结，由系统基于每轮评估聚合计算：

| 维度 | 权重 | 说明 |
|------|------|------|
| 逻辑性 | 25% | 论点结构是否清晰、论证是否递进 |
| 论据质量 | 25% | 证据是否充分、数据是否可靠 |
| 反驳能力 | 25% | 是否能有效回应对方质疑 |
| 语言表达 | 25% | 表达是否清晰有说服力 |

每轮由 `ArgumentEvaluatorTool`（LLM-as-a-Judge）对双方进行独立评分，最终取各轮平均值。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。
