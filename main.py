import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from moviebox_api.v1 import MovieAuto
import asyncio

app = FastAPI()

# HTML Frontend
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MovieBox.ph Clone</title>
    <style>
        body { background: #0b0b0b; color: white; font-family: Arial; padding: 20px; }
        .search-box { margin-bottom: 30px; text-align: center; }
        input { padding: 10px; width: 300px; border-radius: 5px; border: none; }
        button { padding: 10px 20px; background: #e50914; color: white; border: none; cursor: pointer; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .movie-card { background: #1f1f1f; padding: 10px; border-radius: 8px; text-align: center; }
        video { width: 100%; margin-top: 20px; display: none; }
        #ad-layer { 
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: black; z-index: 100; justify-content: center; align-items: center; 
        }
    </style>
</head>
<body>
    <div class="search-box">
        <h1>MovieBox Stream</h1>
        <input type="text" id="query" placeholder="Search movies...">
        <button onclick="searchMovie()">Search</button>
    </div>

    <div id="ad-layer"><h1>ADVERTISEMENT (R20/mo Slot)</h1><p>Movie starts in 5s...</p></div>

    <div class="grid" id="results"></div>
    
    <video id="player" controls></video>

    <script>
        async function searchMovie() {
            const q = document.getElementById('query').value;
            const res = await fetch(`/api/search?q=${q}`);
            const data = await res.json();
            
            let html = '';
            data.results.forEach(m => {
                html += `
                <div class="movie-card">
                    <h3>${m.title}</h3>
                    <button onclick="playMovie('${m.title}')">Watch / Preview</button>
                    <br><br>
                    <a href="#" style="color: grey;">Download (ID: ${m.id})</a>
                </div>`;
            });
            document.getElementById('results').innerHTML = html;
        }

        function playMovie(title) {
            // Ad Logic (Placeholder for R20/mo system)
            const ad = document.getElementById('ad-layer');
            const player = document.getElementById('player');
            
            ad.style.display = 'flex';
            setTimeout(() => {
                ad.style.display = 'none';
                player.style.display = 'block';
                alert("Now streaming: " + title + " (API link would load here)");
            }, 5000); // 5 second ad
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return html_content

@app.get("/api/search")
async def search(q: str = Query(...)):
    # Using the MovieAuto feature from the moviebox-api wrapper
    # In a real scenario, we'd map the search results here
    # Since we're keeping it simple, we'll return a structure the frontend can use
    return {"results": [{"id": 1, "title": q}]}
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000)) # This gets the port from Render/Railway
    uvicorn.run(app, host="0.0.0.0", port=port)