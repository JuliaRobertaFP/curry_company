# IMPORTANDO BIBLIOTECAS
import pandas as pd
import re
from plotly import express as px
import folium
import streamlit as st
import datetime
from PIL import Image
import plotly.graph_objects as go
from streamlit_folium import folium_static
import plotly.graph_objects as go
from haversine import haversine
import numpy as np


st.set_page_config (page_title='Visão Restaurante', layout = 'wide')


# lendo o arquivo 
df = pd.read_csv('train_ftc.csv')

# TRATAMENTO DOS DADOS

#  1. Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias, :]

linhas_vazias = df['Road_traffic_density'] != 'NaN '
df = df.loc[linhas_vazias, :]

linhas_vazias = df['Time_taken(min)'] != 'NaN '
df = df.loc[linhas_vazias, :]

linhas_vazias = df['City'] != 'NaN '
df = df.loc[linhas_vazias, :]

linhas_vazias = df['Festival'] != 'NaN '
df = df.loc[linhas_vazias, :]

# 2. Conversao de texto/categoria/string para numeros inteiros
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )


# 3. Conversao de texto/categoria/strings para numeros decimais
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )


# 4. Conversao de texto para data
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )


# 5 . comando para remover linhas vazias
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )


# 6. comando para remover os espaços após o nome
df.loc[:,'Delivery_person_ID' ] = df.loc[:,'Delivery_person_ID' ].str.strip()
df.loc[:,'Road_traffic_density' ] = df.loc[:,'Road_traffic_density' ].str.strip()
df.loc[:,'Type_of_order' ] = df.loc[:,'Type_of_order' ].str.strip()
df.loc[:,'Type_of_vehicle' ] = df.loc[:,'Type_of_vehicle' ].str.strip()
df.loc[:,'City' ] = df.loc[:,'City' ].str.strip()
df.loc[:,'Time_taken(min)' ] = df.loc[:,'Time_taken(min)' ].str.strip()
df.loc[:,'ID' ] = df.loc[:,'ID' ].str.strip()

# 7. Limpando a coluna de time taken
df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )


# ====================================================================
# Barra Lateral
# ====================================================================

st.header('Marketplace - Visão Restaurantes')



#image_path = ('logo1.png')
image = Image.open( 'logo1.png'  )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')



st.sidebar.markdown("""---""")




st.sidebar.markdown('### Selecione uma Data Limite')
date_slider = st.sidebar.slider(
                                 'Até qual Data?', 
                                  value=datetime.datetime(2022,4,3), 
                                  min_value=datetime.datetime(2022,2,11), 
                                  max_value=datetime.datetime(2022,4,6), 
                                  format='DD-MM-YYYY')


st.sidebar.markdown("""---""")


st.sidebar.markdown('### Quais condições de trânsito gostaria de ver?')
traffic_options = st.sidebar.multiselect( '',
                                      ['Low', 'Medium', 'Hight', 'Jam'],
                                      default = ['Low', 'Medium', 'Hight', 'Jam'] )


st.sidebar.markdown("""---""")

st.sidebar.markdown('Powered by Comunidade DS')


# FILTRO DE DATA
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# FILTRO DE TRÂNSITO
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]


# ====================================================================
# layout Streamlit
# ====================================================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container():
        st.markdown('### Overal Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID' ].unique())
            col1.metric('Entregadores Únicos', delivery_unique)

        
        with col2:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['Distance'] = df.loc[:, cols].apply( lambda x: haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], 
            x['Delivery_location_longitude'])), axis=1)

            avg_distance = np.round(df['Distance'].mean(), 2)
            col2.metric('distância média', avg_distance )


        
        
        with col3:

            # Agrupa e calcula apenas a média de 'Time_taken(min)'
            df_auc = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival')['Time_taken(min)'].mean().reset_index()
            
            # Filtra o valor quando Festival é 'Yes'
            tempo_medio = int(df_auc[df_auc['Festival'] == 'Yes ']['Time_taken(min)'].values[0])
            
            # Exibe no Streamlit
            col3.metric('Tempo Médio de Entrega (Festival)', tempo_medio)


            
        with col4:
              # Agrupa e calcula apenas a média de 'Time_taken(min)'
            df_auc = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival')['Time_taken(min)'].std().reset_index()
            
            # Filtra o valor quando Festival é 'Yes'
            Desvio_Padrao = int(df_auc[df_auc['Festival'] == 'Yes ']['Time_taken(min)'].values[0])
            
            # Exibe no Streamlit
            col4.metric('Desvio Padrão', Desvio_Padrao)


        
        with col5:
            
            # Agrupa e calcula apenas a média de 'Time_taken(min)'
            df_auc = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival')['Time_taken(min)'].mean().reset_index()
            
            # Filtra o valor quando Festival é 'Yes'
            tempo_medio = int(df_auc[df_auc['Festival'] == 'No ']['Time_taken(min)'].values[0])
            
            # Exibe no Streamlit
            col5.metric('Tempo Médio de Entrega', tempo_medio)


        
        with col6:
            # Agrupa e calcula apenas a média de 'Time_taken(min)'
            df_auc = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival')['Time_taken(min)'].std().reset_index()
            
            # Filtra o valor quando Festival é 'Yes'
            Desvio_Padrao = int(df_auc[df_auc['Festival'] == 'No ']['Time_taken(min)'].values[0])
            
            # Exibe no Streamlit
            col6.metric('Desvio Padrão', Desvio_Padrao)



    with st.container():
         st.markdown("""---""")
         st.markdown('#### Distância Média dos Restaurantes por Cidade')

         cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
         df['Distance'] = df.loc[:, cols].apply(lambda x:
                                                   haversine(
                                                       (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                                                   ), axis=1 )
         avg_distance= df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
            
         fig = go.Figure(  data = [go.Pie( labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0]) ] )
         st.plotly_chart(fig)

    

    with st.container():
         st.markdown("""---""")
        
         col1, col2 = st.columns (2, gap='Large')
         with col1:
             st.markdown('#### Tempo Médio e STD de Entrega por Cidade ')
             df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg( {'Time_taken(min)' : ['mean', 'std'] } )
                
             df_aux.columns = ['avg_time', 'std_time']
             df_aux = df_aux.reset_index()
                
                
             fig = go.Figure()
             fig.add_trace (go.Bar(name ='Control', x = df_aux['City'], y = df_aux['avg_time'],
                                   error_y = dict(type='data', array = df_aux ['std_time'],  width=0.1 )))
              
             #fig.update_layout(barmode = 'group')
             st.plotly_chart(fig, use_container_width=True)

         with col2:
             st.markdown('#### Tempo Médio por Tipo de Entrega')
             cols = ['City', 'Time_taken(min)', 'Type_of_order']
             df_aux = df.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)' : ['mean', 'std'] } )
            
             df_aux.columns = ['mean_time', 'std_time']
            
             df_aux = df_aux.reset_index()
            
             df_aux


             

    with st.container():
         st.markdown("""---""")
         st.markdown('#### Tempo Médio por Cidade e Tipo de Tráfego')
         cols =['City', 'Time_taken(min)', 'Road_traffic_density']
         df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)' : ['mean', 'std'] } )
            
         df_aux.columns = ['mean_time', 'std_time']
            
         df_aux = df_aux.reset_index()
            
         fig = px.sunburst( df_aux, path= [ 'City', 'Road_traffic_density' ], values= 'mean_time',
                              color='std_time',  color_continuous_scale= 'RdBu',
                              color_continuous_midpoint= np.average(df_aux['std_time']))
         st.plotly_chart(fig)






























