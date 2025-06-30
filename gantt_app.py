import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from io import BytesIO
import os
import numpy as np
import calendar
import colorsys

# Configuração da página
st.set_page_config(
    page_title="Gráfico de Gantt Interativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para salvar o gráfico em HTML
def salvar_html(fig):
    buffer = BytesIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    html_bytes = buffer.getvalue()
    return html_bytes

# Função para calcular o progresso
def calcular_progresso(etapas):
    hoje = date.today()
    total_etapas = len(etapas)
    if total_etapas == 0:
        return 0
    
    progresso_total = 0.0
    
    for etapa in etapas:
        # Etapas concluídas
        if hoje > etapa["Fim"]:
            progresso_total += 1.0
        # Etapas em andamento
        elif etapa["Início"] <= hoje <= etapa["Fim"]:
            # Calcular progresso proporcional
            duracao = (etapa["Fim"] - etapa["Início"]).days
            dias_passados = (hoje - etapa["Início"]).days
            if duracao > 0:
                progresso_parcial = min(1.0, dias_passados / duracao)
                progresso_total += progresso_parcial
    
    return (progresso_total / total_etapas) * 100  # Converter para porcentagem

# Gerar paleta de cores única para cada etapa (sem matplotlib)
def gerar_paleta_cores(n):
    # Paleta de cores base
    cores_base = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    if n <= len(cores_base):
        return cores_base[:n]
    
    # Gerar cores adicionais usando HSL
    cores = []
    for i in range(n):
        # Variar matiz (hue) uniformemente
        h = i / n
        # Converter HSL para RGB
        r, g, b = colorsys.hls_to_rgb(h, 0.5, 0.8)
        cores.append(f'rgb({int(r*255)},{int(g*255)},{int(b*255)})')
    
    return cores

# Converter data no formato dd.mm.yy para date
def parse_data(data_str):
    try:
        dia, mes, ano = data_str.split('.')
        ano_completo = int(ano) + 2000 if int(ano) < 100 else int(ano)
        return date(ano_completo, int(mes), int(dia))
    except:
        return None

# Calendário visual com cores específicas
def criar_calendario(etapas):
    if not etapas:
        return None
    
    # Encontrar datas mínima e máxima
    datas_inicio = [e["Início"] for e in etapas]
    datas_fim = [e["Fim"] for e in etapas]
    data_min = min(datas_inicio)
    data_max = max(datas_fim)
    
    # Criar dataframe com todos os dias do período
    todos_dias = pd.date_range(start=data_min, end=data_max)
    df_calendario = pd.DataFrame({"Data": todos_dias})
    
    # Gerar paleta de cores para etapas
    cores_etapas = gerar_paleta_cores(len(etapas))
    
    # Para cada dia, determinar quais etapas estão ativas
    for i, etapa in enumerate(etapas):
        df_calendario[f"Etapa_{i}"] = df_calendario["Data"].apply(
            lambda d: etapa["Início"] <= d.date() <= etapa["Fim"]
        )
    
    return df_calendario, cores_etapas

# Formatar data no estilo dd.mm.yy
def formatar_data(dt):
    return dt.strftime("%d.%m.%y")

# Inicialização do estado da sessão
if 'etapas' not in st.session_state:
    st.session_state.etapas = []

# Barra lateral
with st.sidebar:
    st.title("Gerenciamento de Projetos")
    
    # Logo opcional
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.info("Logo não encontrada. Adicione 'logo.png' no diretório do aplicativo.")
    
    # Instruções
    st.markdown("---")
    st.info("**Instruções:**")
    st.markdown("1. Preencha os detalhes da etapa")
    st.markdown("2. Use datas no formato dd.mm.aa (ex: 15.07.25)")
    st.markdown("3. Visualize o gráfico de Gantt")
    st.markdown("4. Salve o cronograma em HTML")
    
    # Barra de progresso na sidebar
    if st.session_state.etapas:
        progresso = calcular_progresso(st.session_state.etapas)
        st.markdown("---")
        st.subheader("Progresso do Projeto")
        st.progress(progresso / 100)
        st.caption(f"Progresso atual: {progresso:.1f}%")

# Título principal
st.title("📊 Cronograma de Projeto - Gráfico de Gantt Interativo")
st.subheader("Planejamento e Acompanhamento de Atividades")

# Barra de progresso principal
if st.session_state.etapas:
    progresso = calcular_progresso(st.session_state.etapas)
    st.subheader(f"Progresso Geral: {progresso:.1f}%")
    st.progress(progresso / 100)

# Seção para imagem do fluxograma (opcional)
fluxograma_path = "fluxograma.png"
if os.path.exists(fluxograma_path):
    st.markdown("---")
    st.header("Fluxograma do Processo")
    st.image(fluxograma_path, use_column_width=True)
    st.caption("Diagrama do fluxo de trabalho do projeto")

# Formulário para adicionar etapas com formato dd.mm.yy
st.markdown("---")
st.header("Adicionar Nova Etapa")

with st.form("etapa_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        etapa = st.text_input("Descrição da Etapa*", placeholder="Ex: Desenvolvimento do protótipo", key="etapa_desc")
        responsaveis = st.text_input("Responsável(is)*", placeholder="Ex: João Silva, Maria Santos", key="etapa_resp")
    with col2:
        data_inicio_str = st.text_input("Data de Início* (dd.mm.aa)", value=date.today().strftime("%d.%m.%y"), key="etapa_inicio")
        data_fim_str = st.text_input("Data de Término* (dd.mm.aa)", value=date.today().strftime("%d.%m.%y"), key="etapa_fim")
    
    observacoes = st.text_area("Observações Adicionais", placeholder="Detalhes importantes sobre a etapa...", key="etapa_obs")
    
    submitted = st.form_submit_button("Adicionar Etapa")
    if submitted:
        if not etapa or not responsaveis:
            st.error("Preencha os campos obrigatórios (*)")
        else:
            data_inicio = parse_data(data_inicio_str)
            data_fim = parse_data(data_fim_str)
            
            if not data_inicio or not data_fim:
                st.error("Formato de data inválido! Use dd.mm.aa (ex: 15.07.25)")
            elif data_inicio > data_fim:
                st.error("A data de início não pode ser posterior à data de término!")
            else:
                nova_etapa = {
                    "Etapa": etapa,
                    "Responsável": responsaveis,
                    "Início": data_inicio,
                    "Fim": data_fim,
                    "Observações": observacoes
                }
                st.session_state.etapas.append(nova_etapa)
                st.success("Etapa adicionada com sucesso!")
                st.rerun()

# Lista de etapas existentes
st.markdown("---")
st.header("Etapas do Projeto")

if not st.session_state.etapas:
    st.info("Nenhuma etapa adicionada ainda. Comece preenchendo o formulário acima.")
else:
    # Opção para limpar todas as etapas
    if st.button("🗑️ Limpar Todas as Etapas", type="primary", key="limpar_todas"):
        st.session_state.etapas = []
        st.success("Todas as etapas foram removidas!")
        st.rerun()
    
    st.markdown("---")
    
    # Exibir etapas com botões de remoção individuais
    for i, etapa in enumerate(st.session_state.etapas):
        with st.container():
            cols = st.columns([0.9, 0.1])
            
            with cols[0]:
                st.subheader(f"Etapa {i+1}: {etapa['Etapa']}")
                st.markdown(f"**Responsável:** {etapa['Responsável']}")
                st.markdown(f"**Período:** {etapa['Início'].strftime('%d.%m.%y')} - {etapa['Fim'].strftime('%d.%m.%y')}")
                if etapa['Observações']:
                    st.markdown(f"**Observações:** {etapa['Observações']}")
                
                # Status da etapa
                hoje = date.today()
                if hoje > etapa["Fim"]:
                    status = "✅ Concluída"
                elif etapa["Início"] <= hoje <= etapa["Fim"]:
                    # Calcular progresso individual
                    duracao = (etapa["Fim"] - etapa["Início"]).days
                    dias_passados = (hoje - etapa["Início"]).days
                    progresso_etapa = min(100, int((dias_passados / duracao) * 100)) if duracao > 0 else 0
                    status = f"⏳ Em Andamento ({progresso_etapa}%)"
                else:
                    status = "⏱️ Pendente"
                
                st.markdown(f"**Status:** {status}")
            
            with cols[1]:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.etapas.pop(i)
                    st.success(f"Etapa '{etapa['Etapa']}' removida com sucesso!")
                    st.rerun()
            
            st.markdown("---")
    
    # Indicador de status baseado na data
    hoje = date.today()
    st.subheader("Status Geral das Etapas")
    
    status_cols = st.columns(3)
    with status_cols[0]:
        st.metric("Total de Etapas", len(st.session_state.etapas))
    
    concluidas = sum(1 for e in st.session_state.etapas if hoje > e["Fim"])
    with status_cols[1]:
        st.metric("Etapas Concluídas", concluidas)
    
    em_andamento = sum(1 for e in st.session_state.etapas if e["Início"] <= hoje <= e["Fim"])
    with status_cols[2]:
        st.metric("Etapas em Andamento", em_andamento)
    
    # Gerar e mostrar gráfico de Gantt com barras
    st.markdown("---")
    st.header("Visualização do Cronograma")
    
    try:
        # Criar DataFrame para o gráfico
        df_gantt = pd.DataFrame(st.session_state.etapas)
        
        # Converter datas para datetime
        df_gantt["Início"] = pd.to_datetime(df_gantt["Início"])
        df_gantt["Fim"] = pd.to_datetime(df_gantt["Fim"])
        
        # Calcular datas mínima e máxima para o eixo x
        data_min = df_gantt["Início"].min() - timedelta(days=3)
        data_max = df_gantt["Fim"].max() + timedelta(days=3)
        
        # Converter para timestamps numéricos (milissegundos)
        df_gantt["Início_ts"] = df_gantt["Início"].astype('int64') // 10**6
        df_gantt["Fim_ts"] = df_gantt["Fim"].astype('int64') // 10**6
        
        # Gerar paleta de cores única para cada etapa
        cores = gerar_paleta_cores(len(df_gantt))
        
        # Criar gráfico de Gantt com barras
        fig = go.Figure()
        
        # Adicionar uma barra para cada etapa
        for i, row in df_gantt.iterrows():
            fig.add_trace(go.Bar(
                y=[row["Etapa"]],
                x=[row["Fim_ts"] - row["Início_ts"]],
                base=row["Início_ts"],
                orientation='h',
                name=row["Etapa"],
                marker_color=cores[i],
                hoverinfo='text',
                hovertext=f"<b>{row['Etapa']}</b><br>"
                          f"Início: {formatar_data(row['Início'])}<br>"
                          f"Fim: {formatar_data(row['Fim'])}<br>"
                          f"Responsável: {row['Responsável']}"
            ))
        
        fig.update_layout(
            barmode='stack',
            title="Cronograma do Projeto",
            height=500,
            hovermode="closest",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title="Linha do Tempo",
                type="date",
                range=[data_min, data_max],
                tickformat="%d.%m.%y"
            ),
            yaxis=dict(
                autorange="reversed",
                title=""
            )
        )
        
        # Adicionar linha para data atual
        fig.add_vline(
            x=pd.to_datetime(hoje).value // 10**6,
            line_dash="dash",
            line_color="red",
            annotation_text="Hoje",
            annotation_position="top right"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Criar calendário visual
        st.markdown("---")
        st.header("Calendário de Execução")
        
        df_calendario, cores_etapas = criar_calendario(st.session_state.etapas)
        
        if df_calendario is not None:
            # Agrupar por ano e mês
            df_calendario["Ano"] = df_calendario["Data"].dt.year
            df_calendario["Mês"] = df_calendario["Data"].dt.month
            df_calendario["Dia"] = df_calendario["Data"].dt.day
            df_calendario["Dia_Semana"] = df_calendario["Data"].dt.dayofweek
            
            meses = df_calendario.groupby(["Ano", "Mês"])
            
            for (ano, mes), grupo in meses:
                st.subheader(f"{calendar.month_name[mes]} {ano}")
                
                # Cabeçalho com dias da semana
                dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
                cols = st.columns(7)
                for i, dia in enumerate(dias_semana):
                    cols[i].write(f"**{dia}**")
                
                # Encontrar primeiro dia do mês
                primeiro_dia = grupo.iloc[0]["Data"]
                dia_semana = primeiro_dia.weekday()
                
                # Criar grid de calendário
                grid = st.columns(7)
                celula_idx = 0
                
                # Espaços vazios para dias antes do primeiro dia do mês
                for _ in range(dia_semana):
                    with grid[celula_idx % 7]:
                        st.write("")
                    celula_idx += 1
                
                # Preencher os dias do mês
                for _, row in grupo.iterrows():
                    # Verificar quantas etapas estão ativas neste dia
                    etapas_ativas = []
                    for i in range(len(st.session_state.etapas)):
                        if row[f"Etapa_{i}"]:
                            etapas_ativas.append(i)
                    
                    with grid[celula_idx % 7]:
                        if etapas_ativas:
                            # Calcular progresso médio ponderado
                            progressos = []
                            for i in etapas_ativas:
                                etapa = st.session_state.etapas[i]
                                duracao = (etapa["Fim"] - etapa["Início"]).days
                                dias_passados = (row["Data"].date() - etapa["Início"]).days
                                progresso = min(1.0, dias_passados / duracao) if duracao > 0 else 0
                                progressos.append(progresso)
                            
                            progresso_medio = np.mean(progressos) * 100
                            
                            # Criar círculo com cores mescladas
                            if len(etapas_ativas) == 1:
                                # Apenas uma etapa - cor sólida
                                st.markdown(
                                    f'<div style="display: flex; justify-content: center;">'
                                    f'<div style="border-radius: 50%; width: 35px; height: 35px; '
                                    f'background-color: {cores_etapas[etapas_ativas[0]]}; display: flex; align-items: center; '
                                    f'justify-content: center; color: white; font-weight: bold; border: 2px solid #555;">'
                                    f'{row["Dia"]}'
                                    f'</div></div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                # Múltiplas etapas - criar gradiente
                                gradiente = "conic-gradient("
                                angulo = 0
                                for i, idx in enumerate(etapas_ativas):
                                    porcentagem = progressos[i] * 100
                                    gradiente += f"{cores_etapas[idx]} {angulo}deg {angulo + porcentagem * 3.6}deg, "
                                    angulo += porcentagem * 3.6
                                gradiente = gradiente.rstrip(", ") + ")"
                                
                                st.markdown(
                                    f'<div style="display: flex; justify-content: center;">'
                                    f'<div style="border-radius: 50%; width: 35px; height: 35px; '
                                    f'background: {gradiente}; display: flex; align-items: center; '
                                    f'justify-content: center; color: black; font-weight: bold; border: 2px solid #555;">'
                                    f'{row["Dia"]}'
                                    f'</div></div>',
                                    unsafe_allow_html=True
                                )
                            
                            # Tooltip com progresso
                            st.caption(f"{progresso_medio:.0f}%")
                        else:
                            # Dia sem etapas
                            st.markdown(
                                f'<div style="display: flex; justify-content: center;">'
                                f'<div style="border-radius: 50%; width: 35px; height: 35px; '
                                f'background-color: #f0f0f0; display: flex; align-items: center; '
                                f'justify-content: center; color: #999; font-weight: bold; border: 2px solid #ddd;">'
                                f'{row["Dia"]}'
                                f'</div></div>',
                                unsafe_allow_html=True
                            )
                    
                    celula_idx += 1
        
        # Opções para salvar
        st.markdown("---")
        st.header("Exportar Cronograma")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_projeto = st.text_input("Nome do Projeto", placeholder="Ex: Projeto Alpha", key="nome_projeto")
            nome_arquivo = st.text_input("Nome do Arquivo HTML", placeholder="Ex: cronograma_projeto", key="nome_arquivo")
        
        with col2:
            st.markdown("")
            st.markdown("")
            if st.button("Salvar Gráfico como HTML"):
                if not nome_arquivo:
                    st.warning("Digite um nome para o arquivo")
                else:
                    html_bytes = salvar_html(fig)
                    st.download_button(
                        label="Baixar Arquivo HTML",
                        data=html_bytes,
                        file_name=f"{nome_arquivo}.html",
                        mime="text/html"
                    )
        
        st.info("O arquivo HTML gerado pode ser aberto em qualquer navegador e contém o gráfico interativo.")
    
    except Exception as e:
        st.error(f"Erro ao gerar o gráfico: {str(e)}")

# Rodapé
st.markdown("---")
st.caption("© 2025 Gestão de Projetos - Todos os direitos reservados | v1.0")