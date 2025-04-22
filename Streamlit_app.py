import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Set up your Snowflake connection
try:
    # Using st.connection("snowflake") to get the connection to Snowflake
    cnx = st.connection("snowflake")
    session = cnx.session()
    st.success("✅ Connected to Snowflake successfully!")
except Exception as e:
    st.error("❌ Failed to connect to Snowflake.")
    st.exception(e)
    st.stop()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

# Input for the name on the order
name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Fetch data from Snowflake
my_dataframe = (session.table("smoothies.public.fruit_options")
                .select(col('FRUIT_NAME'), col('SEARCH_ON')))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Let users select ingredients
incredient_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),  # Use the list of fruit names for the multiselect
    max_selections=5)

if incredient_list:
    # Initialize an empty string to hold the ingredients chosen
    incredient_string = ''
    
    # Loop through the selected ingredients and get the search value
    for fruit_chosen in incredient_list:
        incredient_string += fruit_chosen + ' '
        
        # Get the search value from the dataframe for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        
        # Fetch the nutritional information from the smoothiefroot API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        # Check if the API call was successful
        if smoothiefroot_response.status_code == 200:
            nutrition_data = smoothiefroot_response.json()
            st.dataframe(nutrition_data, use_container_width=True)
        else:
            st.error(f"❌ Could not fetch nutrition data for {fruit_chosen}.")

    # Insert order into Snowflake
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values('{incredient_string}', '{name_on_order}')"""
    
    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error("❌ Failed to place your order.")
            st.exception(e)
