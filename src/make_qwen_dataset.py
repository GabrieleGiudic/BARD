import pandas as pd
import json
import ast # Used to safely evaluate the string representation of the list

def create_structured_dataset(df, prompt_text):
    """
    Generates the first dataset with a structured JSON array as the output.
    """
    output_data = []
    for _, row in df.iterrows():
        video_path = f"videos/{row['urls']}"
        
        # Safely parse the 'actions' string into a Python list of dictionaries
        actions_list = ast.literal_eval(row['actions'])
        
        # Rename the 'color' key to 'jersey_color' to match the prompt's schema
        for action in actions_list:
            if 'color' in action:
                action['jersey_color'] = action.pop('color')

        # Create the conversation structure
        conversation_entry = {
            "video": video_path,
            "conversations": [
                {
                    "from": "human",
                    "value": f"<video>\n{prompt_text}"
                },
                {
                    "from": "gpt",
                    "value": json.dumps(actions_list, indent=2)
                }
            ]
        }
        output_data.append(conversation_entry)
        
    return output_data

def create_caption_dataset(df, prompt_text):
    """
    Generates the second dataset with plain string captions as the output.
    """
    output_data = []
    for _, row in df.iterrows():
        video_path = f"videos/{row['urls']}"
        actions_list = ast.literal_eval(row['actions'])
        
        captions = []
        for action in actions_list:
            player = action.get('player')
            color = action.get('color')
            action_type = action.get('action')
            result = action.get('result')
            assisted = action.get('assisted')
            other_player = action.get('other_player')

            caption = (f"A player with jersey number {player} and jersey_color {color} "
                       f"made a {action_type}")

            # Append shot-specific details
            if 'Shot' in action_type or 'Free' in action_type :
                if result is True:
                    caption += " which result was made"
                    if assisted is True and other_player is not None:
                        caption += f" and was assisted by other player with jersey number {other_player}"
                elif result is False:
                    caption += " which result was miss"
            # Append details for other actions involving a second player
            elif other_player is not None:
                 caption += f" involving other player with jersey number {other_player}"

            captions.append(caption)
        
        # Join all captions for a single video into one string
        final_caption_string = "\n".join(captions)

        # Create the conversation structure
        conversation_entry = {
            "video": video_path,
            "conversations": [
                {
                    "from": "human",
                    "value": f"<video>\n{prompt_text}"
                },
                {
                    "from": "gpt",
                    "value": final_caption_string
                }
            ]
        }
        output_data.append(conversation_entry)
        
    return output_data

if __name__ == "__main__":
    # --- Prompt for Structured JSON Output ---
    prompt_1 = ("""
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
        "player": <jersey_number>,  # integer-like (generally integer value but admit the 00 case), required
        "jersey_color": "<color>",  # string, required (e.g., white, blue, black, green, red, light blue, yellow, purple)
        "action": "<type_of_action>",  # string, required
        "result": <true | false | null>,  # true = made, false = missed, null if not applicable
        "assisted": <true | false | null>,  # true = assisted, false = not assisted, null if not applicable
        "other_player": <jersey_number | null>  # integer-like (generally integer value but admit the 00 case) if another player is involved, null if not
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
    - player (integer-like (generally integer value but admit the 00 case), required) – Jersey number of the player performing the action.
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
    - other_player (integer-like (generally integer value but admit the 00 case) | null, required) –
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
        "other_player": null
      }
    ]
    
    Instructions:
    1. Detect and extract all actions in the video.
    2. Identify players' jersey numbers and colors.
    3. Classify the type of action performed.
    4. Structure the output as a JSON array following the specified format.
    """)

    # --- Prompt for Plain String Caption Output ---
    prompt_2 = ("""
    Analyze the basketball video and extract all player actions. For each action, identify the player’s jersey number, jersey color, and action type. Provide the results as plain string captions.
    
    ---
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
    ---
    
    Output Caption Format:
    "A player with jersey number <jersey_number>, and jersey_color: <color> made a <type_of_action> which result (if a shot) was miss/made (and if a shot was made) was assisted by other player with jersey number <other_player>"
    
    Field Definitions:
    - player (integer-like (generally integer value but admit the 00 case), required) – Jersey number of the player performing the action.
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
    - other_player (integer-like (generally integer value but admit the 00 case) | null, required) –
      - Jersey number of another involved player (e.g., assister).
      - null if no other player is involved.
    
    
    Example Output Captions.
    
    Single action:
        A player with jersey number 23 and jersey_color blue made a 3PT Shot which result was made and was assisted by other player with jersey number 6.
    Multiple actions:
        A player with jersey number 23 and jersey_color blue made a 3PT Shot which result was made and was assisted by other player with jersey number 6.
        A player with jersey number 11 and jersey_color white made a Steal.
        A player with jersey number 32 and jersey_color red made a Foul involving other player with jersey number 15.
    
    ---
    Instructions:
    1. Detect and extract all actions in the video.
    2. Identify each player’s jersey number and jersey color.
    3. Classify the action performed using the allowed list.
    4. Return the results **only as plain string captions (not JSON)**.""")

    # --- Load Data and Run Processing ---
    try:
        df = pd.read_csv('../dataset/dataset_paths.csv', sep=';')
        
        # --- Process and Save Datasets ---
        # Dataset 1: Structured JSON output
        structured_data = create_structured_dataset(df, prompt_1)
        with open('../dataset/dataset_structured_output.json', 'w') as f:
            json.dump(structured_data, f, indent=4)
        print("Successfully created 'dataset_structured_output.json'")

        # Dataset 2: Caption output
        caption_data = create_caption_dataset(df, prompt_2)
        with open('../dataset/dataset_caption_output.json', 'w') as f:
            json.dump(caption_data, f, indent=4)
        print("Successfully created 'dataset_caption_output.json'")

    except FileNotFoundError:
        print("Error: 'data.csv' not found. Please create this file and add your data to it.")
    except Exception as e:
        print(f"An error occurred: {e}")