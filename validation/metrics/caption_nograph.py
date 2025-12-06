import json
import sys
import os
import re
from collections import Counter, defaultdict
import numpy as np
from sklearn.metrics import confusion_matrix

# Define the set of all valid, known actions.
KNOWN_ACTIONS = {
    "2pt shot", "3pt shot", "block", "foul",
    "free throw", "rebound", "steal", "turnover", "violation"
}

# --- Define Action Classes ---
# Maps specific actions to a general class. Actions not in the map belong to their own class.
ACTION_CLASSES = {
    "2pt shot": "shot",
    "3pt shot": "shot",
    "free throw": "shot",
}

def get_action_class(action: str) -> str:
    """Returns the general class for a given action."""
    return ACTION_CLASSES.get(action, action)

def parse_events(text_str: str) -> list:
    """
    Parses natural language string into event dicts.
    FIXES:
    1. Handles multi-word colors (e.g., 'light blue', 'dark green').
    2. Uses finditer to capture ALL events in the text, not just the first one.
    3. Handles missing results (e.g., Rebounds) gracefully.
    """
    if not isinstance(text_str, str) or not text_str.strip():
        return []

    events = []
    
    # Sort actions by length (descending) to ensure "3pt shot" is matched before "shot" if overlapping
    sorted_actions = sorted(list(KNOWN_ACTIONS), key=len, reverse=True)
    
    # Regex Breakdown:
    # 1. jersey_color (.+?)  -> Matches "light blue", "dark green", "red" (stops at " made a")
    # 2. re.IGNORECASE       -> Handles "Free Throw" vs "free throw"
    pattern = re.compile(
        r"A player with jersey number (\S+?) and jersey_color (.+?) "
        r"made a (" + "|".join(re.escape(a) for a in sorted_actions) + ")"
        r"(?: which result was (made|miss))?"
        r"(?: and was assisted by other player with jersey number (\S+))?", 
        re.IGNORECASE
    )

    # Use finditer to loop through ALL matches in the text block
    for match in pattern.finditer(text_str):
        player, jersey_color, action, result_str, other_player_str = match.groups()
        
        # Normalize Result
        result = None
        if result_str:
            if result_str.lower() == 'made':
                result = True
            elif result_str.lower() == 'miss':
                result = False
        
        # Normalize Assisted
        assisted = bool(other_player_str)
        other_player = other_player_str.strip('.') if other_player_str else None
        
        event = {
            "player": player.strip('.'),
            "action": action.lower(),
            "result": result,
            "assisted": assisted,
            "other_player": other_player,
            "jersey_color": jersey_color.strip().lower() # Strip removes surrounding spaces
        }
        events.append(event)
        
    return events
    
    """
    Parses a natural language string containing one or more event descriptions
    into a list of event dictionaries using regular expressions.
    """
    if not isinstance(text_str, str) or not text_str.strip():
        return []

    events = []
    # Pattern remains the same
    pattern = re.compile(
        r"A player with jersey number (\S+?) and jersey_color (\w+?) "
        r"made a (" + "|".join(KNOWN_ACTIONS) + ")"
        r"(?: which result was (made|miss))?"
        r"(?: and was assisted by other player with jersey number (\S+))?", re.IGNORECASE
    )
    
    # FIX: Use finditer on the whole string, treating it as one block 
    # (or you can keep the line split if you prefer, but finditer is safer).
    
    # We replace newlines with spaces just in case a sentence wraps weirdly, 
    # though your current regex likely assumes single-line matches.
    # Ideally, just iterate over the matches:
    
    for match in pattern.finditer(text_str):
        player, jersey_color, action, result_str, other_player_str = match.groups()
        
        result = None
        if result_str and result_str.lower() == 'made':
            result = True
        elif result_str and result_str.lower() == 'miss':
            result = False
        
        assisted = bool(other_player_str)
        other_player = other_player_str.strip('.') if other_player_str else None
        
        event = {
            "player": player.strip('.'),
            "action": action.lower(),
            "result": result,
            "assisted": assisted,
            "other_player": other_player,
            "jersey_color": jersey_color.lower()
        }
        events.append(event)
    
    if len(events)==0:
        print(text_str)
        
    return events
