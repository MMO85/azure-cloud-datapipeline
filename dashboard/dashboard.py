import streamlit as st
import pandas as pd
import plotly.express as px

# اگر از نسخه‌ای استفاده می‌کنی که یک DF ترکیبی با ستون source_mart برمی‌گردونه:
from dashboard.connect_data_warehouse import query_job_listings

# ----------------------------
# Ladda data
# ----------------------------
df = query_job_listings()  # یک DF ترکیبی برمی‌گرداند + ستون source_mart

# استانداردسازی نام ستون‌ها به UPPERCASE تا با کد پایین match شوند
df.columns = [c.upper() for c in df.columns]

# اطمینان از وجود ستون‌های لازم (اگر اسامی کمی فرق دارند، اینجا می‌توان map کرد)
# مثال: اگر در خروجی‌ات "JOB_DESCRIPTION_ID" نام دیگری داشت، اینجا remap کن.
required_cols = [
    "VACANCIES", "OCCUPATION", "OCCUPATION_FIELD", "APPLICATION_DEADLINE",
    "HEADLINE", "JOB_DESCRIPTION", "JOB_DESCRIPTION_HTML", "EMPLOYER_NAME",
    "EMPLOYMENT_TYPE", "SALARY_TYPE", "DURATION", "WORKPLACE_REGION",
    "JOB_DESCRIPTION_ID", "SOURCE_MART"
]
for col in required_cols:
    if col not in df.columns:
        df[col] = pd.NA  # از کرش جلوگیری شود؛ در صورت نیاز map دقیق‌تر بده

# نوع تاریخ
df["APPLICATION_DEADLINE"] = pd.to_datetime(df["APPLICATION_DEADLINE"], errors="coerce")

# ----------------------------
# Mart filter (mapping برای نمایش قشنگ‌تر)
# ----------------------------
MART_DISPLAY_MAP = {
    "marts.mart_bygg_och_anlaggning": "Bygg & Anläggning",
    "marts.mart_kultur_media_design": "Kultur / Media / Design",
    "marts.mart_pedagogik": "Pedagogik",
}

# اگر source_mart در دیتا lower است، UPPER نکرده‌ایم؛ پس با مقدار اصلی مقایسه می‌کنیم
df["SOURCE_MART"] = df["SOURCE_MART"].astype(str)

# لیست مارت‌های موجود در دیتا
available_marts = sorted(df["SOURCE_MART"].dropna().unique())
display_options = [MART_DISPLAY_MAP.get(m, m) for m in available_marts]
display_to_real = {MART_DISPLAY_MAP.get(k, k): k for k in available_marts}

# ----------------------------
# Layout
# ----------------------------
st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")
st.title("HR Analytics Dashboard")

# فیلتر سراسری مارت‌ها (بالای همه تب‌ها)
st.markdown("### Välj datamart(er)")
selected_display = st.multiselect(
    "MARTS",
    options=display_options,
    default=display_options  # پیش‌فرض همه را انتخاب کن
)
selected_marts = [display_to_real[d] for d in selected_display] if selected_display else []

# اعمال فیلتر مارت روی دیتای اصلی
if selected_marts:
    df = df[df["SOURCE_MART"].isin(selected_marts)]
else:
    # اگر کاربر همه را پاک کرد، دیتافریم خالی شود و پیام بدهیم
    df = df.iloc[0:0]

tabs = st.tabs(["Översikt", "Annons-sök & arbetsgivare", "Trender & mönster"])

