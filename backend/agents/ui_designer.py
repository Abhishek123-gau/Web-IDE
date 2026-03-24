import os
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
try:
    from backend.core.streamer import stream_llm_json
except ImportError:
    import sys as _sys, os as _os
    _sys.path.append(_os.path.join(_os.path.dirname(__file__), '..'))
    from core.streamer import stream_llm_json

try:
    from backend.core.models import UITreeState, UIComponent
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.models import UITreeState, UIComponent

class UIDesignerAgent:
    """
    Agent responsible for converting the Planner's instructions into 
    precise modifications of the JSON Component Tree.
    """
    def __init__(self, model_name: str = "qwen2.5-coder:7b", base_url: str = "http://localhost:11434"):
        # We use num_predict for ChatOllama to cap max tokens, leaving enough room for a JSON tree 
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.15, num_predict=4000)
        
        # Enforce JSON output Schema
        self.parser = JsonOutputParser(pydantic_object=UITreeState)
        
        self.designer_prompt = ChatPromptTemplate.from_messages([
            ("system",
            "You are Qwen2.5-Coder, an expert JSON structured Data Architect for a UI System.\n"
            "Your job is to apply the requested UI modifications to the provided JSON tree strictly following the Planner's instructions.\n\n"

            "STRICT RULES:\n"
            "1. Output ONLY valid JSON matching the exact schema.\n"
            "2. Do NOT include any conversational text, explanations, or <think> tags. Output the JSON immediately.\n"
            "3. Do NOT include markdown formatting like ```json.\n"
            "4. Do NOT include text before or after JSON.\n"
            "5. The output MUST match the schema.\n"
            "6. Always return the FULL updated tree.\n\n"

            "Modification rules:\n"
            "- Add components inside the 'children' array.\n"
            "- Modify properties inside the 'props' object. Ensure ALL properties inside 'props' are valid key-value pairs (e.g., \"className\": \"bg-blue-500\").\n"
            "- Keep existing components unless explicitly removed.\n\n"

            "Schema:\n{format_instructions}"
            ),

            ("user",
            "Current UI Tree:\n{ui_tree}\n\n"
            "Planner Instructions:\n{plan}\n\n"
            "Return the updated UI tree."
            )
        ])
        self.chain = self.designer_prompt | self.llm | self.parser

    def design(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        print("--- RUNNING NODE: UI DESIGNER ---")
        
        chat_history = state.get("chat_history", [])
        plan = chat_history[-1] if chat_history else "No plan provided."
        
        ui_tree = state.get("ui_tree", {})
        
        # Determine string representation of current tree
        tree_str = "{}"
        if ui_tree:
            if hasattr(ui_tree, "model_dump_json"):
                tree_str = ui_tree.model_dump_json(indent=2)
            else:
                tree_str = json.dumps(ui_tree, indent=2)
        else:
            # If the tree is entirely empty, seed a default empty Page
            tree_str = json.dumps({
                "root": {
                    "type": "Page",
                    "props": {"className": "min-h-screen bg-gray-50"},
                    "children": []
                }
            }, indent=2)

        try:
            print("💬 Streaming JSON Tree from LLM...")
            updated_json = stream_llm_json(
                self.designer_prompt | self.llm,
                {"ui_tree": tree_str, "plan": plan, "format_instructions": self.parser.get_format_instructions()},
                label="UI DESIGNER AGENT"
            )
            
            if not updated_json:
                raise ValueError("Streamer returned empty JSON. Falling back to original tree.")
            
            print(f"✅ [UI DESIGNER AGENT] TREE COMPLETE\n" + "="*50)
            new_tree_state = UITreeState(**updated_json)
            return {"ui_tree": new_tree_state}
            
        except Exception as e:
            print(f"Error in UIDesignerAgent: {e}")
            # On failure, return the exact original tree untouched
            return {"ui_tree": ui_tree}

def ui_structure_node(state: dict):
    agent = UIDesignerAgent()
    return agent.design(state)
