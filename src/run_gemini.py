
GEMINI_API_KEY = ""

prompt = ("""
Analyze the basketball video and extract all key actions performed by players. Identify the jersey number, jersey color, and action type for each event. Provide the results in a structured JSON array format as shown below:

Possible Actions:
- Turnover
- Foul
- Block
- Rebound
- Steal
- 2PT Shot
- 3PT Shot
- Free Throw
- Violation

Output Format:

Return a JSON array where each object represents an individual action:

[
  {
    "player": <jersey_number>,  # integer, required
    "jersey_color": "<color>",  # string, required (e.g., white, blue, black, green, red, light blue, yellow, purple)
    "action": "<type_of_action>",  # string, required
    "result": <true | false | null>,  # true = made, false = missed, null if not applicable
    "assisted": <true | false | null>,  # true = assisted, false = not assisted, null if not applicable
    "other_player": <jersey_number | null>  # integer if another player is involved, null if not
  },
  {
    "player": <jersey_number>,
    "jersey_color": "<color>",
    "action": "<type_of_action>",
    "result": <true | false | null>,
    "assisted": <true | false | null>,
    "other_player": <jersey_number | null>
  }
]

Field Definitions:
- player (integer, required) – Jersey number of the player performing the action.
- jersey_color (string, required) – The primary color of the player’s jersey.
- action (string, required) – The type of action performed.
- result (boolean | null, required) –
  - true → Successful (e.g., made shot).
  - false → Unsuccessful (e.g., missed shot).
  - null → Not applicable (e.g., turnover, foul, rebound, block, steal).
- assisted (boolean | null, required for shots only) –
  - true → The shot was assisted.
  - false → The shot was unassisted.
  - null → Not applicable for non-shooting actions.
- other_player (integer | null, required) –
  - Jersey number of another involved player (e.g., assister).
  - null if no other player is involved.

Example Output:

[
  {
    "player": 23,
    "jersey_color": "blue",
    "action": "3PT Shot",
    "result": true,
    "assisted": true,
    "other_player": 6,
  },
  {
    "player": 11,
    "jersey_color": "white",
    "action": "Steal",
    "result": null,
    "assisted": null,
    "other_player": null
  },
  {
    "player": 32,
    "jersey_color": "red",
    "action": "Foul",
    "result": null,
    "assisted": null,
    "other_player": 15
  }
]

Instructions:
1. Detect and extract all actions in the video.
2. Identify players' jersey numbers and colors.
3. Classify the type of action performed.
4. Structure the output as a JSON array following the specified format.
"""
)

import pandas as pd

df = pd.read_csv('benchmark.csv', sep=';')

import os
from google import genai
import time
client = genai.Client(api_key=GEMINI_API_KEY)

results = {}

for i in range(0,len(df)):
    
    video_file_path = os.path.join('../validation/multi',df.iloc[i]['files'] +  '.mp4')
    
    try:
        # --- 3. Upload the Video File ---
        print(f"Attempting to upload video file: {video_file_path}")
        myfile = client.files.upload(file=video_file_path)
        print(f"Video file uploaded successfully! File ID: {myfile.name}")
        print(f"Initial file state: {myfile.state}")
    
        # --- 4. Wait for the File to Become ACTIVE ---
        # This loop is crucial for preventing the FAILED_PRECONDITION error.
        while str(myfile.state) == "FileState.PROCESSING":
            print("File is still processing on Google's servers, waiting..." + str(i))
            time.sleep(10) # Wait for 10 seconds before checking again
            # IMPORTANT: You need to re-fetch the file status to get its updated state
            myfile = client.files.get(name=myfile.name)
            print(f"Current file state: {myfile.state}")
    
        if str(myfile.state) == "FileState.ACTIVE":
            print("File is now ACTIVE and ready for use with the model.")
        else:
            # If the file didn't become ACTIVE (e.g., failed processing for some reason)
            print(f"Warning: File state is {myfile.state}. It might not be ready for use.")
            print("Please check the file status in your Google Cloud project or retry the upload.")
            exit() # Exit if the file isn't ready, no point in proceeding
    
        # --- 5. Generate Content Using the ACTIVE File ---
        # Ensure 'contents' list directly contains the File object and string parts.
        print("\nGenerating content (summary and quiz) from the video...")
        
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-06-05", contents=[myfile, prompt] )
        
        results[i] = response.text
    
    except FileNotFoundError:
        print(f"Error: The video file was not found at '{video_file_path}'. Please check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
 
import json

with open("gemini-2.5-pro-preview-06-05.json", "w") as f:
    json.dump(results, f, indent=4)

converted_results = []
number_actions = []
for k in results.keys():
    clean_json_str = results[k].strip('` \n')  # removes ``` and surrounding whitespace
    if clean_json_str.startswith('json'):
        clean_json_str = clean_json_str[4:].strip()
        
    converted_results.append(json.loads(clean_json_str))
    number_actions.append(len(converted_results[k]))

gemini = pd.DataFrame({
    'files': df["files"].to_numpy(),
    'actions_name': converted_results,
    'number_actions': number_actions
})

gemini.to_csv('gemini-2.5-pro-preview-06-05.csv', sep=';', index=False)