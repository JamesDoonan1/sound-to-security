import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import datetime

# Define the tasks and their progress
tasks = [
    {"Sprint": "SCRUM-1", "Task": "Research and Setup", "Start": "15/11/2024", "End": "30/11/2024", "Progress": 100, "Color": "#9467bd"},  # Purple
    {"Sprint": "SCRUM-2", "Task": "Password System Design and Prototyping", "Start": "01/12/2024", "End": "10/01/2025", "Progress": 80, "Color": "#2ca02c"},  # Green
    {"Sprint": "SCRUM-3", "Task": "Prototype Development and AI Integration", "Start": "06/12/2024", "End": "28/02/2025", "Progress": 20, "Color": "#1f77b4"},  # Blue
    {"Sprint": "SCRUM-4", "Task": "Complete System Development & Testing", "Start": "28/02/2025", "End": "15/03/2025", "Progress": 15, "Color": "#ffbf00"},  # Yellow
    {"Sprint": "SCRUM-5", "Task": "Final Testing and Documentation", "Start": "15/12/2024", "End": "30/03/2025", "Progress": 30, "Color": "#17becf"},  # Teal
    {"Sprint": "SCRUM-6", "Task": "Final System Delivery", "Start": "20/03/2025", "End": "31/03/2025", "Progress": 0, "Color": "#8b0000"},  # Dark red
]

# Convert to DataFrame and ensure correct order
df = pd.DataFrame(tasks)
df['Start'] = pd.to_datetime(df['Start'], format='%d/%m/%Y')
df['End'] = pd.to_datetime(df['End'], format='%d/%m/%Y')

# Sort tasks by Sprint to ensure correct order
df = df.sort_values(by='Sprint', ascending=True)

# Fixed current date (19/12/2024)
current_date = pd.to_datetime("19/12/2024", format='%d/%m/%Y')

# Plot Gantt Chart
fig, ax = plt.subplots(figsize=(12, 6))

# Reverse the order of tasks for top-to-bottom plotting
df = df[::-1]  # Reverse the DataFrame to plot SCRUM-1 at the top

# Iterate over tasks and plot with colors
for i, task in enumerate(df.itertuples()):
    ax.barh(task.Task, (task.End - task.Start).days, left=task.Start, 
            color=task.Color, edgecolor='black')
    ax.text(
        task.End, i, f"{task.Progress}%", va='center', ha='left', 
        fontsize=8, color='black', weight='bold'
    )

# Add vertical line for current date (without text label)
ax.axvline(current_date, color='red', linestyle='--', linewidth=2, label='Current Date')

# Formatting the timeline
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.xticks(rotation=45, fontsize=10)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlabel("Timeline", fontsize=12)
ax.set_ylabel("Tasks", fontsize=12)
ax.set_title("Gantt Chart - Project Tasks and Progress", fontsize=14, fontweight="bold")

# Legend for current date
ax.legend()

# Adjust the chart
plt.tight_layout()
plt.grid(axis="x", linestyle="--", linewidth=0.5)
plt.show()
