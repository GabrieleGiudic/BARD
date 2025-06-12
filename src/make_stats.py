import pandas as pd

file = '../validation/multi/validazione_multilabelling.xlsx'

valid = pd.read_excel(file)

new_col = []

for i in range(0,len(valid)):
    new_col.append(len(valid.iloc[i]['Azione'].split("_"))-1)
  
valid.insert(1, "number",new_col)

map_validation_our = {0:{"good":0,"bad":0},
                  1:{"good":0,"bad":0},
                  2:{"good":0,"bad":0},
                  3:{"good":0,"bad":0},
                  4:{"good":0,"bad":0},
                  5:{"good":0,"bad":0},
                  6:{"good":0,"bad":0},
                  7:{"good":0,"bad":0}}

map_validation_nsva  = {0:{"good":0,"bad":0},
                  1:{"good":0,"bad":0},
                  2:{"good":0,"bad":0},
                  3:{"good":0,"bad":0},
                  4:{"good":0,"bad":0},
                  5:{"good":0,"bad":0},
                  6:{"good":0,"bad":0},
                  7:{"good":0,"bad":0}}

our_col = 'Diff Paola+Gabriele vs Andrea'
nsva_col = 'nsva'
remote = 0

files = []
number_actions = []
actions_name = []
for i in range(0,len(valid)):
    number = valid.iloc[i]['number']
    
    values = valid.iloc[i][our_col]
    
    if values  == "remoto":
        remote = remote + 1
    else:
        values = valid.iloc[i][our_col]
        token = ""
        if type(values)==str:
            token = "bad"
        else:
            token ="good"
            files.append(valid.iloc[i]['Video'])

            number_actions.append( valid.iloc[i]['number'])
            
            actions = valid.iloc[i]['Azione'].split("_")[0:-1]
            json_list = []
            
            for action in actions:
                player = action.split("player")
                
                other_player = None
                assisted= None
                
                if ("2" in action or "3" in action or "Free" in action):
                    if len(action.split("assisted by"))>1:
                        other_player = action.split("assisted by")
                        other_player = other_player[1].split()[0]
                        assisted = True
                    else:
                        assisted = False
                
                player = player[1].split()[0]
                color = action.split("color")[1].replace(" ","")
                
                result = None
                if ("2" in action or "3" in action or "Free" in action):
                    result  = True
                    if ("Miss" in action or "miss" in action):
                        result = False
                        
                act = action[action.index(player)+1:action.index("color")]
                
                if "Free" in act:
                    act = "Free Throw"
                elif "2" in act:
                    act = "2PT Shot"
                elif "3" in act:
                     act = "3PT Shot"
                elif "Turn" in act:
                    act = "Turnover"
                elif "Foul" in act:
                     act = "Foul"
                elif "Block" in act:
                     act = "Block"
                elif "Reb" in act:
                     act = "Rebound"
                elif "Steal" in act:
                     act = "Steal"
                elif "Violation" in act:
                     act = "Violation"
                else:
                    raise Exception("no conversion")
                    
                json_list.append({ "player": player,
                                    "jersey_color": color,
                                    "action": act,
                                    "result": result,
                                    "assisted": assisted,
                                    "other_player": other_player}  )
            
            
            actions_name.append(json_list)
            
        map_validation_our[number][token] = map_validation_our[number][token] + 1
            
        values = valid.iloc[i][nsva_col]
        
        token = ""
        if  type(values)==str and values!= "ok":
            token = "bad"
        else:
            token ="good"
            
        map_validation_nsva[number][token] = map_validation_nsva[number][token] + 1

diff = {}    
for k in map_validation_nsva.keys():
    if k ==0:
        continue
    nsva =  map_validation_nsva[k]['good']/(map_validation_nsva[k]['good']+map_validation_nsva[k]['bad'])
    our =  map_validation_our[k]['good']/(map_validation_our[k]['good']+map_validation_our[k]['bad'])
    diff[k] = our-nsva


gemini = pd.DataFrame({
    'files': files,
    'actions_name': actions_name,
    'number_actions': number_actions
})

gemini.to_csv('benchmark.csv', sep=';', index=False)