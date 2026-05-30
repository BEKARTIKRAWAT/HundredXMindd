from langchain_ollama import OllamaLLM
import re
eval_llm = OllamaLLM(model="llama3.2:latest")
def evaluate_answer(question: str, answer: str) -> dict:
    prompt = f"""You are a strict evaluator. Score the following answer from 1 to 10 (10 = perfect). Return ONLY a JSON object with keys "score" and "reason". No extra text.
Question: {question}
Answer: {answer}
Output: {{"score": <int>, "reason": "<brief>"}}"""
    result = eval_llm.invoke(prompt).strip()
    # Extract JSON using regex
    match = re.search(r'\{[^}]*"score"\s*:\s*(\d+)[^}]*\}', result, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        # Also try to extract reason
        reason_match = re.search(r'"reason"\s*:\s*"([^"]*)"', result)
        reason = reason_match.group(1) if reason_match else "Auto-evaluated"
        return {"score": score, "reason": reason}
    else:
        # Fallback: if no JSON, try to find a number 1-10
        numbers = re.findall(r'\b([1-9]|10)\b', result)
        if numbers:
            return {"score": int(numbers[0]), "reason": "Extracted from text"}
        return {"score": 5, "reason": "Default score due to parsing error"}
