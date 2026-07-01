# StoryTime

StoryTime is an autonomous AI pipeline that generates short-form viral videos (TikTok, Reels, Shorts) from a simple prompt. 

## Features
- **Viral Scripting Engine:** Uses Llama 3 (via Groq) or Gemini to draft highly engaging, fast-paced narratives with built-in viral hooks and cliffhangers.
- **Dynamic Pacing:** Splits the script into micro-scenes to ensure rapid visual changes that maximize viewer retention.
- **AI Voiceover:** Uses the open-source **Kokoro TTS** model for high-quality, expressive text-to-speech.
- **Generative AI Visuals:** Uses **Pollinations.ai** to generate custom, context-aware imagery for every single scene.
- **Automated Video Stitching:** Uses **FFmpeg** to automatically stitch the images and audio together, complete with cinematic zoom-pan effects.
- **Viral Metadata:** Automatically generates SEO-optimized YouTube descriptions and hashtags for your video.

## Prerequisites
- Python 3.9+
- FFmpeg installed (`brew install ffmpeg` on macOS)

## Installation
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add your API keys:
   ```
   GEMINI_API_KEY=your_key
   GROQ_API_KEY=your_key
   ```

## Usage
Start the backend server:
```bash
uvicorn server:app --reload
```
Navigate to `http://127.0.0.1:8000` in your browser. Select your AI engine, enter a topic, and hit Generate!
