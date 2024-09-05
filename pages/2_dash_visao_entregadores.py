#importando libraries
import pandas as pd 
import plotly.express as px 
import folium
from haversine import haversine 
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

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
st.header( 'Marketplace - Visão Entregadores')

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

    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_veiculo = df1['Vehicle_condition'].max()
            st.metric('Melhor condição', melhor_veiculo)
        with col4:
            pior_veiculo = df1['Vehicle_condition'].min()
            st.metric('Pior condição', pior_veiculo)

        #titulo
        with st.container():
            st.markdown("---")
            st.header('Avaliações')

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações médias por entregador')
            avaliacao_entregador = (df1.loc[ : , ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                    .groupby('Delivery_person_ID')
                                    .mean()
                                    .reset_index())
            st.dataframe(avaliacao_entregador)
        with col2:
            st.markdown('##### Avaliações médias por transito')
            avaliacao_media_desvp_por_trafego = (df1.loc[ : , ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                 .groupby('Road_traffic_density')
                                                 .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            avaliacao_media_desvp_por_trafego.columns=['Delivery_mean', 'Delivery_std']
            avaliacao_media_desvp_por_trafego = avaliacao_media_desvp_por_trafego.reset_index()
            st.dataframe(avaliacao_media_desvp_por_trafego)

            st.markdown('##### Avaliações médias por clima')
            avaliacao_media_desvp_por_clima = (df1.loc[ : , ['Delivery_person_Ratings', 'Weatherconditions']]
                                               .groupby('Weatherconditions')
                                               .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            avaliacao_media_desvp_por_clima.columns=['Delivery_mean', 'Delivery_std']
            avaliacao_media_desvp_por_clima = avaliacao_media_desvp_por_clima.reset_index()
            st.dataframe(avaliacao_media_desvp_por_clima)

         #titulo
        with st.container():
            st.markdown("---")
            st.header('Velocidade de entrega')

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            entregadores_mais_rapidos = (df1.loc[ : , ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                                         .groupby(['City', 'Delivery_person_ID'])
                                         .min()
                                         .sort_values(['Time_taken(min)', 'City'])
                                         .reset_index())

            aux1 = entregadores_mais_rapidos.loc[entregadores_mais_rapidos['City'] == 'Metropolitian', : ].head(10)
            aux2 = entregadores_mais_rapidos.loc[entregadores_mais_rapidos['City'] == 'Urban', : ].head(10)
            aux3 = entregadores_mais_rapidos.loc[entregadores_mais_rapidos['City'] == 'Semi-Urban', : ].head(10)

            entregadores_rapidos = pd.concat([aux1, aux2, aux3]).reset_index(drop=True)
            st.dataframe(entregadores_rapidos)
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            entregadores_mais_lentos = (df1.loc[ : , ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                                        .groupby(['City', 'Delivery_person_ID'])
                                        .min()
                                        .sort_values(['Time_taken(min)', 'City'], ascending=False)
                                        .reset_index())
            aux1 = entregadores_mais_lentos.loc[entregadores_mais_lentos['City'] == 'Metropolitian', : ].head(10)
            aux2 = entregadores_mais_lentos.loc[entregadores_mais_lentos['City'] == 'Urban', : ].head(10)
            aux3 = entregadores_mais_lentos.loc[entregadores_mais_lentos['City'] == 'Semi-Urban', : ].head(10)
            entregadores_lentos = pd.concat([aux1, aux2, aux3]).reset_index(drop=True)
            st.dataframe(entregadores_lentos)

            