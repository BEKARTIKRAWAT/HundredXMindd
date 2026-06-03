import importlib
import os
import sys
TOOLS_DIR = os.path.dirname(__file__)
sys.path.insert(0, TOOLS_DIR)
def load_all_tools():
    tools = {}
    for filename in os.listdir(TOOLS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            modname = filename[:-3]
            try:
                module = importlib.import_module(modname)
                if hasattr(module, modname):
                    tools[modname] = getattr(module, modname)
                else:
                    for attr in dir(module):
                        if callable(getattr(module, attr)) and not attr.startswith('_'):
                            tools[modname] = getattr(module, attr)
                            break
            except Exception as e:
                print(f"Error loading {modname}: {e}")
    return tools
_dynamic_tools = load_all_tools()
def get_tool(name):
    return _dynamic_tools.get(name)
