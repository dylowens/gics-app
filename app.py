import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Sector, IndustryGroup, Industry, SubIndustry
import os
from streamlit_agraph import agraph, Node, Edge, Config

import requests

# Set page config
st.set_page_config(
    page_title="GICS Hierarchy Explorer",
    page_icon="📊",
    layout="wide"
)

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if st.button("🔌 Test Stripe Checkout"):
    try:
        API_URL = "https://oqviryuptkdwbcbwkyxc.supabase.co/functions/v1/create-checkout-session"
        
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            },
            json={
                "items": [{"name": "Coffee", "price": 500, "quantity": 1}]
            }
        )

        st.write("🔍 Raw response text:", response.text)

        data = response.json()
        if "url" in data:
            st.success("✅ Redirecting to Stripe Checkout...")
            checkout_url = data["url"]
            st.markdown(f"""
                <a href="{checkout_url}" target="_blank">
                    <button style='padding:0.5rem 1rem; font-size:1rem; background:#635bff; color:white; border:none; border-radius:6px; cursor:pointer;'>
                        👉 Continue to Stripe Checkout
                    </button>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Unexpected response format.")
    except Exception as e:
        st.error(f"❌ Could not reach checkout function: {e}")



db_path = os.path.abspath("gics.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Initialize database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Title and Description
st.title("📊 GICS Hierarchy Explorer")
st.markdown("""
Explore the **Global Industry Classification Standard (GICS)** through interactive visualizations.  
GICS is a standardized system for classifying companies into sectors and industries, developed by MSCI (Morgan Stanley Capital International) and S&P Dow Jones.  

<span style='font-size: 0.9em; color: gray;'><em>MSCI and S&P Dow Jones create tools to track and analyze markets.</em></span>  
This classification system serves as a valuable reference for anyone looking to understand the structure of the global economy.

🔗 [Learn more about GICS](https://www.msci.com/our-solutions/indexes/gics)
""", unsafe_allow_html=True)

# Get all sectors for filtering
sectors = session.query(Sector).all()

# --- Hierarchical View & Data Statistics in one row ---
st.header("📂 Hierarchical View & Data Statistics")
col1, col2 = st.columns([3, 1])

with col1:
    # Sector filter in the first column
    selected_sector = st.selectbox(
        "Select Sector", ["All"] + [sector.name for sector in sectors], index=0
    )

    if selected_sector == "All":
        sectors_to_display = session.query(Sector).all()
    else:
        sectors_to_display = session.query(
            Sector).filter_by(name=selected_sector).all()

    for sector in sectors_to_display:
        with st.expander(f"📁 {sector.name}", expanded=False):
            for ig in sector.industry_groups:
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;📂 **Industry Group:** {ig.name}")
                for industry in ig.industries:
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏭 **Industry:** {industry.name}")
                    for sub in industry.sub_industries:
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏷 **Sub-Industry:** {sub.name}")
                st.markdown("---")

with col2:
    st.header("📊 Data Statistics")
    st.metric("Total Sectors", session.query(Sector).count())
    st.metric("Total Industry Groups", session.query(IndustryGroup).count())
    st.metric("Total Industries", session.query(Industry).count())
    st.metric("Total Sub-Industries", session.query(SubIndustry).count())


# 🌳 Tree Graph
st.header("🌳 Tree Graph")

layout_option = st.radio("Select Graph Layout", [
    "Hierarchical", "Force Directed"])

graph_placeholder = st.empty()

with graph_placeholder.container():
    st.info("🔄 Initializing GICS Tree Graph...")
    with st.spinner(f"Building {layout_option} structure..."):
        nodes = []
        edges = []

        # Root node
        root_id = "root_GICS"
        nodes.append(Node(
            id=root_id,
            label="GICS",
            title="GICS",
            size=25,
            color="#FF4B4B"
        ))

        for sector in sectors:
            sector_id = f"sector_{sector.id}"
            nodes.append(Node(
                id=sector_id,
                label=sector.name,
                title=sector.name,
                size=20,
                color="#FF9B9B"
            ))
            edges.append(Edge(source=root_id, target=sector_id, type="CURVE_SMOOTH"))

            for ig in sector.industry_groups:
                ig_id = f"ig_{ig.id}"
                nodes.append(Node(
                    id=ig_id,
                    label=ig.name,
                    title=ig.name,
                    size=15,
                    color="#4B4BFF"
                ))
                edges.append(Edge(source=sector_id, target=ig_id, type="CURVE_SMOOTH"))

                for industry in ig.industries:
                    industry_id = f"ind_{industry.id}"
                    nodes.append(Node(
                        id=industry_id,
                        label=industry.name,
                        title=industry.name,
                        size=10,
                        color="#9B9BFF"
                    ))
                    edges.append(Edge(source=ig_id, target=industry_id, type="CURVE_SMOOTH"))

                    for sub in industry.sub_industries:
                        sub_id = f"sub_{sub.id}"
                        nodes.append(Node(
                            id=sub_id,
                            label=sub.name,
                            title=sub.name,
                            size=5,
                            color="#DEDEDE"
                        ))
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📊 Data Source: Global Industry Classification Standard (GICS)</p>
    <p>📅 Last updated: 2024</p>
</div>
""", unsafe_allow_html=True)

# Close session
session.close()
