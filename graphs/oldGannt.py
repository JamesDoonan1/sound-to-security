import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

# Define tasks with the same colors as in your new chart
tasks = [
    {"Sprint": "SCRUM-1", "Task": "Research and Setup", "Start": "01/10/2024", "End": "15/10/2024", "Color": "#9467bd"},  # Purple
    {"Sprint": "SCRUM-2", "Task": "Password System Design and Prototyping", "Start": "16/10/2024", "End": "31/10/2024", "Color": "#2ca02c"},  # Green
    {"Sprint": "SCRUM-3", "Task": "Prototype Development and AI Integration", "Start": "01/11/2024", "End": "15/11/2024", "Color": "#1f77b4"},  # Blue
    {"Sprint": "SCRUM-4", "Task": "Complete System Development & Testing", "Start": "16/11/2024", "End": "16/12/2024", "Color": "#ffbf00"},  # Yellow
    {"Sprint": "SCRUM-5", "Task": "Final Testing and Documentation", "Start": "16/12/2024", "End": "31/12/2024", "Color": "#17becf"},  # Teal
    {"Sprint": "SCRUM-6", "Task": "Final System Delivery", "Start": "06/01/2025", "End": "15/02/2025", "Color": "#8b0000"},  # Dark red
]

# Convert to DataFrame
df = pd.DataFrame(tasks)
df['Start'] = pd.to_datetime(df['Start'], format='%d/%m/%Y')
df['End'] = pd.to_datetime(df['End'], format='%d/%m/%Y')

# Reverse the order of tasks to match the old chart
df = df[::-1]

# Plot Gantt Chart
fig, ax = plt.subplots(figsize=(12, 5))

# Iterate over tasks and plot bars with the corresponding colors
for i, task in enumerate(df.itertuples()):
    ax.barh(task.Task, (task.End - task.Start).days, left=task.Start, color=task.Color, edgecolor="none")

# Formatting the timeline
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Display months as labels
plt.xticks(fontsize=10)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlabel("")
ax.set_ylabel("Sprints", fontsize=12)
ax.set_title("Sprint Timeline", fontsize=14, fontweight="bold")

# Add vertical gridlines and adjust layout
plt.grid(axis="x", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.show()
