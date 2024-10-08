# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session # Se comenta debido a que se cambia la forma de conextar a snowflake
from snowflake.snowpark.functions import col

# Para Seccion 04: (Conexion con Frutyvice)
import requests

# --------------------------------------------------------------------
# Seccion 01: Mensaje de inicio de la applicacion

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Name on the order
name_on_order = st.text_input("Name on Smoothie:", "Your name")
st.write("The name on the smoothie will be:", name_on_order)

# --------------------------------------------------------------------
# Seccion 02: Conexion con Snowflake

# # Conexion con snowflake via
# # Snowflake (SiS)
# session = get_active_session() # Se comenta debido a que se cambia la forma de conextar a snowflake
# Streamlit (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------------------------
# Seccion 03: Cuadro de seleccion de ingredientes segun datos de Snowflake

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# Se muestra la tabla obtenida en forma de tabla
# st.dataframe(data=my_dataframe, use_container_width=True)

# Convert the snowpark Dataframe to a Pandas Dataframe so we can use de LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

# Se muestra la tabla obtenida en forma de lista seleccionable
ingredients_list = st.multiselect(
    'Schoose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

# se muestra la seleccion de ingredientes de forma organizada
# st.write(ingredients_list)
# se muestra la seleccion de ingredientes
# st.text(ingredients_list)

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)

    # Declaracion de variable string de ingredientes
    ingredients_string = ''

    # Union de diferentes ingredientes dentro de una misma variable
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        # --------------------------------------------------------------------
        # Seccion 2.A: Tabla de informacion nutricional obtenida de Frutyvice

        # Subtitulo: Informacion nutricional
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Obtencion de informacion cruda de URL
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)

        # # visualizacion de informacion cruda de URL
        # st.text(fruityvice_response.json())

        # Creacion de dt (DataFrame) de la informacion obtenida
        ft_dt = st.dataframe(
            data = fruityvice_response.json()
            , use_container_width=True
        )

    # Visualizacion de ingredientes en un unico campo
    st.write(ingredients_string)

    # Se genera sentencia SQL para insertar datos en tabla smoothies.public.order 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # # Se muestra la sentencia generada
    # st.write(my_insert_stmt)
    # st.stop()

    # # Se muestra un mensaje destacado informativo
    # st.success(my_insert_stmt)

    # Insersion de boton de enviar orden
    time_to_insert = st.button('Submit Order')
    
    # Verificacion y respuesta visual de orden enviada
    if time_to_insert:
        # Ejecucion de sentencia SQL
        session.sql(my_insert_stmt).collect()
        # Mensaje destacado satisfactorio
        st.success('Your Smoothie is ordered!', icon="✅")

