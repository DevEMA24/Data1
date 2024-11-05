import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Set up Streamlit page config
st.set_page_config(page_title="Sales Viewer", layout="wide")

# Title of the application
st.title("Sales Viewer: Sales Per Interval vs. Goal")

# Function to load data
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.xlsx'):
        # Load Excel file
        excel_data = pd.ExcelFile(uploaded_file)
        # Assuming the relevant sheet is named 'Sales Per Interval(All Models)'
        df = excel_data.parse('Sales Per Interval(All Models)')
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        st.error("Only .xlsx and .csv files are supported.")
        return None
    return df

# Function to clean and structure data
def clean_data(df):
    df.columns = [
        'Index', 'Model_ID', 'Date_Time', 'Amount', 'Fee', 'Net', 'Description', 
        'Unknown1', 'Time', 'Type', 'Date', 'Interval', 'Welcome_Message', 
        'Unknown2', 'EMP_ID', 'EMP_ID_2'
    ]
    df = df[['Model_ID', 'Date', 'Amount', 'EMP_ID']]
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Amount', 'Date', 'EMP_ID'], inplace=True)
    return df

# Upload file
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=['xlsx', 'csv'])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.success("File uploaded and data loaded successfully.")
        
        # Clean and structure data
        df = clean_data(df)
        
        # Agent selection
        emp_ids = df['EMP_ID'].unique()
        emp_id = st.selectbox("Select Agent (EMP_ID)", emp_ids)
        
        # Date selection
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # Daily goal input
        goal = st.number_input("Enter the Daily Sales Goal", min_value=0.0, value=50.0)
        
        # Filter data by agent and date range
        mask = (df['EMP_ID'] == emp_id) & (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
        agent_data = df[mask]

        # Group by date and sum up sales
        daily_sales = agent_data.groupby('Date')['Amount'].sum().reindex(
            pd.date_range(start_date, end_date), fill_value=0)

        # Display data and chart
        st.write("### Daily Sales Data", daily_sales)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(daily_sales.index, daily_sales.values, label="Daily Sales", color="skyblue")
        ax.plot(daily_sales.index, [goal] * len(daily_sales), label="Daily Goal", color="orange", linewidth=2)
        
        # Format chart
        ax.set_title(f"Sales Per Interval vs. Goal for Agent {emp_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales Amount")
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        ax.legend()
        st.pyplot(fig)

