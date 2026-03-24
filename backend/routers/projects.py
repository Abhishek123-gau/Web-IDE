import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import Project, User
from db.schemas import ProjectCreate, ProjectResponse
from core.security import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
def get_user_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch all stored projects for the logged-in user."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()
    return projects

@router.post("/", response_model=ProjectResponse)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Initialize a blank project for the user."""
    project = Project(
        title=project_in.title,
        user_id=current_user.id,
        chat_history="[]",
        ui_tree="{}",
        files_json="{}"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.post("/{project_id}/load")
def load_project_to_workspace(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Grabs the exact files_json from the DB, and physically writes 
    them out to generated_workspace/ over-writing what's there. 
    Instant 0-LLM reload.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # The json holds the paths. Example: {"src/App.jsx": "...", ...}
    try:
        files_map = json.loads(project.files_json)
    except:
        files_map = {}
        
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "generated_workspace"))
    
    # Write each file natively out to disk
    for rel_path, content in files_map.items():
        abs_path = os.path.join(workspace_dir, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    return {"message": "Project fully loaded into workspace", "project_title": project.title}

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
