import sys
import os
import subprocess
import atexit
import webbrowser
import time

# Add the parent directory of 'backend' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.graph import app
from backend.core.models import UITreeState

def main():
    print("==================================================")
    print("🤖 Local AI UI Generator")
    print("==================================================")
    
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "generated_workspace"))
    if not os.path.exists(workspace_dir):
        workspace_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "generated_workspace"))
    if not os.path.exists(workspace_dir):
        workspace_dir = os.path.abspath(os.path.join(os.getcwd(), "generated_workspace"))
    print(f"[System]: Starting Live Preview Server in {workspace_dir}...")
    
    # Launch Vite in the background
    try:
        preview_process = subprocess.Popen(
            ["npm", "run", "dev"], 
            cwd=workspace_dir,
            shell=True,
            stdin=subprocess.DEVNULL,  # Prevent Vite from stealing keystrokes
            stdout=subprocess.DEVNULL, # Hide raw server logs from chat interface
            stderr=subprocess.DEVNULL
        )
        
        # Ensure the server dies when the python script dies
        atexit.register(lambda: preview_process.terminate())
        
        print("[System]: Vite Server Running on http://localhost:5173")
        print("[System]: Automatically opening your browser...")
        time.sleep(2) # Give Vite a second to bind to the port
        webbrowser.open("http://localhost:5173")
        
    except Exception as e:
        print(f"[Warning]: Failed to start preview server: {e}")

    print("==================================================")
    print("Welcome! I am a multi-agent system powered by local LLMs.")
    print("I can build and edit a React website for you based on chat.")
    print("Type 'exit' or 'quit' to leave.")
    print("==================================================\n")

    # Initialize persistent state
    current_state = {
        "chat_history": [],
        "ui_tree": {},
        "generated_code": "",
        "build_error": None
    }

    while True:
        user_input = input("You> ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Append user prompt to state
        current_state["chat_history"].append(f"User: {user_input}")

        print("\n[System]: Invoking LangGraph AI Pipeline...")
        
        try:
            # Run the LangGraph computation
            # This triggers Planner -> Designer -> Code Gen -> Preview -> (Optional Loop: Debugger)
            final_state = app.invoke(current_state)
            
            # Update our persistent loop state with the new outputs
            current_state = final_state
            
            # Print latest system plan for transparency
            plan = next((msg for msg in reversed(current_state["chat_history"]) if msg.startswith("System Plan:")), "No specific plan outputted.")
            print(f"\n[Agent Updates]\n{plan}")
            print("\n✅ UI Updated automatically in your browser preview!\n")

        except Exception as e:
            print(f"\n❌ Pipeline Error: {e}")

if __name__ == "__main__":
    main()
