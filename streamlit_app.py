import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import ast
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(layout="wide", page_title="Análise de Reclamações")

# Sidebar - Navegação
st.sidebar.title("Navegação")
aba_selecionada = st.sidebar.radio(
    "Escolha a Análise:",
    [
        "Evolução Temporal",
        "Distribuição Geográfica",
        "Categorias Principais",
        "Status das Reclamações",
        "Eficiência de Resolução",
        "Análise de Texto"
    ]
)

with st.sidebar:
    st.divider()
    usar_fator_cumulativo = st.checkbox("Usar fator cumulativo (Casos por dia)", value=True)


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    return data


# --- LÓGICA DE PROCESSAMENTO ---
def process_data(df):
    # Insira aqui suas transformações, limpeza e engenharia de features
    return df


# --- INTERFACE DO USUÁRIO (UI) ---
def main():
    df_raw = load_data('data/df_final.csv')

    if aba_selecionada == "Evolução Temporal":
        st.header("QA")
        render_temporal_analysis(df_raw)

    elif aba_selecionada == "Distribuição Geográfica":
        st.header("QA")
        render_geographical_heatmap(df_raw)

    elif aba_selecionada == "Categorias Principais":
        st.header("QA")
        render_filtered_segmented_analysis(df_raw)

    elif aba_selecionada == "Status das Reclamações":
        render_status_analysis(df_raw)

    elif aba_selecionada == "Eficiência de Resolução":
        st.header("TODO")
        render_efficiency_analysis(df_raw)

    elif aba_selecionada == "Análise de Texto":
        st.header("WIP")
        render_textual_analysis(df_raw)


