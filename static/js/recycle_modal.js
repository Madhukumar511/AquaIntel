/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* MATERIAL RECYCLING & DISCOVERY MODAL   */
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const RC_DATA = {
    _default: {
        icon: '♻',
        img: 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=400&q=80',
        steps: [
            'Identify the synthetic material from the satellite scan report.',
            'Separate polymer streams at source into rigid and flexible plastics.',
            'Wash and decontaminate to remove saltwater crust and biological fouling.',
            'Transport to certified ocean plastic recovery facilities.',
            'Pelletize clean polymers for high-circularity manufacturing.'
        ]
    },
    plastic: {
        icon: '🧴',
        img: 'https://images.unsplash.com/photo-1604187352050-5e9a7d2ee4e3?w=400&q=80',
        steps: [
            'Separate by polymer density: PET (1), HDPE (2), and PP (5).',
            'Rinse ocean salt and sand to prevent contamination during shredding.',
            'Optical sorter classifies by colour and resin type.',
            'Mechanical shredding produces uniform 5mm flakes.',
            'Wash in caustic soda bath to dissolve adhesive labels and residues.',
            'Extrude clean flakes into high-grade recycled pellets.',
            'Manufacture into ocean-bound certified consumer textiles and containers.'
        ]
    },
    copper: {
        icon: '🔶',
        img: 'https://images.unsplash.com/photo-1609010698086-83523a0a4ef4?w=400&q=80',
        steps: [
            'Extract copper wiring and marine electronics from salvage wreckage.',
            'Strip protective insulation and rubber sheath using mechanical splitters.',
            'Grade into clean Millberry copper (#1) vs mixed wire scrap.',
            'Smelt at 1,085°C in reverberatory furnace.',
            'Cast into cathode plates and export for electrical grid wiring.'
        ]
    },
    aluminium: {
        icon: '⬜',
        img: 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400&q=80',
        steps: [
            'Separate maritime aluminium hulls, masts, and packaging.',
            'Crush and bale to minimize logistic transport volume.',
            'De-coat paints and anodized films via thermal decoating kiln at 500°C.',
            'Melt in rotary induction furnace with minimal fluxing agents.',
            'Recycling saves 95% of energy required to refine primary bauxite.'
        ]
    },
    iron: {
        icon: '⚙️',
        img: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80',
        steps: [
            'Confirm ferrous content using magnetic crane separators.',
            'Gas-axe or hydraulic shear thick marine steel plates.',
            'Feed scrap into Electric Arc Furnace (EAF) with lime flux.',
            'Continuous casting produces billet and structural beams.',
            '100% infinitely recyclable with zero structural degradation.'
        ]
    },
    'e-waste': {
        icon: '💻',
        img: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80',
        steps: [
            'Dismantle navigational transponders and battery casings safely.',
            'Sort Printed Circuit Boards (PCBs) by gold-finger density.',
            'Hydrometallurgical chemical leaching extracts gold, palladium, and copper.',
            'Safely neutralize hazardous lead and cadmium compounds.',
            'Document full chain of custody for international compliance.'
        ]
    },
    steel: {
        icon: '🏗️',
        img: 'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=400&q=80',
        steps: [
            'Segregate marine grade 316 stainless from mild carbon steel.',
            'Decontaminate barnacles and organic coatings.',
            'Melt in basic oxygen furnace or electric arc furnace.',
            'Refine alloy content by Argon Oxygen Decarburization (AOD).',
            'Roll into marine-grade structural plates.'
        ]
    },
    nylon: {
        icon: '🕸️',
        img: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&q=80',
        steps: [
            'Separate tangled synthetic monofilament nets from lead weights.',
            'Chemical depolymerization breaks polymer back to caprolactam monomer.',
            'Purification removes marine salt crystals and degraded additives.',
            'Repolymerize into 100% virgin-equivalent Econyl nylon yarn.',
            'Spin into high-durability apparel, swimwear, and commercial carpet fibers.'
        ]
    },
    microplastic: {
        icon: '🔬',
        img: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80',
        steps: [
            'Surface skim micro-fragments using static electro-coagulation booms.',
            'Centrifugal density separation separates polymer flakes from marine plankton.',
            'Low-temperature catalytic pyrolysis decomposes mixed polymers.',
            'Fractional distillation converts gas output into circular chemical waxes and oils.',
            'Prevents catastrophic bio-accumulation in global marine food webs.'
        ]
    },
    oil: {
        icon: '🛢️',
        img: 'https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?w=400&q=80',
        steps: [
            'Deploy dynamic oleophilic disc skimmers to absorb surface sheen.',
            'Transfer recovered emulsion to onboard decanter centrifuge tanks.',
            'De-emulsify oil from seawater (water discharged at <15 ppm purity).',
            'Heavy hydrocarbon fraction routed to industrial fuel and asphalt blending.',
            'Mitigates oxygen starvation for pelagic surface organisms.'
        ]
    },
    minerals: {
        icon: '💎',
        img: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&q=80',
        steps: [
            'Harvest suspended marine sediment and brine precipitate.',
            'Hydro-cyclone classifies silica sand from mineral salts.',
            'Extract agricultural magnesium chloride and high-purity calcium carbonate.',
            'Use recovered mineral cake in coastal erosion reef restoration blocks.',
            'Zero waste circular utilization.'
        ]
    },
    sargassum: {
        icon: '🌿',
        img: 'https://images.unsplash.com/photo-1544551763-77ef2d0cfc6c?w=400&q=80',
        steps: [
            'Harvest floating Sargassum / algal biomass before beach rotting.',
            'Solar dry and crush into organic seaweed meal.',
            'Extract high-value sodium alginate for pharmaceutical binders.',
            'Anaerobic fermentation yields methane biogas for coastal energy grids.',
            'Residual biomass formulated into organic potassium fertilizer.'
        ]
    }
};

