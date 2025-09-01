import streamlit as st

import datetime
import json
import os
import pytz

from card import PC_Card 
from functions import *

DATA_FILE = "pcs_data.json"

st.set_page_config(layout="wide")
st.title("Gerenciamento de PCs")

if "pcs" not in st.session_state:
    st.session_state.pcs = carregar_dados()
if "mostrar_form_agendar" not in st.session_state:
    st.session_state.mostrar_form_agendar = False

# --- EXIBIÇÃO DOS CARDS ---
st.header("Cards de PCs")
if not st.session_state.pcs:
    st.info("Nenhum PC cadastrado ainda. Use o formulário acima para adicionar um.")
else:
    num_cards = len(st.session_state.pcs)
    for i in range(0, num_cards, 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < num_cards:
                with cols[j]:
                    pc = st.session_state.pcs[i + j]
                    
                    # Defina o fuso horário uma única vez
                    fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
                    agora = datetime.datetime.now(fuso_horario_brasil)

                    cor, status_text = "green", "Disponível"
                    if pc.em_manutencao:
                        cor = "blue"
                        status_text = "Em Manutenção"
                    else:
                        cor_status, status_info = pc.esta_ocupado(agora)

                        if cor_status == "ocupado":
                            cor = "red"
                            status_text = "Ocupado agora"
                        elif cor_status == "quase_ocupado":
                            cor = "yellow"
                            status_text = status_info
                        else: # "disponivel"
                            cor = "green"
                            if status_info == "N/A":
                                status_text = "Disponível"
                            else:
                                status_text = status_info

                    card_style = f"background-color: {cor}; padding: 15px; border-radius: 10px; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px; color: black;"

                    st.markdown(
                        f"""
                        <div style='{card_style}'>
                            <div>
                                <h4>{pc.nome}</h4>
                                <p><strong>URL:</strong> {pc.url}</p>
                                <p><strong>GPU:</strong> {pc.gpu}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    
                    with st.container():
                        st.markdown(f"**Status:** {status_text}")
                        
                        st.markdown("**Próximos Agendamentos:**")
                        if pc.agendamentos:
                            for inicio, fim in pc.agendamentos:
                                st.markdown(f"- **Início:** {inicio.strftime('%d/%m %H:%M')} | **Fim:** {fim.strftime('%d/%m %H:%M')}")
                        else:
                            st.markdown("Nenhum agendamento futuro.")
                        
                        st.checkbox("Em Manutenção", value=pc.em_manutencao, key=f"manutencao_{i+j}", on_change=toggle_manutencao, args=(i+j,))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            with st.popover("Agendar Uso", help="Clique para agendar um período de uso."):
                                st.markdown(f"**Agendando para:** {pc.nome}")
                                
                                with st.form(key=f"form_agendar_{i+j}", clear_on_submit=False):
                                    col_form1, col_form2 = st.columns(2)
                                    with col_form1:
                                        data_inicio = st.date_input("Data de Início", key=f"data_inicio_form_{i+j}", value=datetime.date.today())
                                        hora_inicio = st.time_input("Hora de Início", key=f"hora_inicio_form_{i+j}", value=datetime.time(9, 0))
                                    with col_form2:
                                        data_fim = st.date_input("Data de Fim", key=f"data_fim_form_{i+j}", value=datetime.date.today())
                                        hora_fim = st.time_input("Hora de Fim", key=f"hora_fim_form_{i+j}", value=datetime.time(17, 0))

                                    confirmar_btn = st.form_submit_button("Confirmar Agendamento")
                                    
                                    if confirmar_btn:
                                        data_hora_inicio = datetime.datetime.combine(data_inicio, hora_inicio)
                                        data_hora_fim = datetime.datetime.combine(data_fim, hora_fim)
                                        
                                        # Use a variável 'agora' do fuso horário definido
                                        if data_hora_inicio < agora.replace(tzinfo=None): # Remove o tzinfo para comparar com um datetime naive
                                            st.error("Não é possível agendar uma data no passado.")
                                            conflito = True
                                        elif data_hora_inicio >= data_hora_fim:
                                            st.error("A data e hora de início devem ser anteriores à data e hora de fim.")
                                            conflito = True
                                        else:
                                            conflito = False
                                            for inicio_existente, fim_existente in pc.agendamentos:
                                                if not (data_hora_fim <= inicio_existente or data_hora_inicio >= fim_existente):
                                                    st.error("O agendamento se sobrepõe a um agendamento existente.")
                                                    conflito = True
                                                    break

                                        if not conflito:
                                            pc.agendar_uso(data_hora_inicio, data_hora_fim)
                                            salvar_dados(st.session_state.pcs)
                                            st.success(f"Agendamento para **{pc.nome}** confirmado de {data_hora_inicio.strftime('%d/%m/%Y %H:%M')} a {data_hora_fim.strftime('%d/%m/%Y %H:%M')}!")
                                            st.rerun()