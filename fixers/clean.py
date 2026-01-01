import json

input_path = "golden_claims.jsonl" # This is your current [ ] file
output_path = "golden_claims_FIXED.jsonl"

with open(input_path, "r", encoding="utf-8") as f:
    # 1. Load the entire puzzle at once
    data_array = json.load(f)

print(f"Loaded {len(data_array)} records from the array.")

with open(output_path, "w", encoding="utf-8") as f_out:
    for entry in data_array:
        # 2. Extract the transcript if it's double-encoded
        t = entry.get("transcript", "")
        if isinstance(t, str) and t.strip().startswith('"'):
            try:
                entry["transcript"] = json.loads(t)
            except:
                pass

        # 3. Save each record as a single line
        f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Done! Use {output_path} for your audio script now.")