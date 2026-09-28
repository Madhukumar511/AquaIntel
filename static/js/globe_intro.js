/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* ORBITAL 3D GLOBE INITIALIZATION (Three.js)*/
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

(function () {
    const canvas = document.getElementById('globe-canvas');
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(420, 420);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.z = 2.5;

    const geo = new THREE.SphereGeometry(1, 64, 64);
    const loader = new THREE.TextureLoader();
    loader.crossOrigin = 'anonymous';
    const earthTex = loader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
    const bumpTex = loader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
    const specTex = loader.load('https://unpkg.com/three-globe/example/img/earth-water.png');

    const mat = new THREE.MeshPhongMaterial({
        map: earthTex,
        bumpMap: bumpTex,
        bumpScale: 0.05,
        specularMap: specTex,
        specular: new THREE.Color(0x2255aa),
        shininess: 15
    });
    const earth = new THREE.Mesh(geo, mat);
    scene.add(earth);

    const atmosGeo = new THREE.SphereGeometry(1.02, 64, 64);
    const atmosMat = new THREE.MeshPhongMaterial({
        color: 0x0044cc,
        transparent: true,
        opacity: 0.08,
        side: THREE.FrontSide
    });
    scene.add(new THREE.Mesh(atmosGeo, atmosMat));

    const sun = new THREE.DirectionalLight(0xffffff, 1.2);
    sun.position.set(5, 3, 5);
    scene.add(sun);
    scene.add(new THREE.AmbientLight(0x112244, 0.6));

    const baseTargetY = -(77.59 + 90) * (Math.PI / 180);
    const targetRotX = (12.97) * (Math.PI / 180);
    let targetRotY = baseTargetY;
    earth.rotation.y = baseTargetY - 1.5;

    let startTime = null;
    let phase = 'spin';
    const SPIN_DURATION = 3000;
    const ZOOM_DURATION = 2000;

    const statusMsgs = [
        'INITIALIZING ORBITAL LINK...',
        'ACQUIRING SATELLITE LOCK...',
        'TRIANGULATING GLOBAL SECTOR...',
        'DEPLOYING ASTER SENSOR ARRAY...',
        'UPLINK ESTABLISHED — ENTERING ATMOSPHERE'
    ];
    let msgIdx = 0;
    const statusEl = document.getElementById('globe-status');
    const progressEl = document.getElementById('globe-progress');

    const msgInterval = setInterval(() => {
        msgIdx = Math.min(msgIdx + 1, statusMsgs.length - 1);
        if (statusEl) statusEl.textContent = statusMsgs[msgIdx];
        if (progressEl) progressEl.style.width = ((msgIdx + 1) / statusMsgs.length * 100) + '%';
    }, 900);

    function easeInOut(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    function animate(ts) {
        if (!startTime) startTime = ts;
        const elapsed = ts - startTime;
        requestAnimationFrame(animate);

        if (phase === 'spin') {
            earth.rotation.y += 0.005;
            if (elapsed > SPIN_DURATION) {
                phase = 'zoomin';
                startTime = ts;
                const currentY = earth.rotation.y % (Math.PI * 2);
                let diff = baseTargetY - currentY;
                while (diff < -Math.PI) diff += Math.PI * 2;
                while (diff > Math.PI) diff -= Math.PI * 2;
                targetRotY = earth.rotation.y + diff;
            }
        } else if (phase === 'zoomin') {
            const t = Math.min(elapsed / ZOOM_DURATION, 1);
            const ease = easeInOut(t);
            earth.rotation.y = earth.rotation.y + (targetRotY - earth.rotation.y) * 0.05;
            earth.rotation.x = earth.rotation.x + (targetRotX - earth.rotation.x) * 0.05;
            camera.position.z = 2.5 - ease * 1.8;

            if (t >= 1) {
                phase = 'done';
                clearInterval(msgInterval);
                if (statusEl) statusEl.textContent = 'UPLINK ESTABLISHED — ENTERING ATMOSPHERE';
                if (progressEl) progressEl.style.width = '100%';

                setTimeout(() => {
                    const intro = document.getElementById('globe-intro');
                    if (intro) {
                        intro.style.transition = 'opacity 0.8s ease';
                        intro.style.opacity = '0';
                    }
                    const uiPanel = document.getElementById('ui-panel');
                    if (uiPanel) {
                        uiPanel.style.opacity = '1';
                        uiPanel.style.pointerEvents = 'auto';
                    }
                    const geminiPanel = document.getElementById('gemini-panel');
                    if (geminiPanel) {
                        geminiPanel.style.opacity = '1';
                        geminiPanel.style.pointerEvents = 'auto';
                    }
                    setTimeout(() => {
                        if (intro) intro.style.display = 'none';
                    }, 800);
                }, 600);
            }
        }
        renderer.render(scene, camera);
    }
    requestAnimationFrame(animate);
})();
