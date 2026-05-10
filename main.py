import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# --- THE CORS FIX ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits all domains (Netlify, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permits GET, POST, etc.
    allow_headers=["*"],
)

# Mock database for "Previews" shown before search
TRENDING_MOVIES = [
    {"id": 101, "title": "Inception", "cover": "https://picsum.photos/300/450?random=11"},
    {"id": 102, "title": "The Dark Knight", "cover": "https://picsum.photos/300/450?random=12"},
    {"id": 103, "title": "Interstellar", "cover": "https://picsum.photos/300/450?random=13"},
    {"id": 104, "title": "Gladiator II", "cover": "https://picsum.photos/300/450?random=14"}
]

@app.get("/api/trending")
async def get_trending():
    return {"results": TRENDING_MOVIES}

@app.get("/api/search")
async def search(q: str = Query(...)):
    # Here is where you'd actually call the moviebox-api wrapper
    # For now, returning a result based on search
    return {"results": [{"id": 999, "title": f"Result for: {q}", "cover": "https://picsum.photos/300/450?random=1"}]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)