function getRcData(materialName) {
    const key = materialName.toLowerCase().trim();
    if (key.includes('pet') || key.includes('bottle')) return { name: materialName.trim(), ...RC_DATA['plastic'] };
    if (key.includes('nylon') || key.includes('net') || key.includes('ghost')) return { name: materialName.trim(), ...RC_DATA['nylon'] };
    if (key.includes('micro')) return { name: materialName.trim(), ...RC_DATA['microplastic'] };
    if (key.includes('oil') || key.includes('sheen') || key.includes('hydrocarbon')) return { name: materialName.trim(), ...RC_DATA['oil'] };
    if (key.includes('mineral') || key.includes('salt')) return { name: materialName.trim(), ...RC_DATA['minerals'] };
    if (key.includes('sargassum') || key.includes('algae') || key.includes('organic')) return { name: materialName.trim(), ...RC_DATA['sargassum'] };
    if (key.includes('electronic') || key.includes('e-waste')) return { name: materialName.trim(), ...RC_DATA['e-waste'] };
    if (key.includes('scrap metal') || key.includes('metal') || key.includes('steel')) return { name: materialName.trim(), ...RC_DATA['steel'] };
    if (key.includes('debris') || key.includes('plastic') || key.includes('hdpe')) return { name: materialName.trim(), ...RC_DATA['plastic'] };
    
    for (const k in RC_DATA) {
        if (k !== '_default' && key.includes(k)) {
            return { name: materialName.trim(), ...RC_DATA[k] };
        }
    }
    return { name: materialName.trim(), ...RC_DATA._default };
}

function showRecycleBtn() {
    const btn = document.getElementById('recycle-view-btn');
    if (!btn) return;
    btn.style.display = 'block';
    requestAnimationFrame(() => {
        requestAnimationFrame(() => { btn.style.opacity = '1'; });
    });
}

function hideRecycleBtn() {
    const btn = document.getElementById('recycle-view-btn');
    if (btn) {
        btn.style.opacity = '0';
        setTimeout(() => btn.style.display = 'none', 600);
    }
    closeRecycleCards();
}

