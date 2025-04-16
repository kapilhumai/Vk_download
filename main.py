from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import uuid
import os

app = FastAPI()

# Mount the static directory for CSS/JS if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use the templates directory
templates = Jinja2Templates(directory="templates")

# Home page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle the download request
@app.post("/", response_class=HTMLResponse)
async def download(request: Request, url: str = Form(...)):
    video_id = str(uuid.uuid4())[:8]
    output_filename = f"{video_id}.mp4"

    try:
        # Run yt-dlp to download the video
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", output_filename, url],
            check=True
        )

        # Show result page with download link
        return templates.TemplateResponse("result.html", {
            "request": request,
            "video_url": f"/video/{output_filename}"
        })

    except subprocess.CalledProcessError:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Download failed. Please check the VK URL and try again."
        })

# Serve the downloaded video
@app.get("/video/{filename}")
async def get_video(filename: str):
    if os.path.exists(filename):
        return FileResponse(path=filename, filename=filename, media_type='video/mp4')
    return HTMLResponse(content="File not found", status_code=404)
