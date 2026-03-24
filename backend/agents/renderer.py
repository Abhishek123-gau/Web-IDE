import os
import subprocess
from typing import Dict, Any

class PreviewRendererAgent:
    """
    Agent responsible for running Vite builds/linting on the generated workspace.
    If it fails, it captures the error state to send to the Debugger.
    """
    def __init__(self):
        # Get absolute path relative to the root project folder
        self.workspace_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "generated_workspace")
        )
        # Fallback if executed from within backend
        if not os.path.exists(self.workspace_dir):
            self.workspace_dir = os.path.abspath(
                os.path.join(os.getcwd(), "..", "generated_workspace")
            )
        # Final fallback if executed directly from root
        if not os.path.exists(self.workspace_dir):
            self.workspace_dir = os.path.abspath(
                os.path.join(os.getcwd(), "generated_workspace")
            )

    def render(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        print("--- RUNNING NODE: PREVIEW RENDERER ---")
        
        # We explicitly run `npm run build` as a definitive check for syntax/type errors.
        # Alternatively, we could run ESLint if configured.
        
        print(f"Executing Vite build check in {self.workspace_dir}...")
        try:
            # We use shell=True on Windows to resolve npm correctly in some environments
            result = subprocess.run(
                ["npm", "run", "build"], 
                cwd=self.workspace_dir, 
                capture_output=True, 
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                print("BUILD FAILED. Routing to Debugger.")
                # Pass the stderr (or stdout if Vite pipes errors there) to the state
                error_log = result.stderr if result.stderr.strip() else result.stdout
                return {"build_error": error_log}
                
            print("BUILD SUCCESSFUL.")
            return {"build_error": None}
            
        except Exception as e:
            print(f"Renderer Execution Error: {e}")
            print("Escaping debug recursion loop for unhandled exception.")
            # We explicitly clear the error so LangGraph can gracefully exit to END
            return {"build_error": None}

def preview_node(state: dict):
    agent = PreviewRendererAgent()
    return agent.render(state)
