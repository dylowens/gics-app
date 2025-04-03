import os
import requests
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from streamlit_agraph import agraph, Node, Edge, Config
from models.models import Sector as GICSSector, IndustryGroup as GICSGroup, Industry as GICSIndustry, SubIndustry as GICSSub
from models.naics_models import Sector, IndustryGroup, Industry, SubIndustry  # NAICS models

# --- Page Setup ---
st.set_page_config(page_title="NAICS Hierarchy Explorer", page_icon="📊", layout="wide")

# --- Buy Me a Coffee ---
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
API_URL = "https://oqviryuptkdwbcbwkyxc.supabase.co/functions/v1/create-checkout-session"

if st.button("☕ Buy Me a Coffee"):
    if not SUPABASE_ANON_KEY:
        st.error("❌ SUPABASE_ANON_KEY not set in environment variables.")
    else:
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                },
                json={"items": [{"name": "Coffee", "price": 500, "quantity": 1}]}
            )
            checkout_url = response.json().get("url")
            if checkout_url:
                st.markdown(f"""
                    <a href="{checkout_url}" target="_blank">
                        <button style='padding:0.5rem 1rem; font-size:1rem; background:#635bff; color:white; border:none; border-radius:6px; cursor:pointer;'>
                            👉 Continue to Stripe Checkout
                        </button>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ No checkout URL returned.")
        except Exception as e:
            st.error(f"❌ Could not reach checkout function: {e}")

# --- Database Connections ---
naics_engine = create_engine(f"sqlite:///{os.path.abspath('naics.db')}")
naics_session = sessionmaker(bind=naics_engine)()

gics_engine = create_engine(f"sqlite:///{os.path.abspath('gics.db')}")
gics_session = sessionmaker(bind=gics_engine)()

# --- Title ---
st.title("📊 NAICS Hierarchy Explorer")
st.markdown("""
Explore the North American Industry categories through the **North American Industry Classification System (NAICS)**.

NAICS is the official standard used by the U.S., Canada, and Mexico to classify businesses by industry.  
It organizes the economy into a structured hierarchy—from broad sectors to detailed industry codes.

<span style='font-size: 0.9em; color: gray;'><em>Used for economic analysis, business research, and government reporting.</em></span>  
🔗 [Learn more about NAICS](https://www.census.gov/naics/)
""", unsafe_allow_html=True)

# --- Hierarchical View ---
st.header("📂 Hierarchical View & Data Statistics")
col1, col2 = st.columns([3, 1])

with col1:
    sectors = naics_session.query(Sector).all()
    selected_sector = st.selectbox("Select Sector", ["All"] + [s.name for s in sectors], index=0)

    if selected_sector == "All":
        sectors_to_display = sectors
    else:
        sectors_to_display = [s for s in sectors if s.name == selected_sector]

    for sector in sectors_to_display:
        with st.expander(f"📁 {sector.name}", expanded=False):
            for ig in sector.industry_groups:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📂 **{ig.code} - {ig.name}**", unsafe_allow_html=True)
                for ind in ig.industries:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏭 **{ind.code} - {ind.name}**", unsafe_allow_html=True)
                    for sub in ind.sub_industries:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏷 {sub.name}", unsafe_allow_html=True)
            st.markdown("---")

with col2:
    st.header("📊 Data Statistics")
    st.metric("Total Sectors", naics_session.query(Sector).count())
    st.metric("Total Industry Groups", naics_session.query(IndustryGroup).count())
    st.metric("Total Industries", naics_session.query(Industry).count())
    st.metric("Total Sub-Industries", naics_session.query(SubIndustry).count())



# --- GICS Hierarchical View ---
st.title("📊 GICS Hierarchy Explorer")
st.header("📂 GICS Hierarchical View & Data Statistics")
col1, col2 = st.columns([3, 1])

with col1:
    gics_sectors = gics_session.query(GICSSector).all()
    selected_gics_sector = st.selectbox("Select GICS Sector", ["All"] + [s.name for s in gics_sectors], index=0)

    if selected_gics_sector == "All":
        gics_sectors_to_display = gics_sectors
    else:
        gics_sectors_to_display = [s for s in gics_sectors if s.name == selected_gics_sector]

    for sector in gics_sectors_to_display:
        with st.expander(f"📁 {sector.name}", expanded=False):
            for ig in sector.industry_groups:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📂 **{ig.name}**", unsafe_allow_html=True)
                for ind in ig.industries:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏭 **{ind.name}**", unsafe_allow_html=True)
                    for sub in ind.sub_industries:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏷 {sub.name}", unsafe_allow_html=True)
        st.markdown("---")

with col2:
    st.header("📊 GICS Data Stats")
    st.metric("Total Sectors", gics_session.query(GICSSector).count())
    st.metric("Total Industry Groups", gics_session.query(GICSGroup).count())
    st.metric("Total Industries", gics_session.query(GICSIndustry).count())
    st.metric("Total Sub-Industries", gics_session.query(GICSSub).count())


# --- Tree Graph from GICS DB ---

st.title("🌳 GICS Tree Graph Explorer")
st.header(" Tree Graph - GICS")

st.markdown("""
Explore the **Global Industry Classification Standard (GICS)** through interactive visualizations.  
GICS is a standardized system for classifying companies into sectors and industries, developed by MSCI (Morgan Stanley Capital International) and S&P Dow Jones.  

<span style='font-size: 0.9em; color: gray;'><em>MSCI and S&P Dow Jones create tools to track and analyze markets.</em></span>  
This classification system serves as a valuable reference for anyone looking to understand the structure of the global economy.

🔗 [Learn more about GICS](https://www.msci.com/our-solutions/indexes/gics)
""", unsafe_allow_html=True)

layout_option = st.radio("Select Graph Layout", ["Hierarchical", "Force Directed"])
graph_placeholder = st.empty()

with graph_placeholder.container():
    st.info("🔄 Initializing GICS Tree Graph...")
    with st.spinner(f"Building {layout_option} structure..."):
        nodes, edges = [], []

        root_id = "root_GICS"
        nodes.append(Node(id=root_id, label="GICS", title="GICS", size=25, color="#FF4B4B"))

        gics_sectors = gics_session.query(GICSSector).all()
        for sector in gics_sectors:
            sector_id = f"sector_{sector.id}"
            nodes.append(Node(id=sector_id, label=sector.name, title=sector.name, size=20, color="#FF9B9B"))
            edges.append(Edge(source=root_id, target=sector_id, type="CURVE_SMOOTH"))

            for ig in sector.industry_groups:
                ig_id = f"ig_{ig.id}"
                nodes.append(Node(id=ig_id, label=ig.name, title=ig.name, size=15, color="#4B4BFF"))
                edges.append(Edge(source=sector_id, target=ig_id, type="CURVE_SMOOTH"))

                for industry in ig.industries:
                    industry_id = f"ind_{industry.id}"
                    nodes.append(Node(id=industry_id, label=industry.name, title=industry.name, size=10, color="#9B9BFF"))
                    edges.append(Edge(source=ig_id, target=industry_id, type="CURVE_SMOOTH"))

                    for sub in industry.sub_industries:
                        sub_id = f"sub_{sub.id}"
                        nodes.append(Node(id=sub_id, label=sub.name, title=sub.name, size=5, color="#DEDEDE"))
                        edges.append(Edge(source=industry_id, target=sub_id, type="CURVE_SMOOTH"))

        config_kwargs = {
            "width": 1200,
            "height": 800,
            "directed": True,
            "physics": True,
            "hierarchical": layout_option == "Hierarchical",
            "node_size": 1000,
            "node_color": "#666",
            "node_text_size": 10,
            "edge_color": "#666",
            "edge_width": 1,
            "drag_nodes": True,
            "drag_edges": False,
            "fit_view": True
        }

        if layout_option == "Hierarchical":
            config_kwargs.update({
                "hierarchical_sort_method": "directed",
                "hierarchical_direction": "UD",
                "hierarchical_level_separation": 150,
                "hierarchical_node_separation": 150
            })

        config = Config(**config_kwargs)
        graph_placeholder.empty()
        with graph_placeholder.container():
            agraph(nodes=nodes, edges=edges, config=config)


# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📊 Data Source: NAICS & GICS</p>
    <p>📅 Last updated: 2024</p>
</div>
""", unsafe_allow_html=True)

# --- Close sessions ---
naics_session.close()
gics_session.close()