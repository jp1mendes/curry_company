#importando libraries
import pandas as pd 
import numpy as np
import plotly.express as px 
import folium
from haversine import haversine 
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

#lendo dataset
df = pd.read_csv('train.csv')

#==================================LIMPEZA DA BASE DE DADOS===================================================
df1 = df.copy()

#removendo as linhas com valores não existente (NaN) alterando couluna Delivery_person_Age de object para int
df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :]
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

#removendo as linhas com valores não existente (NaN) alterando couluna multiple_deliveries de object para int
df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

#removendo as linhas com valores não existente (NaN) em City
df1 = df1.loc[df1['City'] != 'NaN ', :]

#removendo as linhas com valores não existente (NaN) em Festival
df1 = df1.loc[df1['Festival'] != 'NaN ', :]

#removendo as linhas com valores não existente (NaN) em Road_traffic_density
df1 = df1.loc[df1['Road_traffic_density'] != 'NaN ', :]

#alterando coluna Delivery_person_Ratings de object para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

#alterando coluna Order_Date de object para datat
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

# retirando espaço vazio dos valores da coluna
df1.loc[: , 'ID'] = df1.loc[: , 'ID'].str.strip()
df1.loc[: , 'Road_traffic_density'] = df1.loc[: , 'Road_traffic_density'].str.strip()
df1.loc[: , 'Type_of_order'] = df1.loc[: , 'Type_of_order'].str.strip()
df1.loc[: , 'Type_of_vehicle'] = df1.loc[: , 'Type_of_vehicle'].str.strip()
df1.loc[: , 'City'] = df1.loc[: , 'City'].str.strip()

#Limpando coluna time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

#===================================================================================================

#================================= barra lateral streamlit =========================================
st.header( 'Marketplace - Visão Restaurantes')

image = Image.open('logo.jpg')
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## fasted Delivery in town')
st.sidebar.markdown( """---""")

st.sidebar.markdown( '## selecione a data limite')


date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown( """---""")

traffic_options = st.sidebar.multiselect(
    'Quais condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown( """---""")
st.sidebar.markdown( '## Powered by João Paulo Mendes')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, : ]

#===================================================================================================
#==================================== layout streamlit =============================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.header('Overall Metrics')
        st.markdown("""---""")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entregadores_unicos = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', entregadores_unicos)

        with col2:
            dist_media_restaurantes = (df1.loc[ : , ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude'] ]
                                       .apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
            dist_media_restaurantes = np.round( dist_media_restaurantes.mean(), 2)
            col2.metric('Distância média das entregas', dist_media_restaurantes)
        with col3:
            tempomedio_nos_festivais = (df1.loc[ : , ['Time_taken(min)', 'Festival']]
                                        .groupby('Festival')
                                        .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_nos_festivais.columns = ['avg_time', 'std']
            tempomedio_nos_festivais = tempomedio_nos_festivais.reset_index()
            tempomedio_nos_festivais = np.round(tempomedio_nos_festivais.loc[ 1 , 'avg_time'], 2)
            col3.metric('Tempo médio de entrega com Festivais', tempomedio_nos_festivais)
        with col4:
            tempomedio_nos_festivais = (df1.loc[ : , ['Time_taken(min)', 'Festival']]
                                        .groupby('Festival')
                                        .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_nos_festivais.columns = ['avg_time', 'std']
            tempomedio_nos_festivais = tempomedio_nos_festivais.reset_index()
            tempomedio_nos_festivais = np.round(tempomedio_nos_festivais.loc[ 1 , 'std'], 2)
            col4.metric('desvio padrão médio de entrega com Festivais', tempomedio_nos_festivais)
        with col5:
            tempomedio_nos_festivais = (df1.loc[ : , ['Time_taken(min)', 'Festival']]
                                        .groupby('Festival')
                                        .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_nos_festivais.columns = ['avg_time', 'std']
            tempomedio_nos_festivais = tempomedio_nos_festivais.reset_index()
            tempomedio_nos_festivais = np.round(tempomedio_nos_festivais.loc[ 0 , 'avg_time'], 2)
            col5.metric('Tempo médio de entrega sem Festivais', tempomedio_nos_festivais)
        with col6:
            tempomedio_nos_festivais = (df1.loc[ : , ['Time_taken(min)', 'Festival']]
                                        .groupby('Festival')
                                        .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_nos_festivais.columns = ['avg_time', 'std']
            tempomedio_nos_festivais = tempomedio_nos_festivais.reset_index()
            tempomedio_nos_festivais = np.round(tempomedio_nos_festivais.loc[ 0 , 'std'], 2)
            col6.metric('desvio padrão médio de entrega sem Festivais', tempomedio_nos_festivais)

    with st.container():
        st.header('Distribuição do Tempo')
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Tempo médio de entrega por cidade')
            tempomedio_desvp_por_cidade = (df1.loc[ : , ['Time_taken(min)', 'City']]
                                           .groupby('City')
                                           .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_desvp_por_cidade.columns = ['avg_time', 'std']
            tempomedio_desvp_por_cidade = tempomedio_desvp_por_cidade.reset_index()
            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control', x=tempomedio_desvp_por_cidade['City'], y=tempomedio_desvp_por_cidade['avg_time'], error_y=dict(type='data', array=tempomedio_desvp_por_cidade['std'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
        
        with col2:
            st.markdown('#### Distribuição da distância')
            tempomedio_desvp_por_cidade_e_pedido = (df1.loc[ : , ['Time_taken(min)', 'City', 'Type_of_order']]
                                                .groupby(['City', 'Type_of_order'])
                                                .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_desvp_por_cidade_e_pedido.columns = ['avg_time', 'std']
            tempomedio_desvp_por_cidade_e_pedido = tempomedio_desvp_por_cidade_e_pedido.reset_index()
            st.dataframe(tempomedio_desvp_por_cidade_e_pedido)


    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Tempo médio de entrega por cidade')
            df1['dist_media_restaurantes'] = df1.loc[ : , ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude'] ].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            media_distancia = df1.loc[:, ['dist_media_restaurantes', 'City']].groupby('City').mean().reset_index()
            fig = go.Figure( data= [ go.Pie( labels= media_distancia['City'], values= media_distancia['dist_media_restaurantes'], pull= [0, 0.1, 0])])
            st.plotly_chart(fig)

        with col2:
            tempomedio_desvp_por_cidade_e_trafego = (df1.loc[ : , ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                                     .groupby(['City', 'Road_traffic_density'])
                                                     .agg({'Time_taken(min)' : ['mean', 'std']}))
            tempomedio_desvp_por_cidade_e_trafego.columns = ['avg_time', 'std']
            tempomedio_desvp_por_cidade_e_trafego = tempomedio_desvp_por_cidade_e_trafego.reset_index()

            fig = px.sunburst(tempomedio_desvp_por_cidade_e_trafego, path=['City', 'Road_traffic_density'], values='avg_time', color_continuous_midpoint=np.average(tempomedio_desvp_por_cidade_e_trafego['std']))
            st.plotly_chart(fig)