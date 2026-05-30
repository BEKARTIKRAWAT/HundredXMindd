from graph import graph, AgentState
def run_with_hitl(question: str):
    config = {"configurable": {"thread_id": "user_1"}}
    initial_state = {
        "question": question,
        "plan": "",
        "retrieved_docs": [],
        "analysis": "",
        "draft_answer": "",
        "approved": False,
        "final_answer": "",
        "score": 0,
        "retries": 0
    }
    print("Running agents with self-evaluation...")
    for event in graph.stream(initial_state, config, stream_mode="values"):
        if "draft_answer" in event and event["draft_answer"]:
            print(f"\n[DRAFT]: {event['draft_answer'][:200]}...")
        if "score" in event:
            print(f"[SCORE]: {event['score']}")
    state = graph.get_state(config)
    draft = state.values.get("draft_answer", "No answer")
    score = state.values.get("score", 0)
    print(f"\n[EVALUATION] Score: {score}/10")
    print(f"Answer: {draft}")
    if score >= 7:
        user_input = input("\nApprove? (yes/y): ").strip().lower()
        if user_input in ["yes", "y"]:
            graph.update_state(config, {"approved": True})
            final_state = graph.invoke(None, config)
            final_ans = final_state.get("final_answer", "No final answer")
            print(f"\n[FINAL]: {final_ans}")
        else:
            print("Rejected.")
    else:
        print(f"Score too low ({score}). Auto-retry may happen, but you can run again.")
if __name__ == "__main__":
    run_with_hitl("What is Retrieval Augmented Generation?")
