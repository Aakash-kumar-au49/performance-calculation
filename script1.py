import pandas as pd
from datetime import datetime
import numpy as np  # Import numpy for NaN handling

# Sample data for testing
data = [
    {
        'id': 44348,
        'Project': 'Do-or-Die',
        'Tracker': 'Emp-tracker-2',
        'Parent task': '',
        'Parent task subject': '',
        'Status': 'Closed',
        'Priority': 'Priority1',
        'Subject': 'Approach paper',
        'Author': 'Akash Kumar CF2024031102',
        'Assignee': 'Akash Kumar CF2024031102',
        'Updated': '10/07/2024 12:08 AM',
        'Category': '',
        'Target version': '',
        'Start date': '06/07/2024',
        'Due date': '09/07/2024',
        'Estimated time': '',
        'Total estimated time': '',
        '% Done': 0,
        'Created': '06/07/2024 11:45 PM',
        'Closed': '10/07/2024 12:08 AM',
        'Last updated by': 'Akash Kumar CF2024031102',
        'Related issues': '',
        'Files': '',
        'Work_Location': 'Working FROM Office',
        'Leave': '',
        'week_off': '',
        'Types_of_work': 'Task',
        'Private': 'No',
        'Description': 'Working on approach paper',
        'Last notes': 'Write a fetch api'
    }
]

# Create DataFrame from sample data
df = pd.DataFrame(data)

# Function to parse dates
def parse_date(date_str, format):
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        return None

# Define date formats
date_formats = {
    'Start date': '%d/%m/%Y',
    'Due date': '%d/%m/%Y',
    'Updated': '%d/%m/%Y %I:%M %p',
    'Created': '%d/%m/%Y %I:%M %p',
    'Closed': '%d/%m/%Y %I:%M %p'
}

# Parse dates with the defined formats
for col, fmt in date_formats.items():
    df[col] = df[col].apply(lambda x: parse_date(x, fmt))

# Convert empty strings in numeric columns to NaN
numeric_cols = ['Estimated time', 'Total estimated time']
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Initialize performance metrics
performance_metrics = []

# Calculate performance for each employee
for assignee, tasks in df.groupby('Assignee'):
    total_tasks = len(tasks)
    on_time_tasks = tasks[tasks['Due date'] >= tasks['Closed']].shape[0]
    delayed_tasks = tasks[tasks['Due date'] < tasks['Closed']].shape[0]
    overdue_tasks = tasks[tasks['Status'] != 'Closed'][tasks['Due date'] < datetime.now()].shape[0]
    milestones_achieved = tasks[tasks['Category'] == 'Milestone'][tasks['Status'] == 'Closed'].shape[0]
    high_priority_tasks = tasks[tasks['Priority'] == 'Priority1'][tasks['Status'] == 'Closed'].shape[0]
    estimated_vs_actual = (tasks['Estimated time'].sub(tasks['Total estimated time'], fill_value=0)).mean()
    leave_days = tasks['Leave'].sum() if 'Leave' in tasks.columns else 0
    
    performance_metrics.append({
        'Assignee': assignee,
        'Total Tasks': total_tasks,
        'On-Time Tasks': on_time_tasks,
        'Delayed Tasks': delayed_tasks,
        'Overdue Tasks': overdue_tasks,
        'Milestones Achieved': milestones_achieved,
        'High-Priority Tasks': high_priority_tasks,
        'Estimated vs Actual Time': estimated_vs_actual,
        'Leave Days': leave_days
    })

# Convert to DataFrame
performance_df = pd.DataFrame(performance_metrics)

# Apply rating criteria
def classify_performance(row):
    if row['On-Time Tasks'] / row['Total Tasks'] > 0.9 and row['Milestones Achieved'] / row['Total Tasks'] > 0.9:
        return 'Excellent'
    elif row['On-Time Tasks'] / row['Total Tasks'] > 0.75 and row['Milestones Achieved'] / row['Total Tasks'] > 0.75:
        return 'Good'
    elif row['On-Time Tasks'] / row['Total Tasks'] > 0.5 and row['Milestones Achieved'] / row['Total Tasks'] > 0.5:
        return 'Average'
    else:
        return 'Poor'

performance_df['Rating'] = performance_df.apply(classify_performance, axis=1)

# Output results
performance_df.to_csv('employee_performance_ratings.csv', index=False)

