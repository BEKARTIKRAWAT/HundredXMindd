from openai import OpenAI
from swarm import Swarm, Agent
# Configure Ollama to work with OpenAI client
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
client = Swarm(client=client)
def transfer_to_research_agent(**kwargs):
    """Transfer to research agent."""
    return research_agent
def transfer_to_writing_agent(**kwargs):
    """Transfer to writing agent."""
    return writing_agent
# Supervisor Agent
supervisor_agent = Agent(
    name="Supervisor",
    instructions="""You are a manager. Route user questions to the appropriate expert agent.
    - Research, facts, definitions → Research Agent
    - Writing, drafting, emails → Writing Agent
    - Otherwise answer directly.
    """,
    functions=[transfer_to_research_agent, transfer_to_writing_agent],
    model="llama3.2:latest"
)
# Research Agent
research_agent = Agent(
    name="Research Agent",
    instructions="You are a research agent. Provide accurate factual information.",
    model="llama3.2:latest"
)
# Writing Agent
writing_agent = Agent(
    name="Writing Agent",
    instructions="You are a writing assistant. Create content in a professional tone.",
    model="llama3.2:latest"
)
def run_agent_swarm(question: str) -> str:
    response = client.run(
        agent=supervisor_agent,
        messages=[{"role": "user", "content": question}],
    )
    return response.messages[-1]["content"]
