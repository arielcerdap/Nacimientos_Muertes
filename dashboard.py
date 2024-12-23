import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar el conjunto de datos
data_path = 'births-and-deaths-projected-to-2100.csv'
data = pd.read_csv(data_path, delimiter=";", engine='python')

# Limpiar y preparar los datos
data.columns = [col.strip() for col in data.columns]  # Eliminar espacios adicionales en los nombres de columnas

# Renombrar columnas para facilitar la comprensión
data.rename(columns={
    "Entity": "País",
    "Code": "Código del País",
    "Year": "Año",
    "Deaths - Sex: all - Age: all - Variant: estimates": "Muertes",
    "Deaths - Sex: all - Age: all - Variant: medium": "Muertes Estimadas",
    "Births - Sex: all - Age: all - Variant: estimates": "Nacimientos",
    "Births - Sex: all - Age: all - Variant: medium": "Nacimientos Estimadas",
}, inplace=True)

# Asegurar que las columnas numéricas estén bien formateadas
indicadores = ["Muertes", "Muertes Estimadas", "Nacimientos", "Nacimientos Estimadas"]
for indicador in indicadores:
    data[indicador] = pd.to_numeric(data[indicador], errors='coerce').fillna(0)

# Crear columnas para el neto entre nacimientos y muertes
data["Neto"] = data["Nacimientos"] - data["Muertes"]
data["Neto Estimado"] = data["Nacimientos Estimadas"] - data["Muertes Estimadas"]

# Configuración de la aplicación Streamlit
st.set_page_config(page_title="Dashboard de Nacimientos y Muertes Estimadas", layout="wide")
st.title("Dashboard de Nacimientos 🍼 y Muertes ⚰️ Estimadas")
st.markdown("**Fuente:** [Kaggle Dataset](https://www.kaggle.com/datasets/shreyasur965/births-and-deaths)")

# Filtros en la barra lateral
st.sidebar.header("Filtros")
paises = st.sidebar.multiselect("Selecciona Países", options=data["País"].unique(), default=data["País"].unique()[:2])
año = st.sidebar.slider("Selecciona Año", int(data["Año"].min()), int(data["Año"].max()), 2000)

# Filtrar datos
data_filtrada = data[(data["País"].isin(paises)) & (data["Año"] == año)]
data_filtrada = data_filtrada.drop(columns=["Código del País"])  # Eliminar la columna del código del país
data_filtrada = data_filtrada[["País", "Año", "Muertes", "Nacimientos", "Neto", "Muertes Estimadas", "Nacimientos Estimadas", "Neto Estimado"]]  # Reordenar columnas
data_filtrada.reset_index(drop=True, inplace=True)  # Resetear el índice para que no se muestre

# Mostrar datos filtrados
st.header(f"Datos para {', '.join(paises)} en {año}")
st.dataframe(data_filtrada.style.format({
    "Año": "{}",
    "Muertes": lambda x: f"{x:,.0f}".replace(",", "."),
    "Muertes Estimadas": lambda x: f"{x:,.0f}".replace(",", "."),
    "Nacimientos": lambda x: f"{x:,.0f}".replace(",", "."),
    "Nacimientos Estimadas": lambda x: f"{x:,.0f}".replace(",", "."),
    "Neto": lambda x: f"{x:,.0f}".replace(",", "."),
    "Neto Estimado": lambda x: f"{x:,.0f}".replace(",", ".")
}))

# Comparación de indicadores
st.subheader("Comparación de Indicadores")
if not data_filtrada.empty:
    data_melted = data_filtrada.melt(id_vars="País", value_vars=indicadores + ["Neto", "Neto Estimado"], var_name="Indicador", value_name="Cantidad")
    data_melted = data_melted[data_melted["Cantidad"] > 0]  # Filtrar registros sin datos
    fig = px.bar(
        data_melted, 
        x="Indicador", 
        y="Cantidad", 
        color="País", 
        barmode="group", 
        title=f"Comparación de Indicadores para {', '.join(paises)} en {año}",
        labels={"Cantidad": "Cantidad (separador de miles)", "Indicador": "Indicadores"},
        text_auto='.2s'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")

# Pie de página
st.sidebar.markdown("**Desarrollado por:** [Ariel Cerda](https://x.com/arielcerdap)")