function openRecycleCards() {
    const modal = document.getElementById('recycle-center-modal');
    const body = document.getElementById('recycle-modal-body');
    if (!modal || !body) return;

    // Extract detected constituents from latest scan
    let detected = [];
    if (window._latestScanBreakdown && Array.isArray(window._latestScanBreakdown)) {
        detected = window._latestScanBreakdown.filter(b => b.percentage > 0.5 && b.id !== 'water');
    } else if (window._rcMaterials && Array.isArray(window._rcMaterials)) {
        detected = window._rcMaterials.map(name => ({ name, percentage: 12.5, color: '#00ff88', category: 'plastic' }));
    }

    const USD_TO_INR = 83.5;
    const VALUE_MAP = {
        pet_bottles: 320,
        hdpe_rigid: 380,
        nylon_nets: 650,
        microplastics: 85,
        oil_sheen: 110,
        minerals: 40,
        sargassum: 55
    };

    // Calculate aggregated telemetry
    let totalPolymerPct = 0;
    let totalValueSum = 0;
    detected.forEach(item => {
        if (item.category === 'plastic' || item.id === 'pet_bottles' || item.id === 'hdpe_rigid' || item.id === 'nylon_nets' || item.id === 'microplastics') {
            totalPolymerPct += item.percentage;
            totalValueSum += item.percentage * (VALUE_MAP[item.id] || 250);
        }
    });
    const blendedRateUSD = totalPolymerPct > 0 ? (totalValueSum / totalPolymerPct) : 250;
    const blendedRateINR = Math.round(blendedRateUSD * USD_TO_INR);

    // Update telemetry bar elements if present
    const tStreams = document.getElementById('rc-telem-streams');
    if (tStreams) tStreams.textContent = `${detected.length} ACTIVE`;
    const tPoly = document.getElementById('rc-telem-polymers');
    if (tPoly) tPoly.textContent = `${totalPolymerPct.toFixed(1)}% YIELD`;
    const tVal = document.getElementById('rc-telem-value');
    if (tVal) tVal.textContent = `₹${blendedRateINR.toLocaleString('en-IN')}/t`;

    if (detected.length === 0) {
        body.innerHTML = `
            <div style="text-align:center; padding:50px 20px; color:#5588aa; font-family:'Share Tech Mono', monospace;">
                <div style="font-size:3em; margin-bottom:15px; color:#00ff88;">✓</div>
                <div style="font-size:1.1em; color:#e8f4ff; letter-spacing:2px; margin-bottom:8px;">SECTOR SCANNED — CLEAR OCEAN WATER</div>
                <div style="font-size:0.8em; color:#5588aa;">Multispectral optical telemetry confirms clear ocean water with zero harvestable debris clusters.</div>
            </div>`;
    } else {
        let cardsHtml = '<div class="rc-grid">';
        detected.forEach(item => {
            const d = getRcData(item.name || item.id);
            const priceUSD = VALUE_MAP[item.id] || 250;
            const priceINR = Math.round(priceUSD * USD_TO_INR);
            const valBadge = priceUSD > 0 
                ? `<span class="rc-val-badge">₹${priceINR.toLocaleString('en-IN')}/t ($${priceUSD})</span>`
                : `<span class="rc-val-badge" style="color:#ffaa00; border-color:rgba(255,170,0,0.3);">HAZARD EXTRACTION</span>`;

            cardsHtml += `
                <div class="rc-card-item" style="border-left-color: ${item.color || '#00ff88'};">
                    <div class="rc-card-top">
                        <div class="rc-hologram-icon" style="color:${item.color || '#00ff88'}; border-color:${item.color || '#00ff88'}55; text-shadow:0 0 12px ${item.color || '#00ff88'}88;">
                            ${d.icon}
                        </div>
                        <div class="rc-meta">
                            <div class="rc-name">${d.name.toUpperCase()}</div>
                            <div class="rc-badges">
                                <span class="rc-pct-badge" style="background:${item.color || '#00ff88'}22; color:${item.color || '#00ff88'}; border:1px solid ${item.color || '#00ff88'}66;">
                                    ${item.percentage ? item.percentage.toFixed(1) + '%' : 'VERIFIED'}
                                </span>
                                ${valBadge}
                            </div>
                            <div class="rc-comp-wrap">
                                <div class="rc-comp-bar" style="background:${item.color || '#00ff88'}; width:${Math.min(item.percentage, 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="rc-steps-list">
                        <div style="font-family:'Share Tech Mono'; font-size:0.73em; color:#00ff88; letter-spacing:1px; margin-bottom:4px;">
                            ◈ RECOVERY & VALORIZATION PROTOCOL (${d.steps.length} STAGES):
                        </div>
                        ${d.steps.slice(0, 3).map((s, idx) => `
                            <div class="rc-step-row">
                                <span class="rc-step-num">[0${idx + 1}]</span>
                                <span>${s}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        });
        cardsHtml += '</div>';
        body.innerHTML = cardsHtml;
    }

    modal.style.display = 'flex';
}

function closeRecycleCards() {
    const modal = document.getElementById('recycle-center-modal');
    if (modal) modal.style.display = 'none';
}

// Global ESC key listener to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeRecycleCards();
});

window.showRecycleBtn = showRecycleBtn;
window.hideRecycleBtn = hideRecycleBtn;
window.openRecycleCards = openRecycleCards;
window.closeRecycleCards = closeRecycleCards;
