console.log("DEBUG: cluster_viz.js Zoomable Tethered Cloud Loaded");

let width, height;
let svg, simulation, zoomLayer, zoom;

function initSVG() {
    const container = document.getElementById('cluster-viz-container');
    if (!container) return;
    
    width = container.clientWidth;
    height = container.clientHeight || (window.innerHeight * 0.7);
    
    d3.select("#cluster-viz-container").selectAll("*").remove();
    
    // Create SVG
    svg = d3.select("#cluster-viz-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; display: block; background: var(--color-bg); cursor: move;");

    // Add Zoom Layer
    zoomLayer = svg.append("g").attr("class", "zoom-layer");

    // Setup Zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 5])
        .on("zoom", (event) => {
            zoomLayer.attr("transform", event.transform);
        });

    svg.call(zoom);

    // Add a "Fit to View" button overlay
    d3.select("#cluster-viz-container").append("button")
        .text("Fit to View")
        .attr("style", "position: absolute; bottom: 10px; right: 10px; z-index: 100; padding: 5px 10px; border-radius: 4px; border: 1px solid #ddd; background: #fff; cursor: pointer; font-family: var(--font-body); font-size: 12px;")
        .on("click", fitToView);

    if (!document.querySelector(".d3-tooltip")) {
        d3.select("body").append("div")
            .attr("class", "d3-tooltip")
            .style("opacity", 0);
    }
}

function fitToView() {
    if (!zoomLayer) return;
    const bounds = zoomLayer.node().getBBox();
    if (bounds.width === 0) return;

    const fullWidth = width;
    const fullHeight = height;
    const widthPadding = 100;
    const heightPadding = 100;

    const midX = bounds.x + bounds.width / 2;
    const midY = bounds.y + bounds.height / 2;

    const scale = 0.85 / Math.max(bounds.width / fullWidth, bounds.height / fullHeight);
    
    svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity
            .translate(fullWidth / 2, fullHeight / 2)
            .scale(scale)
            .translate(-midX, -midY)
    );
}

Shiny.addCustomMessageHandler('toggle_detail_pane', function(message) {
    const el = document.getElementById('detail-pane-container');
    if (!el) return;
    if (message.open) {
        el.classList.add('is-open');
    } else {
        el.classList.remove('is-open');
    }
});

Shiny.addCustomMessageHandler('update_cluster_data', function(message) {
    const data = message.data;
    const clusters = message.clusters;
    
    initSVG();
    if (!data || data.length === 0) return;

    // 1. Create Nodes
    const clusterNodes = clusters.map(c => ({
        id: `cluster-${c.value}`,
        name: c.value,
        isCluster: true,
        radius: 10,
        x: width / 2,
        y: height / 2
    }));

    const itemNodes = data.map(d => ({
        ...d,
        id: `item-${d.id}`,
        isCluster: false,
        radius: 15,
        x: width / 2 + (Math.random() - 0.5) * width,
        y: height / 2 + (Math.random() - 0.5) * height
    }));

    const allNodes = [...clusterNodes, ...itemNodes];

    // 2. Create Links
    const links = itemNodes.map(d => {
        const target = clusterNodes.find(c => c.name === d.clusterValue);
        return target ? { source: d.id, target: target.id } : null;
    }).filter(l => l !== null);

    // 3. Setup Simulation
    simulation = d3.forceSimulation(allNodes)
        .force("charge", d3.forceManyBody().strength(d => d.isCluster ? -2500 : -30))
        .force("link", d3.forceLink(links)
            .id(d => d.id)
            .distance(70)
            .strength(1))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(d => d.isCluster ? 110 : d.radius + 4))
        .force("x", d3.forceX(width / 2).strength(0.08))
        .force("y", d3.forceY(height / 2).strength(0.08));

    // 4. Draw Cluster Labels
    const labels = zoomLayer.selectAll(".cluster-label")
        .data(clusterNodes)
        .enter()
        .append("text")
        .attr("class", "cluster-label")
        .attr("text-anchor", "middle")
        .attr("style", "font-family: var(--font-heading); font-weight: 900; font-size: 14px; fill: var(--color-accent); text-transform: uppercase; letter-spacing: 2px; pointer-events: none; opacity: 0.7;")
        .text(d => d.name);

    // 5. Draw Items
    const nodeGroups = zoomLayer.selectAll(".node-group")
        .data(itemNodes)
        .enter()
        .append("g")
        .attr("class", "node-group")
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).select("circle").attr("stroke", "#000").attr("stroke-width", 2);
            const tooltip = d3.select(".d3-tooltip");
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`<strong>${d.title}</strong><br/>${d.clusterValue}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (event, d) => {
            d3.select(event.currentTarget).select("circle").attr("stroke", "none");
            d3.select(".d3-tooltip").transition().duration(500).style("opacity", 0);
        })
        .on("click", (event, d) => {
            Shiny.setInputValue("view_item", d.id.replace("item-", ""), {priority: "event"});
        });

    const defs = zoomLayer.append("defs");
    
    nodeGroups.each(function(d, i) {
        const group = d3.select(this);
        const safeId = `img-${d.id.replace(/[^a-zA-Z0-9]/g, '')}-${i}`;
        
        if (d.imgUrl) {
            defs.append("pattern")
                .attr("id", safeId)
                .attr("width", 1)
                .attr("height", 1)
                .append("image")
                .attr("xlink:href", d.imgUrl)
                .attr("width", d.radius * 2)
                .attr("height", d.radius * 2)
                .attr("preserveAspectRatio", "xMidYMid slice");

            group.append("circle")
                .attr("r", d.radius)
                .attr("fill", `url(#${safeId})`)
                .attr("stroke", "#eee");
        } else {
            group.append("circle")
                .attr("r", d.radius)
                .attr("fill", "#eee")
                .attr("stroke", "#ddd");
        }
    });

    simulation.on("tick", () => {
        nodeGroups.attr("transform", d => `translate(${d.x},${d.y})`);
        labels.attr("x", d => d.x).attr("y", d => d.y);
    });

    // Auto-fit after the simulation has had a chance to run (1 second)
    setTimeout(fitToView, 1200);
});
