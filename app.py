import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard AutoViz", layout="wide")

st.title("📊 Dashboard Intelligent")

# Upload
uploaded_file = st.file_uploader("Importer un fichier CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    # -------------------------
    # Détection des types
    # -------------------------

    date_cols = []

    for col in df.columns:
        try:
            converted = pd.to_datetime(df[col])
            if converted.notna().sum() > len(df) * 0.8:
                df[col] = converted
                date_cols.append(col)
        except:
            pass

    quantitative_cols = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    qualitative_cols = [
        col for col in df.columns
        if col not in quantitative_cols
        and col not in date_cols
    ]

    # -------------------------
    # Sidebar
    # -------------------------

    st.sidebar.header("Paramètres")

    x_var = st.sidebar.selectbox(
        "Variable X",
        ["Aucune"] + list(df.columns)
    )

    y_var = st.sidebar.selectbox(
        "Variable Y",
        ["Aucune"] + list(df.columns)
    )

    # -------------------------
    # Filtre simple
    # -------------------------

    filter_col = st.sidebar.selectbox(
        "Filtrer",
        ["Aucun"] + qualitative_cols
    )

    filtered_df = df.copy()

    if filter_col != "Aucun":
        values = df[filter_col].dropna().unique()

        selected = st.sidebar.multiselect(
            "Valeurs",
            values,
            default=values
        )

        filtered_df = filtered_df[
            filtered_df[filter_col].isin(selected)
        ]

    # -------------------------
    # Détection graphique
    # -------------------------

    auto_chart = None

    if x_var != "Aucune" and y_var == "Aucune":

        if x_var in qualitative_cols:
            auto_chart = "Bar Chart"

        elif x_var in quantitative_cols:
            auto_chart = "Histogram"

    elif x_var != "Aucune" and y_var != "Aucune":

        if x_var in quantitative_cols and y_var in quantitative_cols:
            auto_chart = "Scatter Plot"

        elif (
            x_var in qualitative_cols
            and y_var in quantitative_cols
        ):
            auto_chart = "Box Plot"

        elif (
            x_var in date_cols
            and y_var in quantitative_cols
        ):
            auto_chart = "Line Chart"

    chart_type = st.sidebar.selectbox(
        "Type de graphique",
        [
            "Auto",
            "Bar Chart",
            "Histogram",
            "Scatter Plot",
            "Box Plot",
            "Line Chart"
        ]
    )

    if chart_type == "Auto":
        chart_type = auto_chart

    # -------------------------
    # Titre dynamique
    # -------------------------

    title = f"{chart_type}"

    if x_var != "Aucune":
        title += f" - {x_var}"

    if y_var != "Aucune":
        title += f" vs {y_var}"

    st.header(title)

    fig = None

    # -------------------------
    # Graphiques
    # -------------------------

    if chart_type == "Bar Chart":

        counts = (
            filtered_df[x_var]
            .value_counts()
            .reset_index()
        )

        counts.columns = [x_var, "Count"]

        fig = px.bar(
            counts,
            x=x_var,
            y="Count",
            title=title
        )

    elif chart_type == "Histogram":

        fig = px.histogram(
            filtered_df,
            x=x_var,
            title=title
        )

    elif chart_type == "Scatter Plot":

        fig = px.scatter(
            filtered_df,
            x=x_var,
            y=y_var,
            title=title
        )

    elif chart_type == "Box Plot":

        fig = px.box(
            filtered_df,
            x=x_var,
            y=y_var,
            title=title
        )

    elif chart_type == "Line Chart":

        fig = px.line(
            filtered_df.sort_values(x_var),
            x=x_var,
            y=y_var,
            title=title
        )

    if fig:
        st.plotly_chart(
            fig,
            use_container_width=True
        )
