import streamlit as st
import pandas as pd
import plotly.express as px
from datos import CANDIDATOS, PREGUNTAS

st.set_page_config(page_title="Match Electoral UC", page_icon="🗳️", layout="centered")

st.title("🗳️ Match Electoral UC - CT Ingeniería")
st.markdown("Descubre qué candidato se alinea mejor con tus ideas mediante votación ciega.")

# 1. ESTADO DE LA APLICACIÓN
cargo = "CT Ingeniería"
preguntas_cargo = PREGUNTAS[cargo]
ejes_unicos = list(set([p['eje'] for p in preguntas_cargo]))

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {}

st.divider()

# 2. RENDERIZAR PREGUNTAS
for i, p in enumerate(preguntas_cargo):
    st.subheader(f"📌 {p['eje']}")
    st.write(p['pregunta'])
    
    opciones_texto = [op['texto'] for op in p['opciones']]
    
    seleccion = st.radio(
        "Tu preferencia:",
        opciones_texto,
        key=f"q_{i}",
        index=None
    )
    st.session_state.respuestas[i] = seleccion
    st.divider()

# 3. EL SEGUNDO FILTRO (Ponderación)
st.subheader("⭐ Segundo Filtro: Tus Prioridades")
st.markdown("Para afinar tu resultado, selecciona los **3 temas** que consideras más urgentes para la Escuela. Las propuestas que elijas en estas áreas tendrán doble puntaje.")
prioridades = st.multiselect(
    "Selecciona hasta 3 temas:",
    ejes_unicos,
    max_selections=3
)

st.divider()

# 4. CÁLCULO Y RESULTADOS
if st.button("Ver mi candidato más afín 📊", type="primary"):
    if None in st.session_state.respuestas.values() or len(st.session_state.respuestas) < len(preguntas_cargo):
        st.error("Por favor, responde todas las preguntas para ver tu resultado.")
    else:
        # Inicializar contadores
        puntos = {candidato: 0 for candidato in CANDIDATOS[cargo]}
        puntos_por_eje = {candidato: {eje: 0 for eje in ejes_unicos} for candidato in CANDIDATOS[cargo]}
        
        # Calcular puntajes
        for i, p in enumerate(preguntas_cargo):
            respuesta_usuario = st.session_state.respuestas[i]
            eje = p['eje']
            
            # Multiplicador del Segundo Filtro
            valor_punto = 2 if eje in prioridades else 1
            
            for op in p['opciones']:
                if op['texto'] == respuesta_usuario:
                    for cand in op['candidatos']:
                        puntos[cand] += valor_punto
                        puntos_por_eje[cand][eje] += valor_punto

        # Mostrar Resultados
        st.header("🏆 Tu Match Electoral")
        
        ranking = sorted(puntos.items(), key=lambda x: x[1], reverse=True)
        ganador = ranking[0][0]
        
        st.success(f"### Tu mayor afinidad es con: **{ganador}**")
        
        # Gráfico General
        df_general = pd.DataFrame(ranking, columns=["Candidato", "Puntos"])
        fig_bar = px.bar(df_general, x="Puntos", y="Candidato", orientation='h', color="Candidato")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico Radar
        st.header("🎯 Desglose por Áreas")
        datos_radar = []
        for cand, ejes in puntos_por_eje.items():
            for eje_nombre, puntaje in ejes.items():
                datos_radar.append({"Candidato": cand, "Eje": eje_nombre, "Puntos": puntaje})
        
        df_radar = pd.DataFrame(datos_radar)
        fig_radar = px.line_polar(df_radar, r='Puntos', theta='Eje', color='Candidato', line_close=True)
        st.plotly_chart(fig_radar, use_container_width=True)