# ----------------------------
# Flik 1: Översikt
# ----------------------------
with tabs[0]:
    st.header("📊 Översikt")
    st.markdown("""
    <div style="background-color:#2c3e50; padding:15px; border-radius:8px; 
                max-width:900px; margin-bottom:20px; color:#ffffff;">
    <p style="font-size:16px; line-height:1.6; text-align:justify;">
    Den här dashboarden ger en översikt över aktuella platsannonser från Arbetsförmedlingen, 
    indelade efter region och yrkesområde. Syftet är att hjälpa 
    rekryterare och talent acquisition-specialister att snabbt få insikter om arbetsmarknaden. 

    Här kan du se nyckeltal för antal annonser, antal tjänster, 
    vanligaste yrken samt topp arbetsgivare inom valt område.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("Ingen data att visa för valda datamarter.")
    else:
        filter_col, spacer, result_col = st.columns([1, 0.3, 3])

        with filter_col:
            regions = sorted(df["WORKPLACE_REGION"].dropna().unique())
            default_region = "Stockholms län" if "Stockholms län" in regions else (regions[0] if regions else None)
            selected_region = st.selectbox(
                "📍 Välj region", regions, index=(regions.index(default_region) if default_region else 0), key="region_tab1"
            ) if regions else None
            df_region = df[df["WORKPLACE_REGION"] == selected_region] if selected_region else pd.DataFrame()

            occ_fields = sorted(df_region["OCCUPATION_FIELD"].dropna().unique()) if not df_region.empty else []
            selected_field = st.selectbox("🗂️ Välj yrkesområde", occ_fields, key="field_tab1") if occ_fields else None
            df_filtered = df_region[df_region["OCCUPATION_FIELD"] == selected_field] if selected_field else pd.DataFrame()

        with result_col:
            if not df_filtered.empty:
                st.subheader(f"KPIer för {selected_field} i {selected_region}")

                col1, col2, col3 = st.columns(3)
                col1.metric("📑 Antal annonser", len(df_filtered))
                col2.metric("👥 Totalt antal tjänster", int(df_filtered["VACANCIES"].fillna(0).sum()))
                col3.metric("🏢 Antal arbetsgivare", df_filtered["EMPLOYER_NAME"].nunique())

                # امن‌تر: اگر groupby خالی شد، از try/except استفاده کن
                try:
                    top_job = df_filtered.groupby("OCCUPATION")["VACANCIES"].sum().idxmax()
                    st.markdown("**👷 Mest annonserade yrke**")
                    st.markdown(
                        f"<p style='font-size:25px; font-weight:normal; margin-top:-10px'>{top_job}</p>",
                        unsafe_allow_html=True
                    )
                except ValueError:
                    st.write("Ingen yrkesdata.")

                try:
                    top_employer = df_filtered.groupby("EMPLOYER_NAME")["VACANCIES"].sum().idxmax()
                    st.markdown("**🏢 Topp arbetsgivare**")
                    st.markdown(
                        f"<p style='font-size:25px; font-weight:normal; margin-top:-10px'>{top_employer}</p>",
                        unsafe_allow_html=True
                    )
                except ValueError:
                    st.write("Ingen arbetsgivardata.")
            else:
                st.info("Ingen data för vald kombination av filter.")

# ----------------------------
# Flik 2: Annons-sök & arbetsgivare
# ----------------------------
with tabs[1]:
    st.header("🔎 Annons-sök & arbetsgivarinformation")
    st.markdown("""
    <div style="background-color:#2c3e50; padding:15px; border-radius:8px; 
                max-width:900px; margin-bottom:20px; color:#ffffff;">
    <p style="font-size:16px; line-height:1.6; text-align:justify;">
    I den här fliken kan du söka dig ner på detaljnivå. 
    Börja med att välja region och yrkesområde, och fortsätt sedan till yrke och arbetsgivare. 
    Du kan därefter granska enskilda annonser med detaljer som tjänstetyp, 
    varaktighet, lön och hela annonstexten.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("Ingen data att visa för valda datamarter.")
    else:
        filter_col, spacer, result_col = st.columns([1, 0.3, 3])

        with filter_col:
            regions = sorted(df["WORKPLACE_REGION"].dropna().unique())
            default_region = "Stockholms län" if "Stockholms län" in regions else (regions[0] if regions else None)
            selected_region = st.selectbox(
                "📍 Välj region", regions, index=(regions.index(default_region) if default_region else 0), key="region_tab2"
            ) if regions else None
            df_region = df[df["WORKPLACE_REGION"] == selected_region] if selected_region else pd.DataFrame()

            if not df_region.empty:
                occ_fields = sorted(df_region["OCCUPATION_FIELD"].dropna().unique())
                selected_field = st.selectbox("🗂️ Välj yrkesområde", occ_fields, key="field_tab2") if occ_fields else None
                df_field = df_region[df_region["OCCUPATION_FIELD"] == selected_field] if selected_field else pd.DataFrame()

                if not df_field.empty:
                    occupations = sorted(df_field["OCCUPATION"].dropna().unique())
                    selected_occupation = st.selectbox("👷 Välj yrke", occupations, key="occ_tab2") if occupations else None
                    df_occ = df_field[df_field["OCCUPATION"] == selected_occupation] if selected_occupation else pd.DataFrame()

                    if not df_occ.empty:
                        employers = sorted(df_occ["EMPLOYER_NAME"].dropna().unique())
                        selected_employer = st.selectbox("🏢 Välj arbetsgivare", employers, key="employer_tab2") if employers else None
                        df_employer = df_occ[df_occ["EMPLOYER_NAME"] == selected_employer] if selected_employer else pd.DataFrame()
                    else:
                        df_employer = pd.DataFrame()
                else:
                    df_employer = pd.DataFrame()
            else:
                df_employer = pd.DataFrame()

        with result_col:
            if not df_employer.empty:
                num_ads = len(df_employer)
                st.markdown(
                    f"### 📋 {num_ads} annons(er) för **{selected_occupation}** i **{selected_region}** – {selected_employer}"
                )

                df_display = df_employer.copy()
                if pd.api.types.is_datetime64_any_dtype(df_display["APPLICATION_DEADLINE"]):
                    df_display["APPLICATION_DEADLINE"] = df_display["APPLICATION_DEADLINE"].dt.strftime("%Y-%m-%d")
                else:
                    df_display["APPLICATION_DEADLINE"] = pd.to_datetime(df_display["APPLICATION_DEADLINE"], errors="coerce").dt.strftime("%Y-%m-%d")

                st.dataframe(
                    df_display[["HEADLINE", "EMPLOYMENT_TYPE", "DURATION", "APPLICATION_DEADLINE"]],
                    use_container_width=True,
                )

                selected_ad = st.selectbox("📄 Välj annons", df_employer["HEADLINE"].dropna().unique(), key="ad_tab2")
                ad_details = df_employer[df_employer["HEADLINE"] == selected_ad].iloc[0]

                st.markdown(f"## {ad_details['HEADLINE']}")

                col1, spacer, col2 = st.columns([1, 0.3, 1])
                with col1:
                    st.write(f"**Arbetsgivare:** {ad_details.get('EMPLOYER_NAME', '-')}")
                    st.write(f"**Region:** {ad_details.get('WORKPLACE_REGION', '-')}")
                    st.write(f"**Yrkesområde:** {ad_details.get('OCCUPATION_FIELD', '-')}")
                    st.write(f"**Yrke:** {ad_details.get('OCCUPATION', '-')}")
                with col2:
                    st.write(f"**Anställningstyp:** {ad_details.get('EMPLOYMENT_TYPE', '-')}")
                    st.write(f"**Varaktighet:** {ad_details.get('DURATION', '-')}")
                    st.write(f"**Lön:** {ad_details.get('SALARY_TYPE', '-')}")
                    deadline_val = ad_details.get('APPLICATION_DEADLINE', pd.NaT)
                    deadline_str = deadline_val.strftime('%Y-%m-%d') if isinstance(deadline_val, pd.Timestamp) and not pd.isna(deadline_val) else '-'
                    st.write(f"**Deadline:** {deadline_str}")

                st.markdown("### 📝 Annonstext")
                st.write(ad_details.get("JOB_DESCRIPTION", "-"))
            else:
                st.info("Ingen annons finns för vald kombination av filter.")

# ----------------------------
# Flik 3: Trender & mönster
# ----------------------------
with tabs[2]:
    st.header("📈 Trender & Mönster")
    st.markdown("""
    <div style="background-color:#2c3e50; padding:15px; border-radius:8px; 
                max-width:900px; margin-bottom:20px; color:#ffffff;">
    <p style="font-size:16px; line-height:1.6; text-align:justify;">
    Här kan du utforska trender i arbetsmarknaden. 
    Se vilka arbetsgivare som dominerar, hur tjänsterna fördelas över olika anställningstyper, 
    och följa utvecklingen över tid med hjälp av ansökningsdeadlines.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("Ingen data att visa för valda datamarter.")
    else:
        filter_col, spacer, result_col = st.columns([1, 0.3, 3])

        with filter_col:
            regions = sorted(df["WORKPLACE_REGION"].dropna().unique())
            default_region = "Stockholms län" if "Stockholms län" in regions else (regions[0] if regions else None)
            selected_region = st.selectbox(
                "📍 Välj region", regions, index=(regions.index(default_region) if default_region else 0), key="region_tab3"
            ) if regions else None
            df_region = df[df["WORKPLACE_REGION"] == selected_region] if selected_region else pd.DataFrame()

            if not df_region.empty:
                occ_fields = sorted(df_region["OCCUPATION_FIELD"].dropna().unique())
                selected_field = st.selectbox("🗂️ Välj yrkesområde", occ_fields, key="field_tab3") if occ_fields else None
                df_filtered = df_region[df_region["OCCUPATION_FIELD"] == selected_field] if selected_field else pd.DataFrame()
            else:
                df_filtered = pd.DataFrame()

        with result_col:
            if not df_filtered.empty:
                st.subheader(f"Analyser för {selected_field} i {selected_region}")

                # 1. Topp arbetsgivare
                top_employers = (
                    df_filtered.groupby("EMPLOYER_NAME")["VACANCIES"]
                    .sum(min_count=1)
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )
                if not top_employers.empty:
                    fig1 = px.bar(
                        top_employers,
                        x="EMPLOYER_NAME",
                        y="VACANCIES",
                        text="VACANCIES",
                        title="🏢 Topp arbetsgivare",
                    )
                    fig1.update_traces(
                        textposition="outside",
                        hovertemplate="<b>Arbetsgivare:</b> %{x}<br><b>Tjänster:</b> %{y}<extra></extra>"
                    )
                    fig1.update_layout(xaxis_tickangle=-45, xaxis_title=None, yaxis_title=None)
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("Ingen arbetsgivardata.")

                # 2. Fördelning av anställningstyper
                type_dist = df_filtered.groupby("EMPLOYMENT_TYPE")["VACANCIES"].sum(min_count=1).reset_index()
                if not type_dist.empty:
                    fig2 = px.pie(
                        type_dist,
                        names="EMPLOYMENT_TYPE",
                        values="VACANCIES",
                        hole=0.4,
                        title="📝 Fördelning av anställningstyper",
                    )
                    fig2.update_traces(
                        hovertemplate="<b>Anställningstyp:</b> %{label}<br><b>Tjänster:</b> %{value}<extra></extra>"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Ingen data för anställningstyp.")

                # 3. Antal tjänster över deadlines
                if pd.api.types.is_datetime64_any_dtype(df_filtered["APPLICATION_DEADLINE"]):
                    trend_src = df_filtered
                else:
                    trend_src = df_filtered.copy()
                    trend_src["APPLICATION_DEADLINE"] = pd.to_datetime(trend_src["APPLICATION_DEADLINE"], errors="coerce")

                trend = (
                    trend_src.groupby(trend_src["APPLICATION_DEADLINE"].dt.date)["VACANCIES"]
                    .sum(min_count=1)
                    .reset_index()
                    .rename(columns={"APPLICATION_DEADLINE": "DATE"})
                )
                if not trend.empty:
                    fig3 = px.line(
                        trend,
                        x="DATE",
                        y="VACANCIES",
                        markers=True,
                        title="📅 Antal tjänster över ansökningsdeadlines",
                    )
                    fig3.update_traces(
                        hovertemplate="<b>Datum:</b> %{x}<br><b>Tjänster:</b> %{y}<extra></extra>"
                    )
                    fig3.update_layout(xaxis_title=None, yaxis_title=None)
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Ingen trenddata.")
            else:
                st.info("Ingen data för vald kombination av filter.")
