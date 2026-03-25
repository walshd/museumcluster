# MuseumCluster: A Generous V&A Explorer

MuseumCluster is a "generous" interface for exploring the Victoria and Albert (V&A) Museum's collection. Instead of a blank search box, it invites exploration by presenting a clustered, visual overview of items from the moment it's opened.

## 🖼️ The Experience

*   **Generous Start:** Launches with a broad selection of art from the V&A, immediately populating the view.
*   **Clustered Visualization:** Uses a tethered force-directed graph (D3.js) to group items by **Category**, **Material**, or **Place of Origin**.
*   **Sliding Detail Pane:** Clicking an item smoothly slides in a detailed metadata panel from the right, allowing for deep dives without losing visual context.
*   **Minimalist Aesthetic:** A warm, paper-like color palette (`#fffbf0`) paired with high-contrast typography.

## 🎨 Design & Typography

The interface follows a strict aesthetic:
- **Headings & Logo:** *Bricolage Grotesque* (for a bold, modern feel)
- **Body Text:** *Geist* (for clean, legible metadata)
- **Color Palette:**
    - Background: `#fffbf0` (Cream)
    - Surface/Sidebar: `#f2efe4` (Linen)
    - Accents: `#000000` & `#111111` (Black)

## 🛠️ Tech Stack

- **Backend:** [Shiny for Python](https://shiny.posit.co/py/) — managing reactive state and API orchestration.
- **Frontend Visualization:** [D3.js (v7)](https://d3js.org/) — powering the custom clustered force simulation.
- **API:** [V&A Collections API (v2)](https://developers.vam.ac.uk/guide/v2/welcome.html) — fetching real-time museum data.
- **Styling:** Vanilla CSS with custom properties for a unified theme.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A modern web browser

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:walshd/museumcluster.git
    cd museumcluster
    ```

2.  **Set up a virtual environment (optional but recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the app:**
    ```bash
    shiny run app.py
    ```
    The app will typically be available at `http://localhost:8000`.

## 📁 Project Structure

- `app.py`: The main Shiny application logic and UI definition.
- `api_client.py`: A specialized client for interacting with the V&A V2 API.
- `cluster_viz.js`: Custom D3.js code for the clustered tethered-cloud visualization.
- `styles.css`: Custom styling, including the sliding drawer logic and theme variables.

---

*Part of a series on Generous Interfaces for Museum Collections.*
