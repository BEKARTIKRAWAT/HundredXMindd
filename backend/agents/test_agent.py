from graph import graph, AgentState
def run_agent(question: str):
    initial_state: AgentState = {
        "question": question,
        "plan": "",
        "retrieved_docs": [],
        "analysis": "",
        "draft_answer": "",
        "approved": False,
        "final_answer": ""
    }
    result = graph.invoke(initial_state)
    print(f"Question: {question}")
    print(f"Plan: {result['plan'][:200]}...")
    print(f"Draft answer: {result['draft_answer']}")
    print(f"Final answer: {result['final_answer']}")
    return result
if __name__ == "__main__":
    run_agent("What is Retrieval Augmented Generation?")
