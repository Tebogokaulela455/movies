import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto
import uvicorn

app = FastAPI()

# Redundant but safe for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ma = MovieAuto()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MovieBox.ph Replica</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            :root { --primary: #ffbb00; --bg: #050505; --card: #121212; --text: #eeeeee; }
            body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; }
            header { padding: 15px 6%; background: #000; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; sticky: top; }
            .logo { color: var(--primary); font-size: 1.8rem; font-weight: 900; cursor: pointer; letter-spacing: -1px; }
            .search-bar { display: flex; background: #111; border: 1px solid #333; border-radius: 25px; padding: 5px 15px; width: 300px; }
            .search-bar input { background: transparent; border: none; color: white; width: 100%; outline: none; }
            .search-bar button { background: transparent; border: none; color: var(--primary); cursor: pointer; font-weight: bold; }
            .container { padding: 40px 6%; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 25px; }
            .movie-card { background: var(--card); border-radius: 12px; overflow: hidden; transition: 0.3s; border: 1px solid #222; position: relative; }
            .movie-card:hover { transform: translateY(-10px); border-color: var(--primary); }
            .movie-card img { width: 100%; height: 270px; object-fit: cover; }
            .movie-info { padding: 12px; text-align: center; }
            .movie-info h3 { font-size: 0.9rem; margin: 0 0 10px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .btn { width: 100%; padding: 10px; border-radius: 6px; border: none; font-size: 0.75rem; font-weight: bold; cursor: pointer; margin-bottom: 5px; }
            .watch-btn { background: var(--primary); color: black; }
            #player-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 10000; justify-content: center; align-items: center; }
            .player-container { width: 90%; max-width: 1100px; position: relative; }
            video { width: 100%; border-radius: 8px; background: #000; }
            .close { position: absolute; top: -50px; right: 0; color: white; font-size: 2.5rem; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo" onclick="location.reload()">MOVIEBOX</div>
            <div class="search-bar">
                <input type="text" id="query" placeholder="Search movies...">
                <button onclick="searchMovie()">SEARCH</button>
            </div>
        </header>
        <div class="container">
            <h2 id="title">Trending Now</h2>
            <div class="grid" id="results"></div>
        </div>
        <div id="player-overlay">
            <div class="player-container">
                <div class="close" onclick="closePlayer()">&times;</div>
                <video id="video-player" controls autoplay></video>
            </div>
        </div>
        <script>
            async function loadTrending() {
                const res = await fetch('/api/trending');
                const data = await res.json();
                render(data.results);
            }
            async function searchMovie() {
                const q = document.getElementById('query').value;
                if(!q) return;
                document.getElementById('title').innerText = "Results for: " + q;
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                render(data.results);
            }
            function render(movies) {
                const grid = document.getElementById('results');
                grid.innerHTML = movies.map(m => `
                    <div class="movie-card">
                        <img src="${m.poster || m.cover || ''}" onerror="this.src='https://via.placeholder.com/180x270?text=No+Poster'">
                        <div class="movie-info">
                            <h3>${m.title}</h3>
                            <button class="btn watch-btn" onclick="playMovie('${m.id}')">WATCH</button>
                        </div>
                    </div>
                `).join('');
            }
            async function playMovie(id) {
                const overlay = document.getElementById('player-overlay');
                const video = document.getElementById('video-player');
                overlay.style.display = 'flex';
                const res = await fetch(`/api/get_stream?movie_id=${id}`);
                const data = await res.json();
                if (data.stream_url) {
                    if (data.stream_url.includes('.m3u8')) {
                        if (Hls.isSupported()) {
                            const hls = new Hls();
                            hls.loadSource(data.stream_url);
                            hls.attachMedia(video);
                        } else { video.src = data.stream_url; }
                    } else { video.src = data.stream_url; }
                }
            }
            function closePlayer() {
                const v = document.getElementById('video-player');
                v.pause(); v.src = "";
                document.getElementById('player-overlay').style.display = 'none';
            }
            window.onload = loadTrending;
        </script>
    </body>
    </html>
    """

@app.get("/api/trending")
async def get_trending():
    try:
        return {"results": ma.movies() or []}
    except:
        return {"results": []}

@app.get("/api/search")
async def search(q: str = Query(...)):
    try:
        return {"results": ma.search(q) or []}
    except:
        return {"results": []}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    try:
        results = ma.search(movie_id)
        if results and 'url' in results[0]:
            return {"stream_url": results[0]['url']}
        return {"error": "No stream found"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)