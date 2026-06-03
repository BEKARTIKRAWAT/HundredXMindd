import json
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:latest")
def debate(question: str, rounds: int = 1) -> str:
    # Agent 1
    agent1 = llm.invoke(f"Answer concisely: {question}")
    # Agent 2 critiques and improves
    agent2 = llm.invoke(f"Critique this answer and give a better one. Answer to critique: '{agent1}'. Your improved answer:")
    for _ in range(rounds):
        agent1 = llm.invoke(f"Improve your answer after hearing this: '{agent2}'. Your new answer:")
        agent2 = llm.invoke(f"Improve your answer after hearing this: '{agent1}'. Your new answer:")
    # Judge: output JSON with "final_answer" key
    judge_prompt = f"""Question: {question}
Candidate A: {agent1}
Candidate B: {agent2}
Decide the correct answer. Output ONLY a JSON object: {{"final_answer": "your answer here"}}"""
    response = llm.invoke(judge_prompt)
    try:
        # Extract JSON block
        start = response.find('{')
        end = response.rfind('}') + 1
        data = json.loads(response[start:end])
        return data.get("final_answer", "Unable to determine")
    except:
        # Fallback: take last line
        return response.strip().split('\n')[-1]
