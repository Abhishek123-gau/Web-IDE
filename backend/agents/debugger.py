import os
import re
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

class DebuggerAgent:
    """
    Agent responsible for analyzing build or runtime errors from the React app, 
    and outputting ONLY the corrected source code for the broken component.
    """
    
    def __init__(self, model_name: str = "deepseek-r1:latest", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.1)
        
        self.debug_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an Expert React Debugger. You are provided with faulty React component code "
             "and the resulting build/lint error message.\n\n"
             "Rules:\n"
             "1. Diagnose the issue using the error message.\n"
             "2. Fix the error in the provided code.\n"
             "3. **OUTPUT ONLY THE CORRECTED RAW REACT JSX CODE**. Do not include markdown code block wrappers like ```jsx or ```. "
             "Do not include any explanations. Do not include 'Here is the fixed code'."
            ),
            ("user", 
             "Faulty Code:\n"
             "{faulty_code}\n\n"
             "Error Message:\n"
             "{error_message}\n\n"
             "Return ONLY the fixed code."
            )
        ])
        
        self.chain = self.debug_prompt | self.llm
        
        # Path to where generated code is temporarily saved natively
        self.components_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "generated_workspace", "src", "components")
        )

    def _extract_component_from_error(self, error_message: str) -> Optional[str]:
        """
        Attempts to parse Vite/ESLint error logs to find which component file failed.
        Mock implementation: expects something like 'Error in src/components/Hero.jsx'
        """
        match = re.search(r'([a-zA-Z0-9_-]+)\.jsx', error_message)
        if match:
             return match.group(1)
        return None

    def debug(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        print("--- RUNNING NODE: DEBUGGER ---")
        
        error_msg = state.get("build_error")
        if not error_msg:
             print("No active error. Skipping debug.")
             return {"build_error": None}
             
        component_name = self._extract_component_from_error(error_msg)
        
        if not component_name:
             print(f"DEBUG FAILURE: Could not extract failing component name from error log: {error_msg}")
             print("Exiting debug loop to prevent infinite recursion.")
             return {"build_error": None}
             
        # Read the faulty file
        file_path = os.path.join(self.components_dir, f"{component_name}.jsx")
        if not os.path.exists(file_path):
             print(f"DEBUG FAILURE: {file_path} not found on disk. Exiting debug loop.")
             return {"build_error": None}
             
        with open(file_path, "r", encoding="utf-8") as f:
             faulty_code = f.read()

        print("\n" + "="*50)
        print(f"🐛 [DEBUGGER AGENT] ANALYZING {component_name}.jsx...")
        print("="*50)
        print(f"[INPUT CACHE]\nError Message (Vite):\n{error_msg}\n")
        
        try:
            # Invoke LLM
            response = self.chain.invoke({
                "faulty_code": faulty_code,
                "error_message": error_msg
            })
            
            fixed_code = response.content.strip()
            print(f"✅ [DEBUGGER AGENT] GENERATED FIX FOR {component_name}.jsx:\n{fixed_code[:300]}...\n" + "="*50)
            
            # Strict cleanup: LLMs often ignore "no markdown" rules
            if fixed_code.startswith("```"):
                fixed_code = re.sub(r"^```(jsx|javascript|tsx|ts|react)?", "", fixed_code)
                fixed_code = re.sub(r"```$", "", fixed_code).strip()
                
            # Overwrite the faulty file natively
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            
            # Note: We clear the build error so the graph loop knows it's ready to retry rendering
            return {"build_error": None}
            
        except Exception as e:
            print(f"Debugger Exception: {e}")
            return {"build_error": None}


def debug_node(state: dict):
    agent = DebuggerAgent()
    return agent.debug(state)
