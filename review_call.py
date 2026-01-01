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
import linecache

client_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=client_key)

transcript_output_filename = "tele_json_output.jsonl"
comparison_check_filename = "review_call.jsonl"
print("Uploading file...")
audio_file = client.files.upload(file="audio_files/telephone_call-9-algieba-IN.wav")

prompt_text = f"""
Transcribe the audio file. This audio file has two speakers, denoted "Speaker 1" and "Speaker 2". Speaker 1 is the 
claims agent, gathering information from Speaker 2, who is the insured person calling for assistance. 

Please generate a transcript of Speaker 1 and Speaker 2 talking in the below format:

Speaker 1: ....
Speaker 2: ....
Speaker 1: ....
Speaker 2: ....


In the Audio file, Speaker 1 should gather the below information through out the conversation:
- The policy number of the insured (Policy Number is all numbers in the format: ###-###-###-###)
- The Date of Birth and full name of the insured
- The Phone number or email of the insured
- The date and time of the incident
- The location of the incident
- A brief description of the incident
- If there were any injuries
- If a police report was filed
- If the car was totaled or if it is still driveable
- How many others were involved, and if they have their contact information


Speaker 2 might not have all the answers, but can generate most of them. 
Before Speaker 1 ends the call, they should generate a claim number for the incident report. The claim number should be only capital letters 
in the format: AA-AA-AA-AA

Your output should ONLY be in the "Speaker 1: Speaker 2:" format, simulating the transcript of an audio file.
"""
audio_transcript = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[prompt_text, audio_file]
)

json_prompt = """In the below transcript, please save the following variables in json format:

{
    "policy_info": {
        "policy_number": "###-###-###-###",
        "insured_full_name": "",
        "date_of_birth": "YYY-MM-DD"
    },
    "contact_details": {
        "phone_number": "###-###-####",
        "email": "jane.doe@example.com"
    },
    "incident_details": {
        "timestamp": "",
        "location": "",
        "description": "",
        "injuries_reported": ,
        "police_report_filed":,
        "claim_number":
    },
    "vehicle_status": {
        "is_drivable": ,
        "is_totaled_estimate": 
    },
    "third_party_info": {
        "others_involved_count": ,
        "has_third_party_contact_info": ,
        "third_party_notes": ""
    }

    TRANSCRIPT:
}
""" + audio_transcript.text

json_script = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=json_prompt
)

with open("json_files/json.jsonl", "r", encoding="utf-8") as f:
        for current_index, line in enumerate(f):
            if current_index == 9:
                old_json = line.strip()
check_prompt = f""" Please compare the following two json contents to confirm that they are the same. 
They should match, except for some of the variables that are freeform (third_part_notes, description, etc). For the
freeform variables, please just assess whether the contents themselves are saying a similar thing.
Please output "TRUE" if the jsons are functionally the same, if not, please output "FALSE" and state what is not correct.
JSON_1: {json_script.text}
JSON_2: {old_json}"""

double_check = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=check_prompt
)

print(f"TRANSCRIPT: {audio_transcript.text}")
print(f"JSON_NEW: {json_script.text}")
print(f"JSON_OLD: {old_json}")
print(f"CHECK: {double_check.text}")

"""
with open(transcript_output_filename, "a", encoding="utf-8") as f:
    # Convert dict to string and add a newline
    f.write(json.dumps(response.text) + "\n")

with open(json_output_filename, "a", encoding="utf-8") as f:
    # Convert dict to string and add a newline
    f.write(json.dumps(json_script.text) + "\n")

with open(comparison_check_filename, "a", encoding="utf-8") as f:
    # Convert dict to string and add a newline
    f.write(json.dumps(double_check.text) + "\n")
"""