def parse_events_(text_str: str) -> list:
    """
    Parses a natural language string containing one or more event descriptions
    into a list of event dictionaries using regular expressions.
    """
    if not isinstance(text_str, str) or not text_str.strip():
        return []

    events = []
    # Added re.IGNORECASE to the pattern and convert action/color to lowercase
    pattern = re.compile(
        r"A player with jersey number (\S+?) and jersey_color (\w+?) "
        r"made a (" + "|".join(KNOWN_ACTIONS) + ")"
        r"(?: which result was (made|miss))?"
        r"(?: and was assisted by other player with jersey number (\S+))?", re.IGNORECASE
    )
    lines = text_str.strip().splitlines()

    for line in lines:
        match = pattern.search(line)
        if match:
            player, jersey_color, action, result_str, other_player_str = match.groups()
            result = None
            if result_str and result_str.lower() == 'made':
                result = True
            elif result_str and result_str.lower() == 'miss':
                result = False
            
            assisted = bool(other_player_str)
            other_player = other_player_str.strip('.') if other_player_str else None
            
            event = {
                "player": player.strip('.'),
                "action": action.lower(),
                "result": result,
                "assisted": assisted,
                "other_player": other_player,
                "jersey_color": jersey_color.lower()
            }
            events.append(event)
    return events

def normalize_actions(events: list, known_actions: set):
    """Replaces any action not in the known set with 'Unknown'."""
    if not events:
        return []
    for event in events:
        if event.get('action') not in known_actions:
            event['action'] = 'unknown'
    return events

