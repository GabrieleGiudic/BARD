import pandas as pd
import ast

benchmark = pd.read_csv('benchmark.csv', sep=';')

gemini = pd.read_csv('gemini-2.5-pro-preview-06-05.csv', sep=';')

number_actions = 0

number_actions_tolerance = 0

total_action = 0

# Global match counters
action_match = 0
color_match = 0
player_match = 0
result_match = 0
assisted_match = 0
other_player_match = 0

# Stepwise counters
action_only = 0
action_color = 0
action_color_player = 0
action_color_player_result = 0
action_color_player_result_assisted = 0
perfect_match = 0

action_dependent = False

for i in range(0,len(benchmark)):
    if benchmark.iloc[i]['number_actions'] == gemini.iloc[i]['number_actions']:
        number_actions += 1
    if (benchmark.iloc[i]['number_actions'] +1>= gemini.iloc[i]['number_actions'] and 
         benchmark.iloc[i]['number_actions'] -1<= gemini.iloc[i]['number_actions'] ):
         number_actions_tolerance += 1

    bench_list = ast.literal_eval(benchmark.iloc[i]['actions_name'])
    gem_list = ast.literal_eval(gemini.iloc[i]['actions_name'])
    total_action += len(bench_list)
    for j in range(0,len(bench_list)):
        start_search = 0
        for k in range(start_search,len(gem_list)):
            # Flags
            action_flag = gem_list[k]['action'] == bench_list[j]['action']
            if not action_flag:
                continue
            color_flag = gem_list[k]['jersey_color'] == bench_list[j]['jersey_color']
            player_flag = str(gem_list[k]['player']) == bench_list[j]['player']
            
            assisted_flag = gem_list[k]['assisted'] == bench_list[j]['assisted']
            other_player_flag = str(gem_list[k]['other_player']) == str(bench_list[j]['other_player'])
            result_flag = gem_list[k]['result'] == bench_list[j]['result']
            
            # Count global flags
            if action_flag:
                action_match += 1
            if color_flag:
                color_match += 1
            if player_flag:
                player_match += 1
            if result_flag:
                result_match += 1
            if assisted_flag:
                assisted_match += 1
            if other_player_flag:
                other_player_match += 1
                
            # Stepwise nested condition check with counters
            if action_flag:
                action_only += 1
                if color_flag:
                    action_color += 1
                    if player_flag:
                        action_color_player += 1
                        if result_flag:
                            action_color_player_result += 1
                            if assisted_flag:
                                action_color_player_result_assisted += 1
                                if other_player_flag:
                                    perfect_match += 1
            
            
            start_search = k
            break
            
                
                
                
        
        
        