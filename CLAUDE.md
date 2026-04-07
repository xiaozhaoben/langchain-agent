# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a smart customer service system for robot vacuum cleaners (智扫通机器人智能客服), built with LangChain/LangGraph using the ReAct (Reasoning + Acting) pattern. It integrates RAG retrieval-augmented generation, multi-tool orchestration, and middleware architecture.

## Commands

### Run the Web Application
```bash
streamlit run app.py
```

### Run the Agent via Command Line
```bash
python agent/react_agent.py
```

### Initialize Vector Store (RAG Knowledge Base)
```bash
python rag/vector_store.py
```

### Test RAG Service
```bash
python rag/rag_service.py
```

## Architecture

### Core Components

- **ReactAgent** (`agent/react_agent.py`): The main agent using LangChain's `create_agent` with ReAct pattern. Orchestrates tools and middleware.

- **Tools** (`agent/tools/agent_tools.py`): 7 intelligent tools:
  - `rag_summarize`: Vector store retrieval for professional knowledge
  - `get_weather`: City weather query
  - `get_user_location`: User location retrieval
  - `get_user_id`: User identity retrieval
  - `get_current_month`: Current month retrieval
  - `fetch_external_data`: External data query for usage reports
  - `fill_context_for_report`: Context injection for report generation mode

- **Middleware** (`agent/tools/middleware.py`): Three middleware components:
  - `monitor_tool`: Logs tool calls and detects report mode trigger
  - `log_before_model`: Logs state before model invocation
  - `report_prompt_switch`: Dynamically switches prompts between normal/report modes

- **RAG Service** (`rag/rag_service.py` + `rag/vector_store.py`): ChromaDB-based vector storage with semantic search using Ollama embeddings.

- **Model Factory** (`model/factory.py`): Creates ChatTongyi (通义千问) for chat and OllamaEmbeddings for vectorization.

### Key Patterns

1. **ReAct Flow**: User query → Thinking → Action (tool call) → Observation → Re-thinking → Final Answer

2. **Dynamic Prompt Switching**: When `fill_context_for_report` tool is called, middleware sets `runtime.context['report'] = True`, triggering the prompt switch to report generation mode.

3. **Configuration**: All configs are YAML files in `config/`:
   - `agent.yml`: External data path
   - `chroma.yml`: Vector store settings (collection name, persist directory, chunk size)
   - `prompts.yml`: Prompt template file paths
   - `rag.yml`: Model names for chat and embeddings

4. **Knowledge Base**: PDF/TXT files in `data/` are automatically chunked and indexed. MD5 hashes prevent duplicate loading.

## Important Notes

- **Comments and prompts are in Chinese** - maintain this convention when adding new code or prompts.

- **Tool call constraints**: The `fill_context_for_report` tool must be called before `fetch_external_data` when generating reports (enforced in the main prompt).

- **Maximum 5 tool calls** per query (defined in main_prompt.txt).

- **Config Loading**: Configs are loaded at module level in `utils/config_handler.py` using YAML. Access via `rag_conf`, `chroma_conf`, `prompts_conf`, `agent_conf` globals.

- **Path Resolution**: Always use `get_abs_path()` from `utils/path_tool.py` for relative paths to ensure correct resolution from project root.
