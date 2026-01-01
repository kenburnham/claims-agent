from google import genai
from google.genai import types
import os
import base64
import wave
import io
import numpy as np
from scipy.signal import butter, lfilter
import random
import json

def telephone_filter(data, sample_rate=24000):
    # 1. Create a Bandpass Filter (300Hz to 3400Hz)
    lowcut = 300.0
    highcut = 3400.0
    nyq = 0.5 * sample_rate
    low = lowcut / nyq
    high = highcut / nyq
    # 5th order Butter filter
    b, a = butter(2, [low, high], btype='band')
    # Convert raw bytes to numpy array
    audio_array = np.frombuffer(data, dtype=np.int16)
    # Apply the filter
    filtered_audio = lfilter(b, a, audio_array)
    resampled_audio = filtered_audio[::3]
    return resampled_audio.astype(np.int16)

client_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=client_key)
base_filename = "audio_files/telephone_call"
extension = ".wav"
transcript_filepath = "json_files/transcripts.jsonl"
accents = {
    "US": ["puck", "kore", "charon", "leda", "fenrir",  "callirrhoe", "erinome", "umbriel", "despina", "pulcherrima"],
    "GB": ["algenib", "schedar", "autonoe", "sadaltager", "sadachbia"],
    "IN": ["gacrux", "achird", "achernar", "algieba", "laomedeia"],
    "ES": ["zubenelgenubi", "iapetus", "zephyr","orus"]
}
accent_descriptions = {
    "US": "a standard American accent",
    "GB": "a formal, posh British accent",
    "IN": "a relatively thick Indian accent",
    "ES": "a relatively thick Spanish accent"
}
with open(transcript_filepath, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        current_transcript = json.dumps(data, indent=4)
        # Pick a random region, then a random voice from that region
        selected_region = random.choice(list(accents.keys()))
        selected_voice = random.choice(accents[selected_region])
        description = accent_descriptions[selected_region]
        # 3. Inject the random choice into the config
        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker='Speaker1',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Aoede')
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker='Speaker2',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=selected_voice)
                        )
                    ),
                ]
            )
        )

        print(f"Generating conversation number {i}. Speaker 2 is using voice: {selected_voice} from region: {selected_region}")

        prompt_text = f"""
        [STYLE GUIDE: Speaker1 is a insurance claims support specialist, they sound professional. Speaker2 has {description} and sounds very tired.] 
        Please read the following transcript of their support call conversation. Please provide normal breaks between speakers, to simulate a conversation, do not simply read straight through. TRANSCRIPT: {current_transcript}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config
            )
        )
        audio_part = response.candidates[0].content.parts[0]
        finish_reason = response.candidates[0].finish_reason
        if finish_reason != "STOP":
            print(f"Warning: Audio not generated. Reason: {finish_reason}")
            # Logic for blocked content goes here
        elif hasattr(audio_part, 'inline_data'):
            raw_data = response.candidates[0].content.parts[0].inline_data.data
            tele_audio = telephone_filter(raw_data, sample_rate=24000)
            filename = f"{base_filename}-{i}-{selected_voice}-{selected_region}{extension}"
            # 2. Save at 8000 Hz for the final "crushed" effect
            with wave.open(filename, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(8000) # This is the "Telephone" speed
                wav_file.writeframes(tele_audio.tobytes())
            print(f"Successfully created: {filename}")
