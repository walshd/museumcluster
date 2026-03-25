# MuseumCluster: Generous Museum Interface

## Objective
Create a "generous museum interface" using the V&A Collections API that allows users to search the collection and view results clustered by various metadata dimensions (e.g., category, material, place). The interface will prioritize visibility, richness, and exploration, moving away from the "search box as a gatekeeper" model.

## Key Files & Context
- `MuseumCluster/app.py`: Main Shiny for Python application.
- `MuseumCluster/api_client.py`: Module for interacting with the V&A API V2.
- `MuseumCluster/styles.css`: Custom CSS for a generous, image-heavy layout.
- `MuseumCluster/GEMINI.md`: Local project instructions.

## Implementation Steps

### Phase 1: API Integration
1.  Implement a `VAClient` class in `api_client.py` to handle:
    -   `search(query, page, page_size)`: Standard keyword search.
    -   `get_clusters(query, cluster_field)`: Fetch summary data for a specific field.
    -   `get_object(object_id)`: Fetch detailed metadata for a single item.
2.  Ensure robust error handling and pagination support.

### Phase 2: Core Application Structure (Shiny for Python)
1.  Initialize `app.py` with a basic Shiny layout.
2.  Implement a "Show First" landing page displaying a curated or random set of high-quality items.
3.  Add a search interface that triggers both item retrieval and cluster analysis.

### Phase 3: Generous UI & Clustering
1.  Implement a "Cluster View" where results are grouped visually (e.g., using card groups or a grid layout).
2.  Allow users to switch the clustering dimension (e.g., "Cluster by Material", "Cluster by Category").
3.  Use custom CSS to ensure a rich, image-centric display (masonry layout if possible, or large consistent thumbnails).
4.  Implement an "Item Detail" view (modal or slide-over) showing full metadata and a link to the high-res IIIF image.

### Phase 4: Styling & Refinement
1.  Apply "Generous Interface" principles:
    -   Minimize white space where appropriate to show more content.
    -   Provide clear visual hierarchies.
    -   Avoid "no results found" by suggesting alternatives or showing broad categories.
2.  Optimize image loading (lazy loading).

## Verification & Testing
1.  **Functional Testing:**
    -   Search for common terms (e.g., "chair", "textile") and verify results appear.
    -   Verify that switching clusters updates the UI correctly.
    -   Verify item detail view displays correct data.
2.  **API Testing:**
    -   Test API responses for various queries and handle empty/error states.
3.  **UI/UX Review:**
    -   Ensure the interface feels "generous" and exploratory.
