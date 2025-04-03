import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os
import altair as alt
from PIL import Image
import io
import base64

# Configuration for the multi-page app
st.set_page_config(
    page_title="GHSS Cherpu Admission Portal",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
SCHOOL_NAME = "GHSS CHERPU"
ADMISSION_YEAR = 2025
STREAMS = ["BIO", "CS", "HUM", "COM"]
SECOND_LANGUAGES = ["MAL", "HIN", "SKT"]
CASTES = ["GEN", "ETB", "MUSLIM", "SC", "LSA", "OBH", "DV", "VK", "KN", "KU", "ST", "OBCHRISTIAN"]
STATUS_OPTIONS = ["PERMANENT", "TEMPORARY"]

# Load or create the dataframe
@st.cache_data
def load_data():
    if os.path.exists('admission_data.csv'):
        return pd.read_csv('admission_data.csv')
    else:
        columns = ['Name', 'Rank', 'Stream', 'Second_Language', 'Caste', 
                 'Admission_Status', 'Date_of_Admission']
        return pd.DataFrame(columns=columns)

# Save data to CSV
def save_data(df):
    df.to_csv('admission_data.csv', index=False)
    
# Save TC records
def save_tc_data(student_info):
    tc_file = 'tc_records.csv'
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Add TC date
    student_info['TC_Date'] = today
    
    # Check if file exists
    if os.path.exists(tc_file):
        tc_df = pd.read_csv(tc_file)
        tc_df = pd.concat([tc_df, pd.DataFrame([student_info])])
    else:
        tc_df = pd.DataFrame([student_info])
    
    # Save TC records
    tc_df.to_csv(tc_file, index=False)

# Function to clear form fields
def clear_form_fields():
    for key in st.session_state.keys():
        if key.startswith('form_'):
            st.session_state[key] = ""
    st.session_state.form_rank = 1
    st.session_state.form_stream = STREAMS[0]
    st.session_state.form_language = SECOND_LANGUAGES[0]
    st.session_state.form_caste = CASTES[0]
    st.session_state.form_status = STATUS_OPTIONS[0]

# Custom header with school logo
def display_header():
    col1, col2 = st.columns([1, 3])
    
    # School Logo (using a placeholder icon)
    with col1:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <h1 style="font-size: 60px; margin: 0;">🏫</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # School name and title
    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom: 0px;">{SCHOOL_NAME}</h1>
        <h3 style="margin-top: 0px; color: #636363;">Admission Portal {ADMISSION_YEAR}</h3>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

# Initialize session states
if 'students_df' not in st.session_state:
    st.session_state.students_df = load_data()

# Initialize form fields
for field in ['name', 'rank', 'stream', 'language', 'caste', 'status']:
    if f'form_{field}' not in st.session_state:
        if field == 'rank':
            st.session_state[f'form_{field}'] = 1
        elif field == 'stream':
            st.session_state[f'form_{field}'] = STREAMS[0]
        elif field == 'language':
            st.session_state[f'form_{field}'] = SECOND_LANGUAGES[0]
        elif field == 'caste':
            st.session_state[f'form_{field}'] = CASTES[0]
        elif field == 'status':
            st.session_state[f'form_{field}'] = STATUS_OPTIONS[0]
        else:
            st.session_state[f'form_{field}'] = ""

# Display the header
display_header()

# Create sidebar navigation
pages = {
    "New Admission": "📝",
    "Stream-wise View": "👥",
    "TC Issuance": "🔖",
    "Data Analysis": "📊"
}

# Add a sidebar with navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()), format_func=lambda x: f"{pages[x]} {x}")

# Initialize page-specific variables
if selection == "New Admission":
    # Clear button in sidebar
    if st.sidebar.button("🔄 Clear Form"):
        clear_form_fields()
        st.rerun()
        
    st.header("New Student Admission")
    
    # Create a form for student admission
    with st.form("admission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("Student Name", value=st.session_state.form_name).upper()
            rank = st.number_input("Rank", min_value=1, step=1, value=st.session_state.form_rank)
            stream = st.selectbox("Stream", options=STREAMS, index=STREAMS.index(st.session_state.form_stream) if st.session_state.form_stream in STREAMS else 0)
        
        with col2:
            second_language = st.selectbox("Second Language", options=SECOND_LANGUAGES, 
                                  index=SECOND_LANGUAGES.index(st.session_state.form_language) if st.session_state.form_language in SECOND_LANGUAGES else 0)
            caste = st.selectbox("Caste", options=CASTES, index=CASTES.index(st.session_state.form_caste) if st.session_state.form_caste in CASTES else 0)
            admission_status = st.selectbox("Admission Status", options=STATUS_OPTIONS, 
                               index=STATUS_OPTIONS.index(st.session_state.form_status) if st.session_state.form_status in STATUS_OPTIONS else 0)
        
        # Date is automatically set to today
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        
        col1, col2, col3 = st.columns(3)
        # Submit button
        with col1:
            submitted = st.form_submit_button("Submit")
        with col2:
            clear_form = st.form_submit_button("Clear Form")
            
        if clear_form:
            clear_form_fields()
            st.rerun()
            
        if submitted:
            # Update session state
            st.session_state.form_name = student_name
            st.session_state.form_rank = rank
            st.session_state.form_stream = stream
            st.session_state.form_language = second_language
            st.session_state.form_caste = caste
            st.session_state.form_status = admission_status
            
            # Check if student is already admitted
            if student_name and any(st.session_state.students_df['Name'] == student_name):
                st.error(f"A student with name {student_name} is already admitted!")
            elif not student_name:
                st.error("Please enter student name!")
            else:
                # Add new student to DataFrame
                new_student = {
                    'Name': student_name,
                    'Rank': rank,
                    'Stream': stream,
                    'Second_Language': second_language,
                    'Caste': caste,
                    'Admission_Status': admission_status,
                    'Date_of_Admission': today_date
                }
                
                # Append data to the DataFrame
                new_df = pd.DataFrame([new_student])
                st.session_state.students_df = pd.concat([st.session_state.students_df, new_df])
                
                # Save data
                save_data(st.session_state.students_df)
                
                st.success(f"Student {student_name} admitted successfully to {stream} stream!")
                
                # Clear form fields after successful submission
                clear_form_fields()
                st.rerun()
    
    # Display current admission data
    if not st.session_state.students_df.empty:
        st.subheader("Recent Admissions")
        # Show only the last 5 entries for quick view
        recent_df = st.session_state.students_df.sort_values('Date_of_Admission', ascending=False).head(5)
        st.dataframe(recent_df, use_container_width=True)
        
        # Show counts by stream
        st.subheader("Current Admission Status")
        stream_counts = st.session_state.students_df['Stream'].value_counts().reset_index()
        stream_counts.columns = ['Stream', 'Count']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(stream_counts, use_container_width=True)
        
        with col2:
            chart = alt.Chart(stream_counts).mark_bar().encode(
                x=alt.X('Stream:N', title='Stream'),
                y=alt.Y('Count:Q', title='Number of Students'),
                color=alt.Color('Stream:N', legend=None)
            ).properties(
                title='Students by Stream'
            )
            st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No students admitted yet.")

elif selection == "Stream-wise View":
    st.header("Stream-wise Student Lists")
    
    # Create tabs for different streams
    tabs = st.tabs(STREAMS)
    
    for i, stream in enumerate(STREAMS):
        with tabs[i]:
            st.subheader(f"{stream} Stream Students")
            
            # Filter data for this stream
            stream_df = st.session_state.students_df[st.session_state.students_df['Stream'] == stream]
            
            if not stream_df.empty:
                # Sort by rank
                stream_df = stream_df.sort_values('Rank')
                
                # Display the dataframe
                st.dataframe(stream_df, use_container_width=True)
                
                # Download button for this stream's data
                csv = stream_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{stream}_stream_students.csv">Download {stream} Stream Data</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Students", len(stream_df))
                
                with col2:
                    permanent = len(stream_df[stream_df['Admission_Status'] == 'PERMANENT'])
                    st.metric("Permanent", permanent)
                
                with col3:
                    temporary = len(stream_df[stream_df['Admission_Status'] == 'TEMPORARY'])
                    st.metric("Temporary", temporary)
                
                # Show second language distribution
                st.subheader("Second Language Distribution")
                language_counts = stream_df['Second_Language'].value_counts().reset_index()
                language_counts.columns = ['Language', 'Count']
                
                chart = alt.Chart(language_counts).mark_bar().encode(
                    x=alt.X('Language:N', title='Second Language'),
                    y=alt.Y('Count:Q', title='Number of Students'),
                    color=alt.Color('Language:N', legend=None)
                ).properties(
                    title=f'Second Language Distribution - {stream} Stream',
                    height=300
                )
                st.altair_chart(chart, use_container_width=True)
                
            else:
                st.info(f"No students admitted to {stream} stream yet.")

elif selection == "TC Issuance":
    st.header("Issue Transfer Certificate (TC)")
    
    if not st.session_state.students_df.empty:
        # Show current students for reference
        with st.expander("View Current Students"):
            st.dataframe(st.session_state.students_df, use_container_width=True)
        
        # TC form
        with st.form("tc_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                tc_name = st.text_input("Student Name for TC").upper()
                tc_stream = st.selectbox("Stream", options=STREAMS)
            
            with col2:
                tc_rank = st.number_input("Rank", min_value=1, step=1)
                tc_reason = st.text_input("Reason for TC (Optional)")
            
            tc_submitted = st.form_submit_button("Issue TC")
            
            if tc_submitted:
                # Find the student
                mask = (
                    (st.session_state.students_df['Name'] == tc_name) & 
                    (st.session_state.students_df['Stream'] == tc_stream) & 
                    (st.session_state.students_df['Rank'] == tc_rank)
                )
                
                if mask.any():
                    # Get student info before removing
                    student_info = st.session_state.students_df[mask].iloc[0].to_dict()
                    if tc_reason:
                        student_info['TC_Reason'] = tc_reason
                    
                    # Drop the student from DataFrame
                    st.session_state.students_df = st.session_state.students_df[~mask]
                    save_data(st.session_state.students_df)
                    
                    # Save TC record
                    save_tc_data(student_info)
                    
                    st.success(f"TC issued for {tc_name} from {tc_stream} stream.")
                else:
                    st.error("Student not found! Please check name, stream and rank.")
        
        # Display TC records if available
        if os.path.exists('tc_records.csv'):
            st.subheader("TC Records")
            tc_df = pd.read_csv('tc_records.csv')
            st.dataframe(tc_df.sort_values('TC_Date', ascending=False), use_container_width=True)
            
            # Download TC records
            csv = tc_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="tc_records.csv">Download TC Records</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No students admitted yet.")

elif selection == "Data Analysis":
    st.header("Admission Data Analysis")
    
    # Add option to export data
    st.sidebar.subheader("Export Options")
    
    if st.sidebar.button("Export All Admission Data"):
        csv = st.session_state.students_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="admission_data.csv">Download Complete Admission Data</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
    
    if os.path.exists('tc_records.csv'):
        if st.sidebar.button("Export TC Records"):
            tc_df = pd.read_csv('tc_records.csv')
            csv = tc_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="tc_records.csv">Download TC Records</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
    
    if not st.session_state.students_df.empty:
        # Create analysis options
        analysis_tabs = st.tabs([
            "Stream Distribution", 
            "Admission Status", 
            "Caste Distribution", 
            "Second Language", 
            "Date-wise Analysis"
        ])
        
        # Tab 1: Stream Distribution
        with analysis_tabs[0]:
            st.subheader("Students by Stream")
            
            # Create DataFrame for plot
            stream_counts = st.session_state.students_df['Stream'].value_counts().reset_index()
            stream_counts.columns = ['Stream', 'Count']
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(stream_counts, use_container_width=True)
            
            with col2:
                chart = alt.Chart(stream_counts).mark_bar().encode(
                    x=alt.X('Stream:N', title='Stream'),
                    y=alt.Y('Count:Q', title='Number of Students'),
                    color=alt.Color('Stream:N', legend=None)
                ).properties(
                    title='Students by Stream'
                )
                st.altair_chart(chart, use_container_width=True)
        
        # Tab 2: Admission Status
        with analysis_tabs[1]:
            st.subheader("Admission Status Analysis")
            
            # Create pivot table
            status_pivot = pd.pivot_table(
                st.session_state.students_df, 
                values='Name',
                index='Stream',
                columns='Admission_Status',
                aggfunc='count',
                fill_value=0
            ).reset_index()
            
            # Convert to a format suitable for Altair
            status_data = pd.melt(
                status_pivot, 
                id_vars=['Stream'], 
                var_name='Status', 
                value_name='Count'
            )
            
            # Display the data
            st.dataframe(status_pivot, use_container_width=True)
            
            # Create chart
            chart = alt.Chart(status_data).mark_bar().encode(
                x=alt.X('Stream:N', title='Stream'),
                y=alt.Y('Count:Q', title='Number of Students'),
                color=alt.Color('Status:N'),
                xOffset='Status:N'  # Group bars by status
            ).properties(
                title='Admission Status by Stream'
            )
            st.altair_chart(chart, use_container_width=True)
        
        # Tab 3: Caste Distribution
        with analysis_tabs[2]:
            st.subheader("Caste-wise Distribution")
            
            # Create DataFrame for plot
            caste_counts = st.session_state.students_df['Caste'].value_counts().reset_index()
            caste_counts.columns = ['Caste', 'Count']
            
            # Display the data
            st.dataframe(caste_counts, use_container_width=True)
            
            # Create chart
            chart = alt.Chart(caste_counts).mark_bar().encode(
                x=alt.X('Caste:N', sort='-y', title='Caste'),
                y=alt.Y('Count:Q', title='Number of Students'),
                color=alt.Color('Caste:N', legend=None)
            ).properties(
                title='Students by Caste'
            )
            st.altair_chart(chart, use_container_width=True)
            
            # Stream-wise caste distribution
            st.subheader("Caste Distribution by Stream")
            
            # Create pivot table
            caste_pivot = pd.pivot_table(
                st.session_state.students_df, 
                values='Name',
                index='Stream',
                columns='Caste',
                aggfunc='count',
                fill_value=0
            ).reset_index()
            
            st.dataframe(caste_pivot, use_container_width=True)
        
        # Tab 4: Second Language
        with analysis_tabs[3]:
            st.subheader("Second Language Distribution")
            
            # Create DataFrame for plot
            language_counts = st.session_state.students_df['Second_Language'].value_counts().reset_index()
            language_counts.columns = ['Second Language', 'Count']
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(language_counts, use_container_width=True)
            
            with col2:
                chart = alt.Chart(language_counts).mark_bar().encode(
                    x=alt.X('Second Language:N', title='Second Language'),
                    y=alt.Y('Count:Q', title='Number of Students'),
                    color=alt.Color('Second Language:N', legend=None)
                ).properties(
                    title='Students by Second Language'
                )
                st.altair_chart(chart, use_container_width=True)
            
            # Stream-wise language distribution
            st.subheader("Second Language by Stream")
            
            # Create pivot table
            language_pivot = pd.pivot_table(
                st.session_state.students_df, 
                values='Name',
                index='Stream',
                columns='Second_Language',
                aggfunc='count',
                fill_value=0
            ).reset_index()
            
            # Convert to a format suitable for Altair
            language_data = pd.melt(
                language_pivot, 
                id_vars=['Stream'], 
                var_name='Language', 
                value_name='Count'
            )
            
            # Display the data
            st.dataframe(language_pivot, use_container_width=True)
            
            # Create chart
            chart = alt.Chart(language_data).mark_bar().encode(
                x=alt.X('Stream:N', title='Stream'),
                y=alt.Y('Count:Q', title='Number of Students'),
                color=alt.Color('Language:N'),
                xOffset='Language:N'  # Group bars by language
            ).properties(
                title='Second Language Distribution by Stream'
            )
            st.altair_chart(chart, use_container_width=True)
        
        # Tab 5: Date-wise Analysis
        with analysis_tabs[4]:
            st.subheader("Date-wise Admission Analysis")
            
            # Ensure Date_of_Admission is in datetime format
            try:
                date_df = st.session_state.students_df.copy()
                date_df['Date_of_Admission'] = pd.to_datetime(date_df['Date_of_Admission'])
                
                # Group by date and stream
                date_stream_counts = date_df.groupby(['Date_of_Admission', 'Stream']).size().reset_index(name='Count')
                
                # Format date for display
                date_stream_counts['Date'] = date_stream_counts['Date_of_Admission'].dt.strftime('%Y-%m-%d')
                
                # Show the data
                st.dataframe(date_stream_counts, use_container_width=True)
                
                # Create chart
                chart = alt.Chart(date_stream_counts).mark_bar().encode(
                    x=alt.X('Date:N', title='Date'),
                    y=alt.Y('Count:Q', title='Number of Students'),
                    color=alt.Color('Stream:N'),
                    xOffset='Stream:N'  # Group bars by stream
                ).properties(
                    title='Daily Admissions by Stream'
                )
                st.altair_chart(chart, use_container_width=True)
                
                # Total admissions per day
                st.subheader("Total Admissions by Date")
                daily_totals = date_df.groupby('Date_of_Admission').size().reset_index(name='Total')
                daily_totals['Date'] = daily_totals['Date_of_Admission'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(daily_totals[['Date', 'Total']], use_container_width=True)
                
                # Create chart for totals
                chart = alt.Chart(daily_totals).mark_line(point=True).encode(
                    x=alt.X('Date:N', title='Date'),
                    y=alt.Y('Total:Q', title='Number of Admissions'),
                    tooltip=['Date', 'Total']
                ).properties(
                    title='Total Daily Admissions Trend'
                )
                st.altair_chart(chart, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error in date analysis: {str(e)}")
                st.info("Please check if the dates in your data are in a valid format (YYYY-MM-DD).")
            
    else:
        st.info("No admission data available for analysis.")

# Add a footer
st.markdown("---")
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <p>© {ADMISSION_YEAR} {SCHOOL_NAME} Admission Portal</p>
    <p>Made with ❤️ for Education</p>
</div>
""", unsafe_allow_html=True)