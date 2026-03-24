import os
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
try:
    from backend.core.streamer import stream_llm
except ImportError:
    import sys as _sys, os as _os
    _sys.path.append(_os.path.join(_os.path.dirname(__file__), '..'))
    from core.streamer import stream_llm
import json
import re

# Temporary import path for our models since this will be run from the root or within backend/
try:
    from backend.core.models import UITreeState, UIComponent
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.models import UITreeState, UIComponent

class CodeGeneratorAgent:
    """
    Agent responsible for converting a json component tree into responsive React + Tailwind code.
    Designed to work with DeepSeek-Coder by 
    chunking generation per component instead of attempting a whole-app generation at once.
    """
    
    def __init__(self, model_name: str = "deepseek-coder:6.7b", base_url: str = "http://localhost:11434", workspace_dir: str = "generated_workspace"):
        # Initialize standard directory paths for the output structure
        self.src_dir = "src"
        self.components_dir = os.path.join(self.src_dir, "components")
        self.pages_dir = os.path.join(self.src_dir, "pages")
        
        # We will hold the generated files in memory mapping -> {filepath: filecontent}
        self.generated_files: Dict[str, str] = {}
        
        # Setup the local LLM using Langchain's Ollama integration
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.1)
        
        # Define the system prompt for generating a single responsive component
        self.component_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are DeepSeek-Coder, an expert Frontend Developer and UI Designer. Your task is to generate a SINGLE reusable React component using Tailwind CSS.\n"
             "CRITICAL STRICT RULES:\n"
             "1. Output ONLY RAW REACT CODE. No markdown fences (```jsx). No explanations. No conversation.\n"
             "2. Do NOT say 'Here is the code' or 'Sure, here is'.\n"
             "3. If child components are specified, you MUST import them using `import ChildName from './ChildName';`.\n"
             "4. Do NOT include anything outside of the imports and the default export.\n"
             "5. CRITICAL: If child components are given, you MUST structurally include `<ChildName />` tags inside your component's JSX `return (...)` block to physically render them on screen.\n"
             "6. AESTHETICS: Make the design absolutely stunning, modern, and premium! Use rounded corners (rounded-2xl), soft shadows (shadow-xl), smooth gradients, hover micro-interactions (hover:scale-105 transition-all), and proper spacing.\n"
             "7. PROPS: If props like 'label', 'text', 'value', or 'className' are passed, you MUST inject them dynamically into the component's JSX.\n"
             "8. CRITICAL: Do NOT invent or import any other random components (like 'Text', 'Icon', etc). Only use standard HTML tags or the exact children passed to you."
            ),
            ("user", 
             "Create a React component named '{component_name}'.\n"
             "It should incorporate the following data/props:\n{props_json}\n"
             "It should contain the following child components:\n{children_list}\n"
            )
        ])
        
        self.component_chain = self.component_prompt | self.llm
        
        # New prompt for generating the final cohesive Page that wires everything up
        self.page_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are DeepSeek-Coder, an expert Frontend Developer and UI Designer. Your task is to generate the SINGLE React Page (Home.jsx) that pieces together the provided UI components.\n"
             "CRITICAL STRICT RULES:\n"
             "1. Output ONLY RAW REACT CODE. No markdown fences (```jsx). No explanations. No conversation.\n"
             "2. You MUST import the generic child components from '../components/<Name>'.\n"
             "3. STATE AND LOGIC: If this app resembles a calculator, a form, or any interactive tool, you MUST use `useState` and function callbacks to wire up the interactive logic!\n"
             "4. PROPS: You must pass the required props to the children so they render properly (e.g., text, labels, onClick).\n"
             "5. AESTHETICS: Wrap the page in a beautiful Tailwind CSS layout (min-h-screen bg-gray-50 flex flex-col).\n"
            ),
            ("user", 
             "Create the React page named '{page_name}'.\n"
             "You have the following child components available to import and use. Read their signatures to understand what props they need:\n"
             "{available_components_context}\n\n"
             "Please render these components together cohesively and wire them together using React state if interactivity is implied."
            )
        ])
        
        self.page_chain = self.page_prompt | self.llm
        
        # Tracking to ensure we don't regenerate the same component multiple times
        self._generated_component_names: set = set()

    def generate_codebase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main entrypoint for the LangGraph node.
        Reads the ui_tree from the state, generates the files, and returns the modified state.
        """
        tree_data = state.get("ui_tree")
        if not tree_data:
            return {"generated_code": "Error: No UI Tree provided."}
        print("Tree data is : ", tree_data  )  
        # Parse into Pydantic model
        if isinstance(tree_data, dict):
            tree = UITreeState(**tree_data)
        else:
            tree = tree_data
            
        self.generated_files = {}
        self._generated_component_names = set()
        
        # 1. Scaffolding standard setup (App.jsx, index.css)
        self._generate_scaffolding()
        
        # 2. Traverse the component tree and generate reusable components via LLM
        root_component = tree.root
        self._traverse_and_build(root_component)
        
        # 3. Generate the Page that holds the primary UI Tree
        self._generate_page(root_component)
        
        # In the context of the workflow, we either return the stringified codebase 
        # for a later Node to write to disk, or write it directly.
        # Here we format a large string summarizing the generated files.
        code_summary = self._format_files_for_state()
        
        # (Optional) You can directly write them to a workspace folder here:
        # self.write_to_workspace("./generated_workspace")
        
        return {"generated_code": code_summary}

    def _traverse_and_build(self, node: UIComponent):
        """Recursively isolates complex components and sends them to the LLM for generation."""
        if node.type != "Page" and node.type[0].isupper() and node.type not in self._generated_component_names:
            self._call_llm_for_component(node)
            self._generated_component_names.add(node.type)
            
        for child in node.children or []:
            if isinstance(child, UIComponent):
                self._traverse_and_build(child)

    def _call_llm_for_component(self, node: UIComponent):
        """Uses the local LLM to generate a specific React component string."""
        print("\n" + "="*50)
        print(f"⚙️ [CODE GENERATOR AGENT] WRITING {node.type}.jsx...")
        print("="*50)
        
        # Prepare inputs for the LLM
        props_str = json.dumps(node.props, indent=2)
        children_types = [child.type for child in (node.children or [])]
        children_str = ", ".join(children_types) if children_types else "None"
        
        print(f"[INPUT CACHE]\nProps passed: {props_str}")
        print(f"Children nodes to render: {children_str}\n")
        
        try:
            content = stream_llm(
                self.component_chain,
                {"component_name": node.type, "props_json": props_str, "children_list": children_str},
                label=f"CODE GEN [{node.type}]"
            )
            
            # Robustly extract code block if the LLM hallucinated markdown headers
            match = re.search(r"```(?:jsx|javascript|tsx|ts|react)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
            else:
                # Fallback: if there are no backticks, try to clean raw strings just in case
                content = content.replace("```jsx", "").replace("```", "").strip()
                
            filepath = os.path.join(self.components_dir, f"{node.type}.jsx").replace("\\", "/")
            self.generated_files[filepath] = content
            print(f"✅ [CODE GENERATOR AGENT] BUILT {node.type}.jsx:\n{content[:300]}...\n" + "="*50)
            
        except Exception as e:
            print(f"Error generating {node.type}: {str(e)}")
            # Fallback trivial generation on LLM failure
            fallback = f"export default function {node.type}() {{ return <div className='p-4 border border-red-500'>Error loading {node.type} Component</div> }}\n"
            filepath = os.path.join(self.components_dir, f"{node.type}.jsx").replace("\\", "/")
            self.generated_files[filepath] = fallback

    def _generate_page(self, root_node: UIComponent):
        """Generates a Next.js or React page that imports and maps out the generated components using the LLM."""
        print("\n" + "="*50)
        print(f"⚙️ [CODE GENERATOR AGENT] COMPOSING ROOT PAGE {root_node.type}.jsx...")
        print("="*50)
        
        # Build context for the LLM to know what it has to work with
        available_components_context = []
        for child in root_node.children or []:
            if child.type != "Page" and child.type[0].isupper():
                # Give a signature hint based on the props this child was initialized with
                props_hint = json.dumps(child.props, indent=2)
                available_components_context.append(f"- Component: `{child.type}` | Original Intended Props: {props_hint}")
                
        context_str = "\n".join(available_components_context)

        try:
            content = stream_llm(
                self.page_chain,
                {"page_name": "Home", "available_components_context": context_str},
                label="CODE GEN [Home Page]"
            )
            
            # Robust extraction of jsx codeblock
            match = re.search(r"```(?:jsx|javascript|tsx|ts|react)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
            else:
                content = content.replace("```jsx", "").replace("```", "").strip()
                
            filepath = os.path.join(self.pages_dir, "Home.jsx").replace("\\", "/")
            self.generated_files[filepath] = content
            print(f"✅ [CODE GENERATOR AGENT] BUILT Home.jsx:\n{content[:300]}...\n" + "="*50)
            
        except Exception as e:
            print(f"Error generating Home Page: {str(e)}")
            # Fallback simple generation if the LLM completely fails
            imports = [f"import {c.split('`')[1]} from '../components/{c.split('`')[1]}';" for c in available_components_context if '`' in c]
            components_to_render = [f"      <{c.split('`')[1]} />" for c in available_components_context if '`' in c]
            fallback_code = f"import React from 'react';\n" + "\n".join(imports) + \
                            f"\n\nexport default function Home() {{\n  return (\n    <div className=\"min-h-screen bg-white\">\n" + \
                            "\n".join(components_to_render) + "\n    </div>\n  );\n}\n"
            filepath = os.path.join(self.pages_dir, "Home.jsx").replace("\\", "/")
            self.generated_files[filepath] = fallback_code

    def _generate_scaffolding(self):
        """Generates the main entry point files like App.jsx."""
        
        app_code = """import React from 'react';
