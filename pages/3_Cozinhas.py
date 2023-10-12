#IMPORTANDO AS BIBLIOTECAS
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import inflection
import streamlit as st
from PIL import Image
import locale
from streamlit_folium import folium_static



st.set_page_config (page_title = 'Cozinhas', page_icon='🍽️', layout='wide')


# ============================================
# Importando o dataset
# ============================================

df = pd.read_csv('zomato.csv')


# ============================================
# Funções
# ============================================

def rename_columns(df):
    df1 = df.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

df1 = rename_columns(df)

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

df1['country_code'] = df['country_code'].apply(country_name)

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

df1['price_range'] = df['price_range'].apply(create_price_tye)
    
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

df1['color_name'] = df['rating_color'].apply(color_name)


def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe:
    
        Tipos de Limpeza:
        1. Remoção dos dados nan
        2. Categorizando todos os restaurantes somente por um tipo de culinária.
        3. Remoção de duplicados
        4. Exclusão da coluna 'Switch to order menu'
        
    
        Input: Dataframe
        Output: Dataframe"""

#Realizada a exclusão da coluna 'Switch to order menu', após avaliação da tabela descritiva (não há valores relevantes para utilização dela)

    df1 = df1.drop ('switch_to_order_menu', axis=1)

#Realizada a exclusão de dados duplicados do dataframe
    
    df1 = df1.drop_duplicates()

#Retirando valores vazios da coluna 'Cuisines'

    limp_linhas = df1['cuisines'] != ""
    df1 = df1.loc[limp_linhas, :]
    df1['cuisines'] = df1['cuisines'].astype (str)


    limp_linhas = df1['cuisines'] != "nan"
    df1 = df1.loc[limp_linhas, :]
    df1['cuisines'] = df1['cuisines'].astype (str)

#Categorizando todos os restaurantes somente por um tipo de culinária.
    df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    return (df1)


def top_cuisines (df1, top_asc):
    #função para gerar os gráficos barras de melhor e pior tipos de culinárias

    df_aux = (df1.loc[:,['cuisines','aggregate_rating']]
                 .groupby('cuisines')
                 .mean()
                     .sort_values('aggregate_rating', ascending=top_asc).head(qtde_rest).reset_index())
    df_aux = round(df_aux,2)
    fig = (px.bar(df_aux, x='cuisines', y='aggregate_rating', title=f'Top {qtde_rest}  Tipos de Culinárias',
            text_auto=True,
             labels={'aggregate_rating':'Média das Avaliações',
                    'cuisines' : 'Culinária'}))
       
    fig.update_layout(title_x=0.2)
    fig.update_layout(title_font_color='black')

    fig.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)
    return fig


# ============================================
# REALIZANDO A LIMPEZA DO DATAFRAME
# ============================================

df1 = clean_code (df)

# ============================================
# Barra Lateral
# ============================================


st.sidebar.markdown ('# Filtros')

default_options = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
country_options = st.sidebar.multiselect ('Escolha os Paises que Deseja visualizar as Informações:',
                                           df1['country_code'].unique(), default=default_options)


qtde_rest = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar:', 0, 20, 10)



default2_options = ['Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian', 'Others', 'Tex-Mex', 'Vegetarian', 'Durban', 'Beverages', 'Coffee', 'Pizza', 'Chinese', 'European', 'Seafood', 'Fresh Fish', 'Fish and Chips', 'Street Food' ]
cuisine_options = st.sidebar.multiselect ('Escolha os Tipos de Culinária:',
                                           df1['cuisines'].unique(), default=default2_options)



st.sidebar.markdown( """---""" )
st.sidebar.markdown( '#### Powered by Wellington Silva' )
                                           
#Filtro dos Países
linhas_selecionadas = df1['country_code'].isin (country_options)
df1 = df1.loc[linhas_selecionadas, :]   

#Filtro das Culinárias
linhas_selecionadas = df1['cuisines'].isin (cuisine_options)
df1 = df1.loc[linhas_selecionadas, :]


#Filtro Qtde de restaurantes
#df1 = df1.groupby('country_code').filter(lambda x: x['cuisines'].nunique() >= qtde_rest)
                                 

# =======================================
# Layout no Streamlit
# =======================================

st.title( ' 🍽️ Visão Tipos de Cozinhas' )

st.container()
st.markdown ('## Melhores Restaurantes dos Principais tipos Culinários')
        
col1, col2, col3, col4 = st.columns (4, gap='small')

with st.container():
    with col1:
        #Nome do tipo de culinária com a maior nota
        df_aux = (df1.loc[:,['cuisines','aggregate_rating']]
                     .groupby('cuisines')
                     .mean()
                     .sort_values('aggregate_rating', ascending=False).reset_index().head(10))
        melhor = df_aux.iloc[0,0]
        col1.metric ( label='Melhor Culinária', value=melhor, help= "Nome tipo Culinária com a maior nota" )
    
    with col2:
        #Maior nota do tipo de culinária 
        df_aux = (df1.loc[:,['cuisines','aggregate_rating']]
                     .groupby('cuisines')
                     .mean()
                     .sort_values('aggregate_rating', ascending=False).reset_index().head(10))
        df_aux = round(df_aux, 2)
        melhor_nota = df_aux.iloc[0,1]
        ajuda_html = f' Maior nota tipo Culinária conforme filtros realizados'
        col2.metric ( 'Nota Melhor Culinária', melhor_nota, help=ajuda_html)
    
    with col3:
        #Nome do tipo de culinária com a menor nota
        df_aux = (df1.loc[:,['cuisines','aggregate_rating']]
                     .groupby('cuisines')
                     .mean()
                     .sort_values('aggregate_rating', ascending=True).reset_index().head(10))
        pior = df_aux.iloc[0,0]
        col3.metric ( 'Pior Culinária', pior, help= "Nome tipo Culinária com a menor nota")
    
    with col4:
        #Menor nota do tipo de culinária
        df_aux = (df1.loc[:,['cuisines','aggregate_rating']]
                     .groupby('cuisines')
                     .mean()
                     .sort_values('aggregate_rating', ascending=True).reset_index().head(10))
        df_aux = round(df_aux, 2)
        pior_nota = df_aux.iloc[0,1]
        col4.metric ( 'Nota Pior Culinária', pior_nota, help='Menor nota tipo Culinária conforme filtros realizados')
    
      
        
st.container()    

st.write(f'## Top {qtde_rest} Restaurantes \n')

#INCLUSAO DO DATAFRAME
df_aux = (df1.loc[:,['restaurant_id', 'restaurant_name', 'country_code', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes' ]]
             .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
             .head(qtde_rest)
             .reset_index(drop=True))
st.dataframe(df_aux)     


st.container()
col6, col7 = st.columns(2)

with col6:
    #função para gerar o gráfico de barra do melhor tipo de culinárias
    
    fig = top_cuisines (df1, top_asc=False)
    st.plotly_chart (fig, use_container_width=True, theme='streamlit')
    
with col7:
    #função para gerar o gráfico de barra do pior tipo de culinárias
    fig = top_cuisines (df1, top_asc=True)
    st.plotly_chart (fig, use_container_width=True, theme='streamlit')
