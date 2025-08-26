import streamlit as st
import pandas as pd
from dotenv import load_dotenv

import os

load_dotenv()

st.set_page_config(layout="wide")
st.title("Visualizador de Planilhas")

st.markdown("""
    Insira o link de compartilhamento da sua planilha do Google Sheets.
    
    Apenas URLs no formato TSV (separado por tabulação) são suportados.
""")

link_planilha = os.getenv("GSpage")

st.write(link_planilha)

if link_planilha:
    try:
        df = pd.read_csv(link_planilha, sep='\t', on_bad_lines='skip', decimal=",")
        st.success("Planilha carregada com sucesso!")
        
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar a planilha. Verifique o link e se a planilha está pública. Erro: {e}")