from google import genai
from google.genai import types
import os
import base64
import wave
import io
import numpy as np
from scipy.signal import butter, lfilter

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

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts", 
    contents="Please read this text with a warm, friendly, and helpful tone: 'Hello! I am your AI thought partner. How can I help you today?'",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name='Aoede' # Other options include 'Kore', 'Charon', 'Fenrir'
                )
            )
        )
    )
)

# 2. Get the data
# The SDK often returns base64-encoded text inside a bytes object
raw_data = response.candidates[0].content.parts[0].inline_data.data

tele_audio = telephone_filter(raw_data, sample_rate=24000)


# 2. Save at 8000 Hz for the final "crushed" effect
with wave.open("telephone_output3.wav", "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(8000) # This is the "Telephone" speed
    wav_file.writeframes(tele_audio.tobytes())

print("Success! 'output_speech.wav' is now a valid, playable file.")

