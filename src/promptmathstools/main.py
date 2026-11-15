from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
# Import StaticFiles for css, js file while rendering widget.html
from fastapi.staticfiles import StaticFiles
from promptmathstools.apiRouter import operations
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Math AI Capstone API",
    description="Multi-tool LangChain Math Solver with Prompt Engineering & Live Event Streaming",
    version="1.0.0",
)


# Allow your React frontend to connect
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8921"],  # Update this to your frontend's URL
    allow_methods=["*"],
    allow_headers=["*"],
)'''


# Explicit route to catch "/" and send index.html directly
@app.get("/")
async def root():
    print("\n [root()] started")
    try:
        return FileResponse("frontend/index.html")
    except Exception as error:
        print(f"\n [root()] error: {error!r}")
        raise
    finally:
        print("\n [root()] ended")


# Include the auth router
app.include_router(operations.router)

# Static directory mounted to capture style.css and app.js
app.mount("/", StaticFiles(directory="frontend"), name="frontend")