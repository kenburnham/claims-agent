import json
import glob
import os

input_file = "json_files/golden_claims.jsonl"
output_file = "json_files/golden_claims_with_audio.jsonl"
audio_folder = "audio_files" # Change this to your folder path

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    for i, line in enumerate(f_in):
        data = json.loads(line)
        
        # 1. Create a search pattern for the specific index 'i'
        # This looks for: telephone-call-0-*.mp3, telephone-call-1-*.mp3, etc.
        search_pattern = os.path.join(audio_folder, f"telephone_call-{i}-*.wav")
        
        # 2. Use glob to find any file matching that pattern
        matching_files = glob.glob(search_pattern)
        
        if matching_files:
            # We take the first match [0] and get just the filename (not the full path)
            full_path = matching_files[0]
            file_name = os.path.basename(full_path)
            
            # 3. Add the filename as a new independent variable
            data["audio_filename"] = file_name
            print(f"Linked Index {i} to {file_name}")
        else:
            data["audio_filename"] = None
            print(f"Warning: No audio found for Index {i}")

        # 4. Write the updated record to the new file
        f_out.write(json.dumps(data, ensure_ascii=False) + "\n")