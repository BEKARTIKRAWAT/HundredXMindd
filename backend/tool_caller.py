from tools.calculator import calculator
from tools.file_reader import file_reader
from web_search import web_search
TOOLS = {
    "calculator": calculator,
    "file_reader": file_reader,
    "web_search": web_search
}
def call_tool(tool_name: str, params: dict) -> str:
    """Execute a tool with given parameters and return the result."""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found. Available: {list(TOOLS.keys())}"
    tool_func = TOOLS[tool_name]
    try:
        result = tool_func(**params)
        return str(result)
    except TypeError as e:
        return f"Error: Missing or invalid parameters for {tool_name}: {e}"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
