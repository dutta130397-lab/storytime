import os
import json
import asyncio
import subprocess
import requests
import urllib.parse
from typing import List, Dict, Any, AsyncGenerator
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import sqlite3
import hashlib

from google import genai
from google.genai import types
from groq import Groq
from kokoro import KPipeline
import soundfile as sf
import numpy as np

# Load env variables
load_dotenv()

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT)''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# Kokoro pipelines initialization (lazy loading)
pipelines = {}

def get_pipeline(lang_code):
    if lang_code not in pipelines:
        pipelines[lang_code] = KPipeline(lang_code=lang_code)
    return pipelines[lang_code]

progress_queues: Dict[str, asyncio.Queue] = {}

class GenerateRequest(BaseModel):
    topic: str
    niche: str
    style: str
    episodes: int
    voice_id: str
    llm_provider: str
    client_id: str
    script_override: str = ""

class ChatRequest(BaseModel):
    messages: List[dict]

class AuthRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.get("/api/library")
async def get_library(username: str = ""):
    videos = []
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith("_final.mp4"):
                # If a username is provided, only return videos that start with {username}_
                if username and not f.startswith(f"{username}_"):
                    continue
                    
                client_id_ep = f.replace("_final.mp4", "")
                metadata_path = os.path.join(OUTPUT_DIR, f"{client_id_ep}_metadata.json")
                
                title = f"Video {client_id_ep}"
                description = "No description available"
                hashtags = ""
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as mf:
                        try:
                            meta = json.load(mf)
                            title = meta.get("title", title)
                            description = meta.get("description", description)
                            hashtags = meta.get("hashtags", hashtags)
                        except Exception:
                            pass
                
                videos.append({
                    "url": f"/output/{f}",
                    "title": title,
                    "description": description,
                    "hashtags": hashtags,
                    "id": client_id_ep
                })
    return {"videos": videos}

