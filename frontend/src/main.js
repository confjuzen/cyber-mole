import * as THREE from 'three';

// Scene, Camera, Renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('warehouseCanvas') });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;

// Camera position for top-down view
camera.position.set(10, 10, 10);
camera.lookAt(0, 0, 0);

// Lighting
const ambientLight = new THREE.AmbientLight(0x6e6a86, 0.4); // Rosé Pine muted color
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xe0def4, 0.6); // Rosé Pine text color
directionalLight.position.set(10, 10, 5);
scene.add(directionalLight);

// Grid (warehouse floor)
const gridSize = 20;
const gridHelper = new THREE.GridHelper(gridSize, gridSize);
scene.add(gridHelper);

// Robots and paths
let robots = [];
let paths = [];
let shelves = [];
let shelfItems = [];

function createRobot(position) {
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshBasicMaterial({ color: 0xeb6f92 }); // Rosé Pine love color
    const robot = new THREE.Mesh(geometry, material);
    robot.position.set(position.x, 0.5, position.z);
    scene.add(robot);
    return robot;
}

function drawPath(points, color = 0x9ccfd8) { // Rosé Pine foam color
    const geometry = new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(p.x, 0.1, p.z)));
    const material = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
    const line = new THREE.Line(geometry, material);
    scene.add(line);
    paths.push(line);
    return line;
}

function createShelves() {
    const shelfWidth = 4;
    const shelfHeight = 2;
    const shelfDepth = 1;
    const numShelves = 5;
    const shelfSpacing = 3;

    for (let i = 0; i < 4; i++) {
        const x = -8 + i * shelfSpacing;
        for (let j = 0; j < 3; j++) {
            const z = -5 + j * shelfSpacing;
            createShelfUnit(x, z, shelfWidth, shelfHeight, shelfDepth, numShelves);
        }
    }
}

function createShelfUnit(x, z, width, height, depth, numShelves) {
    const shelfMaterial = new THREE.MeshLambertMaterial({ color: 0x403d52 }); // Rosé Pine surface color

    // Vertical posts
    const postGeometry = new THREE.BoxGeometry(0.1, height, 0.1);
    const post1 = new THREE.Mesh(postGeometry, shelfMaterial);
    post1.position.set(x - width/2, height/2, z - depth/2);
    scene.add(post1);

    const post2 = new THREE.Mesh(postGeometry, shelfMaterial);
    post2.position.set(x + width/2, height/2, z - depth/2);
    scene.add(post2);

    const post3 = new THREE.Mesh(postGeometry, shelfMaterial);
    post3.position.set(x - width/2, height/2, z + depth/2);
    scene.add(post3);

    const post4 = new THREE.Mesh(postGeometry, shelfMaterial);
    post4.position.set(x + width/2, height/2, z + depth/2);
    scene.add(post4);

    // Horizontal shelves
    const shelfGeometry = new THREE.BoxGeometry(width, 0.1, depth);
    for (let k = 0; k < numShelves; k++) {
        const y = (k + 1) * (height / (numShelves + 1));
        const shelf = new THREE.Mesh(shelfGeometry, shelfMaterial);
        shelf.position.set(x, y, z);
        scene.add(shelf);

        shelves.push(shelf);
    }
}

// Event listeners
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

document.getElementById('simulateBtn').addEventListener('click', async () => {
    const algorithm = document.getElementById('algorithm').value;
    // Call backend /simulate with params
    const response = await fetch('http://localhost:5004/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm, robots: 1 })
    });
    const data = await response.json();
    // Update visualization with paths/robots
    clearPaths();
    // Example: draw a simple path
    const samplePath = [{x: 0, y: 0}, {x: 5, y: 5}, {x: 10, y: 0}];
    drawPath(samplePath);
    console.log('Simulation started:', data);
});

document.getElementById('loadDataBtn').addEventListener('click', async () => {
    await loadCleanedData();
});

async function loadCleanedData() {
    try {
        const response = await fetch('http://localhost:5004/api/get-items');
        const data = await response.json();
        if (data && data.length > 0) {
            visualizeDataOnShelves(data);
        }
    } catch (error) {
        console.error('Error loading cleaned data:', error);
        // Don't alert if no data available
    }
}

function visualizeDataOnShelves(data) {
    // Clear existing items
    shelfItems.forEach(item => scene.remove(item));
    shelfItems = [];

    // Group data by format
    const formatGroups = {};
    data.forEach(item => {
        if (!formatGroups[item.format]) formatGroups[item.format] = [];
        formatGroups[item.format].push(item);
    });

    const formats = Object.keys(formatGroups);
    let shelfIndex = 0;

    formats.forEach((format, index) => {
        const items = formatGroups[format];
        const shelf = shelves[shelfIndex + index % shelves.length];
        placeItemsOnShelf(shelf, items, format);
        shelfIndex++;
    });
}

function placeItemsOnShelf(shelf, items, format) {
    const itemSize = getSizeForFormat(format);
    const itemColor = getColorForFormat(format);
    const itemGeometry = new THREE.BoxGeometry(itemSize.width, itemSize.height, itemSize.depth);
    const itemMaterial = new THREE.MeshLambertMaterial({ color: itemColor });

    const shelfWidth = shelf.geometry.parameters.width;
    const shelfDepth = shelf.geometry.parameters.depth;
    const numItems = Math.min(items.length, 10); // Limit to 10 per shelf for simplicity

    for (let i = 0; i < numItems; i++) {
        const x = shelf.position.x - shelfWidth/2 + (i % 5) * (itemSize.width + 0.2) + itemSize.width/2;
        const z = shelf.position.z - shelfDepth/2 + Math.floor(i / 5) * (itemSize.depth + 0.2) + itemSize.depth/2;
        const y = shelf.position.y + itemSize.height/2 + 0.05;

        const itemMesh = new THREE.Mesh(itemGeometry, itemMaterial);
        itemMesh.position.set(x, y, z);
        scene.add(itemMesh);
        shelfItems.push(itemMesh);
    }
}

function getSizeForFormat(format) {
    const sizes = {
        'Vinyl': { width: 0.3, height: 0.3, depth: 0.3 },
        'CD': { width: 0.15, height: 0.15, depth: 0.15 },
        'Cassette': { width: 0.2, height: 0.1, depth: 0.2 },
        'DVD': { width: 0.15, height: 0.15, depth: 0.15 }
    };
    return sizes[format] || { width: 0.2, height: 0.2, depth: 0.2 };
}

function getColorForFormat(format) {
    const colors = {
        'Vinyl': 0xf6c177, // Rosé Pine gold
        'CD': 0x9ccfd8,   // Rosé Pine foam
        'Cassette': 0xeb6f92, // Rosé Pine love
        'DVD': 0xa7c080    // Rosé Pine pine
    };
    return colors[format] || 0x31748f; // Default to Rosé Pine muted
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

animate();

// Initial setup
robots.push(createRobot({x: 0, y: 0}));
createShelves();
console.log('Warehouse simulator loaded');

// Auto-load cleaned data if available
loadCleanedData();