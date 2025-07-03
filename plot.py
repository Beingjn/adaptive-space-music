# dashboard.py
import ast, io, requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tickets Dashboard", layout="wide")

# 🔗 Hard-coded Excel link
DATA_URL = "https://raw.githubusercontent.com/Beingjn/Streamlit_Chatbot_Example/main/new_categories1.xlsx"  

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    # download the file first (safer for some hosts)
    content = requests.get(url, timeout=15).content
    df = pd.read_excel(io.BytesIO(content))

    # ensure 'categories' is a list
    def _to_list(x):
        try:
            return x if isinstance(x, list) else ast.literal_eval(str(x))
        except Exception:
            return []
    df["categories"] = df["categories"].apply(_to_list)
    return df

df = load_data(DATA_URL)

# ── Sidebar filter ─────────────────────────────────────────────
all_countries = sorted(df["country"].dropna().unique())
country = st.sidebar.selectbox("Country", ["All"] + all_countries)
data = df if country == "All" else df[df["country"] == country]

# Model
model_opts = sorted(data["model"].dropna().unique())
model = st.sidebar.selectbox("Model", ["All"] + model_opts)
data = data if model == "All" else data[data["model"] == model]

# ── Counts for pies ────────────────────────────────────────────
country_counts = (
    data["country"].value_counts(dropna=False)
        .rename_axis("country").reset_index(name="count")
)

cat_counts = (
    data.explode("categories")
        .fillna({"categories": "Uncategorized"})
        .replace({"categories": {"": "Uncategorized"}})
        ["categories"].value_counts()
        .rename_axis("category").reset_index(name="count")
)

# ── Charts ────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Tickets by Country")
    st.plotly_chart(
        px.pie(country_counts, names="country", values="count", hole=0.4),
        use_container_width=True,
    )

with c2:
    st.subheader("Tickets by Category")
    st.plotly_chart(
        px.pie(cat_counts, names="category", values="count", hole=0.4),
        use_container_width=True,
    )

with st.expander("Raw data"):
    st.dataframe(data.head())
