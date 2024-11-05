import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Set up Streamlit page config
st.set_page_config(page_title="Sales Viewer", layout="wide")

# Title of the application
st.title("Sales Viewer: CGR Shift Sales vs. Goal")

# Function to load data from the specific sheet "Sales Viewer (Manager)"
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.xlsx'):
        # Load the specific sheet
        df = pd.read_excel(uploaded_file, sheet_name='Sales Viewer (Manager)')
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        st.error("Only .xlsx and .csv files are supported.")
        return None
    return df

# Function to parse and transform data
def parse_data(df):
    # Step 1: Identify the initial columns with agent information
    agent_info_cols = ['EMP_ID', 'NAME', 'STATUS', 'CGR/CRPH GOAL']
    agent_info_df = df[agent_info_cols]

    # Step 2: Identify date blocks, assuming each date block has 3 columns (e.g., Date, CGR, CRPH Goal)
    date_blocks = df.columns[4:]  # Skipping first 4 columns for agent info
    unique_dates = list(set([col.split()[0] for col in date_blocks]))

    # Step 3: Create a list to store parsed rows
    parsed_rows = []

    # Step 4: Iterate over each row to extract date blocks for each agent
    for _, row in df.iterrows():
        emp_id = row['EMP_ID']
        name = row['NAME']
        status = row['STATUS']
        cgr_goal = row['CGR/CRPH GOAL']
        
        for date in unique_dates:
            # Extract sales and goal data for each date block
            try:
                cgr_sales = row[f'{date} CGR']
                crph_goal = row[f'{date} CRPH Goal']
                parsed_rows.append({'EMP_ID': emp_id, 'Name': name, 'Date': date, 'CGR': cgr_sales, 'CRPH Goal': crph_goal})
            except KeyError:
                continue  # Skip if any date-specific columns are missing

    # Convert parsed data to DataFrame
    parsed_df = pd.DataFrame(parsed_rows)
    # Ensure Date column is in datetime format
    parsed_df['Date'] = pd.to_datetime(parsed_df['Date'], errors='coerce')
    return parsed_df

# Upload file
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=['xlsx', 'csv'])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.success("File uploaded and data loaded successfully.")
        
        # Parse and structure data
        parsed_df = parse_data(df)
        
        # Agent selection
        emp_ids = parsed_df['EMP_ID'].unique()
        emp_id = st.selectbox("Select Agent (EMP_ID)", emp_ids)
        
        # Date selection
        min_date = parsed_df['Date'].min()
        max_date = parsed_df['Date'].max()
        start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)
        
        # Filter data by agent and date range
        mask = (parsed_df['EMP_ID'] == emp_id) & (parsed_df['Date'] >= pd.to_datetime(start_date)) & (parsed_df['Date'] <= pd.to_datetime(end_date))
        agent_data = parsed_df[mask]

        # Group by date and sum up CGR and CRPH Goal for each day
        daily_sales = agent_data.groupby('Date')[['CGR', 'CRPH Goal']].sum().reindex(
            pd.date_range(start_date, end_date), fill_value=0)

        # Display data and chart
        st.write("### Daily CGR Sales Data vs. Goal", daily_sales)

        # Plotting with improved layout
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(daily_sales.index, daily_sales['CGR'], label="CGR Shift Sales", color="skyblue")
        ax.plot(daily_sales.index, daily_sales['CRPH Goal'], label="CGR Shift Sales Goal", color="orange", linewidth=2)
        
        # Format chart for better readability
        ax.set_title(f"Daily CGR Shift Sales vs. Goal for Agent {emp_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales Amount")
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        ax.legend()
        
        # Display chart in Streamlit
        st.pyplot(fig)
