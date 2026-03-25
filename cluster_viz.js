console.log("DEBUG: cluster_viz.js Zoomable Tethered Cloud Loaded");

let width, height;
let svg, simulation, zoomLayer, zoom;

function initSVG() {
    console.log("DEBUG: initSVG called");
    const container = document.getElementById('cluster-viz-container');
    if (!container) {
        console.error("DEBUG: #cluster-viz-container not found!");
        return;
    }
    
    width = container.clientWidth;
    height = container.clientHeight || window.innerHeight; // Ensure a valid height fallback
    
    console.log(`DEBUG: initSVG Container Size: ${width}x${height}`);
    
    // Only remove SVG content, not the overlay buttons
    d3.select("#cluster-viz-container").selectAll("svg").remove();
    
    // Create SVG
    svg = d3.select("#cluster-viz-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "width: 100%; height: 100%; display: block; background: var(--color-bg); cursor: move;");

    console.log("DEBUG: SVG appended");

    // Add Zoom Layer
    zoomLayer = svg.append("g").attr("class", "zoom-layer");

    // Setup Zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on("zoom", (event) => {
            zoomLayer.attr("transform", event.transform);
        });

    svg.call(zoom);

    // Setup click for existing UI button
    const fitBtn = document.getElementById('btn-fit-view');
    if (fitBtn) {
        fitBtn.onclick = fitToView;
    }

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
    const currentField = message.field;
    
    initSVG();
    if (!data || data.length === 0) return;

    if (currentField === 'place') {
        renderMapViz(data);
    } else {
        renderForceViz(data, clusters);
    }
});

const PLACE_COORDS = {
    "United Kingdom": [0.1278, 51.5074],
    "France": [2.3522, 48.8566],
    "Italy": [12.4964, 41.9028],
    "Germany": [13.4050, 52.5200],
    "China": [116.4074, 39.9042],
    "Japan": [139.6917, 35.6895],
    "India": [77.2090, 28.6139],
    "United States": [-95.7129, 37.0902],
    "Iran": [51.3890, 35.6892],
    "Egypt": [31.2357, 30.0444],
    "Netherlands": [4.9041, 52.3676],
    "Spain": [-3.7038, 40.4168],
    "Belgium": [4.3517, 50.8503],
    "Switzerland": [8.2275, 46.8182]
};

function renderMapViz(data) {
    const projection = d3.geoNaturalEarth1()
        .scale(width / 2.2) // Even larger scale to provide maximum space
        .translate([width / 2, height / 2]);

    const path = d3.geoPath().projection(projection);

    // Load world map
    d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").then(function(world) {
        zoomLayer.append("g")
            .selectAll("path")
            .data(world.features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("fill", "var(--color-surface2)")
            .attr("stroke", "var(--color-border)")
            .attr("stroke-width", 0.5);

        // Map items to nodes
        const nodes = data.map(d => {
            let coords = d.coords;
            if (!coords && PLACE_COORDS[d.clusterValue]) {
                coords = PLACE_COORDS[d.clusterValue];
            }
            
            let targetPos = [width / 2, height / 2];
            if (coords) {
                targetPos = projection(coords);
            } else {
                targetPos = [width / 2, height * 0.8]; 
            }

            return { 
                ...d, 
                x: width / 2 + (Math.random()-0.5)*100, 
                y: height / 2 + (Math.random()-0.5)*100,
                targetX: targetPos[0],
                targetY: targetPos[1]
            };
        });

        // Use force simulation to cluster at points but prevent overlap
        simulation = d3.forceSimulation(nodes)
            .force("x", d3.forceX(d => d.targetX).strength(0.3)) // Increased strength
            .force("y", d3.forceY(d => d.targetY).strength(0.3)) // Increased strength
            .force("collide", d3.forceCollide().radius(18))
            .force("charge", d3.forceManyBody().strength(-5));

        drawNodes(nodes);

        simulation.on("tick", () => {
            zoomLayer.selectAll(".node-group").attr("transform", d => `translate(${d.x},${d.y})`);
        });

        setTimeout(fitToView, 500);
    });
}

function renderForceViz(data, clusters) {
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
        .attr("style", "font-family: var(--font-heading); font-weight: 900; font-size: 14px; fill: var(--color-accent); text-transform: uppercase; letter-spacing: 2px; cursor: pointer; opacity: 0.7;")
        .text(d => d.name)
        .on("click", (event, d) => {
            Shiny.setInputValue("search_query", d.name);
        });

    drawNodes(itemNodes);

    simulation.on("tick", () => {
        zoomLayer.selectAll(".node-group").attr("transform", d => `translate(${d.x},${d.y})`);
        labels.attr("x", d => d.x).attr("y", d => d.y);
    });

    setTimeout(fitToView, 1200);
}

function drawNodes(itemNodes) {
    const nodeGroups = zoomLayer.selectAll(".node-group")
        .data(itemNodes)
        .enter()
        .append("g")
        .attr("class", "node-group")
        .attr("transform", d => `translate(${d.x},${d.y})`)
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
            const id = d.id.startsWith("item-") ? d.id.replace("item-", "") : d.id;
            Shiny.setInputValue("view_item", id, {priority: "event"});
        });

    const defs = zoomLayer.append("defs");
    
    nodeGroups.each(function(d, i) {
        const group = d3.select(this);
        const safeId = `img-${d.id.toString().replace(/[^a-zA-Z0-9]/g, '')}-${i}`;
        const radius = 15;
        
        if (d.imgUrl) {
            defs.append("pattern")
                .attr("id", safeId)
                .attr("width", 1)
                .attr("height", 1)
                .append("image")
                .attr("xlink:href", d.imgUrl)
                .attr("width", radius * 2)
                .attr("height", radius * 2)
                .attr("preserveAspectRatio", "xMidYMid slice");

            group.append("circle")
                .attr("r", radius)
                .attr("fill", `url(#${safeId})`)
                .attr("stroke", "#eee");
        } else {
            group.append("circle")
                .attr("r", radius)
                .attr("fill", "#eee")
                .attr("stroke", "#ddd");
        }
    });
}

