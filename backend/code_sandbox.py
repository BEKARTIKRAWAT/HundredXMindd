import subprocess
import tempfile
import os
def run_python_code(code: str, timeout: int = 30) -> str:
    """
    Runs Python code in a sandboxed temporary file.
    Returns stdout + stderr output.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ['python', tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Execution timed out (max {} seconds).".format(timeout)
    except Exception as e:
        return f"Execution error: {str(e)}"
    finally:
        os.unlink(tmp_path)
