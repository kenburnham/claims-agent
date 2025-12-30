from google import genai
from google.genai import types
import os
import base64
import wave
import io
import numpy as np
from scipy.signal import butter, lfilter
import random

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





base_filename = "telephone_call"
extension = ".wav"



accents = {
"US": ["puck", "kore", "aoede", "charon", "leda", "fenrir", "zephyr", "orus", "callirrhoe", "erinome", "umbriel"],
    "GB": ["algenib", "schedar", "achernar", "autonoe", "laomedeia", "sadaltager", "algieba", "sadachbia"],
    "AU": ["gacrux", "achird"],
    "ES": ["zubenelgenubi", "pulcherrima", "despina", "iapetus"]
}
accent_descriptions = {
    "US": "a standard American accent",
    "GB": "a formal, posh British accent",
    "AU": "a thick, friendly Australian Outback accent",
    "ES": "a melodic Spanish accent speaking English"
}
for i in range(1, 6):
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

    print(f"Generating conversation. Speaker 2 is using voice: {selected_voice} from region: {selected_region}")

    prompt_text = f"""
    [STYLE GUIDE: Speaker1 is a professional receptionist. Speaker2 has {description} and sounds very tired.]
    Speaker1: Hello, you've reached the support line, how may I assist you today?
    Speaker2: Thanks for answering, its been a long day! I have many questions to ask you. 
    """
    # 4. Request the audio
    # You can even prompt Gemini to describe the accent based on the voice chosen!
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config
        )
    )

    # 2. Get the data
    # The SDK often returns base64-encoded text inside a bytes object
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
