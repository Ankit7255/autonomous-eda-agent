# Auto-Analyst: Autonomous Data Science & EDA Agent

**Live Application:** [https://autonomous-eda-agent-wstuozc4q6bux2tacgalfh.streamlit.app/]

Auto-Analyst is an autonomous data exploration and analysis system. The agent ingests raw tabular datasets, inspects column schemas and distributions, formulates an analytical plan, dynamically generates Python code, and executes it within a controlled environment. 

The architecture features a self-correcting feedback loop powered by LangGraph, enabling runtime exception recovery without human intervention.

---

## Architecture Overview

The system operates as a stateful cyclical graph (`StateGraph`), coordinating between planning, code synthesis, runtime execution, and synthesis.

```text
+-----------------------+
|  User Dataset Upload  |
+-----------+-----------+
            |
            v
+-----------------------+
|     Planner Node      | <--- Generates structured EDA strategy
+-----------+-----------+
            |
            v
+-----------------------+       (Exception Captured / Retry)
|      Coder Node       | <------------------------------------+
+-----------+-----------+                                      |
            |                                                  |
            v                                                  |
+-----------------------+       Execution Failed (Traceback)   |
|     Executor Node     +--------------------------------------+
+-----------+-----------+
            |
            | Execution Success
            v
+-----------------------+
|     Reporter Node     | <--- Synthesizes metrics into Executive Report
+-----------+-----------+
            |
            v
+-----------------------+
| Final UI & Artifacts  |
+-----------------------+




autonomous EDA agent/
├── core/
│   ├── __init__.py         # Package initialization
│   ├── state.py            # TypedDict state schema definition
│   ├── prompts.py          # LLM prompt templates and engineering guardrails
│   ├── executor.py         # Code execution sandbox and error interceptor
│   └── graph.py            # LangGraph workflow, nodes, and conditional edges
├── artifacts/              # Local target directory for generated plots
├── data/                   # Temporary upload directory for datasets
├── app.py                  # Streamlit application entry point
├── main.py                 # Standalone pipeline test harness
├── requirements.txt        # Python package dependencies
└── .gitignore              # Environment variable and artifact exclusions



```


## Core Design Principles


1. State Isolation: The workflow state tracks dataset metadata, execution tracebacks, runtime iteration counts, and generated visual artifacts.

2. Self-Healing Loop: Runtime errors (e.g., KeyError, ZeroDivisionError, ValueError) are intercepted and formatted into diagnostic prompts for the Coder node, allowing automatic code refactoring up to a configured threshold.

3. Dynamic Visualization Guardrails: Enforces cardinality checks during the planning and coding stages to prevent plotting unreadable high-cardinality categorical data.

4. Executive Synthesis: Converts raw execution metrics and outputs into structured markdown reporting with domain-specific recommendations.


## Technical Stack


| Layer | Component | Description |
|---|---|---|
| **Orchestration** | LangGraph | State machine managing cyclical execution and self-healing loops |
| **LLM Engine** | Google Gemini API | Structured reasoning, code generation, and executive reporting |
| **Execution Runtime** | Python 3.11+ / Sandbox | Local execution environment with captured I/O streams |
| **Data & Viz** | Pandas, NumPy, Seaborn, Matplotlib | Tabular data manipulation and statistical visualization |
| **Interface** | Streamlit | Web interface for file ingestion, log streaming, and rendering |


