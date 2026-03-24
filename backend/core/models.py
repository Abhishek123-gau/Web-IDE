from typing import List, Literal, Dict, Any, Optional
from pydantic import BaseModel, Field

# 1. Define Valid Component Types
ComponentType = str

# 2. Define the exact Component Node
class UIComponent(BaseModel):
    """Represents a single UI node in the component tree."""
    
    type: ComponentType = Field(
        ...,
        description="The type of the component (e.g., Navbar, Hero, Button)."
    )
    
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs for properties like styling (e.g., tailwind classes), text content, src links, etc."
    )
    
    # Use forward reference string since UIComponent is self-referencing
    children: Optional[List['UIComponent']] = Field(
        default_factory=list,
        description="Nested child components within this node."
    )

# Required by Pydantic to resolve forward references like List['UIComponent']
UIComponent.model_rebuild() #it runs the recusve to get it in proper format instead of reference things

# 3. Define the Root UI Tree State
class UITreeState(BaseModel):
    """The root representation of the entire generated webpage."""
    
    root: UIComponent = Field(
        ...,
        description="The root node of the webpage, usually of type 'Page'."
    )

# ==========================================
# Planner Output Schema
# ==========================================
class PlannerOutput(BaseModel):
    """The structured output format from the Planner agent."""
    
    explanation: str = Field(
        ...,
        description="A detailed, multi-sentence explanation of the design approach, layout strategy, and component choices (especially if the UI tree is new), or a brief reasoning for modifications."
    )
    
    action_plan_steps: List[str] = Field(
        ...,
        description="A list of concise, actionable steps for the UI Designer. Each step must describe ONE UI change (add, modify, or remove) targeting exact component names."
    )

# ==========================================
# Generate and Print the JSON Schema
# Useful for providing strict generation rules to LLMs
# ==========================================
if __name__ == "__main__":
    import json
    
    # Generate schema
    schema = UITreeState.model_json_schema()
    
    print("--- UI Tree JSON Schema ---")
    print(json.dumps(schema, indent=2))
    
    print("\n--- Example Instantiation ---")
    # Example usage creating a tree
    example_tree = UITreeState(
        root=UIComponent(
            type="Page",
            props={"className": "min-h-screen bg-gray-50"},
            children=[
                UIComponent(
                    type="Navbar",
                    props={"title": "My Startup"},
                    children=[]
                ),
                UIComponent(
                    type="Hero",
                    props={
                        "headline": "Build faster",
                        "subheading": "The ultimate AI tool",
                        "className": "py-20 text-center"
                    },
                    children=[
                        UIComponent(
                            type="Button",
                            props={"label": "Get Started", "variant": "primary"},
                            children=[]
                        )
                    ]
                )
            ]
        )
    )
    
    print(example_tree.model_dump_json(indent=2))
