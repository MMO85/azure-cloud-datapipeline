# dashboard.py
import streamlit as st
import pandas as pd
from connect_data_warehouse import query_job_listings

st.set_page_config(page_title="Technical Field Job Ads", layout="wide")

@st.cache_data(ttl=3600)
def load_df() -> pd.DataFrame:
    df = query_job_listings()
    # یک‌دست‌سازی نام ستون‌ها برای ارجاع راحت
    df.columns = [c.lower() for c in df.columns]
    # ستون‌های کلیدی را به نوع درست تبدیل کن
    if "application_deadline" in df.columns:
        df["application_deadline"] = pd.to_datetime(df["application_deadline"], errors="coerce")
    if "vacancies" in df.columns:
        df["vacancies"] = pd.to_numeric(df["vacancies"], errors="coerce").fillna(0).astype(int)
    return df

def layout():
    df = load_df()

    st.title("🧰 Technical Field Job Ads")
    st.write("This dashboard shows technical field job ads from Arbetsförmedlingen’s data warehouse.")

    # --- KPIs ---
    st.markdown("## 📊 Vacancies")
    cols = st.columns(3)
    with cols[0]:
        st.metric(label="Total", value=int(df["vacancies"].sum()) if not df.empty else 0)
    with cols[1]:
        st.metric(label="Unique employers", value=df["employer_name"].nunique() if "employer_name" in df else 0)
    with cols[2]:
        st.metric(label="Occupations", value=df["occupation"].nunique() if "occupation" in df else 0)

    # --- Table ---
    st.markdown("## 🧾 Job listings data")
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    layout()
