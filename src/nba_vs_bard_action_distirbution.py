import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import chi2_contingency

# Set Seaborn style for beautiful graphs
sns.set_theme(style="whitegrid", context="talk")

# --- Part 1: Load Data (Manual Entry from provided table) ---

# Data dictionary based on your table



data_source = {
    "Category": [
        "Rebound", "2PT shots", "3PT shots", "FT", "Foul", 
        "AST", "TO", "Steal", "Blocks", "Violations"
    ],
    "Observed_Count": [
        108516, 127073, 92454, 53312, 45746, 
        65312, 35174, 20184, 11995, 577
    ],
    "BARD_Count": [
    106051,  # Rebound
    124795,  # 2PT shots
    94213,   # 3PT shots
    54259,   # FT
    48339,   # Foul
    67083,   # AST
    34035,   # TO
    20224,   # Steal
    10852,   # Blocks
    493      # Violations
]
}

BARD_num = 14676

# Create DataFrame
df = pd.DataFrame(data_source)

# Calculate Total Observed
total_observed = df["Observed_Count"].sum()

# Calculate Observed Percentage (for plotting comparison)
df["Observed_Pct"] = (df["Observed_Count"] / total_observed) * 100


total_BARD = df["BARD_Count"].sum()

# Calculate Observed Percentage (for plotting comparison)
df["BARD_Pct"] = (df["BARD_Count"] / total_BARD) * 100

print(f"Total Observed Actions: {total_observed}")
print(df)

# --- Part 2: Process Data for Plot 1 (Relative Comparison) ---

# We need to 'melt' the dataframe to make it suitable for a side-by-side bar chart
# We want columns: Category, Percentage, Source (Observed vs BARD)

data_rel = []

for index, row in df.iterrows():
    # Observed Data Entry
    data_rel.append({
        "Category": row["Category"],
        "Percentage": row["Observed_Pct"],
        "Source": "Observed 2024-25"
    })
    # BARD Data Entry
    data_rel.append({
        "Category": row["Category"],
        "Percentage": row["BARD_Pct"],
        "Source": "BARD"
    })

df_rel = pd.DataFrame(data_rel)

# --- Part 3: Generate Graphs ---

# GRAPH 1: Relative Distribution Comparison (Observed vs BARD)
plt.figure(figsize=(14, 7))
ax1 = sns.barplot(
    data=df_rel,
    x="Category",
    y="Percentage",
    hue="Source",
    palette={"Observed 2024-25": "#3498db", "BARD": "#e74c3c"},
    edgecolor="black",
    linewidth=1,
    alpha=0.85
)

plt.title("Action Distribution: Observed 2024-25 vs BARD", fontsize=18, weight='bold')
plt.xlabel("Action Type", fontsize=14)
plt.ylabel("Percentage (%)", fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.legend(title="Dataset")
sns.despine()
plt.tight_layout()
plt.show() 

# Save Graph 1
# output_filename_rel = '../figure/action_rel_distribution.png'
# plt.savefig(output_filename_rel)

# GRAPH 2: Absolute Distribution (Observed Counts Only)
plt.figure(figsize=(14, 7))

# Create a color palette based on counts
ax2 = sns.barplot(
    data=df,
    x="Category",
    y="Observed_Count",
    palette="viridis",
    edgecolor="black",
    linewidth=1,
    alpha=0.9
)

# Annotate bars with exact counts
for p in ax2.patches:
    ax2.annotate(f'{int(p.get_height())}', 
                 (p.get_x() + p.get_width() / 2., p.get_height()), 
                 ha = 'center', va = 'center', 
                 xytext = (0, 9), 
                 textcoords = 'offset points',
                 fontsize=12, fontweight='bold')

plt.title("Observed Absolute Distribution (2024-25)", fontsize=18, weight='bold')
plt.xlabel("Action Type", fontsize=14)
plt.ylabel("Count", fontsize=14)
plt.xticks(rotation=45, fontsize=12)
sns.despine()
plt.tight_layout()
plt.show() 


obs_counts = df["Observed_Pct"].values/100*BARD_num


# 2. Calculate Expected Counts based on BARD Percentages
# Expected = Total_Observed * (BARD_Percent / 100)
exp_counts = df["BARD_Pct"].values/100*BARD_num

# 3. Build Contingency Table for Chi-Square Test of Independence
# (comparing the distribution shape of Observed vs BARD)
contingency_table = np.vstack([obs_counts, exp_counts])

# 4. Run Chi-square test
chi2_stat, p_value, dof, expected_freq = chi2_contingency(contingency_table)

print("\n=== Chi-square test of independence ===")
print(f"Chi-square statistic: {chi2_stat:.4f}")
print(f"Degrees of freedom: {dof}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Result: Reject null hypothesis (The distributions are significantly different).")
else:
    print("Result: Fail to reject null hypothesis (The distributions are statistically similar).")