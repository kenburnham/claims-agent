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

client_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=client_key)

transcript_output_filename = "json_files/transcripts.jsonl"
json_output_filename = "json_files/json.jsonl"
comparison_check_filename = "json_files/check.jsonl"
transcript_count = 50
incidents = ["Low-Speed Collision (Fender Bender): Minor impact where the car is still drivable but has visible body damage.", 
             "Vandalism: Keying, spray paint, or intentional damage to the vehicle's exterior.", 
             "Hit and Run (Parked): Finding the car damaged in a parking lot with no note left by the other driver.", 
             "Animal Strike: Hitting a deer or other large animal, which usually falls under Comprehensive coverage rather than Collision.", 
             "Glass and Windshield Damage: A star or crack in the windshield caused by a rock on the highway. Many policies cover this with $0$ deductible.", 
             "Pothole Damage: Blown tires or rim damage caused by poor road conditions.", 
             "Minor Scrapes: Scraping a mailbox or a garage door frame while parking, resulting in paint transfer or small dents.", 
             "Lockout or Battery Issues: These usually fall under Roadside Assistance rather than a standard insurance claim.", 
             "Total Loss Collision: Accident where the vehicle is non-drivable and the repair costs likely exceed the car's value.", 
             "Multi-Vehicle Pileups: Accident involving three or more cars, which create complex liability issues.", 
             "Injury or Fatality: Any incident where medical attention is required. This is a high-exposure claim that require immediate legal and bodily injury adjusters.", 
             "Vehicle Theft: When a car is stolen and not recovered. This requires coordination with law enforcement and title verification.", 
             "Structural Fire: Damage caused by engine fires or external fires (like a garage fire) that compromise the vehicle's frame.", 
             "Severe Weather/Natural Disaster: Flood damage (water in the cabin), car being crushed by a fallen tree, or massive hail damage across all panels."
]
for i in range(1, (transcript_count + 1)):
    # Pick a random region, then a random voice from that region
    incident_choice = random.choice(incidents)
    prompt_text = f"""
    You are creating a random car insurance claim, Your response needs to have two speakers, denoted "Speaker 1" and "Speaker 2". Speaker 1 is the 
    claims agent, gathering information from Speaker 2, who is the insured person calling for assistance. The issue they are calling about is a: {incident_choice}
        
    Please generate a transcript, simulating Speaker 1 and Speaker 2 talking in the below format:

    Speaker 1: Thank you for calling support, I am here to help. What is your issue?
    Speaker 2: ....
    Speaker 1: ....
    Speaker 2: ....


    Speaker 1 needs to gather the below information through out the conversation:
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


    Simulate a real world scenario where Speaker 2 might not have all the answers, but can generate most of them. Before Speaker 1
    ends the call, they should generate a claim number for the incident report. The claim number should be only capital letters 
    in the format: AA-AA-AA-AA

    Your output should ONLY be in the "Speaker 1: Speaker 2:" format, simulating the transcript of an audio file.
    """
    # 4. Request the audio
    # You can even prompt Gemini to describe the accent based on the voice chosen!
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text
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
    """ + response.text

    json_script = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=json_prompt
    )

    check_prompt = f""" Please compare the following transcript with the following json to confirm that the json appropriately pulled all of the correct information.
    If all looks good, please output "TRUE", if not, please output "FALSE" and state what is not correct.
    TRANSCRIPT: {response.text}
    JSON: {json_script.text}"""

    double_check = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=check_prompt
    )

    print(f"TRANSCRIPT: {response.text}")
    print(f"JSON: {json_script.text}")
    print(f"CHECK: {double_check.text}")

    with open(transcript_output_filename, "a", encoding="utf-8") as f:
        # Convert dict to string and add a newline
        f.write(json.dumps(response.text) + "\n")
    
    with open(json_output_filename, "a", encoding="utf-8") as f:
        # Convert dict to string and add a newline
        f.write(json.dumps(json_script.text) + "\n")
    
    with open(comparison_check_filename, "a", encoding="utf-8") as f:
        # Convert dict to string and add a newline
        f.write(json.dumps(double_check.text) + "\n")