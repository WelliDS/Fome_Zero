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




st.set_page_config ( page_title = "Home", page_icon="🏠", layout='wide', initial_sidebar_state='auto')


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





# ============================================
# REALIZANDO A LIMPEZA DO DATAFRAME
# ============================================

df1 = clean_code (df)

# ============================================
# Barra Lateral
# ============================================



col1, col2 = st.sidebar.columns([1, 3])

image_path=('fome_zero_logo.png')
image = Image.open( image_path )
col1.image( image, width=35) 


col2.write ('# Fome Zero')


st.sidebar.markdown ('# Filtros')

default_options = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
country_options = st.sidebar.multiselect ('Escolha os Paises que Deseja visualizar as Informações:',
                                           df1['country_code'].unique(), default=default_options)


st.sidebar.write ('### Dados Tratados')


@st.cache_data
def convert_df(df1):
    # Função para converter o dataframe em um arquivo CSV
    return df1.to_csv().encode('utf-8')

csv = convert_df(df1)


st.sidebar.download_button(
    label="Download",
    data=csv,
    file_name='dados.csv',
    mime='text/csv')



st.sidebar.markdown( """---""" )
st.sidebar.markdown( '#### Powered by Wellington Silva' )
                                           
#Filtro de Condição de Trânsito
linhas_selecionadas = df1['country_code'].isin (country_options)
df1 = df1.loc[linhas_selecionadas, :]                                       
                                           

# =======================================
# Layout no Streamlit
# =======================================


st.title( ' 🍴 Fome Zero!' )
st.markdown (' ## O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.markdown ('### Temos as seguintes marcas dentro da nossa plataforma:')

st.container()

        
col1, col2, col3, col4, col5 = st.columns (5, gap='small')

with st.container():
    with col1:
        #Quantidade de restaurantes cadastrados
        df_aux = df1.loc[:, ['restaurant_id']].count()
        col1.metric ( label='Restaurantes Cadastrados', value=df_aux, help='Quantidade Restaurantes conforme filtro')
    
    with col2:
        #Quantidade de países 
        df_aux = df1.loc[:,'country_code'].nunique()
        col2.metric ( label='Países Selecionados', value=df_aux, help='Quantidade de Países conforme filtro')
    
    with col3:
        #Quantidade de cidades
        df_aux = df1.loc[:, 'city'].nunique()
        col3.metric ( label='Cidades Cadastradas', value=df_aux, help='Quantidade de Cidades conforme filtro')
    
    with col4:
        #Quantidade de Avaliações feitas na plataforma
        df_aux = df1.loc[:,'votes'].sum()
        locale.setlocale(locale.LC_ALL, '')
        df_aux = locale.format_string('%d', df_aux, grouping=True)
        col4.metric ( label='Avaliações na Plataforma', value=df_aux, help='Qtde Avaliações conforme filtro')
        
    with col5:
        #Quantidade de tipos de culinárias feitas na plataforma
        df_aux = df1.loc[:,'cuisines'].nunique()
        col5.metric ( label='Tipos de Culinárias Oferecidas', value=df_aux, help='Qtde Avaliações conforme filtro')
        

st.container()
st.write ('### 🌎 Mapa com a Localização dos restaurantes')

df_aux = (df1.loc[:, ['city', 'aggregate_rating', 'currency', 'cuisines', 'color_name', 'restaurant_id','latitude', 'longitude', 'average_cost_for_two', 'restaurant_name']]
             .groupby(['city', 'cuisines','color_name', 'currency', 'restaurant_id', 'restaurant_name'])
             .median().reset_index())


map1 = folium.Map()
marker_cluster = folium.plugins.MarkerCluster().add_to(map1)

                    
for i in range ( len (df_aux) ):
    popup_html = f'<div style="width: 250px;">' \
                 f"<b>{df_aux.loc[i, 'restaurant_name']}</b><br><br>" \
                 \
                 f"Preço para dois: {df_aux.loc[i, 'average_cost_for_two']:.2f} ( {df_aux.loc[i, 'currency']})<br> " \
                 f"Type: {df_aux.loc[i, 'cuisines']}<br>" \
                 f"Nota: {df_aux.loc[i, 'aggregate_rating']}/5.0" \
                 f'</div>'
    folium.Marker ([df_aux.loc[i, 'latitude'], df_aux.loc[i, 'longitude']],
                   popup=popup_html, width=500, height=500, tooltip='clique aqui', parse_html=True,  
                   zoom_start=30, tiles= 'Stamen Toner', 
                   icon=folium.Icon(color=df_aux.loc[i, 'color_name'] , icon='home')).add_to(marker_cluster)
    
folium_static(map1)