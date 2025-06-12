import os
import json

import pickle
import pandas as pd

def load_pkl(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

# Initialize stats
stats = {
    "ast": 0,
    "turn": 0,
    "reb": 0,
    "foul": 0,
    "2ptmade": 0,
    "2ptmiss": 0,
    "3ptmiss": 0,
    "3ptmade": 0,
    "freemade": 0,
    "freemiss": 0,
    "block": 0,
    "steal": 0,
    "violation":0
}

# Function to update stats based on input action
def update_stats(action):
    action = action.lower()  # Convert action to lowercase
    updated_stat_key = None  # To store the updated stat key
    updated_stat_key_2 = None
    
    if "free" in action:
        if "miss" in action:
            updated_stat_key = "freemiss"
        elif not "miss" in action:
            updated_stat_key = "freemade"
    elif "ast" in action:
        updated_stat_key = "ast"
        if "3pt" in action:
            updated_stat_key_2 = "3ptmade"
        else:
            updated_stat_key_2= "2ptmade"
            
    elif "3pt" in action:
        if "miss" in action:
            updated_stat_key = "3ptmiss"
        elif not "miss" in action:
            updated_stat_key = "3ptmade"
    elif "pts" in action or "shot" in action or "layup" in action or "dunk" in action or "jumper" in action:
         if "miss" in action:
            updated_stat_key = "2ptmiss"
         elif not "miss" in action:
             updated_stat_key = "2ptmade"
    elif "turn" in action:
        updated_stat_key = "turn"
    
    elif "reb" in action:
        updated_stat_key = "reb"
    elif "violation"in action:
         updated_stat_key = "violation"
    elif "foul" in action  or "technical" in action:
        updated_stat_key = "foul"
    
    elif "block" in action:
        updated_stat_key = "block"
     
    elif "steal" in action:
        updated_stat_key = "steal"

    return (updated_stat_key, updated_stat_key_2)  # Return whether increment was made and the updated stat key

def switch(player,action_key,additional_key,other_player,color):
# Determine action based on input key
    if action_key == "freemade":
        action = "Free Throw"
        result = True
        assisted = False
    elif action_key == "freemiss":
        action = "Free Throw"
        result = False
        assisted = False
    elif action_key == "2ptmade":
        action = "2PT Shot"
        result = True
        assisted = False
    elif action_key == "2ptmiss":
        action = "2PT Shot"
        result = False
        assisted = False
    elif action_key == "3ptmade":
        action = "3PT Shot"
        result = True
        assisted = False
    elif action_key == "3ptmiss":
        action = "3PT Shot"
        result = False
        assisted = False
    elif action_key == "turn":
        action = "Turnover"
        result = None
        assisted = None
    elif action_key == "foul":
        action = "Foul"
        result = None
        assisted = None
    elif action_key == "block":
        action = "Block"
        result = None
        assisted = None
    elif action_key == "reb":
        action = "Rebound"
        result = None
        assisted = None
    elif action_key == "steal":
        action = "Steal"
        result = None
        assisted = None
    elif action_key == "violation":
        action = "Violation"
        result = None
        assisted = None
    elif action_key == "ast":
         action = additional_key
         result = True
         assisted = True
         if additional_key == "2ptmade":
             action = "2PT Shot"
         elif additional_key == "3ptmade":
             action = "3PT Shot"
         else:
             raise Exception("not supported assisted action")
    else:
        raise Exception("missing action")

    # Add or update the action in the data
    if action == "2ptmade":
        print('here')
    return {
        "player": player,
        "action": action,
        "result": result,
        "assisted": assisted,
        "other_player": other_player,
        "color": color
    }


# Define preprocessing functions
def process(dataset, colors, urls,values,numbers):
    
    # Process and save images and labels
    for key in dataset.keys():
        vals = []
        info_multi_data = dataset[key]["info_multi"]
        for j in range(0,len(info_multi_data)):
            if "Tip To" in info_multi_data[j] or "tag" in info_multi_data[j] or "Ejection" in info_multi_data[j] or not "number" in info_multi_data[j]:
                print(info_multi_data[j])
                continue
            
        
            color = colors["1"] if "team1" in info_multi_data[j] else colors["2"]
            stat, second_stat = update_stats(info_multi_data[j])
            idx = info_multi_data[j].find("number")  # Find first occurrence
            label = info_multi_data[j][idx+6:idx+8]
            number1 = label.strip()
             
            number2 = None
            if stat == "ast":
                idx = info_multi_data[j].find("number", idx + 1) 
                label = info_multi_data[j][idx+6:idx+8]
                number2 = label.strip()
            val = switch(number1,stat,second_stat,number2,color)
            vals.append(val)
            
        if len(vals)>0:
            urls.append(dataset[key]["url"])
            values.append(vals)
            numbers.append(len(vals))

def save_dataset(input_folder,output_folder):
    
    tokens = []
    with os.scandir(input_folder) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name!='src':
                tokens.append(entry.name)
            
    actions = []
    urls = []
    numbers = []
    for token in tokens:
        print(token)
        p = os.path.join(input_folder,token,"info_multi.pkl")
        dataset = load_pkl(p)
        json_file = os.path.join(input_folder,token,"color.json" ) 
        with open(json_file, "r") as file:
            colors = json.load(file)
        
        process(dataset,colors,urls,actions,numbers)
    
    df = pd.DataFrame({
    'urls': urls,
    'actions': actions,
    'numerosity':numbers
    })
    
    return df
            
# Create dataset
input_folder = './../data'
output_folder = './../dataset'

df = save_dataset(input_folder,output_folder)

df = df[df["numerosity"] <= 5] #remove class with more than 5 actions

df.to_csv(os.path.join(output_folder,"dataset.csv"), index=False, sep=';')



#MAKE SOME GRAPHS

import matplotlib.pyplot as plt
import numpy as np


# Histogram data
counts, bins = np.histogram(df["numerosity"], bins=5)

# Colors for each bar
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # blue, orange, green, red, purple

# Plot setup
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars with different colors
bar_widths = np.diff(bins) * 0.9
bar_positions = bins[:-1] + np.diff(bins) * 0.05  # Shift to center

bar_container = ax.bar(bar_positions, counts, width=bar_widths,
                       color=colors, edgecolor='black',
                       align='edge', linewidth=1)


# Annotate bars with counts
for rect in bar_container:
    height = rect.get_height()
    if height > 0:
        ax.text(rect.get_x() + rect.get_width()/2, height + 0.4, f'{int(height)}', 
                ha='center', va='bottom', fontsize=13, fontweight='bold')

# Styling
ax.set_title('Number of Action per Class', fontsize=20, fontweight='bold', color='#333333')
ax.set_xlabel('Number of Action per Class', fontsize=15)
ax.set_ylabel('Frequency', fontsize=15)
ax.grid(axis='y', linestyle='--', alpha=0.6)
ax.set_facecolor('#fafafa')
fig.patch.set_facecolor('#ffffff')

bin_centers = (bins[:-1] + bins[1:]) / 2

# Set x-ticks at bin centers
numbers = np.array(list(range(1, 6)))
plt.xticks(bin_centers, labels=[f'{int(center)}' for center in numbers], fontsize=13)
plt.yticks(fontsize=13)

plt.tight_layout()
plt.savefig('../figures/histogram.png', dpi=300)
plt.show()


#Check category
action_map = {}
for i in range(0,len(df)):
    action_list = df.iloc[i]['actions']
    for action in action_list:
        assisted = action['assisted']
        suffix = ""
        if assisted:
            suffix = " AST"
        if action['action']+suffix in action_map.keys():
            action_map[action['action']+suffix] = action_map[action['action']+suffix] + 1
        else:
            action_map[action['action']+suffix] = 1
            
number_actions = 0
for k in action_map.keys():
    number_actions = number_actions + action_map[k]
    
# Convert to DataFrame
df = pd.DataFrame(list(action_map.items()), columns=["Action", "Count"])
df = df.sort_values(by="Count", ascending=False)

# 9 unique colors
colors = [
    '#1f77b4',  # blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22'   # olive
]

# Plot setup
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(df["Action"], df["Count"], color=colors, edgecolor='black', linewidth=1)

# Annotate each bar
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 100, f'{height}', 
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Styling
ax.set_title("Count of Each Action Type ("+ str(number_actions) +")", fontsize=20, fontweight='bold', color='#333333')
ax.set_xlabel('Action Type', fontsize=15)
ax.set_ylabel('Count', fontsize=15)
ax.set_facecolor('#fafafa')
fig.patch.set_facecolor('#ffffff')
ax.grid(axis='y', linestyle='--', alpha=0.6)

plt.xticks(rotation=45, fontsize=13)
plt.yticks(fontsize=13)
plt.tight_layout()
plt.savefig('../figures/action_bar_chart_unique_colors.png', dpi=300)
plt.show()