/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* SCAN CONTROLLER, DECK.GL & ROI LOGIC   */
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const USD_TO_INR = 83.5;

// Realistic Indian & Global Circular Plastic Scrap Value per Metric Ton (USD)
const RECOVERY_MARKET_RATES = {
    pet_bottles: 320,   // Recycled PET flakes (~₹26,700/ton)
    hdpe_rigid: 380,    // High-density PE crates/drums (~₹31,700/ton)
    nylon_nets: 650,    // Marine Nylon-6 ghost gear (~₹54,200/ton)
    microplastics: 85,  // Agglomerate pyrolysis scrap (~₹7,100/ton)
    oil_sheen: 110,     // Reclaimed industrial hydrocarbons (~₹9,200/ton)
    minerals: 40,       // Suspended marine salts/sediments (~₹3,300/ton)
    sargassum: 55,      // Organic compost/biostimulant (~₹4,600/ton)
    water: 0            // Pure seawater
};

function formatINR(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return '₹0';
    const isNeg = amount < 0;
    const abs = Math.abs(amount);
    let str = '';
    if (abs >= 10000000) {
        str = '₹' + (abs / 10000000).toFixed(2) + ' Cr';
    } else if (abs >= 100000) {
        str = '₹' + (abs / 100000).toFixed(2) + ' L';
    } else {
        str = '₹' + Math.round(abs).toLocaleString('en-IN');
    }
    return isNeg ? '−' + str : str;
}

// Typewriter Terminal Animation
let typeInterval;
function typeWriter(text, elementId, speed = 18) {
    clearInterval(typeInterval);
    const target = document.getElementById(elementId);
    if (!target) return;
    target.innerHTML = '';
    let i = 0;
    typeInterval = setInterval(() => {
        if (i < text.length) {
            target.innerHTML += text.charAt(i);
            i++;
        } else {
            target.innerHTML += '<span class="blinking-cursor"></span>';
            clearInterval(typeInterval);
        }
    }, speed);
}

// Gemini Panel Actions
let geminiExpanded = false;
function toggleGeminiExpand() {
    const panel = document.getElementById('gemini-panel');
    const btn = document.getElementById('gemini-expand-btn');
    if (!panel || !btn) return;
    geminiExpanded = !geminiExpanded;
    panel.style.width = geminiExpanded ? '520px' : '360px';
    panel.style.transition = 'width 0.3s ease, opacity 1.5s ease';
    btn.textContent = geminiExpanded ? '⬡ COLLAPSE' : '⬡ EXPAND';
}

function copyGeminiOutput(e) {
    const text = document.getElementById('ai-insight')?.innerText || '';
    navigator.clipboard.writeText(text).then(() => {
        const btn = e?.target || document.querySelector('button[onclick*="copyGeminiOutput"]');
        if (btn) {
            const old = btn.textContent;
            btn.textContent = '✓ COPIED';
            setTimeout(() => btn.textContent = old, 2000);
        }
    });
}

// ROI Calculation Engine
let globalWastePct = 35.0; // Default baseline yield (35%)
let globalValuePerTon = 280.0; // Default blended value ($280/ton)

function calculateROI() {
    const tons = Math.max(0.1, parseFloat(document.getElementById('roi-tons')?.value) || 25);
    const costPerTonINR = Math.max(0, parseFloat(document.getElementById('roi-cost')?.value) || 4500);

    // Yield = Tons collected × (% of usable recyclable polymer / 100)
    const usableYieldTons = tons * (globalWastePct / 100.0);
    const revenueUSD = usableYieldTons * globalValuePerTon;
    const revenueINR = revenueUSD * USD_TO_INR;
    const totalCostINR = tons * costPerTonINR;
    const profitINR = revenueINR - totalCostINR;

    const revEl = document.getElementById('roi-revenue');
    if (revEl) {
        revEl.innerText = formatINR(revenueINR);
        revEl.style.fontSize = "1.3em";
    }
    const costEl = document.getElementById('roi-total-cost');
    if (costEl) costEl.innerText = '−' + formatINR(totalCostINR);

    const profitEl = document.getElementById('roi-profit');
    if (profitEl) {
        profitEl.innerText = formatINR(profitINR);
        profitEl.className = profitINR >= 0 ? "stat-val highlight-green" : "stat-val highlight-red";
    }

    // Synchronize Gemini Intelligence Core Est. Recovery display strictly with ROI
    const gpRecEl = document.getElementById('gp-recovery');
    if (gpRecEl) {
        gpRecEl.textContent = formatINR(revenueINR);
    }
}

