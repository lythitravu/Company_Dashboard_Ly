import streamlit as st
import pandas as pd

# Initialize session state for table data
if "data" not in st.session_state:
    st.session_state.data = {
        "First Name": ["Baby", "Baby"],
        "Last Name": ["Kaka", "Kuku"]
    }

st.title("Simple Name Table")

# Input fields
first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")

# Add button
if st.button("Add Entry"):
    if first_name and last_name:
        st.session_state.data["First Name"].append(first_name)
        st.session_state.data["Last Name"].append(last_name)

# Display table
df = pd.DataFrame(st.session_state.data)
st.table(df)
