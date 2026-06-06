import os
def file_reader(filepath: str, max_lines: int = 50) -> str:
    """Read a text file and return its content (first `max_lines` lines)."""
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        content = ''.join(lines[:max_lines])
        if len(lines) > max_lines:
            content += f"\n... (truncated, {len(lines)-max_lines} more lines)"
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"
