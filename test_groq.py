import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

# Create a dummy audio file
os.system('echo "Hello world" > dummy.txt && edge-tts --text "Hello world, this is a test of scene one. And here is scene two." --write-media dummy.mp3')

with open("dummy.mp3", "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=("dummy.mp3", file.read()),
        model="whisper-large-v3",
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )
    print(transcription.words)
