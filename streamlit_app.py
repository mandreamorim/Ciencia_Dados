import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(layout="wide", page_title="Análise de Reclamações")

st.sidebar.title("Navegação")
aba_selecionada = st.sidebar.radio(
    "Escolha a Análise:",
    [
        "Evolução Temporal",
        "Distribuição Geográfica",
        "Distribuição Espacial",
        "Categorias Principais",
        "Status das Reclamações",
        "Eficiência de Resolução",
        "Análise Estatística de Textos",
        "Mineração de Texto"
    ]
)

with st.sidebar:
    # st.divider()
    # usar_fator_cumulativo = st.checkbox("Usar fator cumulativo (Casos por dia)", value=False)
    usar_fator_cumulativo = False


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    return data

def aplicar_filtros_globais(df):
    df = df.copy()

    df['DESCRICAO'] = df['DESCRICAO'].fillna('').astype(str)

    df['TAMANHO_TEXTO'] = df['DESCRICAO'].str.len()

    bins = [0, 100, 300, 600, float('inf')]
    labels = ['Curto (0-100)', 'Médio (101-300)', 'Longo (301-600)', 'Muito Longo (600+)']

    df['FAIXA_TEXTO'] = pd.cut(
        df['TAMANHO_TEXTO'],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    st.sidebar.markdown("## Filtros Globais")


    estados = sorted(df['ESTADO'].dropna().unique())
    estados_selecionados = st.sidebar.multiselect(
        "Estado",
        options=estados,
        default=estados
    )


    status_opcoes = sorted(df['STATUS'].dropna().unique())
    status_selecionados = st.sidebar.multiselect(
        "Status",
        options=status_opcoes,
        default=status_opcoes
    )

  
    faixas_texto = labels
    faixas_selecionadas = st.sidebar.multiselect(
        "Faixa de tamanho do texto",
        options=faixas_texto,
        default=faixas_texto
    )

    
    df_filtrado = df[
        (df['ESTADO'].isin(estados_selecionados)) &
        (df['STATUS'].isin(status_selecionados)) &
        (df['FAIXA_TEXTO'].astype(str).isin(faixas_selecionadas))
    ].copy()

    return df_filtrado


def main():
    df_raw = load_data('data/df_final.csv')
    df_filtrado_global = aplicar_filtros_globais(df_raw)

    if aba_selecionada == "Evolução Temporal":
        st.header("QA")
        render_temporal_analysis(df_filtrado_global)

    elif aba_selecionada == "Distribuição Geográfica":
        st.header("QA")
        render_geographical_heatmap(df_filtrado_global)
        
    elif aba_selecionada == "Distribuição Espacial":
        st.header("QA")
        render_pareto_estados(df_filtrado_global)

    elif aba_selecionada == "Categorias Principais":
        st.header("QA")
        render_filtered_segmented_analysis(df_filtrado_global)

    elif aba_selecionada == "Status das Reclamações":
        render_status_analysis(df_filtrado_global)

    elif aba_selecionada == "Eficiência de Resolução":
        st.header("TODO")
        render_efficiency_analysis(df_filtrado_global)

    elif aba_selecionada == "Análise Estatística de Textos":
        st.header("QA")
        render_statistical_textual_analysis(df_filtrado_global)
        
    elif aba_selecionada == "Mineração de Texto":
        st.header("WIP")
        render_textual_analysis(df_filtrado_global)


def render_status_analysis(df):
    st.subheader("Distribuição dos Status das Reclamações")

    # Excluimos
    # if usar_fator_cumulativo:
    #     # Usa o peso do campo CASOS_POR_DIA
    #     status_counts = df.groupby('STATUS')['CASOS_POR_DIA'].sum().reset_index()
    #     status_counts.columns = ['STATUS', 'Quantidade']
    #     label_analise = "Cumulativo (Casos por Dia)"
        
    #     # Para calcular resolvidas com peso
    #     resolvidas = df[df['STATUS'].str.contains('RESOLVIDO', case=False)]['CASOS_POR_DIA'].sum()
    # else:
    status_counts = df['STATUS'].value_counts().reset_index()
    status_counts.columns = ['STATUS', 'Quantidade']
    label_analise = "Frequência de Registros"
        
    resolvidas = df[df['STATUS'].str.contains('RESOLVIDO', case=False)].shape[0]

    total_reclamacoes = status_counts['Quantidade'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", int(total_reclamacoes))

    taxa_resolucao = (resolvidas / total_reclamacoes) * 100 if total_reclamacoes > 0 else 0

    col2.metric("Resolvidas", int(resolvidas))
    col3.metric("Taxa de Solução", f"{taxa_resolucao:.1f}%")

    st.markdown("---")
    

    fig = px.pie(
        status_counts,
        values='Quantidade',
        names='STATUS',
        hole=0.5,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Safe,
        title=f"Distribuição por Status - {label_analise}"
    )

    fig.update_layout(
        height=700,
        width=900
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Ver dados brutos de status ({label_analise})"):
        status_counts_display = status_counts.copy()
        status_counts_display['Quantidade'] = status_counts_display['Quantidade'].astype(int)
        st.table(status_counts_display.set_index('STATUS'))

def render_statistical_textual_analysis(df):
    st.header("Análise Estatística: Status vs. Tamanho do Texto")

    df = df.copy()

    df['DESCRICAO'] = df['DESCRICAO'].fillna('').astype(str)
    df['TAMANHO TEXTO'] = df['DESCRICAO'].str.len()

    bins = [0, 100, 300, 600, float('inf')]
    labels = [
        'Curto (0–100)',
        'Médio (101–300)',
        'Longo (301–600)',
        'Muito Longo (601+)'
    ]

    df['FAIXA TEXTO'] = pd.cut(
        df['TAMANHO TEXTO'],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

  
    total_registros = len(df)
    media_tamanho = df['TAMANHO TEXTO'].mean()
    mediana_tamanho = df['TAMANHO TEXTO'].median()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Reclamações", f"{total_registros:,}")
    col2.metric("Média de Caracteres", f"{media_tamanho:.0f}")
    col3.metric("Mediana de Caracteres", f"{mediana_tamanho:.0f}")

    st.markdown("---")

 
    st.subheader("Boxplot: Tamanho do Texto por Status")

    fig_box = px.box(
        df,
        x='STATUS',
        y='TAMANHO TEXTO',
        color='STATUS',
        points='outliers',
        title="Distribuição do Tamanho do Texto por Status",
        labels={
            'STATUS': 'Status',
            'TAMANHO TEXTO': 'Quantidade de Caracteres'
        },
        template="plotly_dark"
    )

    fig_box.update_layout(
        height=600,
        xaxis_tickangle=-35,
        showlegend=False
    )

    st.plotly_chart(fig_box, use_container_width=True)

    
    st.subheader("Status por Faixa de Tamanho do Texto (%)")

    cruzamento_desc_status = pd.crosstab(
        df['FAIXA TEXTO'],
        df['STATUS'],
        normalize='index'
    ) * 100

    cruzamento_desc_status = cruzamento_desc_status.reset_index()

    fig_stacked = px.bar(
        cruzamento_desc_status,
        x='FAIXA TEXTO',
        y=cruzamento_desc_status.columns[1:],
        title="Distribuição Percentual dos Status por Faixa de Texto",
        labels={
            'value': 'Percentual (%)',
            'FAIXA TEXTO': 'Faixa de Tamanho do Texto',
            'variable': 'Status'
        },
        template="plotly_dark"
    )

    fig_stacked.update_layout(
        barmode='stack',
        height=600,
        xaxis_tickangle=-20
    )

    st.plotly_chart(fig_stacked, use_container_width=True)

 
    st.subheader("Resumo Estatístico do Tamanho do Texto por Status")

    resumo_status = df.groupby('STATUS')['TAMANHO TEXTO'].agg([
        'count', 'mean', 'median', 'min', 'max'
    ]).reset_index()

    resumo_status.columns = [
        'Status', 'Quantidade', 'Média', 'Mediana', 'Mínimo', 'Máximo'
    ]

    resumo_status['Média'] = resumo_status['Média'].round(2)
    resumo_status['Mediana'] = resumo_status['Mediana'].round(2)

    st.dataframe(resumo_status, use_container_width=True, hide_index=True)


    with st.expander("Ver tabela percentual: Status vs. Faixa de Texto"):
        tabela_exibir = pd.crosstab(
            df['FAIXA TEXTO'],
            df['STATUS'],
            normalize='index'
        ) * 100

        st.dataframe(tabela_exibir.round(2), use_container_width=True)

def render_geographical_heatmap(df):
    st.header("Distribuição geográfica das reclamações")

    df = df.copy()
    df['DATA'] = pd.to_datetime(df['DATA'])

    tipo_filtro = st.selectbox(
        "Filtrar mapa por:",
        ["Ano", "Mês"]
    )

    if tipo_filtro == "Ano":
        anos_disponiveis = sorted(df['DATA'].dt.year.dropna().unique())
        ano_selecionado = st.selectbox("Selecione o ano:", anos_disponiveis)
        df_filtrado = df[df['DATA'].dt.year == ano_selecionado].copy()
        titulo_periodo = f"Ano {ano_selecionado}"

    else:
        meses_pt = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        df['ANO_MES'] = df['DATA'].dt.to_period('M')
        opcoes_mes = sorted(df['ANO_MES'].dropna().unique())

        opcoes_formatadas = {
            periodo: f"{meses_pt[periodo.month]}/{periodo.year}"
            for periodo in opcoes_mes
        }

        periodo_selecionado = st.selectbox(
            "Selecione o mês:",
            opcoes_mes,
            format_func=lambda x: opcoes_formatadas[x]
        )

        df_filtrado = df[df['ANO_MES'] == periodo_selecionado].copy()
        titulo_periodo = opcoes_formatadas[periodo_selecionado]

    if df_filtrado.empty:
        st.warning("Não há dados disponíveis para o período selecionado.")
        return


    todos_estados = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    df_base = pd.DataFrame({'id': todos_estados})

  
    if usar_fator_cumulativo:
        estado_counts = df_filtrado.groupby('ESTADO')['CASOS_POR_DIA'].sum().reset_index()
        label_analise = "Cumulativo (Casos por Dia)"
    else:
        estado_counts = df_filtrado['ESTADO'].value_counts().reset_index()
        label_analise = "Frequência de Registros"

    estado_counts.columns = ['id', 'total']
    estado_counts['log_total'] = np.log10(estado_counts['total'] + 1)

    estado_counts = pd.merge(df_base, estado_counts, on='id', how='left').fillna(0)

    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

    fig = px.choropleth(
        estado_counts,
        geojson=geojson_url,
        locations='id',
        featureidkey="properties.sigla",
        color='log_total',
        color_continuous_scale="Reds",
        hover_name='id',
        hover_data={'log_total': False, 'total': True},
        scope="south america",
        template="plotly_dark",
        title=f"Mapa de Calor - {label_analise} ({titulo_periodo})"
    )

    fig.update_geos(
        visible=False,
        fitbounds="locations",
        projection_type="mercator"
    )

    max_total = estado_counts['total'].max()

    fig.update_layout(
        height=700,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(
            title="Escala (Log)",
            tickvals=[np.log10(x) for x in [1, 10, 100, 1000] if x <= max_total and x > 0],
            ticktext=[str(x) for x in [1, 10, 100, 1000] if x <= max_total and x > 0]
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    df_sorted = estado_counts.sort_values(by='total', ascending=False)
    quantia_total = df_sorted['total'].sum()

    top_20_count = max(1, int(len(df_sorted) * 0.2))
    top_20_estados = df_sorted.head(top_20_count)

    soma_top_20 = top_20_estados['total'].sum()
    percentual_top_20 = (soma_top_20 / quantia_total) * 100 if quantia_total > 0 else 0

    if percentual_top_20 >= 80:
        st.error(
            f"**Aviso:** Os {top_20_count} estados com mais registros concentram "
            f"**{percentual_top_20:.1f}%** de todas as reclamações. "
            f"O volume está altamente centralizado."
        )

    st.markdown("---")

    df_top5 = df_sorted[['id', 'total']].copy()
    df_top5['total'] = df_top5['total'].astype(int)
    df_top5.columns = ['Estado', 'Quantidade']

    with st.expander(f"Contagem bruta por estado ({label_analise} - {titulo_periodo})"):
        st.table(df_top5.set_index('Estado'))

def render_pareto_estados(df):
    st.header("Distribuição Espacial - Pareto dos Estados")

    df = df.copy()
    df['DATA'] = pd.to_datetime(df['DATA'])

  
    tipo_filtro = st.selectbox(
        "Filtrar Pareto por:",
        ["Ano", "Mês"]
    )

    if tipo_filtro == "Ano":
        anos_disponiveis = sorted(df['DATA'].dt.year.dropna().unique())
        ano_selecionado = st.selectbox("Selecione o ano:", anos_disponiveis)
        df_filtrado = df[df['DATA'].dt.year == ano_selecionado].copy()
        titulo_periodo = f"Ano {ano_selecionado}"

    else:
        meses_pt = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        df['ANO_MES'] = df['DATA'].dt.to_period('M')
        opcoes_mes = sorted(df['ANO_MES'].dropna().unique())

        opcoes_formatadas = {
            periodo: f"{meses_pt[periodo.month]}/{periodo.year}"
            for periodo in opcoes_mes
        }

        periodo_selecionado = st.selectbox(
            "Selecione o mês:",
            opcoes_mes,
            format_func=lambda x: opcoes_formatadas[x]
        )

        df_filtrado = df[df['ANO_MES'] == periodo_selecionado].copy()
        titulo_periodo = opcoes_formatadas[periodo_selecionado]

    if df_filtrado.empty:
        st.warning("Não há dados disponíveis para o período selecionado.")
        return

  
    if usar_fator_cumulativo:
        estado_counts = df_filtrado.groupby('ESTADO')['CASOS_POR_DIA'].count().reset_index()
        label_analise = "Cumulativo (Casos por Dia)"
    else:
        estado_counts = df_filtrado['ESTADO'].value_counts().reset_index()
        label_analise = "Frequência de Registros"

    estado_counts.columns = ['id', 'total']

    df_pareto = estado_counts.copy()
    df_pareto = df_pareto[df_pareto['total'] > 0].copy()

    if df_pareto.empty:
        st.warning("Não há dados suficientes para gerar o gráfico de Pareto.")
        return


    df_pareto = df_pareto.sort_values(by='total', ascending=False).reset_index(drop=True)

    total_geral = df_pareto['total'].sum()
    df_pareto['percentual'] = (df_pareto['total'] / total_geral) * 100
    df_pareto['percentual_acumulado'] = df_pareto['percentual'].cumsum()

    estados_80 = df_pareto[df_pareto['percentual_acumulado'] <= 80]

    if len(estados_80) < len(df_pareto):
        estados_80 = df_pareto.iloc[:len(estados_80) + 1]

    estados_criticos = estados_80['id'].tolist()


    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_pareto['id'],
        y=df_pareto['total'],
        name='Quantidade',
        marker=dict(
            color=['crimson' if x in estados_criticos else 'indianred' for x in df_pareto['id']]
        ),
        hovertemplate='<b>%{x}</b><br>Quantidade: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_pareto['id'],
        y=df_pareto['percentual_acumulado'],
        name='% Acumulado',
        mode='lines+markers',
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        template="plotly_dark",
        title=f"Gráfico de Pareto - Estados Críticos ({label_analise} | {titulo_periodo})",
        height=650,
        margin=dict(t=60, b=40, l=40, r=40),
        xaxis=dict(
            title="Estado",
            tickangle=-45
        ),
        yaxis=dict(
            title="Quantidade de Reclamações",
            side='left'
        ),
        yaxis2=dict(
            title="Percentual Acumulado (%)",
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode="x unified"
    )

    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(df_pareto) - 0.5,
        y0=80,
        y1=80,
        xref="x",
        yref="y2",
        line=dict(dash="dash")
    )

    fig.add_annotation(
        x=df_pareto['id'].iloc[min(len(df_pareto)-1, 2)],
        y=78,
        text="80%",
        showarrow=False,
        yref="y2"
    )

    st.plotly_chart(fig, use_container_width=True)


    qtd_criticos = len(estados_criticos)
    perc_criticos = df_pareto[df_pareto['id'].isin(estados_criticos)]['percentual'].sum()

    st.info(
        f"**Estados críticos identificados pelo Pareto:** "
        f"Os **{qtd_criticos} estados mais críticos** concentram aproximadamente "
        f"**{perc_criticos:.1f}%** do total de reclamações em **{titulo_periodo}**."
    )

    with st.expander("Ver tabela de Pareto por estado"):
        df_exibir = df_pareto[['id', 'total', 'percentual', 'percentual_acumulado']].copy()
        df_exibir.columns = ['Estado', 'Quantidade', '% Individual', '% Acumulado']
        df_exibir['Quantidade'] = df_exibir['Quantidade'].astype(int)
        df_exibir['% Individual'] = df_exibir['% Individual'].round(2)
        df_exibir['% Acumulado'] = df_exibir['% Acumulado'].round(2)

        st.dataframe(df_exibir, use_container_width=True)

def render_temporal_analysis(df):
    st.header("Evolução Temporal de Reclamações")

    df = df.copy()
    df['DATA'] = pd.to_datetime(df['DATA'])

    df = df.groupby(df['DATA'].dt.date)['CASOS_POR_DIA'].count().reset_index()
    df['DATA'] = pd.to_datetime(df['DATA'])
    df = df.sort_values('DATA')

    todas_datas = pd.date_range(df['DATA'].min(), df['DATA'].max(), freq='D')
    df = (
        df.set_index('DATA')
          .reindex(todas_datas, fill_value=0)
          .rename_axis('DATA')
          .reset_index()
    )

    opcoes_janela = {
        "1 dia (Diário)": "1D",
        # "3 dias (Curto prazo)": "3D",
        "7 dias (Semanal)": "7D",
        "15 dias (Quinzena)": "15D",
        "Mensal": "MS"
    }

    label_selecionada = st.selectbox(
        "Selecione a janela de análise combinada:",
        list(opcoes_janela.keys()),
        index=2
    )

    frequencia = opcoes_janela[label_selecionada]

    
    if frequencia == "MS":
        ano_referencia = df['DATA'].dt.year.mode()[0]

        todos_meses = pd.date_range(
            start=f"{ano_referencia}-01-01",
            end=f"{ano_referencia}-12-01",
            freq="MS"
        )

        df_agregado = (
            df.set_index('DATA')
              .resample('MS')['CASOS_POR_DIA']
              .sum()
              .reindex(todos_meses, fill_value=0)
              .reset_index()
              .rename(columns={'index': 'DATA'})
        )
    else:
        df_agregado = (
            df.set_index('DATA')
              .resample(frequencia)['CASOS_POR_DIA']
              .sum()
              .reset_index()
        )

 
    df_agregado = df_agregado[df_agregado['CASOS_POR_DIA'] > 0].copy()

    if df_agregado.empty:
        st.warning("Não há dados positivos para exibir nessa agregação.")
        return

  
    if frequencia == "MS":
        meses_pt = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        df_agregado['ROTULO_X'] = df_agregado['DATA'].dt.month.map(meses_pt)
        titulo_y = "Reclamações por Mês"

    elif frequencia == "1D":
        df_agregado['ROTULO_X'] = df_agregado['DATA'].dt.strftime('%d/%m')
        titulo_y = "Reclamações por Dia"

    else:
        df_agregado['ROTULO_X'] = df_agregado['DATA'].dt.strftime('%d/%m')
        titulo_y = f"Reclamações por período ({label_selecionada})"

    if frequencia == "MS":
        tickvals = df_agregado['DATA']
        ticktext = df_agregado['ROTULO_X']
    else:
        max_rotulos = 12
        total_pontos = len(df_agregado)

        if total_pontos <= max_rotulos:
            tickvals = df_agregado['DATA']
            ticktext = df_agregado['ROTULO_X']
        else:
            indices = np.linspace(0, total_pontos - 1, max_rotulos, dtype=int)
            tickvals = df_agregado.iloc[indices]['DATA']
            ticktext = df_agregado.iloc[indices]['ROTULO_X']


    pico_row = df_agregado.loc[df_agregado['CASOS_POR_DIA'].idxmax()]
    data_pico = pico_row['DATA']
    total_pico = int(pico_row['CASOS_POR_DIA'])

    fig = px.line(
        df_agregado,
        x='DATA',
        y='CASOS_POR_DIA',
        markers=True,
        labels={
            'DATA': 'Período',
            'CASOS_POR_DIA': titulo_y
        },
        template="plotly_dark"
    )

    fig.update_layout(
        height=500,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        hovermode="x unified"
    )

    fig.update_xaxes(
        title="Períodos do Ano",
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        gridcolor='rgba(255,255,255,0.1)'
    )

    fig.update_yaxes(
        title=titulo_y,
        gridcolor='rgba(255,255,255,0.1)'
    )

    st.plotly_chart(fig, use_container_width=True)

    if frequencia == "MS":
        meses_pt_extenso = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        mes_nome = meses_pt_extenso[data_pico.month]

        st.info(
            f"**Mês com maior volume:** "
            f"{mes_nome}/{data_pico.year} "
            f"registrou **{total_pico}** reclamações."
        )

    elif frequencia == "1D":
        st.info(
            f"**Dia com maior volume:** "
            # f"{data_pico.strftime('%d/%m/%Y')} "
            f"registrou **{total_pico}** reclamações."
        )

    else:
        st.info(
            f"**Maior volume em {label_selecionada}:** "
            f"registrou **{total_pico}** reclamações agregadas."
        )

    with st.expander("Ver tabela agregada"):
        st.dataframe(df_agregado, use_container_width=True)

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

    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Contagem ({label_analise}) por categoria"):
        st.table(cat_counts.set_index('Categoria'))

def render_textual_analysis(df):

    textos = df['DESCRICAO'].dropna().astype(str)
    texto_completo = " ".join(textos).lower()

  
    stopwords_pt = set([
        "a", "e", "o", "que", "de", "do", "da", "em", "um", "para", "é", "com",
        "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos",
        "como", "mas", "foi", "ao", "ele", "das", "tem", "à", "seu", "sua",
        "ou", "ser", "quando", "muito", "há", "nos", "já", "está", "eu",
        "também", "só", "pelo", "pela", "até", "isso", "ela", "entre", "era",
        "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me",
        "esse", "eles", "estão", "você", "tinha", "foram", "essa", "num",
        "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas",
        "este", "esta", "estes", "estas", "aquele", "aquela", "isto", "aquilo", "outro", "tive", "hoje", "aqui", "bem", "porém", "hora", "sendo","vez", "r", "casa", "agora", "lá", "onde", "são", "veze", "toda", "nao", "estou", "assim", "outra", "dado", "data",
        "meus", "dia", "vou", "seria", "momento", "fui", "pra", "mail", "qual", "fiz", "coisa", "sou", "havia", "pois", "estava"
    ])

    stopwords_pt.update(["pão", "açúcar", "pao", "acucar", "cliente", "loja", "pedido", "reclame"])

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='black',  
        colormap='Reds',  
        stopwords=stopwords_pt,
        max_words=100,
        collocations=False  
    ).generate(texto_completo)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor='black')
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")  

    st.pyplot(fig)


def render_efficiency_analysis(df):
    st.header("Eficiência de Resolução por Categoria")

    st.markdown("""
    Análise do **percentual de reclamações resolvidas por categoria**, 
    avaliando a eficiência da empresa na solução de diferentes tipos de problemas.
    """)

    df_copy = df.copy()
    df_copy['CATEGORIA'] = df_copy['CATEGORIA'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x
    )

    df_copy['RESOLVIDO'] = df_copy['STATUS'].str.contains('RESOLVIDO', case=False, na=False).astype(int)

    if usar_fator_cumulativo:
        label_analise = "Cumulativo (Casos por Dia)"
        df_copy['PESO'] = df_copy['CASOS_POR_DIA']
    else:
        label_analise = "Frequência de Registros"
        df_copy['PESO'] = 1

    df_copy['PESO_RESOLVIDO'] = df_copy['PESO'] * df_copy['RESOLVIDO']

    df_exploded = df_copy.explode('CATEGORIA')

    categorias_para_descartar = ['PÃO DE AÇÚCAR']
    df_filtrado = df_exploded[~df_exploded['CATEGORIA'].str.upper().isin(categorias_para_descartar)]

    cat_total = df_filtrado.groupby('CATEGORIA')['PESO'].sum()
    cat_resolvidas = df_filtrado.groupby('CATEGORIA')['PESO_RESOLVIDO'].sum()

    eficiencia = pd.DataFrame({
        'Total': cat_total,
        'Resolvidas': cat_resolvidas
    }).fillna(0)

    eficiencia['Não Resolvidas'] = eficiencia['Total'] - eficiencia['Resolvidas']
    eficiencia['Taxa de Resolução (%)'] = (eficiencia['Resolvidas'] / eficiencia['Total'] * 100).round(2)

    eficiencia = eficiencia.sort_values('Total', ascending=False).head(15)

    col1, col2, col3 = st.columns(3)

    total_geral = eficiencia['Total'].sum()
    resolvidas_geral = eficiencia['Resolvidas'].sum()
    taxa_geral = (resolvidas_geral / total_geral * 100) if total_geral > 0 else 0

    col1.metric("Total Analisado", f"{int(total_geral):,}")
    col2.metric("Resolvidas", f"{int(resolvidas_geral):,}")
    col3.metric("Taxa de Resolução", f"{taxa_geral:.1f}%")

    st.markdown("---")

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