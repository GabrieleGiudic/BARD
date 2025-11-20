import pandas as pd
import json

# Path to your CSV
csv_path = "../data/players.csv"

# Load CSV with all columns as strings (prevents 00 -> 0.0)
df = pd.read_csv(csv_path, sep=";", dtype=str, keep_default_na=False, na_values=[""])

# Strip whitespace from all string values
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Function to filter out empty or "nan" values (keep true strings)
def valid_numbers(series):
    return series[series.notna() & (series != "") & (series.str.lower() != "nan")]

# Clean up columns
df["Team"] = valid_numbers(df["Team"])
df["Number"] = valid_numbers(df["Number"])
df["Number2"] = valid_numbers(df["Number2"])

# Build dictionary
team_numbers = {}

for _, row in df.iterrows():
    team = row["Team"]
    num1 = row["Number"]
    num2 = row["Number2"]

    if team not in team_numbers:
        team_numbers[team] = set()

    if isinstance(num1, str) and num1.strip():
        team_numbers[team].add(num1.strip())

    if isinstance(num2, str) and num2.strip():
        team_numbers[team].add(num2.strip())

# Convert sets to **lexicographically sorted lists** (pure string sort)
team_numbers = {
    team: sorted(list(nums), key=lambda s: (len(s), s))  # keeps "00" before "0" properly
    for team, nums in team_numbers.items()
}

# Save to JSON
json_path = "../team_numbers/team_numbers.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(team_numbers, f, indent=4, ensure_ascii=False)

print(f"✅ Saved team-number mapping (including Number2) to {json_path}")
