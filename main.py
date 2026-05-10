import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto
import uvicorn

app = FastAPI()

# Robust CORS configuration to allow local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ma = MovieAuto()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # Serving the HTML directly from the backend solves the CORS "null" origin error
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MovieBox Live</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            :root { --primary: #ffbb00; --bg: #050505; --card: #121212; --text: #fff; }
            body { background: var(--bg); color: var(--text); font-family: sans-serif; margin: 0; }
            header { padding: 15px 5%; background: #000; display: flex; justify-content: space-between; border-bottom: 1px solid #222; }
            .logo { color: var(--primary); font-size: 1.5rem; font-weight: bold; cursor: pointer; }
            .search-bar input { padding: 8px; border-radius: 4px; border: 1px solid #333; background: #111; color: #fff; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; padding: 20px 5%; }
            .card { background: var(--card); border-radius: 8px; overflow: hidden; text-align: center; border: 1px solid #222; }
            .card img { width: 100%; height: 260px; object-fit: cover; }
            .card h3 { font-size: 0.9rem; margin: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .watch-btn { background: var(--primary); border: none; padding: 10px; width: 90%; margin-bottom: 10px; font-weight: bold; cursor: pointer; border-radius: 4px; }
            #player-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:100; justify-content:center; align-items:center; }
            video { width: 80%; max-width: 1000px; background: #000; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo" onclick="location.reload()">MOVIEBOX</div>
            <div class="search-bar">
                <input type="text" id="q" placeholder="Search..." onkeypress="if(event.key==='Enter') doSearch()">
            </div>
        </header>
        <div class="grid" id="display"></div>
        <div id="player-overlay" onclick="this.style.display='none'; document.getElementById('vid').pause();">
            <video id="vid" controls autoplay></video>
        </div>
        <script>
            async function load(path) {
                const res = await fetch(path);
                const data = await res.json();
                const grid = document.getElementById('display');
                grid.innerHTML = data.results && data.results.length ? data.results.map(m => `
                    <div class="card">
                        <img src="${m.poster || m.cover || ''}" onerror="this.src='https://via.placeholder.com/200x300?text=No+Poster'">
                        <h3>${m.title}</h3>
                        <button class="watch-btn" onclick="event.stopPropagation(); play('${m.id}')">WATCH</button>
                    </div>
                `).join('') : "<h2>No results found.</h2>";
            }
            async function doSearch() {
                const q = document.getElementById('q').value;
                await load('/api/search?q=' + encodeURIComponent(q));
            }
            async function play(id) {
                const res = await fetch('/api/get_stream?movie_id=' + id);
                const data = await res.json();
                if(data.stream_url) {
                    const v = document.getElementById('vid');
                    document.getElementById('player-overlay').style.display='flex';
                    if (Hls.isSupported() && data.stream_url.includes('.m3u8')) {
                        const hls = new Hls();
                        hls.loadSource(data.stream_url);
                        hls.attachMedia(v);
                    } else { v.src = data.stream_url; }
                } else { alert("Stream not found."); }
            }
            window.onload = () => load('/api/trending');
        </script>
    </body>
    </html>
    """

@app.get("/api/trending")
async def get_trending():
    try:
        # ma.movies() often returns a list directly or a dict depending on the wrapper version
        movies = ma.movies()
        return {"results": movies if isinstance(movies, list) else []}
    except Exception as e:
        print(f"Trending Error: {e}")
        return {"results": []}

@app.get("/api/search")
async def search(q: str = Query(...)):
    try:
        results = ma.search(q)
        return {"results": results if isinstance(results, list) else []}
    except Exception as e:
        print(f"Search Error: {e}")
        return {"results": []}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    try:
        # We attempt to find the stream URL from the search result for that ID
        results = ma.search(movie_id)
        if results and isinstance(results, list):
            for item in results:
                if item.get('id') == movie_id and 'url' in item:
                    return {"stream_url": item['url']}
        return {"error": "No stream found"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)