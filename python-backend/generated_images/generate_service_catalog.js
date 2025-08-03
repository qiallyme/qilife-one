# generate_service_catalog.py

import pandas as pd
import json
from pathlib import Path

# ─ CONFIG ────────────────────────────────────────────────────────────────
CSV_FILE    = Path("services_with_images.csv")
OUTPUT_FILE = Path("service_catalog_snippet.html")
BOOKING_BASE= "https://www.qially.me/book?service="
# ─────────────────────────────────────────────────────────────────────────

if not CSV_FILE.exists():
    raise FileNotFoundError(f"Put your CSV here as '{CSV_FILE.name}' and try again.")

# 1) Load CSV and fill defaults
df = pd.read_csv(CSV_FILE)
df['serviceType']           = df['serviceType'].fillna("Other")
df['servicePrice']          = df['servicePrice'].fillna("")
df['serviceDescription']    = df['serviceDescription'].fillna("")
df['serviceScope']          = df['serviceScope'].fillna("")
df['exclusions']            = df['exclusions'].fillna("")

# 2) Build category dropdown
categories   = sorted(df['serviceType'].unique().tolist())
options_html = "\n".join(f'<option value="{c}">{c}</option>' for c in categories)

# 3) Generate the HTML snippet
html = f"""
<style>
  #searchInput, #filterCategory {{
    width: 200px; padding: 0.5rem; margin: 1rem; font-size: 1rem;
  }}
  #controls {{ text-align: center; }}
  .service-grid {{
    display: grid; gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    margin: 1rem;
  }}
  .service-card {{
    overflow: visible;
    position: relative;
    z-index: 1;
    border: 1px solid #ddd; border-radius: 8px; overflow: visible;
    text-align: center; padding: 1rem; background: #fff;
  }}
  .service-card img {{
    width: 100%; height: 150px; object-fit: cover;
    border-bottom: 1px solid #eee;
  }}
  .service-card h3 {{ margin: 0.5rem 0; font-size: 1.1rem; }}
  .service-card .price {{
    font-weight: bold; margin-bottom: 0.5rem; color: #333;
  }}
  .service-card button {{
    padding: 0.5rem 1rem; margin-top: 0.5rem;
    background: #663399; color: #fff; border: none; border-radius: 4px;
    cursor: pointer;
  }}
  .tooltip {{
    display: inline-block; margin-top: 0.5rem; cursor: pointer;
  }}
  .tooltip .tooltiptext {{
    visibility: hidden; width: 420px; background: rgba(0,0,0,0.8);
    color: #fff; text-align: left; padding: 0.5rem; border-radius: 6px;
    position: absolute; z-index: 999; top: auto; bottom: 0; right: 0px;
    font-size: 0.9rem; line-height: 1.2;
  }}
  .tooltip:hover .tooltiptext {{
    visibility: visible;
  }}
</style>

<div id="controls">
  <input type="text" id="searchInput" placeholder="Search services..." />
  <select id="filterCategory">
    <option value="">All Categories</option>
    {options_html}
  </select>
</div>

<div id="service-container" class="service-grid"></div>

<script>
(() => {{
  const raw = {json.dumps(df.to_dict(orient="records"))};
  const services = raw.reduce((acc, s) => {{
    acc[s.serviceSlug] = {{
      name:        s.serviceName,
      category:    s.serviceType,
      imageUrl:    s.imageUrl,
      price:       s.servicePrice,
      description: s.serviceDescription,
      scope:       s.serviceScope,
      exclusions:  s.exclusions,
      bookingUrl:  "{BOOKING_BASE}" + s.serviceSlug
    }};
    return acc;
  }}, {{}});

  const container   = document.getElementById("service-container");
  const searchInput = document.getElementById("searchInput");
  const filterCat   = document.getElementById("filterCategory");

  function render() {{
    const q  = searchInput.value.toLowerCase();
    const fc = filterCat.value;
    container.innerHTML = "";
    Object.values(services)
      .filter(s => (!fc || s.category === fc) &&
                   (!q  || s.name.toLowerCase().includes(q)))
      .forEach(s => {{
        const card = document.createElement("div");
        card.className = "service-card";
        card.innerHTML = `
          <img src="${{s.imageUrl}}" alt="${{s.name}}" loading="lazy"/>
          <h3>${{s.name}}</h3>
          <div class="price">$${{s.price}}.00</div>
          <div class="tooltip">ℹ️
            <span class="tooltiptext">
              <strong>Description:</strong> ${{s.description}}<br>
              <strong>Scope:</strong> ${{s.scope}}<br>
              <strong>Exclusions:</strong> ${{s.exclusions}}
            </span>
          </div>
          <button onclick="location.href='${{s.bookingUrl}}'">Schedule Now</button>
        `;
        container.appendChild(card);
      }});
  }}

  searchInput.addEventListener("input", render);
  filterCat.addEventListener ("change", render);
  render();
}})();
</script>
"""

# 4) Write out
OUTPUT_FILE.write_text(html, encoding="utf-8")
print(f"✅ Updated HTML snippet generated → {OUTPUT_FILE.resolve()}")
