# Import python packages
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Query fruit options
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))
)

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# Display multiselect
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredient_list:
    ingredient_string = ''
    
    for fruit_chosen in ingredient_list:
        ingredient_string += fruit_chosen + ' '

        # Get the corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Call API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch nutrition data for {fruit_chosen}.")

    # Prepare insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredient_string.strip()}', '{name_on_order}')
    """

    # Submit order button
    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error("❌ Error inserting order into the database.")
            st.exception(e)
