import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="ScreenTime Tracker",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&family=Nunito+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
  }

  .stApp { background: #f7f8fc; color: #1a1d2e; }

  h1,h2,h3 { font-family: 'Nunito', sans-serif !important; font-weight: 700; color: #1a1d2e; }

  .hero {
    background: #ffffff;
    border: 1px solid #e4e7f0;
    border-radius: 16px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 2rem;
    border-left: 5px solid #6366f1;
  }
  .hero h1 { color: #1a1d2e; margin: 0 0 .35rem; font-size: 2rem; letter-spacing: -.02em; }
  .hero p  { color: #6b7280; margin: 0; font-size: .95rem; font-weight: 400; }

  .metric-card {
    background: #ffffff;
    border: 1px solid #e4e7f0;
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    text-align: center;
  }
  .metric-label { color: #9ca3af; font-size: .73rem; text-transform: uppercase;
    letter-spacing: .1em; font-weight: 600; }
  .metric-value { color: #1a1d2e; font-family: 'Nunito', sans-serif;
    font-size: 1.75rem; font-weight: 700; margin: .2rem 0 0; }
  .metric-sub   { color: #d1d5db; font-size: .73rem; margin-top: .2rem; }

  .tag-p1 { background: #ede9fe; color: #6366f1; padding: 3px 12px;
    border-radius: 20px; font-size: .8rem; font-weight: 600; }
  .tag-p2 { background: #dbeafe; color: #2563eb; padding: 3px 12px;
    border-radius: 20px; font-size: .8rem; font-weight: 600; }

  div[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e4e7f0;
  }
  div[data-testid="stSidebar"] * { color: #374151 !important; }

  .stTabs [data-baseweb="tab"] {
    color: #9ca3af;
    font-family: 'Nunito', sans-serif;
    font-size: .85rem;
    font-weight: 600;
  }
  .stTabs [aria-selected="true"] {
    color: #6366f1 !important;
    border-bottom: 2px solid #6366f1;
  }
  .stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

  .section-title {
    font-family: 'Nunito', sans-serif;
    color: #9ca3af;
    font-size: .72rem;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-weight: 700;
    margin: 1.8rem 0 .9rem;
    border-bottom: 1px solid #e4e7f0;
    padding-bottom: .45rem;
  }

  /* Override Streamlit default blue tones */
  .stSlider [data-baseweb="slider"] { }
  div[data-testid="stMarkdownContainer"] p { color: #374151; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

P1_COLOR = "#6366f1"   # Indigo
P2_COLOR = "#2563eb"   # Blue

def mins_to_hm(minutes):
    if pd.isna(minutes): return "—"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m"

CS = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#374151",
    font_family="Nunito Sans",
    xaxis=dict(gridcolor="#f0f0f5", linecolor="#e4e7f0"),
    yaxis=dict(gridcolor="#f0f0f5", linecolor="#e4e7f0")
)

# ── CSV Parser ─────────────────────────────────────────────────────────────────
def parse_csv(file, person_name: str) -> dict:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    for c in df.select_dtypes("object").columns:
        df[c] = df[c].astype(str).str.strip()
    df["person"] = person_name
    df["woche"]  = df["woche"].astype(str)
    df["dauer_minuten"] = pd.to_numeric(df["dauer_minuten"], errors="coerce").fillna(0)
    return {
        "tag":   df[df["daten_kategorie"] == "tag_gesamt"].copy(),
        "woche": df[df["daten_kategorie"] == "woche_gesamt"].copy(),
        "apps":  df[df["daten_kategorie"] == "top_app"].copy(),
        "raw":   df
    }

# ── Demo-Daten ─────────────────────────────────────────────────────────────────
@st.cache_data
def make_demo(person: str, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    app_pool = ["WhatsApp","Instagram","YouTube","TikTok","Spotify",
                "Chrome","Maps","Snapchat","Netflix","LinkedIn","Slack"]
    date_map = {
        "10": ["10.03.2026","11.03.2026","12.03.2026"],
        "11": ["13.03.2026","14.03.2026","15.03.2026"],
        "12": ["16.03.2026","17.03.2026","18.03.2026"],
        "13": ["19.03.2026","20.03.2026","21.03.2026"],
    }
    rows_tag, rows_woche, rows_apps = [], [], []
    for w, dates in date_map.items():
        week_total = int(rng.normal(1600, 300))
        rows_woche.append({"woche":w,"datum":dates[0][:5]+".-"+dates[-1][:5]+".",
                           "daten_kategorie":"woche_gesamt","name":"gesamt",
                           "dauer_minuten":week_total,"person":person})
        for d in dates:
            daily = int(rng.normal(week_total/3, 40))
            rows_tag.append({"woche":w,"datum":d,"daten_kategorie":"tag_gesamt",
                             "name":"gesamt","dauer_minuten":daily,"person":person})
            top5 = rng.choice(app_pool, 5, replace=False)
            portions = rng.dirichlet(np.ones(5)) * daily * 0.7
            for app, t in zip(top5, portions):
                rows_apps.append({"woche":w,"datum":d,"daten_kategorie":"top_app",
                                  "name":app,"dauer_minuten":int(t),"person":person})
    all_rows = rows_tag + rows_woche + rows_apps
    return {
        "tag":   pd.DataFrame(rows_tag),
        "woche": pd.DataFrame(rows_woche),
        "apps":  pd.DataFrame(rows_apps),
        "raw":   pd.DataFrame(all_rows)
    }

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Daten hochladen")
    st.markdown('<span class="tag-p1">Person 1</span>', unsafe_allow_html=True)
    name1 = st.text_input("Name", value="Sarah", key="n1")
    file1 = st.file_uploader("CSV hochladen", type="csv", key="f1")
    st.markdown("---")
    st.markdown('<span class="tag-p2">Person 2</span>', unsafe_allow_html=True)
    name2 = st.text_input("Name", value="Bella", key="n2")
    file2 = st.file_uploader("CSV hochladen", type="csv", key="f2")
    st.markdown("---")
    st.markdown("### Optionen")
    pseudonym = st.toggle("App-Namen pseudonymisieren", False)
    show_raw  = st.toggle("Rohdaten anzeigen", False)
    st.markdown("---")
    st.caption("ScreenTime Tracker · Bonusprojekt")

# ── Daten laden ────────────────────────────────────────────────────────────────
def load(file, name, seed):
    try:
        d = parse_csv(file, name) if file else make_demo(name, seed)
    except Exception as e:
        st.error(f"Fehler beim Laden ({name}): {e}")
        d = make_demo(name, seed)
    if pseudonym and len(d["apps"]) > 0:
        mapping = {a: f"App {i+1}" for i, a in enumerate(d["apps"]["name"].unique())}
        d["apps"]["name"] = d["apps"]["name"].map(mapping)
    return d

d1 = load(file1, name1, 42)
d2 = load(file2, name2, 99)

tag_all   = pd.concat([d1["tag"],   d2["tag"]],   ignore_index=True)
woche_all = pd.concat([d1["woche"], d2["woche"]], ignore_index=True)
apps_all  = pd.concat([d1["apps"],  d2["apps"]],  ignore_index=True)
weeks     = sorted(tag_all["woche"].unique(), key=lambda x: int(x) if x.isdigit() else x)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>ScreenTime Duo</h1>
  <p>Semesterprojekt &mdash; Bildschirmzeit-Analyse &middot; {name1} &amp; {name2}</p>
</div>
""", unsafe_allow_html=True)

if not file1 and not file2:
    st.info("Demo-Daten aktiv. Lade deine eigenen CSV-Dateien in der Sidebar hoch.")

# ── KPIs ───────────────────────────────────────────────────────────────────────
tot1   = d1["woche"]["dauer_minuten"].sum()
tot2   = d2["woche"]["dauer_minuten"].sum()
avg1   = d1["tag"]["dauer_minuten"].mean()
avg2   = d2["tag"]["dauer_minuten"].mean()
shared = set(d1["apps"]["name"].str.lower()) & set(d2["apps"]["name"].str.lower())

c1, c2, c3, c4 = st.columns(4)
for col, label, val, sub in [
    (c1, f"Gesamt {name1}",  mins_to_hm(tot1), f"{len(d1['woche'])} Wochen"),
    (c2, f"Gesamt {name2}",  mins_to_hm(tot2), f"{len(d2['woche'])} Wochen"),
    (c3, "Tagesschnitt",     f"{mins_to_hm(avg1)} / {mins_to_hm(avg2)}", f"{name1} vs. {name2}"),
    (c4, "Gemeinsame Apps",  str(len(shared)), "beide genutzt"),
]:
    col.markdown(f"""<div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{val}</div>
      <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Zeitverlauf", "App-Analyse", "Vergleich", "Statistik", "Daten"
])

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

# ════════ TAB 1 ════════════════════════════════════════════════════════════════
with tab1:
    section("Wochentliche Gesamtbildschirmzeit")

    if len(weeks) >= 2:
        wr = st.select_slider("Wochenbereich (KW)", options=weeks,
                              value=(weeks[0], weeks[-1]), key="wr1")
        fw = [w for w in weeks if weeks.index(wr[0]) <= weeks.index(w) <= weeks.index(wr[1])]
    else:
        fw = weeks

    wf = woche_all[woche_all["woche"].isin(fw)]
    fig = px.line(wf, x="woche", y="dauer_minuten", color="person",
                  color_discrete_map={name1: P1_COLOR, name2: P2_COLOR},
                  markers=True, labels={"dauer_minuten": "Minuten / Woche", "woche": "KW"})
    fig.update_traces(line_width=2.5, marker_size=7)
    fig.update_layout(**CS, height=360, hovermode="x unified", legend_title_text="",
                      margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    section("Tagesdetail")
    sel_w = st.selectbox("Woche (KW)", weeks, key="tw")
    daily_sel = tag_all[tag_all["woche"] == sel_w]
    fig2 = px.bar(daily_sel, x="datum", y="dauer_minuten", color="person", barmode="group",
                  color_discrete_map={name1: P1_COLOR, name2: P2_COLOR},
                  labels={"dauer_minuten": "Minuten", "datum": "Datum"})
    fig2.update_layout(**CS, height=320, margin=dict(t=20, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ════════ TAB 2 ════════════════════════════════════════════════════════════════
with tab2:
    section("Top-Apps gesamt pro Person")
    col_a, col_b = st.columns(2)
    for col, d, name, color in [(col_a, d1, name1, P1_COLOR), (col_b, d2, name2, P2_COLOR)]:
        with col:
            top = d["apps"].groupby("name")["dauer_minuten"].sum().nlargest(5).reset_index()
            top["hm"] = top["dauer_minuten"].apply(mins_to_hm)
            fig = px.bar(top, x="dauer_minuten", y="name", orientation="h",
                         color_discrete_sequence=[color], text="hm",
                         labels={"dauer_minuten": "Minuten gesamt", "name": ""})
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(**CS, height=300, margin=dict(t=30, b=10),
                              title=dict(text=f"Top 5 — {name}", font_color=color,
                                         font_size=13, font_family="Nunito"))
            st.plotly_chart(fig, use_container_width=True)

    section("App-Zeitverlauf")
    sel_p  = st.radio("Person", [name1, name2], horizontal=True, key="ap")
    d_sel  = d1 if sel_p == name1 else d2
    top5   = d_sel["apps"].groupby("name")["dauer_minuten"].sum().nlargest(5).index.tolist()
    s_apps = st.multiselect("Apps auswählen", top5, default=top5)

    if len(weeks) >= 2:
        wr2 = st.select_slider("Wochenbereich", options=weeks,
                               value=(weeks[0], weeks[-1]), key="wr2")
        fw2 = [w for w in weeks if weeks.index(wr2[0]) <= weeks.index(w) <= weeks.index(wr2[1])]
    else:
        fw2 = weeks

    aw = (d_sel["apps"][d_sel["apps"]["woche"].isin(fw2) & d_sel["apps"]["name"].isin(s_apps)]
          .groupby(["woche","name"])["dauer_minuten"].sum().reset_index())
    fig3 = px.line(aw, x="woche", y="dauer_minuten", color="name",
                   markers=True, labels={"dauer_minuten": "Minuten", "woche": "KW"})
    fig3.update_layout(**CS, height=360, margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

# ════════ TAB 3 ════════════════════════════════════════════════════════════════
with tab3:
    section("Gemeinsame Apps — Radardiagramm")

    a1 = d1["apps"].copy(); a1["name_l"] = a1["name"].str.lower()
    a2 = d2["apps"].copy(); a2["name_l"] = a2["name"].str.lower()
    shared_l = sorted(set(a1["name_l"]) & set(a2["name_l"]))[:7]

    if len(shared_l) >= 3:
        r1 = a1.groupby("name_l")["dauer_minuten"].sum()
        r2 = a2.groupby("name_l")["dauer_minuten"].sum()
        labels = [s.capitalize() for s in shared_l]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=[r1.get(a, 0) for a in shared_l], theta=labels,
            fill='toself', name=name1, line_color=P1_COLOR, fillcolor="rgba(99,102,241,0.15)"))
        fig_r.add_trace(go.Scatterpolar(r=[r2.get(a, 0) for a in shared_l], theta=labels,
            fill='toself', name=name2, line_color=P2_COLOR, fillcolor="rgba(37,99,235,0.15)"))
        fig_r.update_layout(
            polar=dict(bgcolor="#fafbff",
                       radialaxis=dict(visible=True, gridcolor="#e4e7f0", color="#9ca3af"),
                       angularaxis=dict(gridcolor="#e4e7f0")),
            paper_bgcolor="#ffffff", font_color="#374151",
            font_family="Nunito Sans",
            legend_orientation="h", height=420, margin=dict(t=30))
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Zu wenige gemeinsame Apps — weitere Wochen hinzufügen.")

    section(f"Wochentliche Differenz ({name1} minus {name2})")
    w1s = d1["woche"].groupby("woche")["dauer_minuten"].sum()
    w2s = d2["woche"].groupby("woche")["dauer_minuten"].sum()
    cw  = sorted(set(w1s.index) & set(w2s.index), key=lambda x: int(x) if x.isdigit() else x)
    if cw:
        diff = pd.DataFrame({"woche": cw, "diff": [w1s[w] - w2s[w] for w in cw]})
        diff["farbe"] = diff["diff"].apply(lambda x: P1_COLOR if x >= 0 else P2_COLOR)
        diff["label"] = diff.apply(
            lambda r: f"{name1} +{abs(int(r['diff']))}" if r["diff"] >= 0
                      else f"{name2} +{abs(int(r['diff']))}", axis=1)
        fig4 = px.bar(diff, x="woche", y="diff", color="farbe",
                      color_discrete_map="identity", text="label",
                      labels={"diff": "Differenz in Minuten", "woche": "KW"})
        fig4.add_hline(y=0, line_color="#d1d5db", line_dash="dot")
        fig4.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
        fig4.update_layout(**CS, showlegend=False, height=340, margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

    section("Korrelation der Wochengesamtzeiten")
    if len(cw) > 1:
        mc = pd.DataFrame({name1: [w1s[w] for w in cw],
                           name2: [w2s[w] for w in cw], "woche": cw})
        corr = mc[name1].corr(mc[name2])
        fig5 = px.scatter(mc, x=name1, y=name2, text="woche", trendline="ols",
                          color_discrete_sequence=[P1_COLOR],
                          labels={name1: f"Min/Woche {name1}", name2: f"Min/Woche {name2}"})
        fig5.update_traces(marker_size=10, textposition="top center", textfont_size=9)
        fig5.update_layout(**CS, height=340, margin=dict(t=40),
                           title=dict(text=f"Korrelationskoeffizient r = {corr:.2f}",
                                      font_color="#374151", font_size=13, font_family="Nunito"))
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Mindestens 2 gemeinsame Wochen erforderlich.")

# ════════ TAB 4 ════════════════════════════════════════════════════════════════
with tab4:
    section("Statistische Kennzahlen")

    for d, name, color in [(d1, name1, P1_COLOR), (d2, name2, P2_COLOR)]:
        vals  = d["tag"]["dauer_minuten"]
        stats = {"Mittelwert": vals.mean(), "Median": vals.median(),
                 "Std.-Abw.":  vals.std(),  "Min":    vals.min(), "Max": vals.max()}
        st.markdown(f'<div class="section-title" style="color:{color};border-color:{color}22">{name}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(5)
        for col, (k, v) in zip(cols, stats.items()):
            col.markdown(f"""<div class="metric-card">
              <div class="metric-label">{k}</div>
              <div class="metric-value" style="font-size:1.3rem;color:{color}">{mins_to_hm(v)}</div>
            </div>""", unsafe_allow_html=True)

    section("Boxplot — Tageszeiten pro Woche")
    fig6 = px.box(tag_all, x="woche", y="dauer_minuten", color="person",
                  color_discrete_map={name1: P1_COLOR, name2: P2_COLOR},
                  labels={"dauer_minuten": "Minuten / Tag", "woche": "KW"})
    fig6.update_layout(**CS, height=380, margin=dict(t=20))
    st.plotly_chart(fig6, use_container_width=True)

    section("Heatmap — Tageszeit je Woche und Tag")
    hp  = st.radio("Person", [name1, name2], horizontal=True, key="hp")
    dfh = d1["tag"] if hp == name1 else d2["tag"]
    try:
        pivot = dfh.pivot_table(index="woche", columns="datum",
                                values="dauer_minuten", aggfunc="mean")
        fig7 = px.imshow(pivot, color_continuous_scale="Blues",
                         labels={"color": "Min / Tag"}, aspect="auto")
        fig7.update_layout(paper_bgcolor="#ffffff", font_color="#374151",
                           font_family="Nunito Sans", height=300, margin=dict(t=20))
        st.plotly_chart(fig7, use_container_width=True)
    except Exception:
        st.info("Nicht genug Datenpunkte für die Heatmap.")

# ════════ TAB 5 ════════════════════════════════════════════════════════════════
with tab5:
    if show_raw:
        section("Rohdaten (kombiniert)")
        raw_all = pd.concat([d1["raw"], d2["raw"]], ignore_index=True)
        st.dataframe(raw_all, use_container_width=True, height=400)
        st.download_button("Kombinierte CSV herunterladen",
                           raw_all.to_csv(index=False).encode("utf-8"),
                           "screentime_combined.csv", "text/csv")
    else:
        st.info("Aktiviere 'Rohdaten anzeigen' in der Sidebar.")

    section("CSV-Format")
    example = pd.DataFrame([
        {"woche":"12","datum":"16.03.-22.03.","daten_kategorie":"woche_gesamt","name":"gesamt","dauer_minuten":1765},
        {"woche":"12","datum":"16.03.2026",   "daten_kategorie":"tag_gesamt",  "name":"gesamt","dauer_minuten":225},
        {"woche":"12","datum":"16.03.2026",   "daten_kategorie":"top_app",     "name":"whatsapp","dauer_minuten":54},
        {"woche":"12","datum":"16.03.2026",   "daten_kategorie":"top_app",     "name":"instagram","dauer_minuten":47},
        {"woche":"12","datum":"16.03.2026",   "daten_kategorie":"top_app",     "name":"youtube","dauer_minuten":38},
    ])
    st.dataframe(example, use_container_width=True)
    st.download_button("Vorlage herunterladen",
                       example.to_csv(index=False).encode("utf-8"),
                       "vorlage.csv", "text/csv")
