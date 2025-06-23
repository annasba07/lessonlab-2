from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from routes.lessons import router as lessons_router
from routes.health import router as health_router

load_dotenv()

app = FastAPI(
    title="Lesson Lab 2.0 API",
    description="AI-powered lesson plan generator backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://lessonlab-2.*\.vercel\.app",
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "https://lessonlab-2.onrender.com",
        "https://lessonlab-2.vercel.app"  # Stable production URL
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(lessons_router, prefix="/api/lessons", tags=["lessons"])

# Redirect root to docs for demo convenience
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)