# StoryTime

StoryTime is an autonomous AI pipeline and multi-user web application that generates short-form viral videos (TikTok, Reels, Shorts) from a simple prompt or a custom script.

## Features
- **User Authentication:** Secure local SQLite user management system. Generate and save videos securely to your personal account.
- **Personal Video Library:** Browse all your previously generated videos, complete with saved titles, descriptions, and hashtags.
- **AI Chat Assistant:** A built-in ChatGPT-style interface powered by `openai/gpt-oss-120b` (via Groq) to brainstorm ideas and write highly engaging, fast-paced narratives with viral hooks and cliffhangers.
- **Script Overrides:** Bypass the automatic AI generator and paste your exact brainstormed script directly into the Studio to maintain full creative control.
- **AI Voiceover:** Uses the open-source **Kokoro TTS** model for high-quality, expressive text-to-speech with multiple voice profiles.
- **Generative AI Visuals:** Uses **Pollinations.ai** to generate custom, context-aware imagery for every single scene.
- **Automated Video Stitching:** Uses **FFmpeg** to automatically stitch the images and audio together, complete with cinematic zoom-pan effects and SRT subtitles.

## Prerequisites
- Python 3.9+
- FFmpeg installed (`brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Linux)

## Installation
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add your API keys:
   ```env
   GEMINI_API_KEY=your_key
   GROQ_API_KEY=your_key
   ```
   *(Note: The Groq client is configured to route `openai/gpt-oss-120b`. Ensure your environment is properly set up for this.)*

## Usage
Start the backend server:
```bash
uvicorn server:app --reload
```
Navigate to `http://127.0.0.1:8000` in your browser. 
1. **Register** a new account and log in.
2. Head to the **Assistant** tab to brainstorm your script.
3. Paste it into the **Studio** tab and hit Generate!
4. View your finished videos in your personal **Library**.
