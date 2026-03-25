from shiny import App, render, ui, reactive, Session
import os
import pandas as pd
from api_client import VAClient

# Initialize API Client
client = VAClient()

# Define UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("MuseumCluster", style="font-weight: 800; letter-spacing: -1px; margin-bottom: 0.5rem;"),
        ui.p("Explore the V&A Collections through a generous, clustered interface.", style="color: var(--color-fg-muted); font-size: 0.85rem; margin-bottom: 2rem;"),
        
        ui.input_text("search_query", "Search Collection", placeholder="e.g. 'Art Deco'...", width="100%"),
        ui.hr(),
        ui.input_select("cluster_field_select", "Cluster by:", {
            "category": "Category",
            "material": "Material",
            "place": "Place"
        }, selected="category", width="100%"),
        
        ui.div(
            ui.output_text("results_summary"),
            style="margin-top: 3rem; color: var(--color-fg-muted); font-size: 0.8rem;"
        ),
        ui.div(
            ui.tags.hr(style="margin: 2rem 0 1rem 0; border-top: 1px solid var(--color-border);"),
            ui.p(
                "This project is developed as part of ",
                ui.tags.a("Experimental Museum Interfaces (EMI)", href="https://emi.computing.edgehill.ac.uk/", target="_blank", style="color: var(--color-fg); text-decoration: underline;"),
                " © 2025 • All rights reserved.",
                style="font-size: 0.7rem; color: var(--color-fg-muted); line-height: 1.4;"
            ),
            style="margin-top: auto;"
        ),
        width=280
    ),
    ui.head_content(
        ui.include_css(os.path.join(os.path.dirname(__file__), "styles.css")),
        ui.tags.link(rel="icon", type="image/png", href="/favicon.png?v=1"),
        ui.tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
        ui.tags.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous"),
        ui.tags.link(href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Geist:wght@100..900&display=swap", rel="stylesheet"),
        ui.tags.script(src="https://d3js.org/d3.v7.min.js"),
        ui.include_js(os.path.join(os.path.dirname(__file__), "cluster_viz.js")),
        ui.tags.title("MuseumCluster | Generous V&A Explorer")
    ),
    # Main Content Area: Viz (Full Width) and Detail Pane (Overlay)
    ui.div(
        ui.div(id="cluster-viz-container"),
        ui.tags.button("Fit to View", id="btn-fit-view", class_="btn-fit-view"),
        ui.div(
            ui.output_ui("item_detail_pane"),
            id="detail-pane-container"
        ),
        style="position: relative; overflow: hidden; height: 100vh;"
    )
)

