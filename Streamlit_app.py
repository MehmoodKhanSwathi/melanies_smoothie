# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """
)

name_on_order = st.text_input('Name on smoothie:')
st.write(f'The name on your smoothie will be: {name_on_order}')

session = get_active_session()
my_dataframe = (session.table("smoothies.public.fruit_options")
                .select(col('FRUIT_NAME')))
# st.dataframe(data=my_dataframe, use_container_width=True)

incredient_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe,
    max_selections=5)

if incredient_list:
    # st.write(incredient_list)
    # st.text(incredient_list)
    
    incredient_string = ''
    for fruite_choosen in incredient_list:
        incredient_string += fruite_choosen + ' '

    # st.write(incredient_string)
    
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values('{incredient_string}', '{name_on_order}')"""
    
    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
# sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_wodth=True)
