import pandas as pd
import ast

benchmark = pd.read_csv('benchmark.csv', sep=';')

gemini = pd.read_csv('gemini-2.5-pro-preview-06-05.csv', sep=';')

number_actions = 0

number_actions_tolerance = 0

total_action = 0

# Global match counters

match_stats = {
    "action": 0,
    "jersey_color": 0,
    "player": 0,
    "assisted": 0,
    "result": 0,
    "other_player": 0
}


for i in range(0,len(benchmark)):
    if benchmark.iloc[i]['number_actions'] == gemini.iloc[i]['number_actions']:
        number_actions += 1
    if (benchmark.iloc[i]['number_actions'] +1>= gemini.iloc[i]['number_actions'] and 
         benchmark.iloc[i]['number_actions'] -1<= gemini.iloc[i]['number_actions'] ):
         number_actions_tolerance += 1

    bench_list = ast.literal_eval(benchmark.iloc[i]['actions_name'])
    gem_list = ast.literal_eval(gemini.iloc[i]['actions_name'])
    total_action += len(bench_list)
    for key in match_stats.keys():
        for j in range(0,len(bench_list)):
            for k in range(0,len(gem_list)):
                # Flags
                flag = False
                if key =="player":
                    flag = str(gem_list[k]['player']) == bench_list[j]['player']
                elif key == "other_player":
                    flag = str(gem_list[k]['other_player']) == str(bench_list[j]['other_player'])
                else:
                    flag = gem_list[k][key] == bench_list[j][key]
                
                if flag:
                    match_stats[key]+=1
                    break
                
                    
                    
                
        
        
        