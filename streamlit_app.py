# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

#option = st.selectbox(
#    "What is your favorite fruit?",
#    ("Banana", "Strawberries", "Peaches"),
#)
#
#st.write("Your favorite fruit is:", option)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)

sf_df=my_dataframe.to_pandas()
#st.dataframe(sf_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the 'SEARCH_ON' value for the chosen fruit from the DataFrame
        search_on = sf_df.loc[sf_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Make the API request for the chosen fruit
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        # Store the smoothie data separately, without overwriting sf_df
        smoothie_data = smoothiefroot_response.json()

        # Display the smoothie data in the app
        st.dataframe(data=smoothie_data, use_container_width=True)

    # Insert the order into the database
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+ """')"""
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")
