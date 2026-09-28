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
    const spans = document.querySelectorAll('#materials-list > div span:first-child');
    let materials = Array.from(spans).map(s => s.textContent.trim()).filter(Boolean);

    if (!materials.length && window._rcMaterials) {
        materials = window._rcMaterials;
    }
    while (materials.length < 4) materials.push('Marine Polymer');
    materials = materials.slice(0, 4);

    materials.forEach((mat, i) => {
        const d = getRcData(mat);
        const card = document.getElementById('rc-card-' + i);
        if (!card) return;

        card.innerHTML = `
            <div class="rc-img-box">
                <img src="${d.img}" alt="${d.name}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                <div class="rc-img-fallback" style="display:none;">${d.icon}</div>
            </div>
            <div class="rc-mat-name">◈ ${d.name}</div>
            <div class="rc-mat-sub">DETECTED SURFACE MATERIAL</div>
            <div class="rc-detail-toggle" onclick="openCenterModal('${mat.replace(/'/g, "\\'")}')">
                <span class="rc-toggle-arrow">▸</span> detail
            </div>
        `;

        const animMap = ['rcCard0In', 'rcCard1In', 'rcCard2In', 'rcCard3In'];
        card.style.animation = 'none';
        card.offsetHeight; // trigger reflow
        card.style.animation = animMap[i] + ' 0.55s cubic-bezier(0.175,0.885,0.32,1.275) ' + (i * 0.1) + 's forwards';
    });

    const overlay = document.getElementById('recycle-overlay');
    if (overlay) overlay.style.display = 'block';
}

function closeRecycleCards() {
    const overlay = document.getElementById('recycle-overlay');
    if (overlay) overlay.style.display = 'none';
}

function openCenterModal(matName) {
    const d = getRcData(matName);
    const modalContent = document.getElementById('detail-modal-content');
    if (!modalContent) return;

    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,255,136,0.3); padding: 20px 40px;">
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 1.4em; color: #00ff88; letter-spacing: 2px;">RECYCLE INTELLIGENCE CORE</div>
            <button onclick="closeCenterModal()" style="background: none; border: none; color: #00ff88; font-size: 1.2em; cursor: pointer; font-family: 'Share Tech Mono', monospace;">✕ CLOSE</button>
        </div>
        <div style="display: flex; flex: 1; overflow: hidden;">
            <div style="flex: 1; padding: 40px; border-right: 1px solid rgba(0,255,136,0.2); display: flex; flex-direction: column; overflow-y: auto;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 1em; color: #4da6ff; letter-spacing: 2px; margin-bottom: 10px;">◈ DETECTED MATERIAL</div>
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 2.5em; color: #fff; text-shadow: 0 0 15px rgba(0,255,136,0.5); margin-bottom: 20px;">${d.name.toUpperCase()}</div>
                <div style="width: 100%; height: 250px; border-radius: 8px; overflow: hidden; border: 1px solid rgba(0,255,136,0.4); box-shadow: 0 0 20px rgba(0,255,136,0.15); margin-bottom: 20px;">
                    <img src="${d.img}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div style="color: #8aaabb; font-size: 1.1em; line-height: 1.6; margin-bottom: 20px;">
                    This synthetic constituent was identified via multispectral light bandwidth telemetry.<br>
                    Follow the verified circular economy steps to capture and recycle recovered waste.
                </div>
                <div style="background: rgba(0,255,136,0.05); border-left: 3px solid #00ff88; padding: 15px; border-radius: 4px;">
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.8em; color: #00ff88; letter-spacing: 1px; margin-bottom: 5px;">◈ RECOVERY STEPS</div>
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 1.2em; color: #fff;">${d.steps.length} STAGES IDENTIFIED</div>
                </div>
            </div>
            <div style="flex: 1.5; padding: 40px; overflow-y: auto;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 1em; color: #4da6ff; letter-spacing: 2px; margin-bottom: 10px;">♻ RECOVERY PROTOCOL</div>
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 1.8em; color: #fff; margin-bottom: 30px;">CIRCULAR PROCESS — ${d.name.toUpperCase()}</div>
                <div>
                    ${d.steps.map((s, idx) => `
                        <div style="display: flex; gap: 15px; background: rgba(0,255,136,0.05); padding: 20px; border-left: 3px solid #00ff88; border-radius: 6px; margin-bottom: 15px; opacity: 0; transform: translateX(30px); animation: slideInRight 0.5s ease forwards ${idx * 0.1}s;">
                            <div style="color: #00ff88; font-family: 'Share Tech Mono', monospace; font-size: 1.5em; font-weight: bold;">${String(idx + 1).padStart(2, '0')}</div>
                            <div style="color: #e8f4ff; font-size: 1.1em; line-height: 1.6;">${s}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    const wrapper = document.getElementById('detail-modal-wrapper');
    if (wrapper) wrapper.style.display = 'block';
}

function closeCenterModal() {
    const wrapper = document.getElementById('detail-modal-wrapper');
    const content = document.getElementById('detail-modal-content');
    if (!wrapper || !content) return;
    content.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
    content.style.opacity = '0';
    content.style.transform = 'scale(0.97)';
    setTimeout(() => {
        wrapper.style.display = 'none';
        content.style.transition = '';
        content.style.opacity = '';
        content.style.transform = '';
    }, 260);
}

window.showRecycleBtn = showRecycleBtn;
window.hideRecycleBtn = hideRecycleBtn;
window.openRecycleCards = openRecycleCards;
window.closeRecycleCards = closeRecycleCards;
window.openCenterModal = openCenterModal;
window.closeCenterModal = closeCenterModal;
