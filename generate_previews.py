import os
from kokoro import KPipeline
import soundfile as sf

def generate_previews():
    PREVIEWS_DIR = "output/previews"
    os.makedirs(PREVIEWS_DIR, exist_ok=True)
    
    sample_text = "Constructed millennia ago by a forgotten civilization known as the Architects of the Eclipse, the Obsidian Vault was designed solely to imprison a celestial parasite that had crashed into the Sunken Basin. When rogue explorer Elias Thorne cracked the cipher and triggered the temple's golden gears in 1912, he didn't uncover hidden ancient riches; instead, he unwittingly shattered the temporal stasis field holding the beast, triggering a lockdown mechanism that sealed him in the dark with a cosmic horror that had been starving for three thousand years."
    
    american_voices = [
        'am_adam', 'am_fenrir', 'am_michael', 'am_onyx', 'am_echo', 'am_puck',
        'af_bella', 'af_sarah', 'af_sky', 'af_nicole', 'af_alloy'
    ]
    
    british_voices = [
        'bm_george', 'bm_lewis', 'bm_daniel',
        'bf_emma', 'bf_isabella', 'bf_alice'
    ]
    
    print("Generating American previews...")
    pipeline_a = KPipeline(lang_code='a')
    for voice in american_voices:
        path = os.path.join(PREVIEWS_DIR, f"{voice}.wav")
        if not os.path.exists(path):
            print(f"Generating {voice}...")
            generator = pipeline_a(sample_text, voice=voice, speed=1.0, split_pattern=r'\n+')
            for i, (gs, ps, audio) in enumerate(generator):
                sf.write(path, audio, 24000)
                break
                
    print("Generating British previews...")
    pipeline_b = KPipeline(lang_code='b')
    for voice in british_voices:
        path = os.path.join(PREVIEWS_DIR, f"{voice}.wav")
        if not os.path.exists(path):
            print(f"Generating {voice}...")
            generator = pipeline_b(sample_text, voice=voice, speed=1.0, split_pattern=r'\n+')
            for i, (gs, ps, audio) in enumerate(generator):
                sf.write(path, audio, 24000)
                break

if __name__ == "__main__":
    generate_previews()
