# Import python packages
import requests
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Setup Snowflake session using secrets
connection_parameters = st.secrets["snowflake"]
session = Session.builder.configs(connection_parameters).create()

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name on order
name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Get fruit options from Snowflake (case-sensitive table and column names)
try:
    my_dataframe = session.table('smoothies.public."FRUIT_OPTIONS"').select(
        col('"FRUIT_NAME"'),
        col('"SEARCH_ON"')
    )
    st.write("✅ Successfully connected to the `FRUIT_OPTIONS` table.")
    
    # Convert Snowpark DataFrame to Pandas DataFrame
    pd_df = my_dataframe.to_pandas()

except Exception as e:
    st.error("❌ Error retrieving data from `smoothies.public.FRUIT_OPTIONS`.")
    st.exception(e)
    st.stop()

# Display fruit options in a multiselect
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredient_list:
    ingredient_string = ''
    
    for fruit_chosen in ingredient_list:
        ingredient_string += fruit_chosen + ' '
        
        # Find the search value for the fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        
        # Display nutritional information from an external API (example with watermelon)
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothie_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothie_response.status_code == 200:
            # Convert JSON response to DataFrame and display it
            smoothie_data = smoothie_response.json()
            st.dataframe(smoothie_data, use_container_width=True)
        else:
            st.error(f"Failed to fetch nutrition data for {fruit_chosen}.")

    # Prepare the SQL statement for inserting the order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public."ORDERS" (ingredients, name_on_order)
        VALUES ('{ingredient_string}', '{name_on_order}')
    """
    
    # Insert order into Snowflake
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error("❌ Error inserting order into the database.")
            st.exception(e)

