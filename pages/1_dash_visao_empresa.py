#importando libraries
import pandas as pd 
import plotly.express as px 
import folium
from haversine import haversine 
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='🏭', layout='wide')

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
st.header( 'Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        pedidos_dia = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
        print(pedidos_dia)
        #plotando grafico de barras
        fig = px.bar(pedidos_dia, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            pedidos_trafego = df1.loc[ : , ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            #convertendo para porcentagem
            pedidos_trafego['porcentagem'] = pedidos_trafego['ID'] / pedidos_trafego['ID'].sum()
            print(pedidos_trafego)
            #plotando grafico de pizza
            st.markdown('# Traffic Order Share')
            fig1 = px.pie(pedidos_trafego, values= 'porcentagem', names= 'Road_traffic_density')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            pedidos_cidade_trafego = df1.loc[ : , ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            print(pedidos_cidade_trafego)
            #plotando grafico de bolhas
            st.markdown('# Traffic Order City')
            fig3=px.scatter(pedidos_cidade_trafego, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig3, use_container_width=True)

with tab2:
    with st.container():
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        pedidos_semana = df1.loc[ : , ['ID', 'week_of_year'] ].groupby( 'week_of_year').count().reset_index()
        print(pedidos_semana)
        #plotando grafico de linhas
        st.markdown('# Order by Week')
        fig4=px.line(pedidos_semana, x='week_of_year', y='ID')
        st.plotly_chart(fig4, use_container_width=True)

    with st.container():
        entregadores_unicos_semana = df1.loc[ : , ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        #juntando dois dataframes
        df_aux = pd.merge(pedidos_semana, entregadores_unicos_semana, how= 'inner')
        #criando coluna
        df_aux['entrega_por_entregador'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        print(df_aux)
        #plotando grafico de linhas
        st.markdown('# Order Share by Week')
        fig5 = px.line(df_aux, x='week_of_year', y='entrega_por_entregador')
        st.plotly_chart(fig5, use_container_width=True)

with tab3:
    loc_trafego = df1.loc[ :, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    #plotando mapa
    st.markdown('# Country Maps')
    map = folium.Map()
    for index, location_info in loc_trafego.iterrows():
        folium.Marker([location_info['Delivery_location_latitude' ], location_info['Delivery_location_longitude']]).add_to(map)
    folium_static(map, width=1024, height= 600)