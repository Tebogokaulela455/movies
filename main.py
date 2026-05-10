import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto
import uvicorn

app = FastAPI()

# 1. CORS Configuration (as a backup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the API wrapper
ma = MovieAuto()

# 2. SERVE FRONTEND DIRECTLY (This kills CORS errors forever)
@app.get("/", response_class=HTMLResponse)
async def get_index():
    # We load your index.html file and serve it from the root URL
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html not found in project folder</h1>"

# 3. API ENDPOINTS
@app.get("/api/trending")
async def get_trending():
    try:
        # Calls the trending movies from the library
        movies = ma.movies()
        return {"results": movies if movies else []}
    except Exception:
        return {"results": []}

@app.get("/api/search")
async def search(q: str = Query(...)):
    try:
        results = ma.search(q)
        return {"results": results if results else []}
    except Exception:
        return {"results": []}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    try:
        # Search first to see if details/URL are included in result
        results = ma.search(movie_id) 
        if results and isinstance(results, list):
            for res in results:
                if res.get('id') == movie_id and 'url' in res:
                    return {"stream_url": res['url']}
        
        # Fallback: check if the object has a 'links' or 'get_links' method
        if hasattr(ma, 'get_links'):
            links = ma.get_links(movie_id)
            return {"stream_url": links[0] if links else None}
        elif hasattr(ma, 'links'):
            links = ma.links(movie_id)
            return {"stream_url": links[0] if links else None}
            
        return {"error": "No stream URL found for this ID"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Use the port Render provides, or default to 10000
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)