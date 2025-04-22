# Import python packages
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Set up Snowflake session using Streamlit secrets
connection_parameters = st.secrets["snowflake"]
session = Session.builder.configs(connection_parameters).create()

# App UI
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Get user name
name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Query fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Fruit picker
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Show nutrition info
if ingredient_list:
    ingredient_string = ""
    
    for fruit in ingredient_list:
        ingredient_string += fruit + " "
        
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit} is: {search_on}")
        
        st.subheader(f"{fruit} Nutrition Information")
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        try:
            st.dataframe(data=pd.json_normalize(response.json()), use_container_width=True)
        except Exception as e:
            st.error(f"Error loading API response for {fruit}: {e}")

    # Insert order button
    insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredient_string.strip()}', '{name_on_order}')
    """
    if st.button('Submit Order'):
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! 🥤", icon="✅")
