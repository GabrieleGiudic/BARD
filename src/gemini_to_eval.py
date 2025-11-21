import json
import ast
import pandas as pd

# -----------------------------
# INPUT FILES
# -----------------------------
prediction_csv = "gemini-2.5-pro-preview-06-05_2025.csv"  # prediction CSV
gt_csv = "../validation/2025/benchmark.csv"              # ground truth CSV
output_jsonl = "../validation/2025/pred_gemini.json"    # final output
base_image_path = ""  # leave empty if full paths already exist in CSV

# -----------------------------
# LOAD GROUND TRUTH CSV
# -----------------------------
gt_df = pd.read_csv(gt_csv)
gt_map = {}

for _, row in gt_df.iterrows():
    file_path = row["files"]
    actions = row["actions_name"]
    # normalize filename
    name = file_path.split("/")[-1]
    gt_map[name] = ast.literal_eval(actions)

# -----------------------------
# LOAD PREDICTION CSV
# -----------------------------
pred_df = pd.read_csv(prediction_csv, sep=';')

# -----------------------------
# FUNCTION TO TURN ACTION LIST → TEXT
# -----------------------------
def actions_to_text(actions):
    lines = []
    for act in actions:
        player = act.get("player")
        jersey_color = act.get("color") or act.get("jersey_color")
        action = act.get("action")
        result = act.get("result")
        assisted = act.get("assisted")
        other_player = act.get("other_player")

        line = f"A player with jersey number {player} and jersey_color {jersey_color} made a {action}"

        if result is True:
            line += " which result was made"
            if assisted:
                line += f" and was assisted by other player with jersey number {other_player}"
        elif result is False:
            line += " which result was miss"


        lines.append(line)
    return "\n".join(lines)

# -----------------------------
# PROCESS PREDICTIONS
# -----------------------------
output = []

for _, row in pred_df.iterrows():
    pred_file = row["files"]
    pred_actions = row["actions_name"]

    pred_name = pred_file.split("/")[-1]

    # parse prediction actions
    pred_list = ast.literal_eval(pred_actions)
    pred_text = actions_to_text(pred_list)

    # find matching GT
    if pred_name not in gt_map:
        print(f"WARNING: no GT for {pred_name}")
        continue

    gt_list = gt_map[pred_name]
    gt_text = actions_to_text(gt_list)

    entry = {
        "image": f"{base_image_path}/{pred_name}" if base_image_path else pred_file,
        "ground_truth": gt_text,
        "prediction": pred_text
    }
    output.append(entry)

# -----------------------------
# SAVE JSONL
# -----------------------------
with open(output_jsonl, "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print(f"Saved JSONL: {output_jsonl}")
