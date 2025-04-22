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
    cursor.execute("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options")  # Fixed query here
    fruits_data = cursor.fetchall()
    fruits_df = pd.DataFrame(fruits_data, columns=['FRUIT_NAME', 'SEARCH_ON'])
    st.write("Fruit options loaded successfully.")
except Exception as e:
    st.error(f"Error fetching fruit options from Snowflake: {e}")
    st.stop()

# Allow user to select fruits
incredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruits_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if incredient_list:
    # Loop through selected ingredients and show info
    incredient_string = ''
    for fruit_chosen in incredient_list:
        incredient_string += fruit_chosen + ' '

        # Get the search value from fruits_df
        search_on = fruits_df.loc[fruits_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Fetch nutrition info from external API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        # Check if the response is successful
        if smoothiefroot_response.status_code == 200:
            nutrition_data = smoothiefroot_response.json()
            st.dataframe(pd.DataFrame(nutrition_data), use_container_width=True)
            st.stop
        else:
            st.error(f"Error fetching data for {fruit_chosen}: {smoothiefroot_response.status_code}")

    # Insert order details into Snowflake database
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values('{incredient_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            cursor.execute(my_insert_stmt)  # Insert the order into Snowflake
            conn.commit()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error submitting the order: {e}")
