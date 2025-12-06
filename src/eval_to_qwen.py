import json
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def remap_dataset(file1_path, file2_path, output_path,token):
    # Load first file (list of dicts with image + ground_truth)
    file1 = load_json(file1_path)

    # Load second file (structure + prompt)
    file2 = load_json(file2_path)

    # Extract the human prompt (same for all)
    human_prompt = file2[0]["conversations"][0]["value"]

    remapped = []

    for item in file1:
        image_path = item["image"]
        ground_truth = item["ground_truth"]

        filename = os.path.basename(image_path)

        # Build new video path
        new_video_path = (
            "data" + token + "/" + filename
        )

        # Build new item using second file structure
        new_item = {
            "video": new_video_path,
            "conversations": [
                {
                    "from": "human",
                    "value": human_prompt  # copied from file2
                },
                {
                    "from": "gpt",
                    "value": ground_truth  # read from file1
                }
            ]
        }

        remapped.append(new_item)

    # Save remapped dataset
    with open(output_path, "w") as f:
        json.dump(remapped, f, indent=4)

    print(f"Done! Saved remapped dataset to {output_path}")


# ----------- Example Usage -----------
if __name__ == "__main__":
    remap_dataset(
        r"..\validation\2024\pred_gemini.json",    # input file with image + ground_truth
        r"..\validation\sample.json",    # file with template + human prompt
        r"..\validation\2024\model_input_dataset_2024.json" , # output,
        "2024"
        
    )
