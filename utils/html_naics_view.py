from bs4 import BeautifulSoup

def generate_naics_html(sectors):
    def escape(text):
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = "<div>"
    for sector in sectors:
        html += f"<details><summary>📁 {sector.name}</summary>"
        for ig in sector.industry_groups:
            html += f"<details style='margin-left:20px'><summary>📂 {ig.code} - {ig.name}</summary>"
            for ind in ig.industries:
                html += f"<details style='margin-left:40px'><summary>🏭 {ind.code} - {ind.name}</summary>"
                for sub in ind.sub_industries:
                    html += f"<p style='margin-left:60px'>🏷 {sub.code} - {sub.name}</p>"
                html += "</details>"
            html += "</details>"
        html += "</details>"
    html += "</div>"

    # Clean up highlight styles
    soup = BeautifulSoup(html, "html.parser")
    for b in soup.find_all("b"):
        if b.parent.name == "span":
            b.parent['style'] = "background-color: #ffff66; font-weight: bold;"
    return str(soup)