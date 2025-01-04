import streamlit as st
import pandas as pd
import altair as alt

# Título do app
st.title("Indicadores de Dados de Entregas")

# Opção para carregar uma base de dados (CSV ou Excel)
uploaded_file = st.file_uploader("Carregue sua base de dados (CSV ou Excel)", type=["csv", "xlsx"])

# Inicialização do DataFrame
df = None

# Carregar os dados
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]

    # Leitura da base de dados dependendo da extensão
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == 'xlsx':
        df = pd.read_excel(uploaded_file)

    st.write("Dados Carregados:")
    st.write(df)
else:
    st.write("Nenhum arquivo carregado. Por favor, carregue uma planilha.")

# Verifica se o DataFrame foi carregado corretamente antes de realizar qualquer operação
if df is not None:
    # Garantir que as colunas de data estejam no formato datetime
    df['DATA DO ACIONAMENTO'] = pd.to_datetime(df['DATA DO ACIONAMENTO'], errors='coerce')
    df['DATA REAL DA COLETA'] = pd.to_datetime(df['DATA REAL DA COLETA'], errors='coerce')
    df['DATA PROGRAMADA DA ENTREGA'] = pd.to_datetime(df['DATA PROGRAMADA DA ENTREGA'], errors='coerce')
    df['DATA REAL DE ENTREGA'] = pd.to_datetime(df['DATA REAL DE ENTREGA'], errors='coerce')
    df['DATA REPROGRAMAÇÃO'] = pd.to_datetime(df['DATA REPROGRAMAÇÃO'], errors='coerce')
    df['DATA DE ENTREGA DA REVERSA'] = pd.to_datetime(df['DATA DE ENTREGA DA REVERSA'], errors='coerce')

    # Substituindo valores nulos ou ausentes nas colunas de data
    df.fillna(method='ffill', inplace=True)

    # Adicionar coluna 'VALOR NF' e calcular o total
    if 'VALOR NF' not in df.columns:
        df['VALOR NF'] = 0  # Caso a coluna não exista, criar com valor 0
    df['VALOR NF'] = df['VALOR NF'].fillna(0)  # Substituindo valores ausentes por 0
    total_valor_nf = df['VALOR NF'].sum()

    # Sidebar com opções de navegação
    option = st.sidebar.selectbox(
        "Selecione o gráfico para visualizar",
        ("Status de Entrega", "SLA de Entrega", "Quantidade de Reserva Pedido ao Longo do Tempo", "Análise de Atrasos")
    )

    # Cores solicitadas para o gráfico de Status de Entrega
    color_map_status = {
        'CANCELADO': '#808080',    # cinza escuro
        'COLETADO': '#D3D3D3',     # cinza claro
        'CONCLUÍDO': '#A9A9A9',    # cinza médio
        'EXTRAVIO': '#8B0000',     # vermelho escuro
        'IMPRODUTIVA': '#D60000',  # vermelho claro
    }

    # Gráficos baseados na seleção do usuário
    if option == "SLA de Entrega":
        st.header("SLA de Entrega: Dentro do Prazo vs Fora do Prazo")

        # Dados para o gráfico de SLA
        sla_data = {
            'Status SLA': ['No Prazo', 'Fora do Prazo'],
            'Qtd': [3703, 5],
            'Porcentagem': ['99,87%', '0,13%']
        }
        sla_df = pd.DataFrame(sla_data)

        # Gráfico de pizza para SLA
        fig_sla_pizza = alt.Chart(sla_df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Qtd", type="quantitative"),
            color=alt.Color(field="Status SLA", type="nominal", scale=alt.Scale(domain=['No Prazo', 'Fora do Prazo'], range=['#808080', '#8B0000'])),
            tooltip=['Status SLA', 'Qtd', 'Porcentagem']
        ).properties(title='Classificação de Entregas (Dentro vs Fora do Prazo)')
        st.altair_chart(fig_sla_pizza, use_container_width=True)

        st.write("""
            O gráfico de pizza mostra a distribuição das entregas dentro e fora do prazo. 
            A grande maioria das entregas estão dentro do prazo ('No Prazo'), representando 99,87% do total, 
            enquanto uma pequena fração está fora do prazo ('Fora do Prazo'), com apenas 0,13%.
        """)

    elif option == "Status de Entrega":
        st.header("Análise de Status de Entrega")
        
        # Dados para o gráfico de Status de Entrega
        status_data = {
            'Status de Entrega': ['CANCELADO', 'COLETADO', 'CONCLUÍDO', 'EXTRAVIO', 'IMPRODUTIVA'],
            'Qtd': [3, 211, 3437, 21, 36],
            'Porcentagem': ['0,08%', '5,69%', '92,69%', '0,57%', '0,97%']
        }
        status_df = pd.DataFrame(status_data)

        # Gráfico de barras para Status de Entrega
        fig_status = alt.Chart(status_df).mark_bar().encode(
            x=alt.X('Status de Entrega', sort='-y'),
            y='Qtd',
            color=alt.Color('Status de Entrega', scale=alt.Scale(domain=['CANCELADO', 'COLETADO', 'CONCLUÍDO', 'EXTRAVIO', 'IMPRODUTIVA'], range=['#808080', '#D3D3D3', '#A9A9A9', '#8B0000', '#D60000'])),
            tooltip=['Status de Entrega', 'Qtd', 'Porcentagem']
        ).properties(title='Distribuição do Status da Entrega')
        st.altair_chart(fig_status, use_container_width=True)

        st.write("""
            O gráfico de barras mostra a quantidade de entregas em cada status. A categoria 'Concluído' é a mais predominante, 
            com 92,69% das entregas, seguida por 'Coletado' com 5,69%. 'Extravio', 'Improdutiva' e 'Cancelado' têm pequenas 
            quantidades em comparação com as demais.
        """)

    elif option == "Quantidade de Reserva Pedido ao Longo do Tempo":
        st.header("Quantidade de Reserva Pedido ao Longo do Tempo")

        # Garantir que as datas estejam no formato correto
        df['Data do Acionamento'] = pd.to_datetime(df['DATA DO ACIONAMENTO'], errors='coerce')

        # Contagem de reservas por data
        reservas_por_data = df.groupby(df['Data do Acionamento'].dt.date).size().reset_index(name='Quantidade')

        # Gráfico de linha para quantidade de reservas
        fig_reservas = alt.Chart(reservas_por_data).mark_line().encode(
            x='Data do Acionamento:T',
            y='Quantidade:Q',
            color=alt.value('#A9A9A9')
        ).properties(title='Quantidade de Reserva Pedido ao Longo do Tempo')
        st.altair_chart(fig_reservas, use_container_width=True)

        st.write("""
            O gráfico de linha mostra a evolução das reservas ao longo do tempo, utilizando a cor cinza. 
            É possível observar as variações nas quantidades de pedidos e identificar picos e quedas nas reservas.
        """)

    # Conclusão
    st.header("Conclusão")
    st.write("""
        A análise realizada fornece insights sobre o status das entregas. 
        O gráfico de pizza mostra que a maioria das entregas estão no status 'Concluído', 
        com uma pequena quantidade nas categorias 'Coletado', 'Improdutiva', 'Extravio' e 'Cancelado'. 
        O gráfico de barras complementa essas informações, oferecendo uma visão clara da quantidade de entregas por status.
        Além disso, a análise da quantidade de reservas ao longo do tempo mostra as flutuações nas reservas, 
        permitindo entender melhor o comportamento ao longo do período.
    """)

    # Exibição do valor total
    st.write(f"**Valor Total das Notas Fiscais (VALOR NF): R$ {total_valor_nf:.2f}**")
