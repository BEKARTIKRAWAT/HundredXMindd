@app.post("/web_auto")
@limiter.limit("5/minute")
def web_auto_endpoint(request: Request, req: WebActionRequest):
    try:
        result = perform_action(req.action, req.params)
        return {"action": req.action, "result": result}
    except Exception as e:
        logger.error(f"Web automation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
