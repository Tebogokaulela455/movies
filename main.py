import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto # The wrapper you installed
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the MovieBox API
ma = MovieAuto()

@app.get("/api/trending")
async def get_trending():
    # Gets real trending movies from the API
    movies = ma.movies() 
    return {"results": movies}

@app.get("/api/search")
async def search(q: str = Query(...)):
    # Searches the actual MovieBox database
    results = ma.search(q)
    return {"results": results}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    # This finds the actual playable MP4/Stream link
    # Note: Depending on the API version, you might need to extract the 'url'
    links = ma.get_links(movie_id)
    if links:
        return {"stream_url": links[0]['url']} 
    return {"error": "No link found"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)