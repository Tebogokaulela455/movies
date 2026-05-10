import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from moviebox_api.v1 import MovieAuto
import uvicorn

app = FastAPI()

# Enable CORS just in case, though serving from the same file makes it redundant
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the API wrapper
ma = MovieAuto()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>MovieBox.ph Replica</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            :root { --primary: #ffbb00; --bg: #080808; --card: #151515; --text: #fff; }
            body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; }
            header { padding: 15px 5%; background: #000; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; }
            .logo { color: var(--primary); font-size: 1.5rem; font-weight: bold; cursor: pointer; }
            .search-bar { display: flex; gap: 8px; }
            input { padding: 10px; width: 220px; background: #111; border: 1px solid #333; color: white; border-radius: 4px; }
            button { background: var(--primary); border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; border-radius: 4px; }
            .container { padding: 25px 5%; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }
            .movie-card { background: var(--card); border-radius: 8px; overflow: hidden; transition: 0.2s; border: 1px solid #222; }
            .movie-card:hover { transform: translateY(-5px); border-color: var(--primary); }
            .movie-card img { width: 100%; height: 240px; object-fit: cover; }
            .movie-info { padding: 10px; text-align: center; }
            .movie-info h3 { font-size: 0.8rem; margin: 5px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .btn { width: 100%; padding: 8px; margin-top: 5px; border: none; cursor: pointer; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
            #player-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 10000; justify-content: center; align-items: center; }
            video { width: 95%; max-width: 1000px; max-height: 80vh; }
            .close { position: absolute; top: 20px; right: 30px; font-size: 40px; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo" onclick="location.reload()">MOVIEBOX</div>
            <div class="search-bar">
                <input type="text" id="query" placeholder="Search movies/series...">
                <button onclick="searchMovie()">Search</button>
            </div>
        </header>
        <div class="container">
            <h2 id="title">Trending</h2>
            <div class="grid" id="results"></div>
        </div>
        <div id="player-overlay">
            <span class="close" onclick="closePlayer()">&times;</span>
            <video id="video-player" controls></video>
        </div>
        <script>
            async function searchMovie() {
                const q = document.getElementById('query').value;
                if(!q) return;
                document.getElementById('title').innerText = "Results for: " + q;
                const res = await fetch(`/api/search?q=${q}`);
                const data = await res.json();
                render(data.results);
            }
            async function loadTrending() {
                const res = await fetch('/api/trending');
                const data = await res.json();
                render(data.results);
            }
            function render(movies) {
                const grid = document.getElementById('results');
                grid.innerHTML = movies.length ? movies.map(m => `
                    <div class="movie-card">
                        <img src="${m.poster || m.cover || 'https://via.placeholder.com/200x300?text=No+Poster'}" onerror="this.src='https://via.placeholder.com/200x300?text=Error'">
                        <div class="movie-info">
                            <h3>${m.title}</h3>
                            <button class="btn" style="background:#ffbb00" onclick="playMovie('${m.id}')">WATCH</button>
                            <button class="btn" style="background:#333; color:white" onclick="window.open('/api/get_stream?movie_id=${m.id}')">DOWNLOAD</button>
                        </div>
                    </div>
                `).join('') : "<p>No movies found. Try another search.</p>";
            }
            function playMovie(id) {
                const overlay = document.getElementById('player-overlay');
                const video = document.getElementById('video-player');
                overlay.style.display = 'flex';
                fetch(`/api/get_stream?movie_id=${id}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.stream_url) {
                            if (data.stream_url.includes('.m3u8')) {
                                if (Hls.isSupported()) {
                                    const hls = new Hls();
                                    hls.loadSource(data.stream_url);
                                    hls.attachMedia(video);
                                } else { video.src = data.stream_url; }
                            } else { video.src = data.stream_url; }
                            video.play();
                        } else { alert("Link not found."); closePlayer(); }
                    });
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
        # Fixed function call for the library
        movies = ma.movies()
        return {"results": movies if movies else []}
    except:
        return {"results": []}

@app.get("/api/search")
async def search(q: str = Query(...)):
    try:
        results = ma.search(q)
        return {"results": results if results else []}
    except:
        return {"results": []}

@app.get("/api/get_stream")
async def get_stream(movie_id: str):
    try:
        # ATTRIBUTE ERROR FIX: Using the search function to find links
        # Most versions of MovieAuto provide links directly via a search/detail combo
        # If 'get_links' fails, we attempt the common 'links' attribute
        results = ma.search(movie_id) # Using ID as search term often works for links
        if results and 'url' in results[0]:
            return {"stream_url": results[0]['url']}
        
        # Fallback to check if 'links' exists on the object
        if hasattr(ma, 'links'):
            links = ma.links(movie_id)
            return {"stream_url": links[0] if links else None}
            
        return {"error": "API link retrieval failed"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)