/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* TACTICAL MAP & INTERFACE CONTROLLER    */
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

// UTC Clock
setInterval(() => {
    const el = document.getElementById('topbar-time');
    if (el) el.textContent = new Date().toUTCString().slice(17, 25) + ' UTC';
}, 1000);

// Tab Navigation
function switchTab(tabId, clickedEl) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    clickedEl.classList.add('active');
    const target = document.getElementById('tab-' + tabId);
    if (target) target.classList.add('active');
}

// Map Initialization
let currentViewState = {
    longitude: 77.5946,
    latitude: 12.9716,
    zoom: 10,
    pitch: 50,
    bearing: -15,
    altitude: 1.5,
    maxZoom: 18
};

const deckgl = new deck.DeckGL({
    container: 'map',
    mapStyle: {
        version: 8,
        sources: {
            'esri-satellite': {
                type: 'raster',
                tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
                tileSize: 256,
                maxzoom: 18,
                attribution: '© Esri, Maxar'
            }
        },
        layers: [{ id: 'esri-satellite-layer', type: 'raster', source: 'esri-satellite', minzoom: 0, maxzoom: 18 }]
    },
    initialViewState: currentViewState,
    onViewStateChange: ({ viewState }) => {
        viewState.zoom = Math.min(viewState.zoom, 17.9);
        currentViewState = viewState;
    },
    controller: true,
    layers: []
});

// 3D / Flat View Toggle
let is3D = true;
function toggleView() {
    is3D = !is3D;
    deckgl.setProps({
        initialViewState: {
            longitude: currentViewState.longitude,
            latitude: currentViewState.latitude,
            zoom: currentViewState.zoom,
            pitch: is3D ? 50 : 0,
            bearing: is3D ? -15 : 0,
            transitionDuration: 1000,
            transitionInterpolator: new deck.FlyToInterpolator()
        }
    });
}

// Panel Visibility Management
let panelsVisible = true;
function hidePanels() {
    if (!panelsVisible) return;
    panelsVisible = false;
    document.getElementById('ui-panel')?.classList.add('hidden-left');
    document.getElementById('gemini-panel')?.classList.add('hidden-right');
    const vt = document.getElementById('view-toggle');
    if (vt) {
        vt.style.opacity = '0';
        vt.style.pointerEvents = 'none';
    }
    setTimeout(() => {
        document.getElementById('peek-left')?.classList.add('visible');
        document.getElementById('peek-right')?.classList.add('visible');
    }, 300);
}

function showPanels() {
    if (panelsVisible) return;
    panelsVisible = true;
    document.getElementById('ui-panel')?.classList.remove('hidden-left');
    document.getElementById('gemini-panel')?.classList.remove('hidden-right');
    const vt = document.getElementById('view-toggle');
    if (vt) {
        vt.style.opacity = '1';
        vt.style.pointerEvents = 'auto';
    }
    document.getElementById('peek-left')?.classList.remove('visible');
    document.getElementById('peek-right')?.classList.remove('visible');
}

document.getElementById('map')?.addEventListener('mousedown', (e) => {
    if (
        e.target.closest('#ui-panel') ||
        e.target.closest('#gemini-panel') ||
        e.target.closest('#topbar') ||
        e.target.closest('.peek-btn') ||
        e.target.closest('#view-toggle') ||
        e.target.closest('#targeting-box') ||
        e.target.closest('#recycle-view-btn') ||
        e.target.closest('#recycle-overlay') ||
        e.target.closest('#detail-modal-wrapper')
    ) return;
    hidePanels();
});

// Location Search
function toggleSearch() {
    const container = document.getElementById('search-container');
    const btn = document.getElementById('toggle-search-btn');
    if (!container || !btn) return;
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.innerHTML = '⬡ CLOSE SEARCH';
        document.getElementById('location-input')?.focus();
    } else {
        container.style.display = 'none';
        btn.innerHTML = '🔍 OPEN LOCATION SEARCH';
        const sugg = document.getElementById('search-suggestions');
        if (sugg) sugg.style.display = 'none';
    }
}

let searchTimeout;
const locInput = document.getElementById('location-input');
const suggBox = document.getElementById('search-suggestions');
const coordVal = document.getElementById('selected-coords');
const nameVal = document.getElementById('selected-name');

if (locInput) {
    locInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value;
        if (query.length < 3) {
            if (suggBox) suggBox.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`);
                const data = await res.json();
                if (!suggBox) return;
                suggBox.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(place => {
                        const div = document.createElement('div');
                        div.className = 'search-item';
                        div.innerText = place.display_name;
                        div.onclick = () => {
                            const shortName = place.display_name.split(',')[0];
                            locInput.value = shortName;
                            if (nameVal) nameVal.value = shortName;
                            if (coordVal) coordVal.value = `${place.lat},${place.lon}`;
                            deckgl.setProps({
                                initialViewState: {
                                    ...currentViewState,
                                    longitude: parseFloat(place.lon),
                                    latitude: parseFloat(place.lat),
                                    transitionDuration: 2000,
                                    transitionInterpolator: new deck.FlyToInterpolator()
                                }
                            });
                            suggBox.style.display = 'none';
                            toggleSearch();
                        };
                        suggBox.appendChild(div);
                    });
                    suggBox.style.display = 'block';
                }
            } catch (err) {
                console.error("Search error:", err);
            }
        }, 500);
    });
}

document.addEventListener('click', (e) => {
    if (locInput && suggBox && !locInput.contains(e.target) && !suggBox.contains(e.target)) {
        suggBox.style.display = 'none';
    }
});

// Symmetrical Targeting Box Resize Math
const targetBox = document.getElementById('targeting-box');
const resizeHandle = document.querySelector('.tc-br');
let isResizing = false;

const startResize = (e) => {
    isResizing = true;
    e.stopPropagation();
    if (e.type !== 'touchstart') e.preventDefault();
};

const doResize = (clientX, clientY) => {
    if (!isResizing || !targetBox) return;
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const dx = Math.abs(clientX - centerX);
    const dy = Math.abs(clientY - centerY);
    const newSize = Math.max(100, Math.min(Math.max(dx, dy) * 2 + 20, window.innerWidth * 0.8));
    targetBox.style.width = newSize + 'px';
    targetBox.style.height = newSize + 'px';
};

const stopResize = () => { isResizing = false; };

if (resizeHandle) {
    resizeHandle.addEventListener('mousedown', startResize);
    document.addEventListener('mousemove', (e) => { if (isResizing) doResize(e.clientX, e.clientY); });
    document.addEventListener('mouseup', stopResize);

    resizeHandle.addEventListener('touchstart', startResize, { passive: false });
    document.addEventListener('touchmove', (e) => { if (isResizing) doResize(e.touches[0].clientX, e.touches[0].clientY); }, { passive: false });
    document.addEventListener('touchend', stopResize);
}

// Global Exports
window.deckgl = deckgl;
window.getCurrentViewState = () => currentViewState;
window.switchTab = switchTab;
window.toggleView = toggleView;
window.hidePanels = hidePanels;
window.showPanels = showPanels;
window.toggleSearch = toggleSearch;