def render_status_analysis(df):
    st.subheader("Distribuição dos Status das Reclamações")

    # Determina o tipo de contagem baseado na checkbox
    if usar_fator_cumulativo:
        # Usa o peso do campo CASOS_POR_DIA
        status_counts = df.groupby('STATUS')['CASOS_POR_DIA'].sum().reset_index()
        status_counts.columns = ['STATUS', 'Quantidade']
        label_analise = "Cumulativo (Casos por Dia)"
        
        # Para calcular resolvidas com peso
        resolvidas = df[df['STATUS'].str.contains('RESOLVIDO', case=False)]['CASOS_POR_DIA'].sum()
    else:
        # Considera apenas a frequência (peso 1 por registro)
        status_counts = df['STATUS'].value_counts().reset_index()
        status_counts.columns = ['STATUS', 'Quantidade']
        label_analise = "Frequência de Registros"
        
        # Para calcular resolvidas por frequência
        resolvidas = df[df['STATUS'].str.contains('RESOLVIDO', case=False)].shape[0]

    total_reclamacoes = status_counts['Quantidade'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", int(total_reclamacoes))

    taxa_resolucao = (resolvidas / total_reclamacoes) * 100 if total_reclamacoes > 0 else 0

    col2.metric("Resolvidas", int(resolvidas))
    col3.metric("Taxa de Solução", f"{taxa_resolucao:.1f}%")

    st.markdown("---")

    # Gráfico de Rosca
    fig = px.pie(
        status_counts,
        values='Quantidade',
        names='STATUS',
        hole=0.5,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Safe,
        title=f"Distribuição por Status - {label_analise}"
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada opcional
    with st.expander(f"Ver dados brutos de status ({label_analise})"):
        status_counts_display = status_counts.copy()
        status_counts_display['Quantidade'] = status_counts_display['Quantidade'].astype(int)
        st.table(status_counts_display.set_index('STATUS'))

def render_geographical_heatmap(df):
    st.header("Distribuição geográfica das reclamações")

    todos_estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR',
                     'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    df_base = pd.DataFrame({'id': todos_estados})

    # Determina o tipo de contagem baseado na checkbox
    if usar_fator_cumulativo:
        # Usa o peso do campo CASOS_POR_DIA
        estado_counts = df.groupby('ESTADO')['CASOS_POR_DIA'].sum().reset_index()
        label_analise = "Cumulativo (Casos por Dia)"
    else:
        # Considera apenas a frequência (peso 1 por registro)
        estado_counts = df['ESTADO'].value_counts().reset_index()
        label_analise = "Frequência de Registros"
    
    estado_counts.columns = ['id', 'total']

    estado_counts['log_total'] = np.log10(estado_counts['total'] + 1)

    estado_counts = pd.merge(df_base, estado_counts, on='id', how='left').fillna(0)

    # 2. URL do GeoJSON do Brasil (Estados)
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

    fig = px.choropleth(
        estado_counts,
        geojson=geojson_url,
        locations='id',
        featureidkey="properties.sigla",
        color='log_total',  # Usamos o log para a cor
        color_continuous_scale="Reds",
        hover_name='id',
        hover_data={'log_total': False, 'total': True},
        scope="south america",
        template="plotly_dark",
        title=f"Mapa de Calor - {label_analise}"
    )

    fig.update_geos(
        visible=False,
        fitbounds="locations",
        projection_type="mercator"
    )

    fig.update_layout(
        height=700,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(
            title="Escala (Log)",
            tickvals=[np.log10(x) for x in [1, 10, 100, 1000] if x <= estado_counts['total'].max()],
            ticktext=[str(x) for x in [1, 10, 100, 1000] if x <= estado_counts['total'].max()]
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    df_sorted = estado_counts.sort_values(by='total', ascending=False)
    quantia_total = df_sorted['total'].sum()

    top_20_count = int(len(df_sorted) * 0.2)
    top_20_estados = df_sorted.head(top_20_count)

    soma_top_20 = top_20_estados['total'].sum()
    percentual_top_20 = (soma_top_20 / quantia_total) * 100

    if percentual_top_20 >= 80:
        st.error(
            f"**Aviso:** Os {top_20_count} estados com mais registros concentram **{percentual_top_20:.1f}%** de todas as reclamações. O volume está altamente centralizado.")

    st.markdown("---")


    df_top5 = df_sorted[['id', 'total']].copy()
    df_top5['total'] = df_top5['total'].astype(int)
    df_top5.columns = ['Estado', 'Quantidade']

    with st.expander(f"Contagem bruta por estado ({label_analise})"):
        st.table(df_top5.set_index('Estado'))

def render_temporal_analysis(df):
    st.header("Evolução Temporal de Reclamações")

    df['DATA'] = pd.to_datetime(df['DATA'])
    df = df.sort_values('DATA')

    fig = px.line(
        df,
        x='DATA',
        y='CASOS_POR_DIA',
        labels={'DATA': 'Data', 'CASOS_POR_DIA': 'Nº de Reclamações'},
        template="plotly_dark",
        markers=True
    )

    fig.update_layout(
        height=500,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        hovermode="x unified"
    )

    fig.update_xaxes(title="Período Analisado", gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title="Volume Diário", gridcolor='rgba(255,255,255,0.1)')

    st.plotly_chart(fig, use_container_width=True)

    opcoes_janela = {
        "3 dias (Curto prazo)": 3,
        "7 dias (Semanal)": 7,
        "15 dias (Quinzena)": 15,
        "30 dias (Mensal)": 30
    }
    label_selecionada = st.selectbox("Selecione a janela de análise combinada:", list(opcoes_janela.keys()), index=1)
    n_dias = opcoes_janela[label_selecionada]

    df = df.sort_values('DATA')
    df['SOMA_MOVEL'] = df['CASOS_POR_DIA'].rolling(window=n_dias).sum()

    pico_row = df.nlargest(1, 'SOMA_MOVEL').iloc[0]
    data_fim = pico_row['DATA']
    data_inicio = data_fim - pd.Timedelta(days=n_dias - 1)
    total_periodo = int(pico_row['SOMA_MOVEL'])

    st.info(
        f"**Período Crítico ({n_dias} dias):** {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} "
        f"concentrou **{total_periodo}** reclamações combinadas."
    )

def render_filtered_segmented_analysis(df):
    st.header("Segmentação de Categorias Relevantes")

    df_copy = df.copy()

    df_copy['CATEGORIA'] = df_copy['CATEGORIA'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x
    )

    df_exploded = df_copy.explode('CATEGORIA')

    categorias_para_descartar = ['PÃO DE AÇÚCAR']

    df_filtrado = df_exploded[~df_exploded['CATEGORIA'].str.upper().isin(categorias_para_descartar)]

    if usar_fator_cumulativo:
        cat_counts = df_filtrado.groupby('CATEGORIA')['CASOS_POR_DIA'].sum().reset_index()
        label_analise = "Cumulativo"
    else:
        cat_counts = df_filtrado['CATEGORIA'].value_counts().reset_index()
        label_analise = "Frequência de registros"

    cat_counts.columns = ['Categoria', 'Total']
    cat_counts['Total'] = cat_counts['Total'].astype(int)

    cat_counts = cat_counts.sort_values(by='Total', ascending=False)
    top_10 = cat_counts.head(10)

    fig = px.bar(
        top_10,
        x='Total',
        y='Categoria',
        orientation='h',
        text_auto=True,
        title=f"Categorias: {label_analise}",
        color='Total',
        color_continuous_scale="Reds",
        template="plotly_dark"
    )
    # --- FIM DO TRECHO ALTERADO ---

    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Contagem ({label_analise}) por categoria"):
        st.table(cat_counts.set_index('Categoria'))

def render_textual_analysis(df):

    # 1. Tratamento de dados nulos e concatenação do texto
    textos = df['DESCRICAO'].dropna().astype(str)
    texto_completo = " ".join(textos).lower()

    # 2. Definição de Stopwords em Português
    stopwords_pt = set([
        "a", "e", "o", "que", "de", "do", "da", "em", "um", "para", "é", "com",
        "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos",
        "como", "mas", "foi", "ao", "ele", "das", "tem", "à", "seu", "sua",
        "ou", "ser", "quando", "muito", "há", "nos", "já", "está", "eu",
        "também", "só", "pelo", "pela", "até", "isso", "ela", "entre", "era",
        "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me",
        "esse", "eles", "estão", "você", "tinha", "foram", "essa", "num",
        "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas",
        "este", "esta", "estes", "estas", "aquele", "aquela", "isto", "aquilo"
    ])

    # Opcional: Adicionar termos genéricos do seu negócio que sujam a análise
    stopwords_pt.update(["pão", "açúcar", "pao", "acucar", "cliente", "loja", "pedido", "reclame"])

    # 3. Geração da Nuvem de Palavras
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='black',  # Combina com o plotly_dark
        colormap='Reds',  # Mantém a paleta de cores consistente
        stopwords=stopwords_pt,
        max_words=100,
        collocations=False  # Evita duplicidade de palavras compostas
    ).generate(texto_completo)

    # 4. Renderização no Streamlit via Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='black')
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")  # Remove os eixos do gráfico

    st.pyplot(fig)


def render_efficiency_analysis(df):
    st.header("Eficiência de Resolução por Categoria")

    st.markdown("""
    Análise do **percentual de reclamações resolvidas por categoria**, 
    avaliando a eficiência da empresa na solução de diferentes tipos de problemas.
    """)

    # Preparar dados
    df_copy = df.copy()
    df_copy['CATEGORIA'] = df_copy['CATEGORIA'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x
    )

    # Criar coluna binária para "resolvido" ANTES da explosão
    df_copy['RESOLVIDO'] = df_copy['STATUS'].str.contains('RESOLVIDO', case=False, na=False).astype(int)

    # Determina o peso baseado na checkbox ANTES da explosão
    if usar_fator_cumulativo:
        label_analise = "Cumulativo (Casos por Dia)"
        df_copy['PESO'] = df_copy['CASOS_POR_DIA']
    else:
        label_analise = "Frequência de Registros"
        df_copy['PESO'] = 1

    # Calcular peso resolvido (PESO * RESOLVIDO)
    df_copy['PESO_RESOLVIDO'] = df_copy['PESO'] * df_copy['RESOLVIDO']

    # AGORA explode as categorias
    df_exploded = df_copy.explode('CATEGORIA')

    # Filtrar categorias irrelevantes
    categorias_para_descartar = ['PÃO DE AÇÚCAR']
    df_filtrado = df_exploded[~df_exploded['CATEGORIA'].str.upper().isin(categorias_para_descartar)]

    # Agregar por categoria
    cat_total = df_filtrado.groupby('CATEGORIA')['PESO'].sum()
    cat_resolvidas = df_filtrado.groupby('CATEGORIA')['PESO_RESOLVIDO'].sum()

    # Criar DataFrame com as estatísticas
    eficiencia = pd.DataFrame({
        'Total': cat_total,
        'Resolvidas': cat_resolvidas
    }).fillna(0)

    eficiencia['Não Resolvidas'] = eficiencia['Total'] - eficiencia['Resolvidas']
    eficiencia['Taxa de Resolução (%)'] = (eficiencia['Resolvidas'] / eficiencia['Total'] * 100).round(2)

    # Ordenar por total e pegar top 15
    eficiencia = eficiencia.sort_values('Total', ascending=False).head(15)

    # Métricas gerais
    col1, col2, col3 = st.columns(3)

    total_geral = eficiencia['Total'].sum()
    resolvidas_geral = eficiencia['Resolvidas'].sum()
    taxa_geral = (resolvidas_geral / total_geral * 100) if total_geral > 0 else 0

    col1.metric("Total Analisado", f"{int(total_geral):,}")
    col2.metric("Resolvidas", f"{int(resolvidas_geral):,}")
    col3.metric("Taxa de Resolução", f"{taxa_geral:.1f}%")

    st.markdown("---")

    # Gráfico de Taxa de Resolução
    fig = px.bar(
        eficiencia.reset_index(),
        x='Taxa de Resolução (%)',
        y='CATEGORIA',
        orientation='h',
        title=f"Taxa de Resolução por Categoria (Top 15) - {label_analise}",
        labels={'Taxa de Resolução (%)': 'Taxa de Resolução (%)', 'CATEGORIA': 'Categoria'},
        color='Taxa de Resolução (%)',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        template="plotly_dark",
        text='Taxa de Resolução (%)',
        hover_data={'Total': ':,.0f', 'Resolvidas': ':,.0f'}
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=600,
        xaxis_range=[0, 105]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada
    st.markdown("---")
    with st.expander(f"Ver tabela completa ({label_analise})"):
        tabela_display = eficiencia.copy()
        tabela_display['Total'] = tabela_display['Total'].astype(int)
        tabela_display['Resolvidas'] = tabela_display['Resolvidas'].astype(int)
        tabela_display['Não Resolvidas'] = tabela_display['Não Resolvidas'].astype(int)

        st.dataframe(
            tabela_display.style.background_gradient(
                subset=['Taxa de Resolução (%)'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ).format({
                'Total': '{:,.0f}',
                'Resolvidas': '{:,.0f}',
                'Não Resolvidas': '{:,.0f}',
                'Taxa de Resolução (%)': '{:.2f}%'
            }),
            use_container_width=True
        )


if __name__ == "__main__":
    main()