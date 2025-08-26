import os
import json
import streamlit as st

from card import PC_Card

DATA_FILE = "pcs_data.json"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                return [PC_Card.from_dict(item) for item in data]
            except (json.JSONDecodeError, KeyError):
                return []
    return []

def salvar_dados(pcs):
    with open(DATA_FILE, "w") as f:
        json.dump([pc.to_dict() for pc in pcs], f, indent=4)


def adicionar_pc(url, nome, gpu):
    novo_pc = PC_Card(url, nome, gpu)
    st.session_state.pcs.append(novo_pc)
    salvar_dados(st.session_state.pcs)

def deletar_pc(indice):
    del st.session_state.pcs[indice]
    salvar_dados(st.session_state.pcs)
    st.rerun()

def toggle_manutencao(indice):
    st.session_state.pcs[indice].em_manutencao = not st.session_state.pcs[indice].em_manutencao
    salvar_dados(st.session_state.pcs)

def abrir_form_agendar(indice):
    st.session_state.agendando_pc_indice = indice
    st.session_state.mostrar_form_agendar = True

def fechar_form_agendar():
    st.session_state.mostrar_form_agendar = False