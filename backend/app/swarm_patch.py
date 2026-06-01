# ---------- Agent Swarm Endpoint ----------
from app.agents.agent_swarm import run_agent_swarm
class SwarmRequest(BaseModel):
    question: str
@app.post("/swarm")
@limiter.limit("10/minute")
async def swarm_endpoint(request: Request, swarm_req: SwarmRequest):
    try:
        result = run_agent_swarm(swarm_req.question)
        return {"question": swarm_req.question, "answer": result, "route": "swarm"}
    except Exception as e:
        logger.error(f"Swarm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