// Dashboard Reset
function resetDashboard() {
    targetingActive = false;
    const tBox = document.getElementById('targeting-box');
    if (tBox) tBox.style.display = 'none';

    const sBtn = document.getElementById('scan-btn');
    if (sBtn) {
        sBtn.innerText = "ACTIVATE TARGETING GRID";
        sBtn.style.background = "";
        sBtn.style.borderColor = "";
    }

    const dash = document.getElementById('dashboard-content');
    if (dash) {
        dash.style.opacity = 0;
        setTimeout(() => { dash.style.display = 'none'; }, 500);
    }
    window.deckgl?.setProps({ layers: [] });

    clearInterval(typeInterval);
    const insight = document.getElementById('ai-insight');
    if (insight) insight.innerHTML = 'Awaiting orbital telemetry...<span class="blinking-cursor"></span>';

    globalWastePct = 0;
    const roiRev = document.getElementById('roi-revenue');
    if (roiRev) {
        roiRev.innerText = "Run Scan First";
        roiRev.style.fontSize = "1.1em";
    }
    document.getElementById('roi-total-cost')?.setAttribute('innerText', '—');
    const roiProf = document.getElementById('roi-profit');
    if (roiProf) {
        roiProf.innerText = "—";
        roiProf.className = "stat-val highlight-green";
    }

    document.getElementById('gemini-summary')?.setAttribute('style', 'display:none;');
    document.getElementById('gemini-materials')?.setAttribute('style', 'display:none;');
    const zl = document.getElementById('gemini-zone-label');
    if (zl) zl.textContent = '◈ AWAITING SECTOR SCAN...';
    const ts = document.getElementById('topbar-sector');
    if (ts) ts.textContent = '◈ NO SECTOR SELECTED';

    const bPlastic = document.getElementById('bar-plastic');
    if (bPlastic) bPlastic.style.width = '0%';
    const tPlastic = document.getElementById('txt-plastic');
    if (tPlastic) tPlastic.innerText = '0';

    const bList = document.getElementById('precise-breakdown-list');
    if (bList) bList.innerHTML = '';

    if (typeof hideRecycleBtn === 'function') hideRecycleBtn();
}

// Main 2-Step Tactical Scan Execution
let targetingActive = false;

