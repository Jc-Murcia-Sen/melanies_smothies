# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothies :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Name on the order
name_on_order = st.text_input("Name on Smoothie:", "Your name")
st.write("The name on the smoothie will be:", name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()

# # Se muestra la tabla obtenida en forma de tabla
# st.dataframe(data=my_dataframe, use_container_width=True)

if my_dataframe:

    # Convierte el dataframe en un data editor
    editable_df = st.data_editor(my_dataframe)
    
    # # Funcion experimental igual a la anterior
    # editable_df = st.experimental_data_editor(my_dataframe)
    
    submitted = st.button('Submit')
    
    if submitted:
        
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
    
        try:
            og_dataset.merge(edited_dataset
                            , (og_dataset['order_uid']==edited_dataset['order_uid'])
                            , [when_matched().update({'ORDER_FILLED':edited_dataset['ORDER_FILLED']})]
                            )
            st.success("Order(s) Updated", icon = '👍')
        except:
            st.write('Something went wrong')

else:
    st.success("There are no pending orders right now", icon = '👍')



