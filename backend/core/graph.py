from typing import TypedDict, List, Union, Optional
from langgraph.graph import StateGraph, END

try:
    from backend.core.models import UITreeState
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.models import UITreeState

from backend.agents.planner import planner_node
from backend.agents.ui_designer import ui_structure_node
from backend.agents.code_generator import code_generation_node
from backend.agents.debugger import debug_node
from backend.agents.renderer import preview_node

# Define the Shared State Schema
class UIState(TypedDict):
    chat_history: List[str]
    ui_tree: Union[UITreeState, dict] # Can hold the Pydantic instance or raw dict
    generated_code: str
    build_error: Optional[str] # Used for routing to debugger
# Routing Logic function
def check_preview_status(state: UIState):
    """
    Determines the next node based on whether the preview node emitted an error
    """
    if state.get("build_error"):
        return "debug_node"
    return END

def check_debug_status(state: UIState):
    """
    After the debugger runs, if it cleared the error, end the graph.
    If a real fixable error remains, retry via code_generation_node.
    """
    if state.get("build_error"):
        return "code_generation_node"  # Debugger fixed code, retry preview
    return END  # Debugger escaped - exit gracefully

# Build the Graph
workflow = StateGraph(UIState)

# Add Nodes
workflow.add_node("planner_node", planner_node)
workflow.add_node("ui_structure_node", ui_structure_node)
workflow.add_node("code_generation_node", code_generation_node)
workflow.add_node("preview_node", preview_node)
workflow.add_node("debug_node", debug_node)

# Define the Flow/Edges
workflow.set_entry_point("planner_node")
workflow.add_edge("planner_node", "ui_structure_node")
workflow.add_edge("ui_structure_node", "code_generation_node")
workflow.add_edge("code_generation_node", "preview_node")

# Add Conditional Edge from preview_node
workflow.add_conditional_edges(
    "preview_node",
    check_preview_status,
    {
        "debug_node": "debug_node",
        END: END
    }
)

# Add Conditional Edge from debug_node (prevents infinite loop)
# If debugger fixed the error -> retry code generation
# If debugger couldn't fix (escaped) -> go to END
workflow.add_conditional_edges(
    "debug_node",
    check_debug_status,
    {
        "code_generation_node": "code_generation_node",
        END: END
    }
)

# Compile the Graph
app = workflow.compile()

# Graph exported as app
