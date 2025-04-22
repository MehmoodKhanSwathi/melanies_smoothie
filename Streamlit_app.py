# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

session = get_active_session()
my_dataframe = (session.table("smoothies.public.fruit_options")
                .select(col('FRUIT_NAME')))

incredient_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe,
    max_selections=5)

if incredient_list:
    incredient_string = ''
    for fruite_choosen in incredient_list:
        incredient_string += fruite_choosen + ' '

    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values('{incredient_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# This part was incorrectly indented before:
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
# sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
