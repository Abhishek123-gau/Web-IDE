# Local AI UI Generator: System Documentation

This document explicitly details how the system functions start-to-finish. It tracks the journey of a user query through the backend Python architecture down to the resulting live React website.

---

## The Workflow Journey (Step-By-Step)

### 1. The Entrypoint: `main.py`
- **What Happens**: You run `python backend/main.py`. This starts a CLI loop asking for user input.
- **State Initialization**: A persistent LangGraph `StateGraph` dictionary (`UIState`) is created empty: 
  `{"chat_history": [], "ui_tree": {}, "generated_code": "", "build_error": None}`.
- **The Trigger**: You type a query (e.g., *"Build a SaaS landing page with a navigation bar and a pricing section"*). This query is appended to the `chat_history`.
- **The Execution**: `main.py` calls `app.invoke(current_state)`. This hands control completely to LangGraph (`core.graph.py`).

### 2. Node 1: Planner Agent (`backend/agents/planner.py`)
- **Role**: High-Level Analyst.
- **What Happens**: It reads the user query and the *current* UI tree (which is empty the first time around).
- **LLM Call**: It passes them to the local LLM (`llama3`) via Langchain and asks: *"As a Product Manager, what changes need to be made to satisfy this request?"*
- **Output**: It generates an actionable instruction like *"Add a Navbar and a Pricing section to the root Page container."* It appends this string to the `chat_history` payload.

### 3. Node 2: UI Designer Agent (`backend/agents/ui_designer.py`)
- **Role**: JSON Architect.
- **What Happens**: It receives the Planner's string instructions.
- **LLM Call**: It uses a strict `JsonOutputParser` bound to the `UITreeState` Pydantic class defined in `core.models.py`. It asks the LLM to modify the JSON tree specifically based on the Planner's instructions.
- **Output**: It returns a freshly updated, rigidly typed JSON component tree mapping out layout, types, and empty child arrays. This modifies the `ui_tree` object in the shared graph state.

### 4. Node 3: Code Generator Agent (`backend/agents/code_generator.py`)
- **Role**: React + Tailwind Developer.
- **What Happens**: It reads the updated JSON component tree and recursively traverses it. For each major unique component (e.g., Navbar, Pricing) that it hasn't generated yet, it creates a specific prompt.
- **LLM Call**: It asks the LLM to generate the raw React functional component code using Tailwind CSS for styling, injecting any properties the Designer requested for that node.
- **File System Operations**: 
  - It writes the generated files like `Navbar.jsx` to memory. 
  - It scaffolds the root React boilerplate files (`App.jsx`, `Home.jsx`) to import mapping those newly generated components.
  - It uses a physical utility to forcibly dump these generated text files into your real file system at `ui-system/generated_workspace/src/`.

### 5. Node 4: Preview Renderer Agent (`backend/agents/renderer.py`)
- **Role**: Sandbox Compiler.
- **What Happens**: It serves as a verification gateway. It executes a local shell subprocess running `npm run build` inside the React `generated_workspace/` directory.
- **Success Case**: If Vite compiles the React code without strict syntax errors, the node sets `build_error` to `None`. LangGraph sees this and successfully completes the pipeline.
- **Failure Case**: If Vite fails (e.g., a missing variable or syntax typo from the LLM), the Node captures the Node.js/Vite `stderr` stream entirely, attaches it to the `build_error` state payload, and ends its turn.

### 6. The Graph Router (`core.graph.py`)
- **What Happens**: LangGraph evaluates the conditional edge coming out of the Renderer Agent. 
- If `state["build_error"]` exists...

### 7. Node 5: Debugger Agent (`backend/agents/debugger.py`)
- **Role**: Auto-Healer.
- **What Happens**: It parses the Vite error trace to isolate which specific React file in the `generated_workspace` crashed (e.g., `Pricing.jsx`). It reads that faulty file straight from the disk.
- **LLM Call**: It feeds the faulty code and the exact compiler error back to the LLM and asks, *"Return ONLY the corrected code."*
- **File System Operations**: It overwrites the old, broken `Pricing.jsx` with the LLM's fixed output. It wipes the `build_error` payload in the state back to `None`.
- **The Loop**: LangGraph automatically routes the state *back* to the Code Generator/Renderer to attempt a compilation check again. This loop runs until compilation succeeds natively.

---

## File Structure Breakdown

| Directory/File | Purpose |
| :--- | :--- |
| `backend/main.py` | The CLI entry point that loops chats and kicks off the graph. |
| `backend/core/graph.py` | The absolute blueprint. Dictates the order agents fire and conditionally routes errors. |
| `backend/core/models.py` | Type safety mapping. Ensures the local LLMs adhere strictly to standard React tree concepts (e.g. enforcing Props vs Children concepts). |
| `backend/agents/*.py` | The physical logic for each LLM-empowered persona. Prompts, LLM invocation logic, and file I/O operations. |
| `generated_workspace/` | An independent, standard scaffolded Vite + React application. It acts purely as a dumb sandbox that receives generated React component texts and compiles them natively for browsers. |

---

## How it supports "Chat-Based UI Editing"
Because the system retains the structural architecture in JSON format across chats (`UITreeState`), the system understands context. 

If you say, *"Make the Navigation Bar dark mode"*:
1. The **Planner** knows you only want to affect the `Navbar` component, not the whole Page.
2. The **Designer** receives the exact same JSON tree as before, but only modifies the `Props` object of the `Navbar` JSON element to include `className: "bg-gray-900"`.
3. The **Code Generator** skips regenerating the unchanged nodes, taking the single changed `Navbar` node and querying the LLM for a dark-mode styled version, silently overwriting `Navbar.jsx` in the workspace while leaving your `Pricing.jsx` or your `Hero.jsx` completely untouched.
4. Because Vite has Hot Module Replacement natively, your browser tab instantly refreshes only the Navigation bar block on your screen without wiping the whole site.