import Home from './pages/Home';
import './index.css';

function App() {
  return (
    <Home />
  );
}

export default App;
"""
        filepath = os.path.join(self.src_dir, "App.jsx").replace("\\", "/")
        self.generated_files[filepath] = app_code

    def _format_files_for_state(self) -> str:
        """Serializes the generated dict into a string for LangGraph state if needed."""
        # This is a simple representation. In reality, the node could save them to disk 
        # and simply pass the workspace folder path in the state.
        return json.dumps(self.generated_files, indent=2)

    def write_to_workspace(self, workspace_path: str):
        """Utility function to physically write the generated components to the filesystem."""
        for relative_path, content in self.generated_files.items():
            full_path = os.path.join(workspace_path, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        print(f"CodeGeneratorAgent: Successfully wrote {len(self.generated_files)} files to {workspace_path}")

# ==========================================
# Graph Node Wrapper
# ==========================================
def code_generation_node(state: dict):
    """
    The actual function to be plugged into the LangGraph workflow.
    """
    print("--- RUNNING NODE: CODE GENERATOR ---")
    agent = CodeGeneratorAgent()
    
    # If a build_error exists, we might normally adjust the prompt. For now, we regenerate.
    # In a fully fleshed out system, the CodeGeneratorAgent would accept the error log
    # and ask the LLM to fix the faulty component.
    
    result = agent.generate_codebase(state)
    
    # Write to local workspace for the renderer preview_node to pick up
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "generated_workspace"))
    if not os.path.exists(workspace_dir):
         workspace_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "generated_workspace"))
    if not os.path.exists(workspace_dir):
         workspace_dir = os.path.abspath(os.path.join(os.getcwd(), "generated_workspace"))
         
    agent.write_to_workspace(workspace_dir)
    
    return {"generated_code": result["generated_code"]}
