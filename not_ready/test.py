import json

transcript_filepath = "transcripts.jsonl"

with open(transcript_filepath, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        # Turn the string into a Python Dictionary
        data = json.loads(line)
        
        # Print the WHOLE entry in a readable way
        print(f"--- NEW ENTRY --- i = {i}")
        print(json.dumps(data, indent=4))
        print("\n") # Adds extra space between entries