document.getElementById('scan-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('scan-btn');
    const targetBox = document.getElementById('targeting-box');
    const currentViewState = window.getCurrentViewState();

    if (!targetingActive) {
        targetingActive = true;
        if (targetBox) targetBox.style.display = 'block';
        if (btn) {
            btn.innerText = "EXECUTE DEEP SCAN";
            btn.style.background = "linear-gradient(180deg, #00aa55 0%, #008844 60%, #005522 100%)";
            btn.style.borderColor = "#00ff88";
        }
        typeWriter("Targeting grid active. Resize box over ocean area and execute scan.", 'ai-insight', 20);
        return;
    }

    targetingActive = false;
    if (targetBox) targetBox.style.display = 'none';

    const lat = currentViewState.latitude;
    const lon = currentViewState.longitude;
    const sectorName = document.getElementById('selected-name')?.value || "Ocean Sector";

    // Dynamic radius calculated from pixel size on screen
    const boxWidthPx = targetBox?.offsetWidth || 300;
    const metersPerPx = 156543.03392 * Math.cos(lat * Math.PI / 180) / Math.pow(2, currentViewState.zoom);
    const dynamicRadius = Math.round((boxWidthPx * metersPerPx) / 2);
    const finalRadius = Math.min(Math.max(dynamicRadius, 200), 5000);

    const dash = document.getElementById('dashboard-content');
    const scanner = document.getElementById('scanner');
    const statusDiv = document.getElementById('scan-status');
    const stepText = document.getElementById('scan-step-text');
    const orbitalOverlay = document.getElementById('orbital-scan-overlay');
    const hudStatus = document.getElementById('hud-status-text');
    const hudProgress = document.getElementById('hud-progress-bar');

    if (btn) {
        btn.innerText = "Extracting Data...";
        btn.disabled = true;
    }
    if (dash) {
        dash.style.opacity = 0;
        setTimeout(() => dash.style.display = "none", 500);
    }

    if (scanner) {
        scanner.style.display = "block";
        scanner.animate([{ top: '0px' }, { top: '100vh' }], { duration: 1500, iterations: Infinity });
    }

    // Activate Futuristic Tactical Orbital Scan HUD Overlay
    if (orbitalOverlay) {
        orbitalOverlay.classList.remove('orbital-scan-hidden');
        orbitalOverlay.classList.add('orbital-scan-active');
        if (hudProgress) hudProgress.style.width = '15%';
        if (hudStatus) hudStatus.textContent = 'INITIALIZING ASTER SENSOR ARRAY...';
    }

    const scanSteps = [
        { text: 'CALIBRATING ASTER SENSOR ARRAY...', pct: '25%' },
        { text: `SCANNING SATELLITE TILE (${finalRadius}m RADIUS)...`, pct: '48%' },
        { text: 'RUNNING SPECTRAL MIXTURE ANALYSIS (NNLS)...', pct: '72%' },
        { text: 'COMPUTING BIERMANN FLOATING DEBRIS INDEX (FDI)...', pct: '88%' },
        { text: 'SYNTHESIZING CONSTITUENTS & CLUSTERING...', pct: '96%' }
    ];
    if (statusDiv) statusDiv.style.display = 'block';
    let stepIdx = 0;
    if (stepText) stepText.textContent = '⬡ ' + scanSteps[0].text;
    const stepInterval = setInterval(() => {
        stepIdx++;
        const currentStep = scanSteps[Math.min(stepIdx, scanSteps.length - 1)];
        if (stepText) stepText.textContent = '⬡ ' + currentStep.text;
        if (hudStatus) hudStatus.textContent = currentStep.text;
        if (hudProgress) hudProgress.style.width = currentStep.pct;
    }, 700);

    try {
        // High-level: Relative API endpoint works seamlessly across all ports and environments
        const scanUrl = window.location.origin + '/api/scan';
        const response = await fetch(scanUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat: lat, lon: lon, radius: finalRadius })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || "Orbital Uplink Failed.");
        }

        const result = await response.json();

        // Update orbital telemetry to 100% completion
        if (hudProgress) hudProgress.style.width = '100%';
        if (hudStatus) hudStatus.textContent = 'ORBITAL CLUSTERING COMPLETE (100%)';

        // Store breakdown for Centered Tactical Recycle Center modal
        window._latestScanBreakdown = result.breakdown;

        // Dismiss Orbital HUD overlay smoothly after 550ms so user perceives complete scan
        if (orbitalOverlay) {
            setTimeout(() => {
                orbitalOverlay.classList.remove('orbital-scan-active');
                orbitalOverlay.classList.add('orbital-scan-hidden');
            }, 550);
        }

        // High-level: Distribute clusters into Deck.gl HexagonLayers
        // Direct class mapping from model runner:
        // class_id 0 = Debris / Vessel / Polymers
        // class_id 1 = Water
        // class_id 2 = Minerals / Organic
        const plasticData = result.data.filter(d => d.class_id === 0 && (d.debris_confidence >= 0.20 || d.debris_confidence === undefined));
        const debrisData = result.data.filter(d => d.class_id === 0 && d.debris_confidence < 0.20);
        const cityData = result.data.filter(d => d.class_id === 1);
        const mineralData = result.data.filter(d => d.class_id === 2);

        const plasticLayer = new deck.HexagonLayer({ id: 'plastic-hex', data: plasticData, getPosition: d => [d.lon, d.lat], colorRange: [[255, 51, 51, 230]], radius: 35, coverage: 0.9, opacity: 0.85 });
        const debrisLayer = new deck.HexagonLayer({ id: 'debris-hex', data: debrisData, getPosition: d => [d.lon, d.lat], colorRange: [[255, 140, 0, 220]], radius: 35, coverage: 0.9, opacity: 0.85 });
        const cityLayer = new deck.HexagonLayer({ id: 'city-hex', data: cityData, getPosition: d => [d.lon, d.lat], colorRange: [[0, 102, 255, 140]], radius: 35, coverage: 0.8, opacity: 0.4 });
        const mineralLayer = new deck.HexagonLayer({ id: 'mineral-hex', data: mineralData, getPosition: d => [d.lon, d.lat], colorRange: [[0, 255, 136, 180]], radius: 35, coverage: 0.9, opacity: 0.6 });

        window.deckgl?.setProps({ layers: [cityLayer, mineralLayer, debrisLayer, plasticLayer] });

        if (dash) {
            dash.style.display = "block";
            setTimeout(() => dash.style.opacity = 1, 100);
        }
        document.getElementById('cluster-count').innerText = result.total_clusters;
        document.getElementById('rsi-score').innerText = (result.metrics.fdi_score || result.metrics.rsi_score).toFixed(2);

        const rawDebris = result.metrics.avg_metal;
        const plasticPct = Math.round(rawDebris * 0.55);
        const debrisPct = Math.round(rawDebris - plasticPct);

        document.getElementById('bar-plastic').style.width = plasticPct + '%';
        document.getElementById('bar-metal').style.width = debrisPct + '%';
        document.getElementById('bar-city').style.width = result.metrics.avg_city + '%';
        document.getElementById('bar-minerals').style.width = result.metrics.avg_minerals + '%';

        document.getElementById('txt-plastic').innerText = plasticPct;
        document.getElementById('txt-metal').innerText = debrisPct;
        document.getElementById('txt-city').innerText = result.metrics.avg_city;
        document.getElementById('txt-minerals').innerText = result.metrics.avg_minerals;

        // Render Granular 8-Constituent High-Precision Breakdown
        const breakdownList = document.getElementById('precise-breakdown-list');
        if (breakdownList && result.breakdown && Array.isArray(result.breakdown)) {
            breakdownList.innerHTML = '';
            result.breakdown.forEach(item => {
                breakdownList.innerHTML += `
                    <div style="background:rgba(0,10,30,0.7); border:1px solid rgba(0,102,255,0.18); border-left:3px solid ${item.color}; border-radius:4px; padding:6px 10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                            <span style="font-family:'Share Tech Mono'; font-size:0.7em; color:#cce4ff; letter-spacing:1px;">${item.name}</span>
                            <span style="font-family:'Share Tech Mono'; font-size:0.75em; color:${item.color}; font-weight:bold;">${item.percentage.toFixed(1)}%</span>
                        </div>
                        <div style="background:rgba(0,5,20,0.8); height:4px; border-radius:2px; overflow:hidden;">
                            <div style="background:${item.color}; width:${Math.min(item.percentage, 100)}%; height:100%; transition:width 1.2s ease;"></div>
                        </div>
                    </div>
                `;
            });
        }

        // Calculate dynamic blended market rate and recyclable polymer yield from detected constituents
        let totalValSum = 0;
        let totalPolymerPct = 0;
        if (result.breakdown && Array.isArray(result.breakdown)) {
            result.breakdown.forEach(item => {
                if (item.category === 'plastic' && item.percentage > 0) {
                    const price = RECOVERY_MARKET_RATES[item.id] || 250;
                    totalValSum += (item.percentage / 100.0) * price;
                    totalPolymerPct += item.percentage;
                }
            });
            if (totalPolymerPct > 0) {
                globalValuePerTon = Math.round(totalValSum / (totalPolymerPct / 100.0));
            } else {
                globalValuePerTon = result.intelligence.base_value_per_ton || 250;
            }
        } else {
            globalValuePerTon = result.intelligence.base_value_per_ton || 250;
        }

        // Only solid recyclable polymers contribute to recoverable physical harvest yield
        globalWastePct = totalPolymerPct;

        document.getElementById('roi-zone-type').innerText = result.intelligence.zone_type;
        document.getElementById('roi-value-ton').innerText = formatINR(globalValuePerTon * USD_TO_INR) + '/ton';
        document.getElementById('roi-yield').innerText = globalWastePct.toFixed(1) + "%";
        calculateROI();

        typeWriter("Uplinking to Gemini Core for satellite ocean analysis...", 'ai-insight', 20);

        document.getElementById('gemini-summary').style.display = 'block';
        document.getElementById('gp-zone-type').textContent = result.intelligence.zone_type;
        document.getElementById('gp-rsi').textContent = (result.metrics.fdi_score || result.metrics.rsi_score).toFixed(3);
        document.getElementById('gp-metal').textContent = result.metrics.avg_metal + '%';
        // calculateROI() already synchronized gp-recovery with exact ROI calculation!
        document.getElementById('gemini-zone-label').textContent = '◈ ACTIVE: ' + result.intelligence.zone_type.toUpperCase();
        document.getElementById('topbar-sector').textContent = '◈ TARGET LOCKED: ' + sectorName.toUpperCase();
        document.getElementById('gemini-timestamp').textContent = new Date().toUTCString().slice(17, 25) + ' UTC';

        // Render Dynamic Detected Materials with Exact Percentages
        const matList = document.getElementById('materials-list');
        matList.innerHTML = '';
        
        let detectedList = [];
        if (result.breakdown && Array.isArray(result.breakdown)) {
            detectedList = result.breakdown.filter(b => b.percentage > 1.0 && b.id !== 'water');
        }

        if (detectedList.length > 0) {
            detectedList.forEach((mat) => {
                matList.innerHTML += `
                    <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(0,10,30,0.6);border:1px solid rgba(0,102,255,0.15);
                        border-left:3px solid ${mat.color};
                        border-radius:4px;padding:7px 10px;">
                        <span style="font-family:'Share Tech Mono';font-size:0.75em;color:${mat.color};letter-spacing:1px;">${mat.name} (${mat.percentage.toFixed(1)}%)</span>
                        <span style="font-family:'Share Tech Mono';font-size:0.65em;color:#00ff88;">VERIFIED</span>
                    </div>`;
            });
            document.getElementById('gemini-materials').style.display = 'block';
            window._rcMaterials = detectedList.map(m => m.name);
            if (typeof showRecycleBtn === 'function') showRecycleBtn();
        } else if (result.intelligence.expected_materials) {
            const matArray = result.intelligence.expected_materials.split(',');
            matArray.forEach((mat, i) => {
                const colors = ['#ff3333', '#ffaa00', '#4da6ff', '#00ff88', '#cc88ff'];
                matList.innerHTML += `
                    <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(0,10,30,0.6);border:1px solid rgba(0,102,255,0.15);
                        border-left:3px solid ${colors[i % colors.length]};
                        border-radius:4px;padding:7px 10px;">
                        <span style="font-family:'Share Tech Mono';font-size:0.75em;color:${colors[i % colors.length]};letter-spacing:1px;">${mat.trim()}</span>
                        <span style="font-family:'Share Tech Mono';font-size:0.65em;color:#334466;">DETECTED</span>
                    </div>`;
            });
            document.getElementById('gemini-materials').style.display = 'block';
            window._rcMaterials = result.intelligence.expected_materials.split(',').map(s => s.trim());
            if (typeof showRecycleBtn === 'function') showRecycleBtn();
        }

        const materialsSummary = (detectedList.length > 0)
            ? detectedList.map(d => `${d.name} (${d.percentage.toFixed(1)}%)`).join(', ')
            : result.intelligence.expected_materials;

        const geminiPayload = {
            zone_type: result.intelligence.zone_type,
            materials: materialsSummary,
            rsi: result.metrics.rsi_score,
            fdi: result.metrics.fdi_score || result.metrics.rsi_score,
            waste_pct: result.metrics.avg_metal
        };

        const analyzeUrl = window.location.origin + '/api/analyze';
        const geminiResponse = await fetch(analyzeUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(geminiPayload)
        });
        const gemData = await geminiResponse.json();

        const formatted = `▸ ZONE OVERVIEW\n${gemData.insight}\n\n▸ CONSTITUENTS BREAKDOWN\n${gemData.minerals_breakdown}\n\n▸ RECOVERY PROTOCOL\n${gemData.recommendation}`;
        typeWriter(formatted, 'ai-insight', 18);

    } catch (error) {
        if (orbitalOverlay) {
            orbitalOverlay.classList.remove('orbital-scan-active');
            orbitalOverlay.classList.add('orbital-scan-hidden');
        }
        if (dash) {
            dash.style.display = "block";
            dash.style.opacity = 1;
        }
        typeWriter(`CRITICAL ERROR: ${error.message}\n\n> Verify AquaIntel Core API is online\n> Reposition targeting grid over target ocean waters.`, 'ai-insight', 20);
    } finally {
        if (scanner) scanner.style.display = "none";
        if (orbitalOverlay) {
            orbitalOverlay.classList.remove('orbital-scan-active');
            orbitalOverlay.classList.add('orbital-scan-hidden');
        }
        clearInterval(stepInterval);
        if (statusDiv) statusDiv.style.display = 'none';
        if (btn) {
            btn.innerText = "ACTIVATE TARGETING GRID";
            btn.style.background = "";
            btn.style.borderColor = "";
            btn.disabled = false;
        }
    }
});

window.formatINR = formatINR;
window.typeWriter = typeWriter;
window.toggleGeminiExpand = toggleGeminiExpand;
window.copyGeminiOutput = copyGeminiOutput;
window.calculateROI = calculateROI;
window.resetDashboard = resetDashboard;
