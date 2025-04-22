# Import necessary packages
import requests
import streamlit as st
import pandas as pd
import snowflake.connector

# Streamlit UI setup
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

# User input for the name on the smoothie order
name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Establish Snowflake connection using snowflake.connector
try:
    # Connect to Snowflake using credentials from Streamlit secrets
    conn = snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )
    cursor = conn.cursor()
    st.write("Connected to Snowflake successfully!")
except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
    st.stop()  # Stop the app if there's an error

# Query to get fruit options from Snowflake
try:
    cursor.execute("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options_
