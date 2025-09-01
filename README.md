# Liaan Core

## Sobre o Projeto

**Liaan Core** é uma aplicação web simples e intuitiva, desenvolvida com Streamlit, para gerenciar e agendar o uso de PCs. Com uma interface visual baseada em "cards", o aplicativo permite que você visualize o status de cada máquina (disponível, ocupada, em manutenção) e agende períodos de uso de forma rápida e eficiente.

---

## Funcionalidades Principais

* **Cards de PCs**: Crie e visualize cards para cada PC, mostrando informações como URL, nome e GPU.
* **Gestão de Status**: O status de cada PC é atualizado visualmente através de cores:
    * **Verde**: PC disponível.
    * **Amarelo**: Agendamento próximo (menos de 1 hora).
    * **Vermelho**: PC ocupado no momento.
    * **Azul**: PC em manutenção.
* **Agendamento Inteligente**: Agende períodos de uso com data e hora de início e fim. O sistema previne agendamentos no passado ou que entrem em conflito com agendamentos existentes.
* **Persistência de Dados**: Os dados dos cards são salvos localmente em um arquivo JSON, garantindo que as informações persistam mesmo após o fechamento da aplicação.
* **Visualizador de Planilhas**: Uma página secundária permite carregar e visualizar dados diretamente de uma planilha do Google Sheets (formato TSV).

---

## Como Rodar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o Python 3.9 ou superior instalado.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/MapeamentoLIAAN.git](https://github.com/SEU_USUARIO/MapeamentoLIAAN.git)
    cd MapeamentoLIAAN
    ```

2.  **Crie e ative um ambiente virtual (opcional, mas recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    (Se você não tiver o arquivo `requirements.txt`, crie um com `pip freeze > requirements.txt`).

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```

O aplicativo será aberto automaticamente em seu navegador padrão.

---

## Estrutura do Repositório

* `app.py`: O arquivo principal da aplicação com a página de gerenciamento de PCs.
* `pages/`: Pasta que contém as páginas adicionais da aplicação.
    * `1_planilhas.py`: A página para o visualizador de planilhas.
* `card.py`: O arquivo que define a classe `PC_Card`.
* `pcs_data.json`: O arquivo onde os dados dos PCs são armazenados.
* `requirements.txt`: Lista de bibliotecas Python necessárias.

---
