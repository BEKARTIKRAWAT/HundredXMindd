def route_query(question: str) -> str:
    q = question.lower()
    # Coding keywords
    code_words = [
        "code", "function", "program", "debug", "algorithm",
        "python", "javascript", "c++", "java", "script",
        "write a", "implement", "reverse a string", "sort",
        "array", "list", "loop", "recursion", "api"
    ]
    # Reasoning keywords
    reasoning_words = [
        "calculate", "speed", "average", "sum", "math",
        "solve", "if then", "probability", "logic",
        "train travels", "distance", "time", "rate",
        "equation", "formula", "compute", "how many"
    ]
    if any(word in q for word in code_words):
        return "code"
    if any(word in q for word in reasoning_words):
        return "reasoning"
    return "general"