def lcs_length(a: list, b: list) -> int:
    """Calculates the length of the Longest Common Subsequence between two lists."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i-j-1])
    return dp[m][n]

def _populate_bag_cm_data(gt_counts: Counter, pred_counts: Counter, y_true: list, y_pred: list):
    """
    Helper function to create paired lists for a confusion matrix from unordered counts.
    """
    all_labels = set(gt_counts.keys()) | set(pred_counts.keys())
    for label in all_labels:
        tp = min(gt_counts.get(label, 0), pred_counts.get(label, 0))
        fn = gt_counts.get(label, 0) - tp
        fp = pred_counts.get(label, 0) - tp
        y_true.extend([label] * tp)
        y_pred.extend([label] * tp)
        y_true.extend([label] * fn)
        y_pred.extend(['__MISSING__'] * fn)
        y_true.extend(['__SPURIOUS__'] * fp)
        y_pred.extend([label] * fp)

def are_events_a_perfect_match(event1: dict, event2: dict) -> bool:
    """Checks if two event dictionaries match on all fields."""
    return (
        str(event1.get('action')) == str(event2.get('action')) and
        str(event1.get('player')) == str(event2.get('player')) and
        str(event1.get('jersey_color')).lower() == str(event2.get('jersey_color')).lower() and
        str(event1.get('result')) == str(event2.get('result')) and
        str(event1.get('assisted')) == str(event2.get('assisted')) and
        str(event1.get('other_player')) == str(event2.get('other_player'))
    )

def evaluate_events(gt_events: list, pred_events: list) -> tuple:
    """
    Performs a multi-layered evaluation of events.
    """
    stats = defaultdict(int)
    y_true_bags = defaultdict(list)
    y_pred_bags = defaultdict(list)
    y_true_conditional = defaultdict(list)
    y_pred_conditional = defaultdict(list)
    
    SHOT_ACTIONS = {action for action, group in ACTION_CLASSES.items() if group == 'shot'}
    ASSISTED_SHOT_ACTIONS = {"2pt shot", "3pt shot"}

    # --- Pass 1: Action Match ---
    pred_used_action = [False] * len(pred_events)
    action_matched_pairs = []
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_action[i] and gt_event.get('action') == pred_event.get('action'):
                stats['action_match_tp'] += 1
                action_matched_pairs.append((gt_event, pred_event))
                pred_used_action[i] = True
                break

    # --- Pass 2: Action + Color Match ---
    pred_used_color = [False] * len(pred_events)
    action_color_matched_pairs = []
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_color[i] and \
               gt_event.get('action') == pred_event.get('action') and \
               gt_event.get('jersey_color') == pred_event.get('jersey_color'):
                stats['action_color_match_tp'] += 1
                action_color_matched_pairs.append((gt_event, pred_event))
                pred_used_color[i] = True
                break

    # --- Pass 3: Action + Color + Player Match ---
    pred_used_player = [False] * len(pred_events)
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_player[i] and \
               gt_event.get('action') == pred_event.get('action') and \
               gt_event.get('jersey_color') == pred_event.get('jersey_color') and \
               gt_event.get('player') == pred_event.get('player'):
                stats['action_color_player_match_tp'] += 1
                pred_used_player[i] = True
                break
    
    # === Class-Based Matching ===
    # --- Pass 4: Class Match ---
    pred_used_class = [False] * len(pred_events)
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_class[i] and get_action_class(gt_event.get('action')) == get_action_class(pred_event.get('action')):
                stats['class_match_tp'] += 1
                pred_used_class[i] = True
                break

    # --- Pass 5: Class + Color Match ---
    pred_used_class_color = [False] * len(pred_events)
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_class_color[i] and \
               get_action_class(gt_event.get('action')) == get_action_class(pred_event.get('action')) and \
               gt_event.get('jersey_color') == pred_event.get('jersey_color'):
                stats['class_color_match_tp'] += 1
                pred_used_class_color[i] = True
                break

    # --- Pass 6: Class + Color + Player Match ---
    pred_used_class_player = [False] * len(pred_events)
    for gt_event in gt_events:
        for i, pred_event in enumerate(pred_events):
            if not pred_used_class_player[i] and \
               get_action_class(gt_event.get('action')) == get_action_class(pred_event.get('action')) and \
               gt_event.get('jersey_color') == pred_event.get('jersey_color') and \
               gt_event.get('player') == pred_event.get('player'):
                stats['class_color_player_match_tp'] += 1
                pred_used_class_player[i] = True
                break

    # === Unordered Action/Class CM Data ===
    gt_actions = [e.get('action', 'N/A') for e in gt_events]
    pred_actions = [e.get('action', 'N/A') for e in pred_events]
    gt_action_classes = [get_action_class(a) for a in gt_actions]
    pred_action_classes = [get_action_class(a) for a in pred_actions]

    gt_action_counts = Counter(gt_actions)
    pred_action_counts = Counter(pred_actions)
    _populate_bag_cm_data(gt_action_counts, pred_action_counts, y_true_bags['action'], y_pred_bags['action'])
    
    gt_class_counts = Counter(gt_action_classes)
    pred_class_counts = Counter(pred_action_classes)
    _populate_bag_cm_data(gt_class_counts, pred_class_counts, y_true_bags['class'], y_pred_bags['class'])


    # === Conditional Attribute Accuracy (based on action match) ===
    stats['total_action_matches'] = len(action_matched_pairs)
    stats['total_action_color_matches'] = len(action_color_matched_pairs)

    for gt, pred in action_matched_pairs:
        # Only calculate result accuracy for shot actions
        if gt.get('action') in SHOT_ACTIONS:
            stats['total_shot_action_matches'] += 1
            if gt.get('result') == pred.get('result'):
                stats['correct_result_given_shot_action'] += 1

        # Only calculate assisted accuracy for 2pt/3pt shot actions
        if gt.get('action') in ASSISTED_SHOT_ACTIONS:
            stats['total_assisted_shot_matches'] += 1
            if gt.get('assisted') == pred.get('assisted'):
                stats['correct_assisted_given_assisted_shot'] += 1
            
            if gt.get('assisted') is True and pred.get('assisted') is True:
                stats['total_assisted_true_matches_for_shots'] += 1
                if str(gt.get('other_player')) == str(pred.get('other_player')):
                    stats['correct_other_player_given_assisted_is_true_for_shots'] += 1
            
        y_true_conditional['color_given_action'].append(str(gt.get('jersey_color')))
        y_pred_conditional['color_given_action'].append(str(pred.get('jersey_color')))

    for gt, pred in action_color_matched_pairs:
        y_true_conditional['player_given_action_color'].append(str(gt.get('player')))
        y_pred_conditional['player_given_action_color'].append(str(pred.get('player')))
    
    # Other stats
    stats['total_gt_actions'] = len(gt_events)
    stats['total_pred_actions'] = len(pred_events)

    return stats, y_true_bags, y_pred_bags, y_true_conditional, y_pred_conditional

def print_confusion_matrix(cm, labels, title):
    """Prints a formatted confusion matrix."""
    print(f"\n--- Confusion Matrix: {title} ---")
    if len(labels) == 0:
        print("No data available to generate a confusion matrix.")
        return
        
    # Get max label length for formatting
    max_label_len = max(len(str(label)) for label in labels) if labels else 0
    # Add padding for header
    max_label_len = max(max_label_len, 5) 
    
    print(" " * (max_label_len + 4) + "Predicted")
    # Header row
    header = f"{'True':<{max_label_len+2}} |"
    for label in labels:
        header += f" {str(label):>{max_label_len}}"
    print(header)
    print("-" * len(header))
    
    # Matrix rows
    for i, true_label in enumerate(labels):
        row_str = f" {str(true_label):<{max_label_len}} |"
        for j in range(len(labels)):
            row_str += f" {cm[i, j]:>{max_label_len}}"
        print(row_str)

def main():
    if len(sys.argv) < 2:
        print(f"? Error: Please provide the path to the predictions JSON file.")
        print(f"Usage: python {sys.argv[0]} <path_to_predictions.json>")
        return

    predictions_file = sys.argv[1]
    
    try:
        with open(predictions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"? Error loading or parsing {predictions_file}: {e}")
        return

    total_stats = defaultdict(int)
    y_true_all_bags = defaultdict(list)
    y_pred_all_bags = defaultdict(list)
    y_true_all_conditional = defaultdict(list)
    y_pred_all_conditional = defaultdict(list)
    
    correct_event_count = 0
    correct_event_count_tolerant = 0
    perfect_video_matches = 0
    perfect_ordered_actions = 0
    perfect_unordered_actions = 0
    total_videos = len(data)
    
    for item in data:
        gt_events = parse_events(item.get('ground_truth', ''))
        pred_events = parse_events(item.get('prediction', ''))
        
        # --- Video-level perfect match calculation (ordered) ---
        is_perfect_ordered_match = True
        if len(gt_events) == len(pred_events):
            if len(gt_events) != 0:
                for i in range(len(gt_events)):
                    if not are_events_a_perfect_match(gt_events[i], pred_events[i]):
                        is_perfect_ordered_match = False
                        break
        else:
            is_perfect_ordered_match = False
        if is_perfect_ordered_match:
            perfect_video_matches += 1
        
        # --- Perfect ordered actions ---
        is_perfect_ordered_actions = True
        if len(gt_events) == len(pred_events):
            if len(gt_events) != 0: 
                for i in range(len(gt_events)):
                    if not str(gt_events[i].get('action')) == str(pred_events[i].get('action')):
                        is_perfect_ordered_actions = False
                        break
        else:
            is_perfect_ordered_actions = False
        if is_perfect_ordered_actions:
            perfect_ordered_actions += 1
            
        # --- Perfect unordered actions ---
        gt_actions_list = [str(e.get('action')) for e in gt_events]
        pred_actions_list = [str(e.get('action')) for e in pred_events]
        if Counter(gt_actions_list) == Counter(pred_actions_list):
            perfect_unordered_actions += 1

        # --- Event count accuracy ---
        n_gt = len(gt_events)
        n_pred = len(pred_events)
        if n_gt == n_pred:
            correct_event_count += 1
        if abs(n_gt - n_pred) <= 1:
            correct_event_count_tolerant += 1
            
        gt_events = normalize_actions(gt_events, KNOWN_ACTIONS)
        pred_events = normalize_actions(pred_events, KNOWN_ACTIONS)
        
        item_stats, y_true_item_bags, y_pred_item_bags, y_true_item_cond, y_pred_item_cond = evaluate_events(gt_events, pred_events)
        
        for key, value in item_stats.items():
            total_stats[key] += value
        for field in y_true_item_bags.keys():
            y_true_all_bags[field].extend(y_true_item_bags[field])
            y_pred_all_bags[field].extend(y_pred_item_bags[field])
        for field in y_true_item_cond.keys():
            y_true_all_conditional[field].extend(y_true_item_cond[field])
            y_pred_all_conditional[field].extend(y_pred_item_cond[field])
        
    gt_count = total_stats['total_gt_actions']
    pred_count = total_stats['total_pred_actions']
    
    # --- Print Report Section ---
    print("\n" + "="*75)
    print(f"?? Basketball Event Evaluation Report")
    print(f"    Source File: {os.path.basename(predictions_file)}")
    print("="*75)

    print(f"\n{'Total Ground Truth Events:':<30} {gt_count}")
    print(f"{'Total Predicted Events:':<30} {pred_count}")
    print(f"{'Total Videos Processed:':<30} {total_videos}")

    # --- Section 1: Video-Level Accuracy ---
    print("\n## 1. Video-Level Accuracy")
    print("-" * 75)
    video_accuracy = perfect_video_matches / total_videos if total_videos > 0 else 0
    print(f"{'Perfect Video Accuracy (Ordered):':<35} {video_accuracy:.4f} ({perfect_video_matches}/{total_videos})")
    
    action_ordered_accuracy = perfect_ordered_actions / total_videos if total_videos > 0 else 0
    print(f"{'Perfect Ordered Actions Accuracy:':<35} {action_ordered_accuracy:.4f} ({perfect_ordered_actions}/{total_videos})")
    
    action_unordered_accuracy = perfect_unordered_actions / total_videos if total_videos > 0 else 0
    print(f"{'Perfect Unordered Actions Accuracy:':<35} {action_unordered_accuracy:.4f} ({perfect_unordered_actions}/{total_videos})")
    
    count_accuracy = correct_event_count / total_videos if total_videos > 0 else 0
    print(f"{'Exact Event Count Accuracy:':<35} {count_accuracy:.4f} ({correct_event_count}/{total_videos})")

    count_accuracy_tolerant = correct_event_count_tolerant / total_videos if total_videos > 0 else 0
    print(f"{'Tolerant Count Accuracy (+-1):':<35} {count_accuracy_tolerant:.4f} ({correct_event_count_tolerant}/{total_videos})")

    # --- Section 2: Event-Level Matching Performance ---
    print("\n## 2. Event-Level Matching Performance")
    print("-" * 75)
    
    print("--- Exact Action Match ---")
    tp = total_stats['action_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")

    print("\n--- Action + Color Match ---")
    tp = total_stats['action_color_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")
    
    print("\n--- Action + Color + Player Match ---")
    tp = total_stats['action_color_player_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")

    # --- Class-based matching ---
    print("\n--- Action Class Match ---")
    tp = total_stats['class_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")

    print("\n--- Class + Color Match ---")
    tp = total_stats['class_color_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")
    
    print("\n--- Class + Color + Player Match ---")
    tp = total_stats['class_color_player_match_tp']
    precision = tp / pred_count if pred_count > 0 else 0
    recall = tp / gt_count if gt_count > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"{'Precision:':<15} {precision:.4f} ({tp}/{pred_count})")
    print(f"{'Recall:':<15} {recall:.4f} ({tp}/{gt_count})")
    print(f"{'F1-Score:':<15} {f1:.4f}")

    # --- Section 3: Conditional Attribute Accuracy ---
    print("\n## 3. Conditional Attribute Accuracy")
    print("-" * 75)
    print(" (Accuracy of attributes, given a successful parent match)")
    print(f"{'ATTRIBUTE':<60} | {'ACCURACY'}")
    print("-" * 75)
    
    den = total_stats['total_shot_action_matches']
    num = total_stats['correct_result_given_shot_action']
    acc = num/den if den > 0 else 0
    print(f"{'Result (given correct SHOT Action)':<60} | {acc:.4f} ({num}/{den})")
    
    den = total_stats['total_assisted_shot_matches']
    num = total_stats['correct_assisted_given_assisted_shot']
    acc = num/den if den > 0 else 0
    print(f"{'Assisted status (given correct 2PT/3PT Shot)':<60} | {acc:.4f} ({num}/{den})")
    
    den_op = total_stats['total_assisted_true_matches_for_shots']
    num = total_stats['correct_other_player_given_assisted_is_true_for_shots']
    acc = num/den_op if den_op > 0 else 0
    print(f"{'  -> Other Player (given 2PT/3PT Shot & Assisted is TRUE)':<60} | {acc:.4f} ({num}/{den_op})")
    
    # === MODIFICATION START ===
    # The original calculation was based on a different set of pairs, leading to inconsistencies.
    # This new logic directly uses the results from the dedicated matching passes for consistency.
    den = total_stats['action_match_tp']
    num = total_stats['action_color_match_tp']
    acc = num / den if den > 0 else 0
    print(f"{'Jersey Color (given correct Action)':<60} | {acc:.4f} ({num}/{den})")

    den = total_stats['action_color_match_tp']
    num = total_stats['action_color_player_match_tp']
    acc = num / den if den > 0 else 0
    print(f"{'Player Number (given correct Action & Color)':<60} | {acc:.4f} ({num}/{den})")
    # === MODIFICATION END ===

    # --- Section 4: Detailed Confusion Matrices ---
    print("\n## 4. Detailed Confusion Matrices")
    print("-" * 75)

    # Unordered Action Class CM
    y_true_bag_class = y_true_all_bags.get('class', [])
    y_pred_bag_class = y_pred_all_bags.get('class', [])
    if y_true_bag_class:
        labels = sorted(list(set(y_true_bag_class + y_pred_bag_class)))
        for special_label in ['__SPURIOUS__', '__MISSING__']:
            if special_label in labels:
                labels.remove(special_label)
                labels.append(special_label)
        cm = confusion_matrix(y_true_bag_class, y_pred_bag_class, labels=labels)
        print_confusion_matrix(cm, labels, "Unordered Action Classes")

    # Unordered Action CM
    y_true_bag_action = y_true_all_bags.get('action', [])
    y_pred_bag_action = y_pred_all_bags.get('action', [])
    if y_true_bag_action:
        labels = sorted(list(set(y_true_bag_action + y_pred_bag_action)))
        # Ensure special labels are handled for consistent ordering
        for special_label in ['__SPURIOUS__', '__MISSING__']:
            if special_label in labels:
                labels.remove(special_label)
                labels.append(special_label)
        cm = confusion_matrix(y_true_bag_action, y_pred_bag_action, labels=labels)
        print_confusion_matrix(cm, labels, "Unordered Actions")

    # Conditional Color CM
    y_true = y_true_all_conditional.get('color_given_action', [])
    y_pred = y_pred_all_conditional.get('color_given_action', [])
    if y_true:
        labels = sorted(list(set(y_true + y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        print_confusion_matrix(cm, labels, "Jersey Color (given correct Action)")
        
    y_true = y_true_all_conditional.get('player_given_action_color', [])
    y_pred = y_pred_all_conditional.get('player_given_action_color', [])
    
    if y_true:
       try:
           all_labels = set(y_true + y_pred)
           # Attempt to sort as integers, pushing non-digits to the end
           labels = sorted(list(all_labels), key=lambda x: int(x) if x.isdigit() else float('inf'))
       except (ValueError, TypeError):
           # Fallback to standard string sort if conversion fails
           labels = sorted(list(all_labels))
       
       cm = confusion_matrix(y_true, y_pred, labels=labels)
       print_confusion_matrix(cm, labels, "Jersey Number (given correct Action and Color)")
       
       
    # --- Section 5: Sequence-Level Metrics (DTW-aligned) ---
    print("\n## 5. Sequence-Level Metrics (DTW-aligned)")
    print("-" * 75)

    try:
        from dtw import dtw
        import editdistance
    except ImportError:
        print("⚠️ Missing dependencies: please install via `pip install dtw-python editdistance`.")
        return

    # Collect all action sequences
    all_gt_action_seqs = []
    all_pred_action_seqs = []
    for item in data:
        gt_events = parse_events(item.get('ground_truth', ''))
        pred_events = parse_events(item.get('prediction', ''))
        gt_actions = [str(e.get('action')) for e in gt_events]
        pred_actions = [str(e.get('action')) for e in pred_events]
        if gt_actions or pred_actions:
            all_gt_action_seqs.append(gt_actions)
            all_pred_action_seqs.append(pred_actions)

    # Prepare DTW-based alignment across all sequences
    aligned_gt_all = []
    aligned_pred_all = []
    unique_labels = sorted(list(KNOWN_ACTIONS))

    for gt_seq, pred_seq in zip(all_gt_action_seqs, all_pred_action_seqs):
        if not gt_seq and not pred_seq:
            continue

        # Encode labels as integers
        label_to_int = {l: i for i, l in enumerate(unique_labels)}
        gt_enc = np.array([label_to_int.get(x, -1) for x in gt_seq]).reshape(-1, 1)
        pred_enc = np.array([label_to_int.get(x, -1) for x in pred_seq]).reshape(-1, 1)

        # DTW alignment (no custom distance, default Euclidean)
        alignment = dtw(gt_enc, pred_enc, keep_internals=False)
        path = (alignment.index1, alignment.index2)

        # Recover aligned GT / Pred sequences
        aligned_gt = [gt_seq[i] for i in path[0]]
        aligned_pred = [pred_seq[j] for j in path[1]]

        aligned_gt_all.extend(aligned_gt)
        aligned_pred_all.extend(aligned_pred)

    # Step-level confusion matrix (DTW-aligned)
    if aligned_gt_all:
        labels = sorted(list(set(aligned_gt_all + aligned_pred_all)))
        cm_dtw = confusion_matrix(aligned_gt_all, aligned_pred_all, labels=labels)
        print_confusion_matrix(cm_dtw, labels, "Step-Level Actions (DTW-Aligned)")

    # Sequence-level metrics
    exact_match_count = 0
    similarities = []
    for gt_seq, pred_seq in zip(all_gt_action_seqs, all_pred_action_seqs):
        if gt_seq == pred_seq:
            exact_match_count += 1
        lev = editdistance.eval(gt_seq, pred_seq)
        sim = 1 - lev / max(len(gt_seq), len(pred_seq)) if max(len(gt_seq), len(pred_seq)) > 0 else 1
        similarities.append(sim)

    seq_exact_acc = exact_match_count / len(all_gt_action_seqs) if all_gt_action_seqs else 0
    seq_avg_sim = np.mean(similarities) if similarities else 0

    print(f"\n{'Exact Sequence Match Accuracy:':<40} {seq_exact_acc:.4f} ({exact_match_count}/{len(all_gt_action_seqs)})")
    print(f"{'Average Sequence Similarity (1 - normalized edit dist):':<40} {seq_avg_sim:.4f}")

    print("-" * 75)
    print(f"ℹ️ On average, predicted action sequences are {seq_avg_sim*100:.1f}% similar to ground truth.")

if __name__ == "__main__":
    main()