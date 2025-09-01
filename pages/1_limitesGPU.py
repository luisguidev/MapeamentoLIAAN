import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Visualizador de Planilhas")


link_planilha = st.secrets["GSpage"]

if link_planilha:
    try:
        df = pd.read_csv(link_planilha, sep='\t', on_bad_lines='skip', decimal=",")
        st.success("Planilha carregada com sucesso!")
        
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar a planilha. Verifique o link e se a planilha está pública. Erro: {e}")