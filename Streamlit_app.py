import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Access Snowflake connection details from Streamlit secrets
snowflake_creds = st.secrets["snowflake"]

# Set up the Snowflake connection using the credentials from the secrets
try:
    # Make sure the connection name 'snowflake' matches what you have in Streamlit secrets
    cnx = st.experimental_connection(
        "snowflake",  # This is the name you are giving to the connection
        user=snowflake_creds["user"],
        password=snowflake_creds["password"],
        account=snowflake_creds["account"],
        warehouse=snowflake_creds["warehouse"],
        database=snowflake_creds["database"],
        schema=snowflake_creds["schema"],
        role=snowflake_creds.get("role", "")  # Optional: only if you're using a custom role
    )
    session = cnx.session()
    st.success("✅ Connected to Snowflake successfully!")
except Exception as e:
    st.error("❌ Failed to connect to Snowflake.")
    st.exception(e)
    st.stop()

# Rest of the app code
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """
)

name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

# Fetch fruit options from Snowflake
my_dataframe = (session.table("smoothies.public.fruit_options")
                .select(col('FRUIT_NAME'),
                       col('SEARCH_ON')))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Ingredient selection from user
incredient_list = st.multiselect(
    'Choose upto 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Show fruit names as options
    max_selections=5)

if incredient_list:
    # Build a string of selected ingredients
    incredient_string = ''
    for fruit_chosen in incredient_list:
        incredient_string += fruit_chosen + ' '

        # Get the search value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Fetch nutrition information for the fruit from an external API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        # Display the nutrition data in the app
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    # Construct the SQL insert statement for the smoothie order
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values('{incredient_string}', '{name_on_order}')"""
    
    # Allow the user to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
