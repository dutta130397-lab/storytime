import os
from kokoro import KPipeline
import soundfile as sf

def run_kokoro_test():
    sample_script = "The Dwarka Deep-Dive: During a deep-sea excavation of the submerged, mythological city, divers find a perfectly preserved underwater temple."

    # Lists of all the major built-in voices
    american_voices = [
        'am_adam', 'am_fenrir', 'am_michael', 'am_onyx', 'am_echo', 'am_puck',
        'af_bella', 'af_sarah', 'af_sky', 'af_nicole', 'af_alloy'
    ]
    
    british_voices = [
        'bm_george', 'bm_lewis', 'bm_daniel',
        'bf_emma', 'bf_isabella', 'bf_alice'
    ]

    print("========================================")
    print("Testing American English Voices ('a')")
    print("========================================")
    pipeline_a = KPipeline(lang_code='a') 

    for voice in american_voices:
        print(f"Generating sample for: {voice}...")
        try:
            generator = pipeline_a(sample_script, voice=voice, speed=0.9, split_pattern=r'\n+')
            # We only need the first chunk
            for i, (gs, ps, audio) in enumerate(generator):
                sf.write(f'sample_{voice}.wav', audio, 24000)
                break 
        except Exception as e:
            print(f"  [!] Could not load voice {voice}: {e}")

    print("\n========================================")
    print("Testing British English Voices ('b')")
    print("========================================")
    pipeline_b = KPipeline(lang_code='b') 

    for voice in british_voices:
        print(f"Generating sample for: {voice}...")
        try:
            generator = pipeline_b(sample_script, voice=voice, speed=0.9, split_pattern=r'\n+')
            for i, (gs, ps, audio) in enumerate(generator):
                sf.write(f'sample_{voice}.wav', audio, 24000)
                break 
        except Exception as e:
            print(f"  [!] Could not load voice {voice}: {e}")

    print("\n✅ Done! All samples have been saved to this folder.")

if __name__ == "__main__":
    run_kokoro_test()
