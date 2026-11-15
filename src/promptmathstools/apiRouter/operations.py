import time
import json
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from promptmathstools.agents.math_solver_agent import build_math_agent
from promptmathstools.utility.common import classify_problem_async

router = APIRouter(
    prefix="/operations",
    tags=["operations"],
)


@router.get("/", summary="Operations Home Page", description="Welcome to the Operations Home Page")
async def operationsHome():
    print("\n [operationsHome()] started")
    try:
        return {"message": "Welcome to the Operations Home Page"}
    except Exception as error:
        print(f"\n [operationsHome()] error: {error!r}")
        raise
    finally:
        print("\n [operationsHome()] ended")


# Build the agent once at startup instead of rebuilding on every HTTP request
math_agent_executor = build_math_agent()


# ==========================================
# REQUEST / RESPONSE SCHEMAS
# ==========================================
class MathRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=[
        "I have 100 rupees. I bought 500gm apples. 10kg apples cost was 1000 rupees, so how much am I left with?"
    ])


class MathResponse(BaseModel):
    category: str
    planned_tools: list[str]
    answer: str


# ==========================================
# ENDPOINT 1: STANDARD JSON (Easy Swagger Testing)
# ==========================================
@router.post(
    "/classifyType",
    response_model=MathResponse,
    summary="Classify Math Problem Type",
    description="Classifies the type of math problem and provides a solution.",
)
async def solve_math_json(req: MathRequest):
    print("\n [solve_math_json()] started")
    try:
        # 1. Structured Output Prompting (async invoke)
        classification = await classify_problem_async(req.question)

        # 2. Agent + Tools Execution
        result = await math_agent_executor.ainvoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"Problem category: {classification.category}\n"
                    f"Question: {req.question}"
                ),
            }],
        })

        return MathResponse(
            category=classification.category,
            planned_tools=classification.suggested_tools,
            answer=result["messages"][-1].content,
        )
    except Exception as e:
        print(f"\n [solve_math_json()] error: {e!r}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("\n [solve_math_json()] ended")


# ==========================================
# ENDPOINT 2: LIVE EVENT STREAMING (For HTML/JS UI)
# ==========================================

@router.post("/solveProblem", response_class=StreamingResponse)
async def solve_math_stream(req: MathRequest):
    async def event_generator():
        try:
            t0 = time.perf_counter()
            yield f"data: {json.dumps({'stage': 'classifier', 'status': 'running', 'message': 'Analyzing problem structure & routing...'})}\n\n"
            classification = await classify_problem_async(req.question)
            clf_ms = round((time.perf_counter() - t0) * 1000)

            yield f"data: {json.dumps({'stage': 'classifier', 'status': 'done', 'category': classification.category, 'planned_tools': classification.suggested_tools, 'duration_ms': clf_ms})}\n\n"

            tool_timers = {}
            final_answer = ""
            last_tool_output = ""

            async for event in math_agent_executor.astream_events(
                {"messages": [("user", f"Category: {classification.category}\nQuestion: {req.question}")]},
                version="v2",
            ):
                kind = event["event"]
                run_id = event.get("run_id")

                # 1. Capture LLM Thinking / Planning turns
                if kind == "on_chat_model_start":
                    yield f"data: {json.dumps({'stage': 'llm', 'status': 'running', 'message': 'Agent reasoning & selecting next action...'})}\n\n"

                # 2. Capture Verbose Tool Start (with exact arguments)
                elif kind == "on_tool_start":
                    tool_timers[run_id] = time.perf_counter()
                    yield f"data: {json.dumps({'stage': 'tool', 'status': 'running', 'run_id': run_id, 'tool': event['name'], 'args': event['data'].get('input')})}\n\n"

                # 3. Capture Verbose Tool Result (with duration in ms)
                elif kind == "on_tool_end":
                    elapsed_ms = round((time.perf_counter() - tool_timers.get(run_id, time.perf_counter())) * 1000)
                    raw_out = event["data"].get("output")
                    clean_out = raw_out.content if hasattr(raw_out, "content") else str(raw_out)
                    last_tool_output = clean_out  # Keep track of the latest computed tool result!

                    yield f"data: {json.dumps({'stage': 'tool', 'status': 'done', 'run_id': run_id, 'tool': event['name'], 'args': event['data'].get('input'), 'output': clean_out, 'duration_ms': elapsed_ms})}\n\n"

                # 4. Track latest AI text message reliably regardless of root graph name
                elif kind == "on_chat_model_end":
                    msg = event["data"].get("output")
                    if msg and not getattr(msg, "tool_calls", None):
                        text_val = getattr(msg, "text", None) or getattr(msg, "content", "")

                        if isinstance(text_val, list):
                            text_val = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in text_val)

                        if isinstance(text_val, str) and text_val.strip():
                            final_answer = text_val.strip()
                            
                 # Use the LLM's explanation if available, otherwise fall back directly to the last tool's output!
                resolved_answer = final_answer or last_tool_output or "No answer generated."
                yield f"data: {json.dumps({'stage': 'complete', 'answer': resolved_answer})}\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
