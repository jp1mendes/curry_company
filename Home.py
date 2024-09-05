import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon= '🎲')

#image_path = 'C:/Users/João Paulo Mendes/Desktop/Comunidade DS/Programação Python/Ciclo 6 - Visualização Interativa/'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## fasted Delivery in town')
st.sidebar.markdown( """---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """ 
    Growth Dasboard foi construído para acompanhar as métricas de crescimento dos entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão da Empresa:
        - Visão gerencial: Métricas gerais de comportamento.
        - Visão tática: Indicadores semanais de crescimento.
        - Visão geográfica: Insights de goelocalização.
    - Visão Entregador: 
        - Acompanhamento dos indicadores semanais de cresciemnto.
    - Visão Restaurantes: Indicadores semanais de crescimento dos restaurantes.
    ### Ask For Help: João Paulo Mendes 
    """
)