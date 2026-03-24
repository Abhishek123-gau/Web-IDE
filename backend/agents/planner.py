import os
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
    from backend.core.models import PlannerOutput
except ImportError:
    import sys as _sys, os as _os
    _sys.path.append(_os.path.join(_os.path.dirname(__file__), '..'))
    from core.models import PlannerOutput

class PlannerAgent:
    """
    Agent responsible for analyzing the chat history and the current UI tree,
    then formulating a high-level actionable plan for the UI Designer.
    """
    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.15, num_predict=4000)
        
        self.parser = JsonOutputParser(pydantic_object=PlannerOutput)
        
        self.planner_prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are Qwen2.5, an expert UX/UI Product Manager and Planner.\n\n"
                "Your job is to read the user's UI request, analyze the current JSON UI tree, "
                "and output a structured JSON plan detailing exactly what updates should be made.\n\n"

                "STRICT RULES:\n"
                "1. Output ONLY valid JSON matching the exact schema.\n"
                "2. Provide a detailed, multi-sentence 'explanation' of your approach in the corresponding JSON field.\n"
                "3. Provide a list of 'action_plan_steps'. Each step must describe ONE UI change (add, modify, or remove).\n"
                "4. Use exact component names (e.g., 'Navbar', 'HeroSection').\n"
                "5. If adding a component, specify its location (e.g., 'Add inside Header').\n"
                "6. If the current UI tree is empty ({{}} or similar), your FIRST action step MUST be to add the requested component(s) to the 'root' Page.\n"
                "7. AESTHETICS: When adding components, ALWAYS request premium Tailwind CSS class names (like bg-gradient-to-r, shadow-2xl) by specifying the exact key-value pair for the 'props' object, e.g. 'Set className to bg-gradient-to-r'.\n\n"

                "Schema Instructions:\n{format_instructions}"
            ),
            ("user",
                "Current UI tree:\n{ui_tree}\n\n"
                "User Request:\n{chat_history}\n\n"
                "What UI changes should be made?"
            )
        ])
        
        # NOTE: We keep raw self.llm available because stream_llm_json handles the parser internally
        self.chain = self.planner_prompt | self.llm

    def plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        print("--- RUNNING NODE: PLANNER ---")
        
        chat_history = state.get("chat_history", [])
        if not chat_history:
            return {"chat_history": ["Error: No user prompt provided."]}
            
        ui_tree = state.get("ui_tree", {})
        
        print("\n" + "="*50)
        print("🧠 [PLANNER AGENT] THINKING...")
        print("="*50)
        print(f"[INPUT CACHE]\nHistory length: {len(chat_history)} messages")
        print(f"Current UI Tree explicitly passed: {ui_tree if ui_tree else 'Empty Tree'}\n")
        
        try:
            raw_chat_str = "\n".join(chat_history)
            
            print("💬 Streaming JSON Plan from LLM...")
            
            plan_json = stream_llm_json(
                self.chain,
                {
                    "chat_history": raw_chat_str, 
                    "ui_tree": str(ui_tree),
                    "format_instructions": self.parser.get_format_instructions()
                },
                label="PLANNER AGENT"
            )
            
            if not plan_json:
                raise ValueError("Streamer returned empty JSON plan.")
            
            print(f"\n✅ [PLANNER AGENT] PLAN COMPLETE\n" + "="*50)
            
            # Format the JSON output cleanly into the chat history for downstream agents
            # Downstream agents need plain text instructions, so we stringify it beautifully
            explanation = plan_json.get("explanation", "")
            steps = plan_json.get("action_plan_steps", [])
            
            formatted_plan = f"Explanation:\n{explanation}\n\nAction Steps:\n"
            for i, step in enumerate(steps, 1):
                formatted_plan += f"{i}. {step}\n"
            
            updated_history = chat_history + [f"System Plan:\n{formatted_plan.strip()}"]
            return {"chat_history": updated_history}
            
        except Exception as e:
            print(f"Error in PlannerAgent: {e}")
            return {"chat_history": chat_history + ["System Plan: Error generating plan."]}

def planner_node(state: dict):
    agent = PlannerAgent()
    return agent.plan(state)
