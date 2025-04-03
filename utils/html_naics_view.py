from bs4 import BeautifulSoup

def generate_naics_html(sectors, keyword):
    def highlight(text, kw):
        if not kw:
            return text
        kw_lower = kw.lower()
        index = text.lower().find(kw_lower)
        if index >= 0:
            return (
                text[:index] +
                f"<span style='background-color: #ffff66; font-weight: bold;'>{text[index:index+len(kw)]}</span>" +
                text[index+len(kw):]
            )
        return text

    keyword = keyword.strip().lower()
    matched_codes = {"ig": set(), "ind": set(), "sub": set(), "sector": set()}

    for sector in sectors:
        if keyword and keyword in sector.name.lower():
            matched_codes["sector"].add(sector.name)
        for ig in sector.industry_groups:
            if keyword and keyword in ig.name.lower():
                matched_codes["ig"].add(ig.code)
                matched_codes["sector"].add(sector.name)
            for ind in ig.industries:
                if keyword and keyword in ind.name.lower():
                    matched_codes["ind"].add(ind.code)
                    matched_codes["ig"].add(ig.code)
                    matched_codes["sector"].add(sector.name)
                for sub in ind.sub_industries:
                    if keyword and keyword in sub.name.lower():
                        matched_codes["sub"].add(sub.code)
                        matched_codes["ind"].add(ind.code)
                        matched_codes["ig"].add(ig.code)
                        matched_codes["sector"].add(sector.name)

    html = "<div>"
    for sector in sectors:
        sector_hit = sector.name in matched_codes["sector"]
        sector_label_raw = highlight(sector.name, keyword)
        sector_label = f"<b>{sector_label_raw}</b>" if sector_hit else sector_label_raw
        sector_open = " open" if sector_hit else ""
        html += f"<details{sector_open}><summary>📁 {sector_label}</summary>"

        for ig in sector.industry_groups:
            ig_hit = ig.code in matched_codes["ig"]
            ig_text_raw = f"{ig.code} - {ig.name}"
            ig_label = highlight(ig_text_raw, keyword)
            if ig_hit:
                ig_label = f"<b>{ig_label}</b>"
            ig_open = " open" if ig_hit else ""
            html += f"<details style='margin-left:20px'{ig_open}><summary>📂 {ig_label}</summary>"

            for ind in ig.industries:
                ind_hit = ind.code in matched_codes["ind"]
                ind_text_raw = f"{ind.code} - {ind.name}"
                ind_label = highlight(ind_text_raw, keyword)
                if ind_hit:
                    ind_label = f"<b>{ind_label}</b>"
                ind_open = " open" if ind_hit else ""
                html += f"<details style='margin-left:40px'{ind_open}><summary>🏭 {ind_label}</summary>"

                for sub in ind.sub_industries:
                    sub_text = f"{sub.code} - {sub.name}"
                    sub_label = highlight(sub_text, keyword)
                    html += f"<p style='margin-left:60px'>🏷 {sub_label}</p>"

                html += "</details>"
            html += "</details>"
        html += "</details>"
    html += "</div>"

    return str(BeautifulSoup(html, "html.parser"))