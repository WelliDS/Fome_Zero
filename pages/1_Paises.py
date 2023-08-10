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



st.set_page_config (page_title = 'Países', page_icon='🌎', layout='wide')

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


def number_restaurants_country(df1):
#Função que retorna Gráfico de barras que com a quantidade de restaurantes registrados por país
    df_aux = (df1.loc[:,['country_code','restaurant_id']]
                     .groupby('country_code')
                     .nunique()
                     .sort_values('restaurant_id',ascending=False).reset_index())
    fig = (px.bar(df_aux, x='country_code', y='restaurant_id', title='Quantidade de Restaurantes Registrados por País',
            text_auto=True,
            labels={'restaurant_id':'Quantidade de restaurantes',
                   'country_code' : 'País'}))
       
    fig.update_layout(title_x=0.3)
    fig.update_layout(title_font_color='black')

    fig.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)
    return fig


def number_city_per_country(df1):
#Função que retorna Gráfico de barras que com a quantidade de cidades registradas por país
    
    df_aux = df1.loc[:,['city','country_code']].groupby('country_code').nunique().sort_values('city', ascending=False).reset_index()

    fig2 = (px.bar(df_aux, x='country_code', y='city', title='Quantidade de Cidades Registradas por País',
            text_auto=True,
             labels={'restaurant_id':'Quantidade de restaurantes',
                     'city':'Quantidade de Cidades',
                    'country_code' : 'País'}))
       
    fig2.update_layout(title_x=0.3)
    fig2.update_layout(title_font_color='black')

    fig2.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)
    return fig2


def avg_votes_per_country(df1):
#Função que retorna Gráfico de barras na 1ª coluna com a média de avaliações registradas por país
        
    df_aux = (df1.loc[:,['country_code', 'votes']]
                     .groupby('country_code').mean()
                     .sort_values('votes', ascending=False).reset_index())
    df_aux = round(df_aux,2)
    fig = (px.bar(df_aux, x='country_code', y='votes', title='Média de Avaliações feitas por País',
            text_auto=True,
             labels={'votes':'Quantidade de Avaliações',
                    'country_code' : 'País'}))
       
    fig.update_layout(title_x=0.2)
    fig.update_layout(title_font_color='black')

    fig.update_traces(textfont_size=10, textangle=1, textposition="outside", cliponaxis=False)
    return fig

    
def avg_cost_two_per_country (df1):
#Função que retorna Gráfico de barras na 1ª coluna com a média de valor de prato para dois registradas por país

    df_aux = (df1.loc[:,['country_code','average_cost_for_two','currency']]
                     .groupby('country_code')
                     .agg({'average_cost_for_two': 'mean', 'currency': 'first'})
                     .sort_values('average_cost_for_two', ascending=False).reset_index())

    df_aux = round(df_aux, 2)
    
    fig = (px.bar(df_aux, x='country_code', y='average_cost_for_two', title='Média de Preço de um Prato para Duas Pessoas Por País',
            text_auto=True, text= 'currency',
             labels={'average_cost_for_two':'Preço de Prato para Duas Pessoas',
                    'country_code' : 'País',
                    'currency': 'Moeda'}))
       
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



st.sidebar.markdown( """---""" )
st.sidebar.markdown( '#### Powered by Wellington Silva' )
                                           
#Filtro de Condição de Trânsito
linhas_selecionadas = df1['country_code'].isin (country_options)
df1 = df1.loc[linhas_selecionadas, :]                                       
                                           

# =======================================
# Layout no Streamlit
# =======================================

st.header( ' 🌎 Visão Países' )


st.container()

#Gráfico de barras com o número de restaurantes por país
fig = number_restaurants_country(df1)
st.plotly_chart (fig, use_container_width=True, theme='streamlit')


st.container()

#Gráfico de barras com o número de cidades registradas por país

fig2 = number_city_per_country(df1)
st.plotly_chart (fig2, use_container_width=True, theme='streamlit')


st.container()
col1, col2 = st.columns(2)

with col1: 
    
#Gráfico de barras na 1ª coluna com a média de avaliações registradas por país
    fig = avg_votes_per_country(df1)
    st.plotly_chart (fig, use_container_width=True, theme='streamlit')
            
with col2:
    
#Gráfico de barras na 2ª coluna com a média de Preço de Prato para Duas Pessoas registradas por país
    fig = avg_cost_two_per_country (df1)
    st.plotly_chart (fig, use_container_width=True, theme='streamlit')   
    