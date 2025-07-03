import ast, io, requests, datetime as dt
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Complaints Dashboard", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/Beingjn/Streamlit_Chatbot_Example/main/new_categories1.xlsx"       
DATE_COL = "date"                                            

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    content = requests.get(url, timeout=15).content
    df = pd.read_excel(io.BytesIO(content))

    # make sure categories is a list
    def _to_list(x):
        try:
            return x if isinstance(x, list) else ast.literal_eval(str(x))
        except Exception:
            return []
    df["categories"] = df["categories"].apply(_to_list)

    # parse date column
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    return df

df = load_data(DATA_URL)

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.header("Filters")

# Country
country_opts = sorted(df["country"].dropna().unique())
country = st.sidebar.selectbox("Country", ["All"] + country_opts)
data = df if country == "All" else df[df["country"] == country]

# Model
model_opts = sorted(data["model"].dropna().unique())
model = st.sidebar.selectbox("Model", ["All"] + model_opts)
data = data if model == "All" else data[data["model"] == model]

# Date-range slider
min_d, max_d = data[DATE_COL].min().date(), data[DATE_COL].max().date()
start_d, end_d = st.sidebar.slider(
    "Date range", min_value=min_d, max_value=max_d,
    value=(min_d, max_d), format="YYYY-MM-DD"
)
mask = (data[DATE_COL].dt.date >= start_d) & (data[DATE_COL].dt.date <= end_d)
data = data.loc[mask]

# ── Counts for pies ───────────────────────────────────────────
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
    st.subheader("Complaints by Country")
    fig = px.pie(country_counts, names="country", values="count", hole=0.4)
    fig.update_traces(textinfo="label+value+percent")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Complaints by Category")
    fig = px.pie(cat_counts, names="category", values="count", hole=0.4)
    fig.update_traces(textinfo="label+value+percent")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw data"):
    st.dataframe(data.head())
