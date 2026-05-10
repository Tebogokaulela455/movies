import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto
import uvicorn

app = FastAPI()

# --- THE AGGRESSIVE CORS FIX ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # This allows local files (null) and web files
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ma = MovieAuto()

@app.get("/api/trending")
async def get_trending():
    try:
        # Fetch movies from the wrapper
        movies = ma.movies()
        # Ensure we return valid data even if the wrapper returns None
        return {"results": movies if movies else []}
    except Exception as e:
        return {"results": [], "error": str(e)}

@app.get("/api/search")
async def search(q: str = Query(...)):
    try:
        results = ma.search(q)
        return {"results": results if results else []}
    except Exception as e:
        return {"results": [], "error": str(e)}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    try:
        links = ma.get_links(movie_id)
        if links and len(links) > 0:
            # We look for the first valid MP4 or HLS link
            return {"stream_url": links[0].get('url')}
        return {"error": "No playable link found for this movie."}
    except Exception as e:
        return {"error": f"Failed to fetch links: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)