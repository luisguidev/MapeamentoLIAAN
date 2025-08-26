import streamlit as st
import datetime
import json
import os
from card import PC_Card # Certifique-se de que a classe PC_Card está neste arquivo ou importada corretamente

# --- FUNÇÕES DE PERSISTÊNCIA ---
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

# --- FUNÇÕES AUXILIARES PARA MANIPULAÇÃO ---
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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide")
st.title("Gerenciamento de PCs")

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "pcs" not in st.session_state:
    st.session_state.pcs = carregar_dados()
if "mostrar_form_agendar" not in st.session_state:
    st.session_state.mostrar_form_agendar = False

# --- INTERFACE DE CRIAÇÃO ---
with st.expander("Adicionar Novo PC"):
    with st.form("form_novo_pc", clear_on_submit=True):
        url = st.text_input("URL do PC")
        nome = st.text_input("Nome do PC")
        gpu = st.text_input("GPU")
        submit_button = st.form_submit_button("Criar Card")

    if submit_button and nome:
        adicionar_pc(url, nome, gpu)
        st.success(f"PC '{nome}' adicionado com sucesso!")
        st.rerun()

st.markdown("---")

# --- FORMULÁRIO DE AGENDAMENTO (CONDICIONAL) ---
placeholder_agendamento = st.empty()
if st.session_state.mostrar_form_agendar:
    with placeholder_agendamento.container():
        st.markdown("### Agendar Uso")
        pc_index = st.session_state.agendando_pc_indice
        pc_selecionado = st.session_state.pcs[pc_index]
        
        with st.form(key=f"form_agendar_{pc_index}", clear_on_submit=False):
            st.markdown(f"**Agendando para:** {pc_selecionado.nome}")
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data de Início", key=f"data_inicio_form_{pc_index}", value=datetime.date.today())
                hora_inicio = st.time_input("Hora de Início", key=f"hora_inicio_form_{pc_index}", value=datetime.time(9, 0))
            with col2:
                data_fim = st.date_input("Data de Fim", key=f"data_fim_form_{pc_index}", value=datetime.date.today())
                hora_fim = st.time_input("Hora de Fim", key=f"hora_fim_form_{pc_index}", value=datetime.time(17, 0))

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                confirmar_btn = st.form_submit_button("Confirmar Agendamento")
            with col_btn2:
                cancelar_btn = st.form_submit_button("Cancelar")

            if confirmar_btn:
                data_hora_inicio = datetime.datetime.combine(data_inicio, hora_inicio)
                data_hora_fim = datetime.datetime.combine(data_fim, hora_fim)
                
                if data_hora_inicio >= data_hora_fim:
                    st.error("A data e hora de início devem ser anteriores à data e hora de fim.")
                else:
                    pc_selecionado.agendar_uso(data_hora_inicio, data_hora_fim)
                    salvar_dados(st.session_state.pcs)
                    st.success(f"Agendamento para **{pc_selecionado.nome}** confirmado de {data_hora_inicio.strftime('%d/%m/%Y %H:%M')} a {data_hora_fim.strftime('%d/%m/%Y %H:%M')}!")
                    fechar_form_agendar()
                    st.rerun()
            
            if cancelar_btn:
                fechar_form_agendar()
                st.rerun()

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
                    
                    cor = "green"
                    if pc.em_manutencao:
                        cor = "blue"
                    elif pc.esta_ocupado() == "ocupado":
                        cor = "red"
                    elif pc.esta_ocupado() == "quase_ocupado":
                        cor = "yellow"

                    card_style = f"background-color: {cor}; padding: 15px; border-radius: 10px; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px;"

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
                        st.markdown(f"**Status:** {'Em Manutenção' if pc.em_manutencao else 'Disponível'}")
                        
                        if pc.data_ocupado:
                            inicio = pc.data_ocupado[0].strftime('%d/%m/%Y %H:%M')
                            fim = pc.data_ocupado[1].strftime('%d/%m/%Y %H:%M')
                            st.markdown(f"**Próximo Agendamento:**")
                            st.markdown(f"**Início:** {inicio}")
                            st.markdown(f"**Fim:** {fim}")
                        else:
                            st.markdown("**Próximo Agendamento:** N/A")
                        
                        st.checkbox("Em Manutenção", value=pc.em_manutencao, key=f"manutencao_{i+j}", on_change=toggle_manutencao, args=(i+j,))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Agendar Uso", key=f"agenda_{i+j}"):
                                abrir_form_agendar(i+j)
                                st.rerun()
                        with col_btn2:
                            if st.button("Deletar", key=f"delete_{i+j}"):
                                deletar_pc(i+j)