def server(input, output, session: Session):
    # Reactive state
    current_cluster_field = reactive.Value("category")
    selected_item_id = reactive.Value(None)

    # Effect to toggle the sliding pane via JS
    @reactive.Effect
    async def _toggle_pane():
        item_id = selected_item_id()
        await session.send_custom_message("toggle_detail_pane", {"open": item_id is not None})
    
    # Fetch data
    @reactive.Calc
    def search_results_full():
        query = input.search_query()
        # If no query, use a default broad search for high-quality items
        if not query or len(query) < 2:
            query_to_use = "art" 
        else:
            query_to_use = query
            
        try:
            # First get summary search results
            res = client.search(query_to_use, page_size=60) 
            summary_records = res.get("records", [])
            sids = [r.get("systemNumber") for r in summary_records if r.get("systemNumber")]
            
            # Now fetch full records in bulk (parallel) to get materials/categories
            print(f"DEBUG: Bulk fetching {len(sids)} full records for query '{query_to_use}'...")
            full_records = client.get_objects_bulk(sids)
            print(f"DEBUG: Bulk fetch complete.")
            return full_records
        except Exception as e:
            print(f"DEBUG: Shiny Search error: {e}")
            return []

    @reactive.Calc
    def cluster_data_list():
        query = input.search_query()
        if not query or len(query) < 2:
            query_to_use = "art"
        else:
            query_to_use = query
            
        field = current_cluster_field()
        try:
            res = client.get_clusters(query_to_use, field)
            if isinstance(res, list):
                clusters = [{"value": c.get("value"), "count": c.get("count")} for c in res][:12]
                return clusters
            return []
        except Exception as e:
            return []

    # Push data to JS whenever search results or cluster field changes
    @reactive.Effect
    async def _():
        records = search_results_full()
        
        if not records:
            await session.send_custom_message("update_cluster_data", {"data": [], "clusters": []})
            return

        field = current_cluster_field()
        
        def normalize(val, field_type):
            if not val or val == "Unknown": return "Unknown"
            v = val.lower().strip()
            if field_type == "material":
                if any(x in v for x in ["plastic", "polypro", "polyeth", "resin", "synthetic"]): return "Plastics"
                if "ink" in v: return "Pen and Ink"
                if any(x in v for x in ["wood", "oak", "mahogany", "pine", "walnut", "beech", "plywood"]): return "Wood"
                if any(x in v for x in ["silk", "cotton", "wool", "textile", "fabric", "linen", "velvet"]): return "Textiles"
                if "paper" in v or "card" in v: return "Paper"
                if any(x in v for x in ["metal", "steel", "iron", "brass", "tin", "lead", "alloy", "copper", "bronze", "silver", "gold"]): return "Metal"
                if any(x in v for x in ["ceramic", "porcelain", "earthenware", "stoneware", "clay"]): return "Ceramics"
                if "glass" in v: return "Glass"
            elif field_type == "place":
                if any(x in v for x in ["usa", "united states", "u.s.a.", "new york", "chicago", "california"]): return "United States"
                if any(x in v for x in ["uk", "united kingdom", "great britain", "england", "london", "scotland", "wales", "liverpool", "manchester", "birmingham", "staffordshire", "worcester"]): return "United Kingdom"
                if any(x in v for x in ["france", "paris", "sevres", "lyon"]): return "France"
                if any(x in v for x in ["italy", "rome", "venice", "florence", "milan", "naples"]): return "Italy"
                if any(x in v for x in ["germany", "berlin", "meissen", "dresden", "munich"]): return "Germany"
                if any(x in v for x in ["china", "beijing", "shanghai", "canton", "jingdezhen"]): return "China"
                if any(x in v for x in ["japan", "tokyo", "kyoto", "osaka", "edo"]): return "Japan"
                if any(x in v for x in ["india", "delhi", "mumbai", "calcutta", "bengal"]): return "India"
                if any(x in v for x in ["iran", "persia", "tehran", "isfahan"]): return "Iran"
                if any(x in v for x in ["egypt", "cairo", "alexandria"]): return "Egypt"
                if any(x in v for x in ["netherlands", "holland", "amsterdam", "delft"]): return "Netherlands"
                if any(x in v for x in ["spain", "madrid", "barcelona", "valencia"]): return "Spain"
                if any(x in v for x in ["belgium", "brussels", "antwerp"]): return "Belgium"
                if any(x in v for x in ["switzerland", "zurich", "geneva"]): return "Switzerland"
            elif field_type == "category":
                if "photograph" in v: return "Photographs"
                if "drawing" in v: return "Drawings"
                if "print" in v: return "Prints"
                if "poster" in v: return "Posters"
                if "furniture" in v: return "Furniture"
                if "fashion" in v or "dress" in v or "clothing" in v: return "Fashion"
            return val

        viz_data = []
        for rec in records:
            if not rec: continue
            sid = rec.get("systemNumber")
            
            img_id = None
            if rec.get("images"):
                img_id = rec.get("images")[0]
            
            # Direct extraction from full record
            raw_val = "Unknown"
            coords = None
            
            if field == "category":
                cats = rec.get("categories", [])
                raw_val = cats[0].get("text", "Unknown") if cats else "Unknown"
            elif field == "place":
                places = rec.get("placesOfOrigin", [])
                if places:
                    p_obj = places[0].get("place", {})
                    raw_val = p_obj.get("text", "Unknown")
                    # Try to find lat/long if available in the API response
                    # Note: V&A V2 API sometimes has lat/long in the place object
                    lat = p_obj.get("latitude")
                    lon = p_obj.get("longitude")
                    if lat is not None and lon is not None:
                        coords = [float(lon), float(lat)]
            elif field == "material":
                mats = rec.get("materials", [])
                raw_val = mats[0].get("text", "Unknown").capitalize() if mats else "Unknown"
            
            c_val = normalize(raw_val, field)
            
            # Extract title safely
            titles = rec.get("titles", [])
            title = "Untitled"
            if titles and isinstance(titles, list):
                title = titles[0].get("title", "Untitled")
            elif rec.get("objectType"):
                title = rec.get("objectType")
            
            viz_data.append({
                "id": sid,
                "title": title,
                "imgUrl": f"https://framemark.vam.ac.uk/collections/{img_id}/full/!100,100/0/default.jpg" if img_id else None,
                "clusterValue": c_val,
                "coords": coords
            })

        # CALCULATE LOCAL CLUSTERS
        from collections import Counter
        all_vals = [d['clusterValue'] for d in viz_data if d['clusterValue'] != "Unknown"]
        counts = Counter(all_vals)
        local_clusters = [{"value": k, "count": v} for k, v in counts.most_common(12)]
            
        await session.send_custom_message("update_cluster_data", {
            "data": viz_data,
            "clusters": local_clusters,
            "field": field
        })

    @output
    @render.text
    def results_summary():
        records = search_results_full()
        return f"Showing {len(records)} items clustered by {current_cluster_field()}"

    @reactive.Effect
    @reactive.event(input.cluster_field_select)
    def _():
        current_cluster_field.set(input.cluster_field_select())

    @output
    @render.ui
    def item_detail_pane():
        item_id = selected_item_id()
        if not item_id:
            return ui.div(
                ui.div("Select an item to view details", style="margin-top: 40vh; color: #ccc; font-weight: 600;"),
                class_="detail-pane-empty"
            )
        
        try:
            full_data = client.get_object(item_id)
            item_data = full_data.get("record", {})
            meta = full_data.get("meta", {})
            images = meta.get("images", {})
            
            img_url = images.get("_primary_thumbnail", "").replace("!100,100", "!1000,1000")
            title = item_data.get("titles", [{"title": "Untitled"}])[0].get("title")
            
            # Extract lists
            mats = ", ".join([m.get("text", "") for m in item_data.get("materials", [])])
            cats = ", ".join([c.get("text", "") for c in item_data.get("categories", [])])
            makers = ", ".join([m.get("name", {}).get("text", "") for m in item_data.get("artistMakerPerson", [])])
            
            return ui.div(
                {"class": "detail-pane-content"},
                ui.div(
                    ui.div(
                        ui.input_action_button("close_modal", "Close", class_="btn-close-pane"),
                        class_="detail-pane-header"
                    ),
                    ui.div(title, class_="pane-title")
                ),
                ui.div(
                    ui.tags.img(src=img_url, class_="pane-img") if img_url else ui.div("No image available"),
                    style="margin-bottom: 2rem;"
                ),
                ui.div(
                    ui.div("Object Number", class_="modal-detail-label"),
                    ui.div(item_id, class_="modal-detail-row"),
                    
                    ui.div("Category", class_="modal-detail-label"),
                    ui.div(cats or "Unknown", class_="modal-detail-row"),
                    
                    ui.div("Material", class_="modal-detail-label"),
                    ui.div(mats or "Unknown", class_="modal-detail-row"),
                    
                    ui.div("Maker", class_="modal-detail-label"),
                    ui.div(makers or "Unknown", class_="modal-detail-row"),
                    
                    ui.div("Description", class_="modal-detail-label"),
                    ui.div(item_data.get("summaryDescription", ""), class_="modal-detail-row", style="font-size: 0.9rem; line-height: 1.6;"),
                    
                    ui.div(
                        ui.tags.a("View on V&A Website", href=f"https://collections.vam.ac.uk/item/{item_id}", target="_blank", class_="btn btn-dark w-100", style="margin-top: 1rem; display: inline-block;")
                    )
                )
            )
        except Exception as e:
            print(f"DEBUG: Detail Error: {e}")
            return ui.div("Error loading details.")

    # Observe view_item from JS
    @reactive.Effect
    @reactive.event(input.view_item)
    def _():
        selected_item_id.set(input.view_item())

    # Observe Close button in modal
    @reactive.Effect
    @reactive.event(input.close_modal)
    def _():
        selected_item_id.set(None)

# Define static assets directory
www_dir = os.path.join(os.path.dirname(__file__), "www")
app = App(app_ui, server, static_assets=www_dir)
