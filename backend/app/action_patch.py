# ---------- Action Agent Endpoint (Task Automation) ----------
from backend.action_agent import run_action_agent
class ActionRequest(BaseModel):
    user_id: str
    instruction: str
@app.post("/action")
@limiter.limit("10/minute")
async def action_endpoint(request: Request, action_req: ActionRequest):
    try:
        result = run_action_agent(action_req.user_id, action_req.instruction)
        return {"user_id": action_req.user_id, "instruction": action_req.instruction, "result": result}
    except Exception as e:
        logger.error(f"Action agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
