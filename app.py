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
# Mantener el orden original de los ejes según aparecen en PREGUNTAS
ejes_unicos = []
for p in preguntas_cargo:
    if p['eje'] not in ejes_unicos:
        ejes_unicos.append(p['eje'])

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
st.markdown("Selecciona hasta **3 temas** que consideras más urgentes para la Escuela. Esto nos dirá quién te representa mejor en lo que más te importa.")
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
        puntos_generales = {c: 0 for c in CANDIDATOS[cargo]}
        puntos_prioridades = {c: 0 for c in CANDIDATOS[cargo]}
        ganadores_por_eje = {eje: [] for eje in ejes_unicos}
        
        # Calcular puntajes
        for i, p in enumerate(preguntas_cargo):
            respuesta_usuario = st.session_state.respuestas[i]
            eje = p['eje']
            
            for op in p['opciones']:
                if op['texto'] == respuesta_usuario:
                    for cand in op['candidatos']:
                        puntos_generales[cand] += 1
                        ganadores_por_eje[eje].append(cand)
                        if eje in prioridades:
                            puntos_prioridades[cand] += 1

        # 1. GANADOR GENERAL
        ranking_general = sorted(puntos_generales.items(), key=lambda x: x[1], reverse=True)
        ganador_general = ranking_general[0][0]
        
        # 2. GANADOR PRIORIDADES
        if prioridades:
            ranking_prioridades = sorted(puntos_prioridades.items(), key=lambda x: x[1], reverse=True)
            ganador_prioridad = ranking_prioridades[0][0]
            puntos_max_prio = ranking_prioridades[0][1]
        else:
            ganador_prioridad = None
            puntos_max_prio = 0

        # --- MOSTRAR RESULTADOS ---
        st.header("🏆 Tu Match Electoral")
        
        # A. Afinidad General
        st.success(f"### 🥇 Candidato más afín general: **{ganador_general}**")
        st.write("Este candidato es el que sumó más puntos tomando en cuenta todas tus respuestas por igual.")
        
        # B. Afinidad por Prioridad
        if prioridades and puntos_max_prio > 0:
            st.info(f"### ⭐ Candidato más afín en tus prioridades: **{ganador_prioridad}**")
            st.write(f"Este candidato es el que más te representa exclusivamente en las áreas que marcaste como urgentes ({', '.join(prioridades)}).")
        elif prioridades and puntos_max_prio == 0:
            st.info("### ⭐ Candidato más afín en tus prioridades: **Ninguno**")
            st.write("Curiosamente, tus respuestas en las áreas prioritarias no sumaron puntos para ningún candidato específico (puedes haber elegido opciones sin candidato o hubo un empate en 0).")

        # C. Lista por Área Temática
        st.subheader("🎯 Tu candidato ideal por área temática")
        st.markdown("Este es el detalle de quién te representa en cada eje específico según tus respuestas:")
        
        for eje in ejes_unicos:
            # En caso de que la opción seleccionada tenga más de un candidato (ej: Lista 1A)
            candidatos_eje = " y ".join(ganadores_por_eje[eje])
            st.markdown(f"- **{eje}:** {candidatos_eje}")
        
        st.divider()

        # D. Gráfico de Respaldo Visual
        st.subheader("📊 Desglose de Afinidad General")
        df_general = pd.DataFrame(ranking_general, columns=["Candidato", "Puntos"])
        # Filtrar solo los que tienen más de 0 puntos para un gráfico más limpio
        df_general = df_general[df_general["Puntos"] > 0]
        fig_bar = px.bar(df_general, x="Puntos", y="Candidato", orientation='h', color="Candidato")
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
