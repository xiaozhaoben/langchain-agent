# 🤖 智扫通机器人智能客服系统

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**基于 LangChain ReAct 模式的扫地机器人智能客服系统，集成 RAG 检索增强生成、多工具调用和中间件架构**

---

## 📋 目录

- [项目简介](#-项目简介)
- [✨ 核心特性](#-核心特性)
- [🏗️ 系统架构](#-系统架构)
- [🛠️ 技术栈](#-技术栈)
- [📦 安装部署](#-安装部署)
- [🚀 快速开始](#-快速开始)
- [💡 使用示例](#-使用示例)
- [🔧 配置说明](#-配置说明)
- [📂 项目结构](#-项目结构)
- [🎯 核心功能详解](#-核心功能详解)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)

---

## 项目简介

智扫通机器人智能客服是一个基于 **LangChain/LangGraph** 框架构建的智能对话系统，专门为扫地机器人和扫拖一体机用户提供专业的咨询服务。系统采用 **ReAct (Reasoning + Acting)** 模式，具备自主思考、工具调用和多轮对话能力。

### 🎯 主要能力

- 💬 **智能问答**：基于 RAG 技术的专业知识检索与生成
- 🔧 **多工具协同**：集成天气查询、位置服务、用户数据获取等 7 大工具
- 📊 **个性化报告**：根据用户使用数据自动生成定制化使用报告
- 🌐 **Web 界面**：基于 Streamlit 的现代化交互界面
- ⚡ **流式输出**：实时响应，提升用户体验

---

## ✨ 核心特性

### 🧠 ReAct 推理模式
```
用户提问 → 思考(Reasoning) → 行动(Action) → 观察(Observation) → 再思考 → 最终回答
```
系统遵循严格的"思考→行动→观察→再思考"流程，确保回答逻辑自洽、专业准确。

### 🔍 RAG 检索增强生成
- 基于 ChromaDB 向量数据库的语义检索
- 支持扫地机器人专业知识库的高效查询
- 自动从知识库中提取相关内容并整合回答

### 🛠️ 7 大智能工具

| 工具名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `rag_summarize` | 向量库资料检索 | 专业问题解答、故障处理 |
| `get_weather` | 城市天气查询 | 环境适配建议 |
| `get_user_location` | 用户位置获取 | 地理位置相关咨询 |
| `get_user_id` | 用户身份识别 | 个性化服务 |
| `get_current_month` | 当前月份获取 | 时间相关数据统计 |
| `fetch_external_data` | 外部数据查询 | 使用报告生成 |
| `fill_context_for_report` | 报告上下文注入 | 触发报告模式 |

### 🔄 中间件系统
- **监控中间件**：记录工具调用日志和参数
- **日志中间件**：追踪模型调用前的状态信息
- **动态提示词切换**：根据场景自动切换普通/报告提示词

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│                   (app.py - 用户界面层)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ReactAgent Core                          │
│            (agent/react_agent.py - Agent 核心)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Middleware Pipeline                     │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────────────┐  │   │
│  │  │ monitor_  │ │ log_      │ │ report_prompt_    │  │   │
│  │  │ tool      │ │ before_   │ │ switch            │  │   │
│  │  └───────────┘ └───────────┘ └───────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Tools Registry                         │   │
│  │  rag_summarize │ get_weather │ get_user_location   │   │
│  │  get_user_id   │ fetch_data  │ fill_context        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────────┐
│  RAG Service │  │ Chat Model  │  │ External Data   │
│  (ChromaDB)  │  │ (通义千问)  │  │  (CSV Records)  │
└─────────────┘  └─────────────┘  └─────────────────┘
```

---

## 🛠️ 技术栈

### 核心框架
- **LangChain / LangGraph**: AI Agent 开发框架
- **Streamlit**: Web 应用框架
- **ChromaDB**: 向量数据库

### AI 模型
- **ChatTongyi (通义千问)**: 对话模型
- **Ollama Embeddings**: 文本向量化模型

### 工具库
- **PyYAML**: 配置文件解析
- **Python Logging**: 日志管理

### 运行环境
- **Python**: 3.11+
- **操作系统**: Windows / Linux / macOS

---

## 📦 安装部署

### 前置要求

1. **Python 3.11+**
```bash
python --version  # 确保 Python 版本 >= 3.11
```

2. **虚拟环境** (推荐)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 安装依赖

创建 `requirements.txt` 文件：
```txt
langchain>=0.3.0
langgraph>=0.2.0
langchain-community>=0.3.0
langchain-core>=0.3.0
langchain-ollama>=0.2.0
streamlit>=1.30.0
chromadb>=0.5.0
pyyaml>=6.0
dashscope>=1.14.0
```

安装依赖包：
```bash
pip install -r requirements.txt
```

### 环境配置

确保以下服务可用：
- **通义千问 API**: 用于对话模型调用
- **Ollama 服务**: 用于本地文本向量化 (可选)

---

## 🚀 快速开始

### 方式一：Web 界面启动 (推荐)

```bash
cd langchain-agent
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`

### 方式二：命令行运行

```bash
cd langchain-agent
python agent/react_agent.py
```

### 方式三：Python 交互式

```python
from agent.react_agent import ReactAgent

agent = ReactAgent()

for chunk in agent.execute_stream("扫地机器人如何保养？"):
    print(chunk, end="", flush=True)
```

---

## 💡 使用示例

### 示例 1：基础问答

**用户输入**:
> 扫地机器人在我这个地区气温下如何保养？

**系统响应过程**:
1. 🧠 **思考**: 需要了解用户所在地区的天气情况
2. 🔧 **调用工具**: `get_user_location()` → "深圳"
3. 🔧 **调用工具**: `get_weather("深圳")` → "晴天, 26°C"
4. 🔧 **调用工具**: `rag_summarize("机器人高温保养")` → 检索专业资料
5. 💬 **最终回答**: 结合天气信息和专业知识给出保养建议

### 示例 2：生成使用报告

**用户输入**:
> 给我生成我的使用报告

**系统响应过程**:
1. 🧠 **思考**: 识别为报告生成需求
2. 🔧 **调用工具**: `get_user_id()` → "1001"
3. 🔧 **调用工具**: `get_current_month()` → "2025-06"
4. 🔧 **调用工具**: `fill_context_for_report()` → 注入上下文
5. 🔧 **调用工具**: `fetch_external_data("1001", "2025-06")` → 获取数据
6. 💬 **生成报告**: 输出个性化使用报告

### 示例 3：故障排查

**用户输入**:
> 我的扫地机器人总是卡住怎么办？

**系统响应过程**:
1. 🧠 **思考**: 需要查找故障处理方案
2. 🔧 **调用工具**: `rag_summarize("机器人卡住 故障处理")` → 检索解决方案
3. 💬 **最终回答**: 提供详细的故障排查步骤

---

## 🔧 配置说明

### 主配置文件: `config/agent.yml`

```yaml
external_data_path: data/external/records.csv
```

**参数说明**:
- `external_data_path`: 外部数据文件路径（用户使用记录 CSV）

### RAG 配置: `config/chroma.yml`

```yaml
collection_name: robot_vacuum_collection
persist_directory: ./chroma_db
k: 3  # 检索返回的文档数量
chunk_size: 500
chunk_overlap: 50
```

### Prompt 配置: `config/prompts.yml`

定义各类提示词模板文件的路径：
- 主提示词 (`main_prompt.txt`)
- RAG 总结提示词 (`rag_summarize.txt`)
- 报告生成提示词 (`report_prompt.txt`)

---

## 📂 项目结构

```
langchain-agent/
├── app.py                      # Streamlit Web 入口
├── main.py                     # 命令行入口
├── README.md                   # 项目文档
│
├── config/                     # 配置文件目录
│   ├── agent.yml              # Agent 主配置
│   ├── chroma.yml             # ChromaDB 配置
│   └── prompts.yml            # Prompt 模板配置
│
├── agent/                      # Agent 核心模块
│   ├── react_agent.py         # ReAct Agent 实现
│   └── tools/                 # 工具集
│       ├── agent_tools.py     # 7 个智能工具定义
│       └── middleware.py      # 中间件 (监控/日志/提示词切换)
│
├── rag/                        # RAG 模块
│   ├── rag_service.py         # RAG 服务实现
│   └── vector_store.py        # ChromaDB 向量存储
│
├── model/                      # 模型工厂
│   └── factory.py             # LLM 和 Embedding 模型实例化
│
├── utils/                      # 工具函数
│   ├── config_handler.py      # 配置加载器
│   ├── file_handler.py        # 文件操作工具
│   ├── logger_handler.py      # 日志处理器
│   ├── path_tool.py           # 路径处理工具
│   └── prompt_loader.py       # Prompt 加载器
│
├── prompts/                    # Prompt 模板
│   ├── main_prompt.txt        # 主提示词 (ReAct 流程定义)
│   ├── rag_summarize.txt      # RAG 总结提示词
│   └── report_prompt.txt      # 报告生成提示词
│
├── data/                       # 数据目录
│   └── external/
│       └── records.csv         # 用户使用记录 (10 用户 × 12 月)
│
├── chroma_db/                  # ChromaDB 持久化存储
├── logs/                       # 日志输出目录
└── requirements.txt            # Python 依赖列表
```

---

## 🎯 核心功能详解

### 1. ReAct Agent 引擎

基于 LangChain 的 `create_agent` 构建，支持：

- **自主推理**: 根据 prompt 定义的思考准则进行决策
- **动态工具选择**: 根据问题类型自动选择合适的工具组合
- **多轮迭代**: 最多 5 次工具调用的深度推理链

**代码示例**:
```python
from agent.react_agent import ReactAgent

agent = ReactAgent()

# 流式输出
for chunk in agent.execute_stream("您的查询"):
    print(chunk, end="", flush=True)
```

### 2. RAG 检索系统

**工作流程**:
```
用户查询 → 文本向量化 → ChromaDB 相似度搜索 → Top-K 文档返回 → LLM 整合生成
```

**特点**:
- 语义级检索 (非关键词匹配)
- 可配置的检索数量 (默认 k=3)
- 自动分块和向量化处理

### 3. 中间件架构

#### 监控中间件 (`monitor_tool`)
- 记录每个工具的调用名称和参数
- 捕获异常并记录错误日志
- 检测报告触发信号

#### 日志中间件 (`log_before_model`)
- 在每次模型调用前记录消息状态
- 安全的消息访问机制 (防止空列表异常)

#### 动态提示词切换 (`report_prompt_switch`)
- 普通问答模式: 使用 `main_prompt.txt`
- 报告生成模式: 切换到 `report_prompt.txt`

### 4. 外部数据集成

**数据格式** (`records.csv`):
```csv
用户ID,特征,清洁效率,耗材,对比,时间
"1001","高效",95%,"正常","优于平均","2025-01"
...
```

**数据规模**:
- 10 个模拟用户 (1001-1010)
- 每个用户 12 个月的使用记录
- 共 120 条完整数据记录

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是新功能、Bug 修复还是文档改进。

### 贡献流程

1. **Fork 本仓库**
   ```bash
   git clone https://github.com/xiaozhaoben/langchain-agent.git
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **提交更改**
   ```bash
   git commit -m 'Add amazing feature'
   ```

4. **推送到分支**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **提交 Pull Request**

### 开发规范

- **代码风格**: 遵循 PEP 8 规范
- **注释语言**: 中文注释 (保持与项目一致)
- **Commit Message**: 使用规范的提交信息格式
- **测试**: 新功能需附带测试用例

### Bug 反馈

如发现 Bug 或有改进建议，请通过 GitHub Issues 提交：
- 详细描述问题现象
- 提供复现步骤
- 附带运行环境和日志信息

---

## 📄 许可证

本项目采用 **MIT License** 开源协议。

```
MIT License

Copyright (c) 2025 LangChain Agent Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **项目仓库**: [GitHub Repository](https://github.com/xiaozhaoben/langchain-agent)
- **问题反馈**: [GitHub Issues](https://github.com/xiaozhaoben/langchain-agent/issues)
- **邮箱**: a2502712438@gmail.com

---

## 🙏 致谢

感谢以下开源项目和社区的支持：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 编排框架
- [Streamlit](https://github.com/streamlit/streamlit) - 数据应用框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 开源向量数据库
- [通义千问](https://tongyi.aliyun.com/) - 阿里云大语言模型

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给一个 Star！⭐**

Made with ❤️ by LangChain Agent Team

</div>
