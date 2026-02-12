import os
from langchain_core.prompts import ChatPromptTemplate

def load_prompt(prompt_name: str) -> ChatPromptTemplate:
    """
    Loads a system and user prompt from the prompts/ directory.
    
    Args:
        prompt_name: The basename of the prompt files (e.g., 'classifier')
        
    Returns:
        A ChatPromptTemplate object.
    """
    # Get the project root directory (one level up from app/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    system_path = os.path.join(base_dir, "prompts", "system", f"{prompt_name}.txt")
    user_path = os.path.join(base_dir, "prompts", "user", f"{prompt_name}.txt")
    
    if not os.path.exists(system_path):
        raise FileNotFoundError(f"System prompt not found at {system_path}")
    if not os.path.exists(user_path):
        raise FileNotFoundError(f"User prompt not found at {user_path}")
        
    with open(system_path, "r") as f:
        system_content = f.read().strip()
        
    with open(user_path, "r") as f:
        user_content = f.read().strip()
        
    return ChatPromptTemplate.from_messages([
        ("system", system_content),
        ("user", user_content)
    ])
