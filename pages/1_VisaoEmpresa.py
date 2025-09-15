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


st.set_page_config (page_title='Visão Empresa', layout = 'wide')


#-------------------------------------------Funções-----------------------------------------------------------------------
def country_maps( df ):
        data_plot = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 
        'Road_traffic_density']).median().reset_index()
        
        # Gráfico
        map_ = folium.Map( zoom_start=11 )
        
        for index, location_info in data_plot.iterrows():
            folium.Marker( [location_info['Delivery_location_latitude'],
                         location_info['Delivery_location_longitude']],
                         popup=location_info[['City',  'Road_traffic_density' ]] ).add_to (map_)
        
        folium_static( map_, width=1024, height=600)
        return fig







def week_orders_per_delivery_person( df ):
        df = df
        df['Week_of_Year'] = df['Order_Date'].dt.strftime( '%U' )
        df_aux = df.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    
        # Quantidade de pedidos por entregador por semana
        df_aux1 = df.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
        df_aux2 = df.loc[:, [ 'Delivery_person_ID', 'Week_of_Year'] ].groupby('Week_of_Year').nunique().reset_index()
        
        # união das duas tabelas
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        
        # Quantas entregas na semana / Quantos entregadores únicos por semana
        df_aux['Order_by_Delivery'] = df_aux['ID'] / df_aux ['Delivery_person_ID']
        fig = px.line(df_aux, x='Week_of_Year', y='Order_by_Delivery')
        return fig






def order_by_week( df ):
        df = df
        # criando uma coluna nova chamada semana do ano / strftime -> string for time/ %U para começar primeiro dia da semana no domingo.
        df['Week_of_Year'] = df['Order_Date'].dt.strftime( '%U' )
        df_aux = df.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
        fig = px.line(df_aux, x='Week_of_Year', y='ID')
        return fig





def traffic_order_city(df):
        columns = ['ID', 'City', 'Road_traffic_density']
        df_aux = df.loc[:, columns].groupby( ['City','Road_traffic_density'] ).count().reset_index()
        df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
        fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
        return fig
            




def traffic_order_share(df):
        columns = ['ID', 'Road_traffic_density']
        df_aux= df.loc[:, columns].groupby('Road_traffic_density').count().reset_index()
        df_aux['percen_ID'] = 100 * (df_aux['ID']/ df_aux['ID'].sum())
        fig = px.pie( df_aux, values='percen_ID', names='Road_traffic_density')
        return fig





def order_metric (df):        
         # Quantidade de pedidos por dia
         df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
         df_aux.columns = ['order_date',  'qtd_entregas']
        
         # Gráfico
         fig = px.bar(df_aux, x='order_date', y='qtd_entregas')
         return fig
      




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

st.header('Marketplace - Visão Cliente')




#image_path = ('logo1.png')
image = Image.open( 'logo1.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')



st.sidebar.markdown("""---""")




st.sidebar.markdown('## Selecione uma Data Limite')
date_slider = st.sidebar.slider(
                                 'Até qual Data?', 
                                  value=datetime.datetime(2022,4,3), 
                                  min_value=datetime.datetime(2022,2,11), 
                                  max_value=datetime.datetime(2022,4,6), 
                                  format='DD-MM-YYYY')


st.sidebar.markdown("""---""")



traffic_options = st.sidebar.multiselect( 'Quais condições de trânsito gostaria de ver?',
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


tab1, tab2, tab3 = st.tabs([ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ])


with tab1:
    with st.container():
            # Order Metric
            fig = order_metric (df)
            st.markdown('### Orders By Day')
            st.plotly_chart ( fig, use_container_width=True )

    


    with st.container():
        col1, col2 = st.columns (2)

        
        with col1:
            fig = traffic_order_share (df)
            st.markdown('### Traffic Order Share')
            st.plotly_chart( fig, use_container_width=True)
            
            


        with col2:
            st.markdown('### Traffic Order City')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)






with tab2:



    
    with st.container():
        st.markdown('### Weekly Orders per Delivery Person')
        fig =  week_orders_per_delivery_person( df )
        st.plotly_chart ( fig, use_container_width=True )


    

    with st.container():
        st.markdown('### Order By Week')
        fig = order_by_week (df)
        st.plotly_chart ( fig, use_container_width=True )


     



with tab3:
        st.markdown('### Country Maps')
        fig = country_maps( df )
        



















print('Comando finalizado')