import streamlit as st
import pandas as pd

# Initialize session state for data
if "data" not in st.session_state:
    st.session_state.data = {
        "First Name": ["Ly"],
        "Last Name": ["Vu"],
        "Age": [37]
    }

# Input fields for new entry
first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
age = st.number_input("Age", min_value=0, step=1)

if st.button("Add Entry"):
    if first_name and last_name and age:
        st.session_state.data["First Name"].append(first_name)
        st.session_state.data["Last Name"].append(last_name)
        st.session_state.data["Age"].append(int(age))

df = pd.DataFrame(st.session_state.data)
st.table(df)