@app.get("/api/progress/{client_id}")
async def progress_stream(client_id: str):
    if client_id not in progress_queues:
        progress_queues[client_id] = asyncio.Queue()
        
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            while True:
                message = await progress_queues[client_id].get()
                yield f"data: {json.dumps(message)}\n\n"
                if message.get("status") in ["completed", "error"]:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if client_id in progress_queues:
                del progress_queues[client_id]
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def emit_sync(loop: asyncio.AbstractEventLoop, client_id: str, state: dict):
    async def put_state():
        if client_id in progress_queues:
            await progress_queues[client_id].put(state)
    asyncio.run_coroutine_threadsafe(put_state(), loop)

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def run_generation_pipeline(loop: asyncio.AbstractEventLoop, topic: str, niche: str, style: str, episodes: int, voice_id: str, llm_provider: str, client_id: str, script_override: str = ""):
    try:
        gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # --- Node 0: Full-Series Scribe ---
        emit_sync(loop, client_id, {"step": 0, "status": "processing", "message": "Series Scribe: Drafting full script..."})
        
        viral_framework = (
            "CRITICAL VIRALITY RULES:\n"
            "1. The 3-Second Hook: The very first sentence of Episode 1 MUST be an extreme pattern-interrupt that immediately grabs attention (e.g., a controversial statement, a terrifying fact, or an unbelievable scenario).\n"
            "2. Open Loops: Constantly tease information. Never give the audience all the answers at once. Make them wait until the very end of the final episode for the full payoff.\n"
            "3. High Stakes & Fast Pacing: Keep sentences short, punchy, and visceral. Eliminate fluff. Every single scene must escalate the tension or reveal a twist.\n"
            "4. The Cliffhanger: Every episode (except the finale) MUST end abruptly at the absolute peak of tension to force the viewer to watch the next part."
        )
        
        total_scenes = episodes * 6
        
        if script_override.strip():
            planner_prompt = f"Act as a viral short-form series showrunner. You are creating a highly engaging {episodes}-part TikTok/Reels series. Niche: '{niche}'. Style: '{style}'.\n\nHere is a drafted script from the user:\n\"\"\"{script_override}\"\"\"\n\nCRITICAL RULE: DO NOT write a new story. You must break this EXACT script down into exactly {episodes} episodes. Each episode must have an 'episode_title', a highly clickable 'description', a string of 5-7 SEO 'hashtags', and an array of exactly 6 'scenes'. Each scene must extract the 'spoken_text' from the user's draft sequentially, and include a highly descriptive 'visual_prompt'.\nFINALLY, provide 'visual_continuity_keywords' to keep the art consistent."
        else:
            planner_prompt = f"Act as a viral short-form series showrunner. You are creating a highly engaging {episodes}-part TikTok/Reels series. Niche: '{niche}'. Style: '{style}'. Premise: '{topic}'.\n\n{viral_framework}\n\nFIRST, write a 'full_script_draft' which is the complete narrative from episode 1 to {episodes}. CRITICAL RULE: You must write out the full, word-for-word narration. The draft MUST contain an absolute minimum of {total_scenes} distinct sentences. Do not write a summary. \nSECOND, chop that draft into exactly {episodes} episodes. Each episode must have an 'episode_title', a highly clickable 'description', a string of 5-7 SEO 'hashtags', and an array of exactly 6 'scenes'. Each scene must extract the 'spoken_text' from your draft sequentially, and include a highly descriptive 'visual_prompt'.\nFINALLY, provide 'visual_continuity_keywords' to keep the art consistent."
        
        if llm_provider == "gemini":
            planner_res = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=planner_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "visual_continuity_keywords": types.Schema(type=types.Type.STRING),
                            "full_script_draft": types.Schema(type=types.Type.STRING),
                            "episodes": types.Schema(
                                type=types.Type.ARRAY,
                                items=types.Schema(
                                    type=types.Type.OBJECT,
                                    properties={
                                        "episode_title": types.Schema(type=types.Type.STRING),
                                        "description": types.Schema(type=types.Type.STRING),
                                        "hashtags": types.Schema(type=types.Type.STRING),
                                        "scenes": types.Schema(
                                            type=types.Type.ARRAY,
                                            items=types.Schema(
                                                type=types.Type.OBJECT,
                                                properties={
                                                    "spoken_text": types.Schema(type=types.Type.STRING),
                                                    "visual_prompt": types.Schema(type=types.Type.STRING),
                                                },
                                                required=["spoken_text", "visual_prompt"]
                                            )
                                        )
                                    },
                                    required=["episode_title", "description", "hashtags", "scenes"]
                                )
                            )
                        },
                        required=["visual_continuity_keywords", "full_script_draft", "episodes"]
                    )
                )
            )
            master_plan = json.loads(planner_res.text)
        elif llm_provider == "llama":
            llama_prompt = planner_prompt + "\n\nYou MUST output a valid JSON object containing the string keys: 'visual_continuity_keywords', 'full_script_draft', and 'episodes'. The 'episodes' key must be an array of objects. Each episode object must have an 'episode_title' string, a 'description' string, a 'hashtags' string, and a 'scenes' array. Each scene object must have a 'spoken_text' string and a 'visual_prompt' string."
            
            for attempt in range(3):
                try:
                    chat_completion = groq_client.chat.completions.create(
                        messages=[{"role": "system", "content": "You are a highly precise JSON-outputting assistant."}, {"role": "user", "content": llama_prompt}],
                        model="openai/gpt-oss-120b",
                        response_format={"type": "json_object"},
                    )
                    parsed_res = json.loads(chat_completion.choices[0].message.content)
                    master_plan = parsed_res
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e
                    print(f"Llama generation failed, retrying... (Attempt {attempt+1}): {e}")

        emit_sync(loop, client_id, {"step": 0, "status": "done", "data": master_plan})
        
        final_video_urls = []
        
        # Determine language code for Kokoro
        lang_code = 'b' if voice_id.startswith('b') else 'a'
        pipeline = get_pipeline(lang_code)
        
        # Episode Loop
        for ep_idx, ep_data in enumerate(master_plan.get("episodes", [])):
            ep_num = ep_idx + 1
            
            script_data = ep_data.get("scenes", [])
            
            # Ensure visual continuity keywords are prepended
            continuity_keywords = master_plan.get("visual_continuity_keywords", "")
            for scene in script_data:
                scene["visual_prompt"] = f"{continuity_keywords}, {scene.get('visual_prompt', '')}"
            
            emit_sync(loop, client_id, {"step": 1, "status": "processing", "message": f"Ep {ep_num}/{episodes}: Audio Generation (Kokoro)...", "data": master_plan})
            
            # --- Node 2: Audio (Kokoro) ---
            # Using newline instead of space so Kokoro's split_pattern=r'\n+' can chunk the audio
            # and prevent PyTorch memory freezes from overly long strings
            full_text = "\n".join([scene.get("spoken_text", "") for scene in script_data])
            audio_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_narration.wav")
            
            generator = pipeline(full_text, voice=voice_id, speed=0.9, split_pattern=r'\n+')
            audio_chunks = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_chunks.append(audio)
            
            # Concatenate chunks
            if audio_chunks:
                final_audio = np.concatenate(audio_chunks)
                sf.write(audio_path, final_audio, 24000)
            else:
                raise Exception("Kokoro TTS generated empty audio.")
            
            # Transcription for Timestamps
            with open(audio_path, "rb") as file:
                transcription = groq_client.audio.transcriptions.create(
                    file=(f"ep{ep_num}.wav", file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            words = getattr(transcription, "words", [])
            if not words and isinstance(transcription, dict):
                words = transcription.get("words", [])
                
            srt_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_subs.srt")
            with open(srt_path, "w") as f:
                for i, word_info in enumerate(words):
                    start_val = word_info["start"] if isinstance(word_info, dict) else word_info.start
                    end_val = word_info["end"] if isinstance(word_info, dict) else word_info.end
                    word_val = word_info["word"] if isinstance(word_info, dict) else word_info.word
                    
                    f.write(f"{i+1}\n")
                    f.write(f"{format_timestamp(start_val)} --> {format_timestamp(end_val)}\n")
                    f.write(f"{word_val.strip()}\n\n")

            scene_word_counts = [len(scene["spoken_text"].split()) for scene in script_data]
            whisper_word_count = len(words)
            total_original_words = sum(scene_word_counts)
            
            scene_durations = []
            last_time = 0.0
            current_word_idx = 0
            total_audio_duration = 0.0
            if words:
                total_audio_duration = words[-1]["end"] if isinstance(words[-1], dict) else words[-1].end

            for i, count in enumerate(scene_word_counts):
                if i == len(scene_word_counts) - 1:
                    duration = total_audio_duration - last_time
                else:
                    target_idx = int(current_word_idx + (count / total_original_words) * whisper_word_count)
                    target_idx = min(target_idx, len(words) - 1)
                    
                    word_info = words[target_idx]
                    split_time = word_info["end"] if isinstance(word_info, dict) else word_info.end
                    duration = split_time - last_time
                    last_time = split_time
                    current_word_idx = target_idx
                
                if duration <= 0: duration = 1.0
                scene_durations.append(duration)

            emit_sync(loop, client_id, {"step": 1, "status": "processing", "message": f"Ep {ep_num}/{episodes}: Visuals..."})
            
            # --- Node 3: Visual ---
            scene_clips = []
            for i, (scene, duration) in enumerate(zip(script_data, scene_durations)):
                image_prompt = urllib.parse.quote(scene.get("visual_prompt", ""))
                image_url = f"https://image.pollinations.ai/prompt/{image_prompt}?width=1080&height=1920&nologo=true"
                image_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_scene{i+1}.jpg")
                
                # Added retry loop and status check to prevent corrupt JPGs from breaking ffmpeg
                img_success = False
                for img_attempt in range(3):
                    try:
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status() # Throw error if it's a 404/500 page instead of an image
                        with open(image_path, "wb") as f:
                            f.write(response.content)
                        img_success = True
                        break
                    except Exception as e:
                        print(f"Image {i+1} download failed, retrying... (Attempt {img_attempt+1}): {e}")
                        import time
                        time.sleep(2)
                
                if not img_success:
                    raise Exception(f"Failed to generate image for scene {i+1} after 3 attempts. Pollinations.ai might be down.")
                
                clip_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_scene{i+1}.mp4")
                frames = int(duration * 30)
                
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-i", image_path,
                    "-vf", f"zoompan=z='min(zoom+0.0015,1.1)':d={frames}:x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=1080x1920",
                    "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
                    clip_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                scene_clips.append(clip_path)

            emit_sync(loop, client_id, {"step": 1, "status": "processing", "message": f"Ep {ep_num}/{episodes}: Stitching..."})
            
            # --- Node 4: Editor ---
            list_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_list.txt")
            with open(list_path, "w") as f:
                for clip in scene_clips:
                    f.write(f"file '{os.path.basename(clip)}'\n")
                    
            concated_video_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_concat.mp4")
            
            cmd_concat = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.basename(list_path),
                "-c", "copy", os.path.basename(concated_video_path)
            ]
            subprocess.run(cmd_concat, check=True, cwd=OUTPUT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            final_video_path = os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_final.mp4")
            rel_srt_path = os.path.basename(srt_path)
            
            cmd_final = [
                "ffmpeg", "-y", 
                "-i", os.path.basename(concated_video_path), 
                "-i", os.path.basename(audio_path),
                "-vf", f"subtitles={rel_srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=50,FontName=Arial'",
                "-c:v", "h264_videotoolbox", "-b:v", "5M",
                "-c:a", "aac",
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest",
                os.path.basename(final_video_path)
            ]
            
            subprocess.run(cmd_final, check=True, cwd=OUTPUT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Cleanup ep files
            os.remove(audio_path)
            os.remove(srt_path)
            os.remove(list_path)
            os.remove(concated_video_path)
            for clip in scene_clips:
                os.remove(clip)
            for i in range(len(script_data)):
                os.remove(os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_scene{i+1}.jpg"))
                
            # Save metadata for the library
            metadata = {
                "title": ep_data.get("episode_title", f"Episode {ep_num}"),
                "description": ep_data.get("description", ""),
                "hashtags": ep_data.get("hashtags", "")
            }
            with open(os.path.join(OUTPUT_DIR, f"{client_id}_ep{ep_num}_metadata.json"), "w") as f:
                json.dump(metadata, f)
                
            final_video_urls.append(f"/output/{client_id}_ep{ep_num}_final.mp4")

        # After all episodes complete
        emit_sync(loop, client_id, {"status": "completed", "video_urls": final_video_urls, "data": master_plan})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        emit_sync(loop, client_id, {"status": "error", "message": str(e)})

@app.post("/api/generate")
async def generate_video(req: GenerateRequest, background_tasks: BackgroundTasks):
    if req.client_id not in progress_queues:
        progress_queues[req.client_id] = asyncio.Queue()
        
    loop = asyncio.get_running_loop()
    background_tasks.add_task(run_generation_pipeline, loop, req.topic, req.niche, req.style, req.episodes, req.voice_id, req.llm_provider, req.client_id, req.script_override)
    return {"status": "started", "client_id": req.client_id}

@app.post("/api/chat")
async def chat_assistant(req: ChatRequest):
    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        system_prompt = {
            "role": "system", 
            "content": "You are a highly creative Viral TikTok/Reels Producer. Your job is to brainstorm ideas, write compelling short-form scripts, and format them beautifully. Keep responses snappy and focused on engagement (hooks, pacing, cliffhangers)."
        }
        
        messages = [system_prompt] + req.messages
        
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b"
        )
        
        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/api/register")
async def register(req: AuthRequest):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (req.username, hash_password(req.password)))
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Username already exists"}
    finally:
        conn.close()

@app.post("/api/login")
async def login(req: AuthRequest):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (req.username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(req.password):
        return {"success": True, "username": req.username}
    return {"success": False, "error": "Invalid username or password"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
