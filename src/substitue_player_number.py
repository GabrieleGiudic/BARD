import os
import pandas as pd
import pickle

def load_pkl(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

data_path_orig = r"..\data"

tokens = []
with os.scandir(data_path_orig) as entries:
    for entry in entries:
        if entry.is_dir() and entry.name!='src':
            tokens.append(entry.name)

df = pd.read_csv('../data/players.csv',sep=";")

#Replace complex chars with plain ones
df['Player Name'] = df['Player Name'].str.replace("ć", "c", regex=False)

df['Player Name'] = df['Player Name'].str.replace("č", "c", regex=False)

df['Player Name'] = df['Player Name'].str.replace("ū", "u", regex=False)

df['Player Name'] = df['Player Name'].str.replace("ö", "o", regex=False)

df['Player Name'] = df['Player Name'].str.replace("ņ", "n", regex=False)

df['Player Name'] = df['Player Name'].str.replace("ģ", "g", regex=False)

df['Player Name'] = df['Player Name'].str.replace("ñ", "n", regex=False)
    
df['Player Name'] = df['Player Name'].str.replace("Š", "S", regex=False)

df['Player Name'] = df['Player Name'].str.replace("é", "e", regex=False)
    
df['Player Name'] = df['Player Name'].str.replace("š", "s", regex=False)
df['Player Name'] = df['Player Name'].str.replace(" Jr", "Jr", regex=False)


ref = pd.read_csv('../data/referee.csv',header=None)


count_entry = 0
for token in tokens:
    team1 = token.split("-")[0].upper()
    team2 = token.split("-")[2].upper()
    
    if team1=="BKN":# from our source the team code should be aligned
        team1="BRK"
    if team2=="BKN":
        team2="BRK"
        
    if team1=="CHA":
        team1="CHO"
    if team2=="CHA":
        team2="CHO"
    
    if team1=="PHX":
        team1="PHO"
    if team2=="PHX":
        team2="PHO"
    
    data_path = os.path.join(data_path_orig,token)
    
    
    pkl_file = os.path.join(data_path,"url_info.pkl" ) 
    data = load_pkl(pkl_file)
    
    for i in range(0,len(data)):
        data[i]["info_player_number"] = data[i]["info"]
        
    for r in ref[0]:
        for i in range(0,len(data)):
            if r in data[i]["info_player_number"] :
                 data[i]["info_player_number"]  =  data[i]["info_player_number"] .replace(" ( " + r + " )", "")
                 data[i]["info_player_number"]  =  data[i]["info_player_number"] .replace("(" + r  + ")", "")
                 data[i]["info_player_number"]  =  data[i]["info_player_number"] .replace(r , "")
    
    
    subset_team1 = df[df['Team'] == team1]
    
    subset_team2 = df[df['Team'] == team2]
    manual = []
    count_entry = count_entry + len(data)
    for i in range(0,len(data)):
        
        desc = data[i]["info_player_number"]
        
        full_desc= desc
        
        #Replace complex chars with plain ones
        desc = desc.replace("%27", "'")
        desc = desc.replace("ć", "c")
        desc = desc.replace("č", "c")
        desc = desc.replace("ū", "u")
        desc = desc.replace("ö", "o")
        desc = desc.replace("ņ", "n")
        desc = desc.replace("ģ", "g")
        desc = desc.replace("ñ", "n")
        desc = desc.replace("Š", "S")
        desc = desc.replace("é", "e")
        desc = desc.replace("š", "s")
        desc = desc.replace("í", "i")
        desc = desc.replace(":", " : ")
        desc = desc.replace("(", " ( ")
        desc = desc.replace(")", " ) ")
        desc = desc.replace("\n", " token_next_line ")
        desc = desc.replace(" Jr.", "Jr")
        desc = desc.replace(" III", "")
        desc = desc.replace(" II", "")
        desc = desc.replace("Vs.", "Vs")
        desc = desc.replace(". ", ".")
        
        desc = desc.split()
        new_d = ""
        
            
        for d in desc:
            in_team1 = False
            in_team2 = False
            for n in subset_team1["Player Name"]:
                if in_team1:
                    break
                nn = n.split()
                for nnn in nn:
                    if nnn == d:
                        in_team1 = True
                        break
            for n in subset_team2["Player Name"]:
                if in_team2:
                    break
                nn = n.split()
                for nnn in nn:
                    if nnn == d:
                        in_team2 = True
                        break
            
            if not in_team1 and not in_team2:
                if d in subset_team1["Player Name 2"].to_numpy():
                    val = "1"
                    j = subset_team1["Player Name 2"].to_numpy().tolist().index(d)
                    d = "team"+val +"-number"  + str(int(subset_team1["Number"].iloc[j]))
                   
                if d in subset_team2["Player Name 2"].to_numpy():
                    val = "2"
                    j = subset_team2["Player Name 2"].to_numpy().tolist().index(d)
                    d = "team"+val +"-number"  + str(int(subset_team2["Number"].iloc[j]))
                new_d = new_d + " " + d
                continue
            
            if in_team1 and in_team2:
                curr_t = subset_team1
                val = "1"
                if  "Home: true" in full_desc:
                    curr_t = subset_team2
                    val = "2"
                for j in range(0,len(curr_t["Player Name"])):
                    if d in curr_t["Player Name"].iloc[j]:
                        d = "team"+val +"-number"  + str(int(curr_t["Number"].iloc[j]))
                        break
                
                new_d = new_d + " " + d
                continue
                
            if in_team1:
                for j in range(0,len(subset_team1["Player Name"])):
                    if d in subset_team1["Player Name"].iloc[j]:
                        d = "team1-number"  + str(int(subset_team1["Number"].iloc[j]))
                        break
            if in_team2:
                for j in range(0,len(subset_team2["Player Name"])):
                    if d in subset_team2["Player Name"].iloc[j]:
                        d = "team2-number"  + str(int(subset_team2["Number"].iloc[j]))
                        break
            new_d = new_d + " " + d
       
        if new_d[0] == ' ':
            new_d = new_d[1:]
            
        data[i]["info_player_number"] = new_d  
        
            
            
    pkl_file = os.path.join(data_path,"new_info.pkl" ) 
    with open(pkl_file, 'wb') as file:
        pickle.dump(data, file)
    
print(count_entry)