# Project Folder Structure

```text
ui-system/
├── frontend/                     # Chat & Preview Web Interface
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx   # Chat input and message thread
│   │   │   ├── PreviewPanel.jsx    # Iframe for displaying generated site
│   │   │   └── AgentStatus.jsx     # Visual indicator of current LangGraph node
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # Python Server & LangGraph Orchestration
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py             # Planner Agent logic
│   │   ├── ui_designer.py         # JSON Component Tree builder
│   │   ├── code_generator.py      # React/Tailwind code writer
│   │   ├── debugger.py            # Error analysis and code fixing
│   │   └── renderer.py            # Node/Vite execution manager
│   │
│   ├── core/
│   │   ├── graph.py               # LangGraph workflow definition (Nodes & Edges)
│   │   ├── state.py               # TypedDict for LangGraph state
│   │   ├── llm.py                 # Ollama/vLLM client wrapper
│   │   └── prompts.py             # System prompts for all agents
│   │
│   ├── api/
│   │   └── routes.py              # FastAPI endpoints for WebSocket/Chat
│   │
│   ├── main.py                    # FastAPI application entry point
│   └── requirements.txt
│
└── generated_workspace/          # Directory where generated AI website lives
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    ├── tailwind.config.js         # Tailwind configuration
    └── vite.config.js             # Vite configuration for preview
```
