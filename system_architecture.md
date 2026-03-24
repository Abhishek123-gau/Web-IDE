# Local AI System Architecture: Natural Language to Website UI

## Overview
A chat-based, multi-agent AI system designed to iteratively convert natural language prompts into a functional React + Tailwind website. It uses a Python backend running LangGraph to orchestrate five specialized agents, powered by local open-source LLMs (7B-14B) via Ollama or vLLM.

## Core System Components

### 1. Frontend (Chat & Preview Interface)
- **Chat UI**: Built with React/Next.js to capture user prompts, display chat history, and show agent status.
- **Preview Pane**: An iframe or live-render view to display the generated site natively.

### 2. Backend (Orchestration & State Management)
- **Framework**: FastAPI to handle streaming API requests and WebSocket connections for real-time updates.
- **State Management (LangGraph)**: Maintains a typed state containing chat history, intermediate plans, current JSON Component Tree, generated React code, and rendering errors.
- **LLM Interface**: Interacts with local models (e.g., Llama 3 8B, Mistral 7B) using Ollama/vLLM.

### 3. Multi-Agent Engine
The system employs 5 specialized LangGraph nodes (Agents):

1. **Planner Agent**
   - **Role**: Parses user prompts, understands intent, and maps it to a high-level UI structure.
   - **Input**: User prompt, current UI structure.
   - **Output**: Action plan (e.g., "Add a navigation bar with 3 links").

2. **UI Designer Agent**
   - **Role**: Converts high-level plans into a detailed JSON Component Tree.
   - **Input**: Action plan, current JSON tree.
   - **Output**: Updated JSON Component Tree (specifying layout, nested elements, text content, tailwind classes).

3. **Code Generator Agent**
   - **Role**: Translates the JSON Component Tree into working React + Tailwind CSS code.
   - **Input**: JSON Component Tree.
   - **Output**: Raw string of React code files (e.g., `App.jsx`, components).

4. **Renderer Agent (Environment)**
   - **Role**: Compiles/Hosts the generated code. Runs a local Vite server or Node script to build the website and serve it to the frontend preview pane.
   - **Input**: React source code.
   - **Output**: Preview URL, build logs, and runtime errors (if any).

5. **Debug Agent**
   - **Role**: Self-corrects generated code if the Renderer catches syntactical or build errors.
   - **Input**: Build errors from Renderer, current React code.
   - **Output**: Fixed React code (loops back to Renderer).

## Workflow Execution Flow
1. **User Prompt**: User provides a prompt via the chat UI.
2. **Planning**: Planner agent creates a design spec.
3. **Designing**: UI Designer agent updates the state's JSON tree.
4. **Coding**: Code Generator creates/updates the React code based on the JSON tree.
5. **Rendering & Validation**: Renderer attempts to compile/run the code.
   - **Failure**: If build fails, passes errors to Debug Agent iteratively until resolved or max retries reached.
   - **Success**: Sends success signal + live preview URL to Frontend.
