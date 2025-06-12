import pickle
import os


team_1 = [ "Hawks",
            "Celtics",
            "Nets",
            "Hornets",
            "Bulls",
            "Cavaliers",
            "Mavericks",
            "Nuggets",
            "Pistons",
            "Warriors",
            "Rockets",
            "Pacers",
            "Clippers",
            "Lakers",
            "Grizzlies",
            "Heat",
            "Bucks",
            "Timberwolves",
            "Pelicans",
            "Knicks",
            "Thunder",
            "Magic",
            "76ers",
            "Suns",
            "Trail Blazers",
            "Kings",
            "Spurs",
            "Raptors",
            "Jazz",
            "Wizards"
            ]

team_2 = [f"{team.upper()}" for team in team_1]

tags_fix = ["Ja.","Je.","Jal.","Jay.",
         "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.", 
         "K.", "L.", "M.", "N.", "O.", "P.", "Q.", "R.", "S.", "T.",
         "U.", "V.", "W.", "X.", "Y.", "Z."]

data_path_orig = r"..\data"

tokens = []
with os.scandir(data_path_orig) as entries:
    for entry in entries:
        if entry.is_dir() and entry.name!='src':
            tokens.append(entry.name)
            
for token  in tokens:
    
    path = os.path.join(data_path_orig,token,'new_info.pkl')
   
    with open(path, 'rb') as f:
        sanitized_text = pickle.load(f)
    
    
    for i in range(0,len(sanitized_text)):
        
        value = sanitized_text[i]["info_player_number"]
        
        for tag in tags_fix:
            if tag in value:
                value =  value.replace(tag + " ", "")
        
        
        tags = ["REBOUND","FOUL","foul","Turnover"]
        
        for tag in tags:
            if tag in value :
                i_r =  value.find(tag)
                substr = value[i_r:]
                i_lb = substr.find('(')
                i_rb = substr.find(')')
                if i_lb>0 and i_rb>0 and i_lb<i_rb:
                    value =  value[:i_r + i_lb ] +  value[i_r + i_rb +1 :]
                
        splitter = value.split(" ")
        
        value = ""
        
        for s in range(0,len(splitter)):
            
            for team in team_1:
                if team in splitter[s]:
                    splitter[s] = "team1"
                    
            for team in team_2:
                if team == splitter[s]:
                    splitter[s] = "team2"
                    
        for s in range(1,len(splitter)):
            if (splitter[s] =="BLK" or
                splitter[s] =="PTS" or
                splitter[s] =="STL" or
                splitter[s] =="AST" ):
                continue
            else:
                value = value + " " + splitter[s-1]
            if s == len(splitter)-1:
                value = value + " " + splitter[s]
                
        if value[0] == " ":
            value= value[1:]
            
    
        # value = value.replace("team1-", "")
        # value = value.replace("team2-", "")
        # value = value.replace("number", "Player ")
        value = value.replace(" : Shot Clock" , "")
        value = value.replace("Free Throw Technical" , "Free Throw")
        value = value.replace("1 Of 1" , "")
        value = value.replace("1 Of 2" , "")
        value = value.replace("1 Of 3" , "")
        value = value.replace("2 Of 2" , "")
        value = value.replace("2 Of 3" , "")
        value = value.replace("3 Of 3" , "")
        
        tags = ["Turnover","Shot", "Dunk", "Layup", "Jumper","Turnaround Fadeaway"]
        for tag in tags:
            if tag in value:
                index = value.index(tag)
                token_tag = ""
                if '3PT' in value:
                    token_tag = ' 3PT '
                elif tag in tags[1:]:
                    token_tag = ' 2PT '
                else:
                    token_tag = ' '
                
                if "'" in value:
                    j = value.index("'")
                    k=j
                    while k>=0:
                        if value[k]==" ":
                            break
                        k=k-1
                    value = value[0:k] +  token_tag + value[index:]
                elif  '3PT' in value:
                    k = value.index("3PT") + 3
                    value = value[0:k] + value[index-1:]
                elif "number" in value:
                    k = value.index("number") + 9
                    value = value[0:k] + value[index-1:]
                elif "Turnover" in value:
                    k = value.index("Turnover") + len("Turnover")
                    value = value[0:k]
                else:
                    print("not defined behaviour " + str(value))
                    print(token)
                    
          
        value = value.replace("Turnover Turnover" , "Turnover")     
        
        value = value.replace("Layup" , "Shot")  
        value = value.replace("Jumper" , "Shot") 
        value = value.replace("Dunk" , "Shot")
        value = value.replace("Turnaround Fadeaway" , "Shot")
    
        value = value.replace("T.FOUL" , "FOUL")
        value = value.replace("P.FOUL" , "FOUL")
        value = value.replace("S.FOUL" , "FOUL")
        value = value.replace("Personal Take Foul" , "FOUL")
        value = value.replace("L.B.FOUL" , "FOUL")
        value = value.replace("Offensive Charge Foul" , "FOUL")
        value = value.replace("FLAGRANT.FOUL.TYPE1" , "FOUL")
        value = value.replace("OFF.Foul" , "FOUL")
        value = value.replace("Violation : Defensive Goaltending" , "Violation")

        
        value = value.replace("( P1.T1 )" , "")
        value = value.replace("( P1.T2 )" , "")
        value = value.replace("( P1.T3 )" , "")
        value = value.replace("( P1.T4 )" , "")
        value = value.replace("( P1.PN )" , "")
        value = value.replace("( P2.PN )" , "")
        value = value.replace("( P3.PN )" , "")
        value = value.replace("( P4.PN )" , "")
        
        value = value.replace("( P1 )" , "")
        value = value.replace("( P2 )" , "")
        value = value.replace("( P3 )" , "")
        value = value.replace("( P4 )" , "")
        
        value = value.replace("Sr." , "")
        
        sanitized_text[i]["info_coarse"] = value
            
    pkl_file = os.path.join(data_path_orig,token,"coarse_info.pkl" ) 
    with open(pkl_file, 'wb') as file:
        pickle.dump(sanitized_text, file)
    