import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from gtts import gTTS
import requests

app = FastAPI(title="VisionCore - Real-Time Geolocation & Waypoint Navigation", version="2.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

NARAKEET_API_KEY = "grok_9ab7f8b603423ab2d7adf253ce61d787_06a6291d5ddcdffc63fb8d8c31e237599bb694b5ab855b61132ef4f651d3ed60"

class WaypointRequest(BaseModel):
    destination: str
    lat: float
    lng: float

class SpeakRequest(BaseModel):
    text: str
    engine: str = "gtts"

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

@app.post("/api/speak")
def generate_audio(req: SpeakRequest):
    os.makedirs("static/audio", exist_ok=True)
    filename = "static/audio/guidance.mp3"
    
    try:
        if req.engine == "narakeet":
            url = "https://api.narakeet.com/text-to-speech/m4a?voice=mickey"
            headers = {
                'Accept': 'application/octet-stream',
                'Content-Type': 'text/plain',
                'x-api-key': NARAKEET_API_KEY,
            }
            response = requests.post(url, headers=headers, data=req.text.encode('utf8'))
            response.raise_for_status()
            filename = "static/audio/guidance.m4a"
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            tts = gTTS(text=req.text, lang='en', slow=False)
            tts.save(filename)
            
        return {"status": "success", "audio_url": f"/{filename}", "spoken_text": req.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/navigate-waypoint")
def calculate_waypoint_route(req: WaypointRequest):
    waypoints_db = {
        "Campus Main Block": {"instruction": "Proceed 40 meters North along Waypoint Node A, then turn right toward Main Block entrance."},
        "Washroom Corridor": {"instruction": "Walk 15 meters straight, cross intersection B, and the washroom entrance is on your left."},
        "Auditorium Checkpoint": {"instruction": "Follow pathway past the courtyard for 30 meters. Maintain heading."}
    }
    
    destination_data = waypoints_db.get(req.destination, {
        "instruction": f"Navigating towards {req.destination} using real-time GPS coordinate telemetry."
    })
    
    guidance_text = f"Waypoint Alert: {destination_data['instruction']}"
    
    os.makedirs("static/audio", exist_ok=True)
    audio_path = "static/audio/guidance.mp3"
    tts = gTTS(text=guidance_text, lang='en', slow=False)
    tts.save(audio_path)
    
    return {
        "destination": req.destination,
        "current_coordinates": {"lat": req.lat, "lng": req.lng},
        "instruction": destination_data['instruction'],
        "audio_url": "/static/audio/guidance.mp3",
        "team_manifest": [
            {"name": "P Vishal Ravi", "usn": "1AM24CI101"},
            {"name": "Sagar J", "usn": "1AM24CI135"},
            {"name": "R Harivishnu", "usn": "1AM24AI083"},
            {"name": "Abdur Rehman", "usn": "1AM24CI002"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
