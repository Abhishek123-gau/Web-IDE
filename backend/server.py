import sys
import os
import io
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.graph import app as langgraph_app
from backend.core.models import UITreeState

app = FastAPI(title="Nexus IDE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Stdout Interception for SSE Logs ---
log_queues = []
import re
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class StdoutRedirector(io.StringIO):
    def __init__(self, original_stdout):
        super().__init__()
        self.original_stdout = original_stdout
        self.loop = None

    def write(self, s):
        self.original_stdout.write(s)
        if s and self.loop:
            clean_s = ANSI_ESCAPE.sub('', s)
            if clean_s:
                for q in log_queues:
                    try:
                        self.loop.call_soon_threadsafe(q.put_nowait, clean_s)
                    except Exception:
                        pass
        return len(s)

original_stdout = sys.stdout
redirector = StdoutRedirector(original_stdout)
sys.stdout = redirector

import subprocess
import atexit

@app.on_event("startup")
async def startup_event():
    redirector.loop = asyncio.get_running_loop()
    
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "generated_workspace"))
    if os.path.exists(workspace_dir):
        print(f"[System]: Auto-starting Vite Live Preview in {workspace_dir}...")
        try:
            preview_process = subprocess.Popen(
                ["npm", "run", "dev"], 
                cwd=workspace_dir,
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            atexit.register(lambda: preview_process.terminate())
        except Exception as e:
            print(f"[Warning]: Failed to start preview server: {e}")

@app.get("/api/logs")
async def stream_logs():
    q = asyncio.Queue()
    log_queues.append(q)
    
    async def log_generator():
        try:
            while True:
                chunk = await q.get()
                # Use JSON to safely encode newlines and spaces
                payload = json.dumps({"chunk": chunk})
                yield f"data: {payload}\n\n"
        except asyncio.CancelledError:
            log_queues.remove(q)
            
    return StreamingResponse(log_generator(), media_type="text/event-stream")

# --- Database and Router Initialization ---
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import engine, Base, get_db
from db.models import Project, User
from core.security import get_current_user
from routers import auth, projects

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(projects.router)

# --- Chat Endpoint ---
class ChatRequest(BaseModel):
    project_id: int
    message: str

def get_workspace_files_json():
    import os
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "generated_workspace"))
    files_map = {}
    for root, _, files in os.walk(workspace_dir):
        if "node_modules" in root or "dist" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, workspace_dir)
            if not rel_path.endswith((".jsx", ".js", ".html", ".css", ".scss", ".ts", ".tsx", ".json")):
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    files_map[rel_path.replace("\\", "/")] = f.read()
            except Exception:
                pass
    return json.dumps(files_map)

@app.post("/api/chat")
async def process_chat(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == request.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        history = json.loads(project.chat_history)
    except:
        history = []
    try:
        ui_tree = json.loads(project.ui_tree)
    except:
        ui_tree = {}

    history.append(f"User: {request.message}")
    
    current_state = {
        "chat_history": history,
        "ui_tree": ui_tree,
        "generated_code": "",
        "build_error": None
    }
    
    final_state = await asyncio.to_thread(langgraph_app.invoke, current_state)
    
    new_history = final_state.get("chat_history", [])
    new_ui_tree = final_state.get("ui_tree", {})
    
    project.chat_history = json.dumps(new_history)
    if hasattr(new_ui_tree, "model_dump_json"):
        project.ui_tree = new_ui_tree.model_dump_json()
    else:
        project.ui_tree = json.dumps(new_ui_tree)
    project.files_json = get_workspace_files_json()
    project.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "chat_history": new_history,
        "generated_code": final_state.get("generated_code", ""),
        "build_error": final_state.get("build_error", None)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
