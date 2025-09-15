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

#from haversine import haversine

st.set_page_config (page_title='Visão Entregadores', layout = 'wide')


#------------------------------------------------Funções-------------------------------------------------------------------------------






def top_entregadores( df, top_ascen ):
        df_aux = (df.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                          .groupby(['City', 'Delivery_person_ID'])
                          .mean()
                          .sort_values(['City', 'Time_taken(min)'], ascending = top_ascen))

        df_aux = df_aux.reset_index()

        df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', : ].head(10)
        df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', : ].head(10)
        df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', : ].head(10)
                
        df = pd.concat([ df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
        return df








def clean_code(df):

    """        Esta função tem a responsabilidade de limmpar o dataframe
               Tipos de limmpeza:
               1. Remoção dos dados NaN
               2. Mudança do tipo de coluna de dados
               3. Remoção dos espaços das variáveis de texto
               4. Formatação da coluna de datas
               5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

               Input: Dataframe
               Output: Dataframe
                                                                                        """
    
    
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

    return df






#-----------------------------------Início da estrutura lógica do código--------------------------------------------------


# immport dataset 
df = pd.read_csv('train_ftc.csv')


# Limpando  os dados
df = clean_code(df)


# ====================================================================
# Barra Lateral
# ====================================================================

st.header('Marketplace - Visão Entregadores')



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
# Layout Streamlit
# ====================================================================

tab1, tab2, tab3 = st.tabs([ 'Visão Gerencial', '-', '-' ])

with tab1:
     with st.container():
         st.title('Overall Metrics')
         
         col1, col2, col3, col4 = st.columns (4, gap='Large')

        # IDADE DOS ENTREGADORES
         
         with col1:
                maior_idade = df.loc[:, 'Delivery_person_Age'].max()
                col1.metric('Maior Idade', maior_idade)
             
         with col2:
                menor_idade = df.loc[:, 'Delivery_person_Age'].min()
                col2.metric('Menor Idade', menor_idade)


          # CONDIÇÃO DOS VEÍCULOS
             
         with col3:
                melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
                col3.metric('Melhor Condição', melhor_condicao)
             
         with col4:
                pior_condicao = df.loc[:, 'Vehicle_condition'].min()
                col4.metric('Pior Condição', pior_condicao)


    

     with st.container():
        st.markdown("""---""")
        st.title ('Avaliações')

        col1, col2 = st.columns(2, gap='Large')
        with col1:
                st.markdown('##### Avaliação medida por Entregador')
                df_avg_ratings = (df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings' ]]
                                  .groupby('Delivery_person_ID')
                                  .mean()
                                  .reset_index())
                st.dataframe(df_avg_ratings)

        with col2:
                st.markdown('##### Avaliação Média por Transito')
                df_avg_rattings_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                              .groupby('Road_traffic_density')
                                              .agg({ 'Delivery_person_Ratings': ['mean','std']  }))


                df_avg_rattings_by_traffic.columns = ['mean_ratings', 'std_ratings']
                df_avg_rattings_by_traffic.reset_index()
                st.dataframe(df_avg_rattings_by_traffic )

            

            
                st.markdown('##### Avaliação Média por Clima')
                df_avg_rattings_by_Weatherconditions = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                        .groupby('Weatherconditions')
                                                        .agg({ 'Delivery_person_Ratings': ['mean','std']  }))


                df_avg_rattings_by_Weatherconditions.columns = ['mean_ratings', 'std_ratings']
                df_avg_rattings_by_Weatherconditions.reset_index()
                st.dataframe( df_avg_rattings_by_Weatherconditions)

     with st.container():
        st.markdown("""---""")
        st.title ('Velocidade de Entrega')

        col1, col2 = st.columns(2, gap='Large')
         
        with col1:
                st.markdown('##### Top Entregadores mais Rapidos')
                df1 = top_entregadores(df, top_ascen = True)
                st.dataframe(df1)




        with col2:
                st.markdown('##### Top Entregadores mais Lentos')
                df1 = top_entregadores( df, top_ascen = False )
                st.dataframe(df1)


              


























