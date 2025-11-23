import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ---------------------------------------------------------
# DATA PREPARATION
# ---------------------------------------------------------

# Data 1: Labels per Video
# Sorted by Label Index (1, 2, 3...) as requested
data1 = {
    'Labels': ['1', '2', '3', '4', '5'],
    'Count': [8499, 4319, 1218, 468, 172],
    'Percentage': [57.9, 29.4, 8.3, 3.2, 1.2]
}
df1 = pd.DataFrame(data1)

# Data 2: Action Types
# Sorted by Count Increasing (Smallest to Largest) as requested
data2 = {
    'Action Type': [
        'Violation', 'Block', 'Steal', '3PT Shot AST', 'Turnover', 
        '2PT Shot AST', 'Foul', 'Free Throw', '3PT Shot', '2PT Shot', 'Rebound'
    ],
    'Count': [28, 512, 953, 1394, 1616, 1806, 2305, 2589, 3115, 4143, 5062],
    'Percentage': [0.1, 2.2, 4.1, 5.9, 6.9, 7.7, 9.8, 11.0, 13.2, 17.6, 21.5]
}
df2 = pd.DataFrame(data2)

# ---------------------------------------------------------
# PLOTTING
# ---------------------------------------------------------

# Set global style
sns.set_theme(style="whitegrid")
# Create a figure with 2 subplots (1 row, 2 columns)
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# --- Plot 1: Labels per Video ---
# We want Label 1 at the Bottom and Label 5 at the Top.
# Seaborn draws Top-to-Bottom. So we provide order [5, 4, 3, 2, 1].
order1 = ['5', '4', '3', '2', '1']

# Palette: "Blues" goes from Light to Dark.
# Since 5 is Small and 1 is Large, "Blues" works perfectly to make the largest bar darkest.
palette1 = sns.color_palette("Blues", n_colors=len(df1))

sns.barplot(
    ax=axes[0],
    x="Count",
    y="Labels",
    data=df1,
    order=order1,
    palette=palette1
)

# Annotations for Plot 1
for i, p in enumerate(axes[0].patches):
    # Retrieve data based on the bar's position
    label_val = order1[i]
    row = df1[df1['Labels'] == label_val].iloc[0]
    text = f"{row['Count']} ({row['Percentage']}%)"
    
    axes[0].text(
        p.get_width() + 150, 
        p.get_y() + p.get_height()/2, 
        text, 
        va='center', ha='left', fontsize=12, fontweight='medium'
    )

axes[0].set_title("Distribution of Labels per Video", fontsize=16, fontweight='bold', pad=20)
axes[0].set_xlabel("Count", fontsize=13)
axes[0].set_ylabel("Number of labels per video", fontsize=13)
sns.despine(ax=axes[0], left=True, bottom=True)


# --- Plot 2: Action Types ---
# We want Smallest (Violation) at Bottom, Largest (Rebound) at Top.
# Seaborn draws Top-to-Bottom. So we provide order [Rebound, ..., Violation].
order2 = df2.sort_values('Count', ascending=False)['Action Type'].tolist()

# Palette: "GnBu_r" goes from Dark to Light.
# Since Rebound is Top (First drawn) and Large, we want it Dark.
palette2 = sns.color_palette("GnBu_r", n_colors=len(df2))

sns.barplot(
    ax=axes[1],
    x="Count",
    y="Action Type",
    data=df2,
    order=order2,
    palette=palette2
)

# Annotations for Plot 2
for i, p in enumerate(axes[1].patches):
    label_val = order2[i]
    row = df2[df2['Action Type'] == label_val].iloc[0]
    text = f"{row['Count']} ({row['Percentage']}%)"
    
    axes[1].text(
        p.get_width() + 150, 
        p.get_y() + p.get_height()/2, 
        text, 
        va='center', ha='left', fontsize=12, fontweight='medium'
    )

axes[1].set_title("Distribution of Action Types", fontsize=16, fontweight='bold', pad=20)
axes[1].set_xlabel("Count", fontsize=13)
axes[1].set_ylabel("Action Type", fontsize=13)
sns.despine(ax=axes[1], left=True, bottom=True)

# ---------------------------------------------------------
# SAVE AND SHOW
# ---------------------------------------------------------
plt.tight_layout()
plt.savefig('beautiful_graphs_combined.png', dpi=300)
plt.show()