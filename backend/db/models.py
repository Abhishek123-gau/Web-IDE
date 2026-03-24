from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to projects
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    
    # Store LangGraph chat history array as a JSON string
    chat_history = Column(Text, default="[]") 
    
    # Store the dictionary of LangGraph UI elements as a JSON string
    ui_tree = Column(Text, default="{}") 
    
    # Store the actual file contents spanning the generated_workspace as a JSON string map
    # {"src/App.jsx": "export default function App() { ... }", "src/index.css": "..."}
    files_json = Column(Text, default="{}")
    
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    owner = relationship("User", back_populates="projects")
