import pandas as pd
import sys
from datetime import datetime

input_file = sys.argv[1]
output_file = sys.argv[2]

try:
    # Read CSV data
    df = pd.read_csv(input_file)

    # Print columns to debug
    print("Columns in the CSV file:", df.columns)

    # Strip spaces from column names
    df.columns = df.columns.str.strip()

    # Print columns after stripping spaces to debug
    print("Columns after stripping spaces:", df.columns)

    # Function to parse dates
    def parse_date(date_str, format):
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, format)
            except ValueError:
                return None
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
        if col in df.columns:
            df[col] = df[col].apply(lambda x: parse_date(x, fmt))

    # Convert empty strings in numeric columns to NaN
    numeric_cols = ['Estimated time', 'Total estimated time']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(pd.to_numeric, errors='coerce')
        else:
            df[col] = 0

    # Check if 'Assignee' column exists
    if 'Assignee' not in df.columns:
        print("Error: 'Assignee' column is missing from the CSV file.")
        sys.exit(1)

    # Initialize performance metrics
    performance_metrics = []

    # Calculate performance for each employee
    for assignee, tasks in df.groupby('Assignee'):
        total_tasks = len(tasks)
        on_time_tasks = tasks[tasks['Due date'] >= tasks['Closed']].shape[0]
        delayed_tasks = tasks[tasks['Due date'] < tasks['Closed']].shape[0]
        overdue_tasks = tasks[(tasks['Status'] != 'Closed') & (pd.to_datetime(tasks['Due date'], errors='coerce') < datetime.now())].shape[0]
        milestones_achieved = tasks[(tasks['Category'] == 'Milestone') & (tasks['Status'] == 'Closed')].shape[0]
        high_priority_tasks = tasks[(tasks['Priority'] == 'Priority1') & (tasks['Status'] == 'Closed')].shape[0]
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

    # Output results to CSV
    performance_df.to_csv(output_file, index=False)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
