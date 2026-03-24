import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.ui_designer import UIDesignerAgent
import json

state = {
    "chat_history": ["System Plan: Add a simple navbar at the top of the page."],
    "ui_tree": {}
}

agent = UIDesignerAgent()
result = agent.design(state)
print("\n[FINAL RESULT]:")
print(json.dumps(result.get("ui_tree").model_dump() if hasattr(result.get("ui_tree"), 'model_dump') else result.get("ui_tree"), indent=2))
