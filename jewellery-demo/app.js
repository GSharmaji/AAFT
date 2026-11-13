import * as THREE from './vendor/three.module.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';

/* ---------- catalogue data ---------- */

const METALS = [
  { id: 'yellow', name: '18k yellow gold', color: '#EDBE5F', factor: 1 },
  { id: 'rose', name: '18k rose gold', color: '#E6A48B', factor: 1 },
  { id: 'white', name: '18k white gold', color: '#E9E7E1', factor: 1.03 },
  { id: 'platinum', name: 'Platinum', color: '#D5D9DD', factor: 1.12 },
];
const GEMS = [
  { id: 'diamond', name: 'Lab diamond', tint: '#FFFFFF', core: '#F4F7FF', rate: 45000 },
  { id: 'sapphire', name: 'Sapphire', tint: '#2550D8', core: '#3F6CFF', rate: 30000 },
  { id: 'emerald', name: 'Emerald', tint: '#0C9A58', core: '#22C07A', rate: 35000 },
  { id: 'ruby', name: 'Ruby', tint: '#CF1340', core: '#FF3A5E', rate: 38000 },
];
const SHAPES = [
  { id: 'round', name: 'Round', width: 6.5, ratio: 1 },
  { id: 'oval', name: 'Oval', width: 5.7, ratio: 1.36 },
  { id: 'emerald', name: 'Emerald cut', width: 5.0, ratio: 1.38 },
];
const TONES = [
  { id: 'none', name: 'Studio grey', color: null },
  { id: 't1', name: 'Fair', color: '#F2DCCB' },
  { id: 't2', name: 'Light', color: '#E3BE9F' },
  { id: 't3', name: 'Medium', color: '#CC9B76' },
  { id: 't4', name: 'Tan', color: '#A97550' },
  { id: 't5', name: 'Brown', color: '#7C5136' },
  { id: 't6', name: 'Deep', color: '#4A2F22' },
];
const SHOTS = [
  { id: 'hero', name: 'Hero' },
  { id: 'profile', name: 'Profile' },
  { id: 'top', name: 'Top' },
  { id: 'detail', name: 'Detail' },
  { id: 'tone', name: 'On tone' },
  { id: 'model', name: 'On model' },
];
const PRODUCTS = [
  { id: 'solitaire', kind: 'Ring', name: 'Aria Solitaire', base: 28000, shapes: true, build: buildSolitaire,
    caratLabel: 'Carat', setting: 'Four prong', blurb: 'One stone, four prongs, a plain band. The stone sits high so light gets in from the sides.' },
  { id: 'halo', kind: 'Ring', name: 'Noor Halo', base: 42000, shapes: true, build: buildHalo,
    caratLabel: 'Centre carat', setting: 'Halo, four prong', blurb: 'A ring of small stones around the centre makes it look about half a carat larger.' },
  { id: 'eternity', kind: 'Band', name: 'Eternity Band', base: 36000, shapes: false, build: buildEternity,
    caratLabel: 'Total carat', setting: 'Shared prong, 24 stones', blurb: 'Twenty four matched stones all the way round. Worn alone or stacked.' },
  { id: 'studs', kind: 'Earrings', name: 'Tara Studs', base: 18000, shapes: true, build: buildStuds,
    caratLabel: 'Carat per ear', setting: 'Four prong basket', blurb: 'A matched pair in low baskets, so they sit close to the ear.' },
  { id: 'pendant', kind: 'Pendant', name: 'Drop Pendant', base: 16000, shapes: true, build: buildPendant,
    caratLabel: 'Carat', setting: 'Four prong, fixed bail', blurb: 'A single stone on a fine chain. Sits just below the collarbone.' },
  { id: 'bracelet', kind: 'Bracelet', name: 'Line Bracelet', base: 85000, shapes: false, build: buildBracelet,
    caratLabel: 'Carat', setting: 'Cup set, 46 stones', blurb: 'One unbroken line of stones. Total weight is three times the figure shown on the slider.' },
];

const state = { product: 'solitaire', metal: 'yellow', gem: 'diamond', shape: 'round', carat: 1.2, tone: 'none', shot: 'hero', light: 'studio' };
const $ = (id) => document.getElementById(id);
const find = (list, id) => list.find((x) => x.id === id);
const inr = (n) => 'Rs ' + new Intl.NumberFormat('en-IN').format(Math.round(n / 100) * 100);
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- geometry helpers ---------- */

const UP = new THREE.Vector3(0, 1, 0);
const V = (x, y, z) => new THREE.Vector3(x, y, z);

function stoneGeometry(shape) {
  // Profile is for a stone 1 unit wide: culet at the bottom, table on top, girdle at y = 0.
  const P = (r, y) => new THREE.Vector2(r, y);
  if (shape === 'emerald') {
    const pts = [P(0, -0.42), P(0.2, -0.33), P(0.38, -0.18), P(0.5, -0.02), P(0.5, 0.02), P(0.42, 0.09), P(0.33, 0.15), P(0, 0.15)];
    return {
      shell: new THREE.LatheGeometry(pts, 8, Math.PI / 8).toNonIndexed(),
      core: new THREE.LatheGeometry(pts.slice(0, 4), 8, Math.PI / 8).toNonIndexed(),
    };
  }
  const pts = [P(0, -0.43), P(0.5, -0.015), P(0.5, 0.015), P(0.4, 0.09), P(0.28, 0.15), P(0, 0.15)];
  return {
    shell: new THREE.LatheGeometry(pts, 16).toNonIndexed(),
    core: new THREE.LatheGeometry([P(0, -0.43), P(0.27, -0.2), P(0.5, -0.015)], 16, Math.PI / 16).toNonIndexed(),
  };
}
const smallStoneGeo = new THREE.LatheGeometry(
  [new THREE.Vector2(0, -0.43), new THREE.Vector2(0.5, 0), new THREE.Vector2(0.3, 0.15), new THREE.Vector2(0, 0.15)], 8).toNonIndexed();

function rod(a, b, r, mat) {
  const dir = b.clone().sub(a);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, dir.length(), 12), mat);
  m.position.copy(a).add(b).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(UP, dir.normalize());
  return m;
}
function ellipseTube(a, b, r, y, mat) {
  const pts = [];
  for (let i = 0; i < 48; i++) { const t = (i / 48) * Math.PI * 2; pts.push(V(Math.cos(t) * a, y, Math.sin(t) * b)); }
  return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 96, r, 10, true), mat);
}
function stoneSize(carat, shapeId) {
  const s = find(SHAPES, shapeId);
  const w = s.width * Math.cbrt(carat);
  return { w, l: w * s.ratio, ratio: s.ratio };
}

/* A full gem: clear outer shell plus a mirrored core, which gives the inner sparkle. */
function gem(shape, w, ratio, mats) {
  const g = new THREE.Group();
  const geo = stoneGeometry(shape);
  const shell = new THREE.Mesh(geo.shell, mats.shell);
  const core = new THREE.Mesh(geo.core, mats.core);
  core.scale.setScalar(0.96);
  g.add(core, shell);
  g.scale.set(w * ratio, w, w);
  return g;
}

/* Stone in a four prong basket. Girdle at y = 0, table facing +y. */
function head(shape, size, mats) {
  const { w, l, ratio } = size;
  const g = new THREE.Group();
  g.add(gem(shape, w, ratio, mats));
  g.add(ellipseTube(l * 0.36, w * 0.36, w * 0.05 + 0.12, -w * 0.2, mats.metal));
  const k = shape === 'emerald' ? 0.9 : 0.97;
  const pr = w * 0.045 + 0.13;
  for (let i = 0; i < 4; i++) {
    const a = Math.PI / 4 + (i * Math.PI) / 2;
    const px = (Math.cos(a) * l * k) / 2, pz = (Math.sin(a) * w * k) / 2;
    g.add(rod(V(px * 0.4, -w * 0.46, pz * 0.4), V(px, w * 0.1, pz), pr, mats.metal));
    const tip = new THREE.Mesh(new THREE.SphereGeometry(pr * 1.25, 12, 10), mats.metal);
    tip.position.set(px * 0.93, w * 0.13, pz * 0.93);
    g.add(tip);
  }
  const base = new THREE.Mesh(new THREE.CylinderGeometry(w * 0.2, w * 0.14, w * 0.12, 16), mats.metal);
  base.position.y = -w * 0.47;
  g.add(base);
  return g;
}

function ringOfStones(count, d, place, mats) {
  const inst = new THREE.InstancedMesh(smallStoneGeo, mats.small, count);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = V(d, d, d);
  for (let i = 0; i < count; i++) {
    const { pos, normal } = place((i / count) * Math.PI * 2);
    q.setFromUnitVectors(UP, normal);
    inst.setMatrixAt(i, m.compose(pos, q, s));
  }
  return inst;
}

const BAND_R = 9.2;

/* ---------- pieces ---------- */

function buildSolitaire(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.TorusGeometry(BAND_R, 0.9, 24, 120), mats.metal));
  const h = head(c.shape, size, mats);
  h.position.y = BAND_R + 0.5 + size.w * 0.47;
  g.add(h);
  return { group: g, focus: h.position.clone(), focusSize: size.l, size, top: V(0, 1, 0.001), profile: V(1, 0.14, 0.1), hero: V(0.75, 0.62, 1.25), shadow: true };
}

function buildHalo(c, mats) {
  const out = buildSolitaire(c, mats);
  const { w, l } = out.size;
  const a = l / 2 + 0.95, b = w / 2 + 0.95, y = out.focus.y - w * 0.04;
  const n = Math.round((Math.PI * (a + b)) / 1.42);
  const halo = ringOfStones(n, 1.28, (t) => ({ pos: V(Math.cos(t) * a, y, Math.sin(t) * b), normal: UP }), mats);
  out.group.add(halo, ellipseTube(a, b, 0.7, y - 0.42, mats.metal));
  out.focusSize = l + 3;
  return out;
}

function buildEternity(c, mats) {
  const n = 24;
  const d = Math.min(6.5 * Math.cbrt(c.carat / n), 2.45);
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.TorusGeometry(BAND_R, 1.05, 24, 120), mats.metal));
  g.add(ringOfStones(n, d, (t) => {
    const nrm = V(Math.cos(t), Math.sin(t), 0);
    return { pos: nrm.clone().multiplyScalar(BAND_R + 0.72 + d * 0.2), normal: nrm };
  }, mats));
  return { group: g, focus: V(0, BAND_R + 1, 0), focusSize: 9, size: { w: d, l: d }, top: V(0, 1, 0.001), profile: V(1, 0.14, 0.1), hero: V(0.8, 0.55, 1.2), shadow: true };
}

function buildStuds(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  const gap = size.l / 2 + 3.2;
  for (const sx of [-1, 1]) {
    const h = head(c.shape, size, mats);
    h.add(rod(V(0, -size.w * 0.5, 0), V(0, -size.w * 0.5 - 8, 0), 0.38, mats.metal));
    h.rotation.x = Math.PI / 2;
    h.position.x = sx * gap;
    g.add(h);
  }
  return { group: g, focus: V(gap, 0, 0), focusSize: size.l, size, top: V(0, 0.001, 1), profile: V(1, 0.18, 0.3), hero: V(0.45, 0.3, 1.3), shadow: false };
}

function buildPendant(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  const h = head(c.shape, size, mats);
  h.rotation.x = Math.PI / 2;
  g.add(h);
  const bailY = size.w / 2 + 1.5;
  const bail = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.32, 12, 32), mats.metal);
  bail.position.y = bailY;
  bail.rotation.y = Math.PI / 2;
  g.add(bail);
  const pts = [V(-24, 32, -5), V(-13, 15, -1.5), V(0, bailY + 0.75, 0), V(13, 15, -1.5), V(24, 32, -5)];
  g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 120, 0.3, 8), mats.metal));
  return { group: g, focus: V(0, 0, 0), focusSize: size.l, size, top: V(0, 0.001, 1), profile: V(1, 0.1, 0.45), hero: V(0.35, 0.05, 1.3), shadow: false, frame: { center: V(0, 9, 0), radius: 17 } };
}

function buildBracelet(c, mats) {
  const n = 46, R = 27;
  const d = Math.min(6.5 * Math.cbrt((c.carat * 3) / n), 3.45);
  const g = new THREE.Group();
  const place = (off) => (t) => {
    const nrm = V(Math.cos(t), 0, Math.sin(t));
    return { pos: nrm.clone().multiplyScalar(R + off), normal: nrm };
  };
  g.add(ringOfStones(n, d, place(d * 0.22), mats));
  const cups = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.56, 0.42, 0.55, 16), mats.metal, n);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = V(d, d, d);
  for (let i = 0; i < n; i++) {
    const { pos, normal } = place(-d * 0.12)((i / n) * Math.PI * 2);
    cups.setMatrixAt(i, m.compose(pos, q.setFromUnitVectors(UP, normal), s));
  }
  g.add(cups, ellipseTube(R - d * 0.3, R - d * 0.3, d * 0.2, 0, mats.metal));
  return { group: g, focus: V(0, 0, R), focusSize: 10, size: { w: d, l: d }, top: V(0, 1, 0.001), profile: V(0.2, 0.12, 1), hero: V(0.5, 0.75, 1.1), shadow: true };
}

/* ---------- renderer ---------- */

let renderer, scene, camera, controls, envs, mats, current, shadowMesh;
const canvas = $('view');

function makeEnv(kind) {
  const s = new THREE.Scene();
  const panel = (w, h, d, x, y, z, color, power) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(power) }));
    mesh.position.set(x, y, z);
    s.add(mesh);
  };
  const room = (color) => s.add(new THREE.Mesh(new THREE.BoxGeometry(30, 30, 30), new THREE.MeshBasicMaterial({ color, side: THREE.BackSide })));
  if (kind === 'studio') {
    room('#62676D');
    panel(20, 0.2, 20, 0, 14, 0, '#FFFFFF', 6);        // overhead softbox
    panel(0.2, 18, 5, -14, 2, 4, '#FFF4E6', 11);       // warm key strip
    panel(0.2, 14, 3, 14, 4, -5, '#E8F1FF', 9);        // cool rim strip
    panel(10, 2, 0.2, 3, 0, 14, '#FFFFFF', 5);         // front fill
    panel(18, 0.2, 18, 0, -14, 0, '#FFFFFF', 1.6);     // floor bounce
    for (const [x, y, z] of [[-6, 9, -14], [5, 11, -14], [11, 8, 14], [-10, 10, 14], [-14, 11, -8], [14, 12, 8]]) {
      panel(0.7, 0.7, 0.7, x, y, z, '#FFFFFF', 60);    // pin lights, for glints on facets
    }
  } else if (kind === 'gem') {
    // Bright room broken up by dark and very bright patches: facets pick up a light and dark pattern.
    room('#D5DCE4');
    let seed = 7;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < 64; i++) {
      const dir = V(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize().multiplyScalar(13.5);
      const bright = i % 2 === 0;
      const sz = bright ? 1 + rnd() * 1.6 : 1.8 + rnd() * 2.4;
      panel(sz, sz, sz, dir.x, dir.y, dir.z, bright ? '#FFFFFF' : '#1B2026', bright ? 30 : 1);
    }
  } else {
    room('#8F8672');
    panel(8, 0.2, 8, 3, 14, 2, '#FFE9C4', 2.2);        // one ceiling bulb
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  const tex = pmrem.fromScene(s, 0.03).texture;
  pmrem.dispose();
  return tex;
}

function makeMaterials() {
  return {
    metal: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.13 }),
    shell: new THREE.MeshPhysicalMaterial({ metalness: 0, roughness: 0, transmission: 1, ior: 1.9, thickness: 0.25, dispersion: 2,
      flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.5, attenuationDistance: 6 }),
    core: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.04, flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.4 }),
    small: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.03, flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.7 }),
  };
}

function stageColor() {
  if (state.light === 'phone') return '#B5A88F';
  const tone = find(TONES, state.tone);
  if (tone.color) return tone.color;
  return getComputedStyle(document.documentElement).getPropertyValue('--stage').trim() || '#E3E7E9';
}

function applyLook() {
  const metal = find(METALS, state.metal), g = find(GEMS, state.gem);
  mats.metal.color.set(metal.color);
  mats.shell.color.set(g.id === 'diamond' ? '#FFFFFF' : g.tint).lerp(new THREE.Color('#FFFFFF'), g.id === 'diamond' ? 0 : 0.45);
  mats.shell.attenuationColor.set(g.tint);
  mats.core.color.set(g.core);
  mats.small.color.set(g.core);
  const phone = state.light === 'phone';
  scene.environment = phone ? envs.phone : envs.studio;
  mats.core.envMap = mats.small.envMap = phone ? envs.phone : envs.gem;
  renderer.toneMappingExposure = phone ? 0.78 : 1.05;
  mats.metal.roughness = phone ? 0.3 : 0.13;
  scene.background = new THREE.Color(stageColor());
}

function shadowTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const x = c.getContext('2d');
  const grad = x.createRadialGradient(64, 64, 4, 64, 64, 64);
  grad.addColorStop(0, 'rgba(0,0,0,0.26)');
  grad.addColorStop(0.5, 'rgba(0,0,0,0.08)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = grad;
  x.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

function rebuild() {
  if (current) {
    scene.remove(current.group);
    current.group.traverse((o) => { if (o.geometry && o.geometry !== smallStoneGeo) o.geometry.dispose(); });
  }
  const product = find(PRODUCTS, state.product);
  current = product.build({ carat: state.carat, shape: product.shapes ? state.shape : 'round' }, mats);
  scene.add(current.group);
  const box = new THREE.Box3().setFromObject(current.group);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  current.center = current.frame ? current.frame.center : sphere.center;
  current.radius = current.frame ? current.frame.radius : sphere.radius;
  shadowMesh.visible = current.shadow;
  shadowMesh.position.set(sphere.center.x, box.min.y - 0.05, sphere.center.z);
  shadowMesh.scale.set(Math.max(box.max.x - box.min.x, 6) * 1.7, Math.max(box.max.z - box.min.z, 6) * 1.7, 1);
}

/* Where the camera sits for each of the six shots. */
function shotPose(id) {
  const fit = (r) => (r / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2))) * 0.98;
  const c = current.center, r = current.radius;
  if (id === 'detail') {
    const dist = fit(current.focusSize * 0.75);
    return { target: current.focus.clone(), pos: current.focus.clone().add(current.hero.clone().lerp(current.top, 0.35).normalize().multiplyScalar(dist)) };
  }
  const dir = id === 'profile' ? current.profile : id === 'top' ? current.top : current.hero;
  return { target: c.clone(), pos: c.clone().add(dir.clone().normalize().multiplyScalar(fit(r))) };
}

let tween = null;
function goToShot(id, instant) {
  const pose = shotPose(id);
  if (instant || reduceMotion) {
    camera.position.copy(pose.pos);
    controls.target.copy(pose.target);
    tween = null;
  } else {
    tween = { start: performance.now(), p0: camera.position.clone(), t0: controls.target.clone(), p1: pose.pos, t1: pose.target };
  }
  controls.minDistance = current.focusSize * 1.2;
  controls.maxDistance = current.radius * 9;
}

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

let visible = true, idleSince = 0;
function frame(now) {
  requestAnimationFrame(frame);
  if (!visible || document.hidden) return;
  if (tween) {
    const t = Math.min(1, (now - tween.start) / 650);
    const e = 1 - Math.pow(1 - t, 3);
    camera.position.lerpVectors(tween.p0, tween.p1, e);
    controls.target.lerpVectors(tween.t0, tween.t1, e);
    if (t === 1) tween = null;
  }
  controls.autoRotate = !reduceMotion && !tween && state.shot === 'hero' && now - idleSince > 2500;
  controls.update();
  renderer.render(scene, camera);
}

/* ---------- interface ---------- */

function pressed(container, id) {
  for (const b of container.children) b.setAttribute('aria-pressed', String(b.dataset.id === id));
}
function buttons(container, list, key, render, onPick) {
  for (const item of list) {
    const b = document.createElement('button');
    b.type = 'button';
    b.dataset.id = item.id;
    render(b, item);
    b.addEventListener('click', () => { state[key] = item.id; onPick(item); });
    container.append(b);
  }
}

function price() {
  const p = find(PRODUCTS, state.product), g = find(GEMS, state.gem), m = find(METALS, state.metal);
  const stones = p.id === 'studs' ? 2 : p.id === 'bracelet' ? 3 : 1;
  return (p.base + g.rate * Math.pow(state.carat, 1.6) * stones) * m.factor;
}

function refreshText() {
  const p = find(PRODUCTS, state.product), g = find(GEMS, state.gem), m = find(METALS, state.metal);
  const shape = find(SHAPES, p.shapes ? state.shape : 'round');
  const { w, l } = current.size;
  $('piece-kind').textContent = p.kind;
  $('piece-name').textContent = p.name;
  $('blurb').textContent = p.blurb;
  $('price').textContent = inr(price());
  $('metal-pick').textContent = m.name;
  $('gem-pick').textContent = g.name;
  $('shape-pick').textContent = shape.name;
  $('carat-label').textContent = p.caratLabel;
  $('carat-pick').textContent = state.carat.toFixed(1) + ' ct';
  $('tone-pick').textContent = find(TONES, state.tone).name;
  $('shape-opt').hidden = !p.shapes;
  const mm = shape.ratio === 1 ? `${w.toFixed(1)} mm` : `${l.toFixed(1)} x ${w.toFixed(1)} mm`;
  const rows = [['Stone', g.name], ['Shape', shape.name], [p.caratLabel, state.carat.toFixed(2) + ' ct'],
    [p.shapes ? 'Stone size' : 'Each stone', mm], ['Metal', m.name], ['Setting', p.setting]];
  $('spec').replaceChildren(...rows.flatMap(([k, v]) => {
    const dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = k; dd.textContent = v;
    return [dt, dd];
  }));
  pressed($('rail'), state.product);
  pressed($('metals'), state.metal);
  pressed($('gems'), state.gem);
  pressed($('shapes'), state.shape);
  pressed($('tones'), state.tone);
  pressed($('shots'), state.shot);
  $('light-studio').setAttribute('aria-pressed', String(state.light === 'studio'));
  $('light-phone').setAttribute('aria-pressed', String(state.light === 'phone'));
  $('slot').hidden = state.shot !== 'model';
  $('hint').hidden = state.shot === 'model';
  $('toast').textContent = '';
}

function setShot(id, instant) {
  state.shot = id;
  if (id === 'tone' && state.tone === 'none') state.tone = 't3';
  if (id !== 'model') goToShot(id === 'tone' ? 'hero' : id, instant);
  applyLook();
  refreshText();
}
function update(shapeChanged) {
  if (shapeChanged) { rebuild(); goToShot(state.shot === 'model' || state.shot === 'tone' ? 'hero' : state.shot, true); }
  applyLook();
  refreshText();
}

function buildInterface() {
  buttons($('rail'), PRODUCTS, 'product', (b, p) => {
    b.setAttribute('role', 'listitem');
    b.innerHTML = `<span class="ph"></span><b></b><span></span>`;
    b.children[1].textContent = p.name;
    b.children[2].textContent = 'from ' + inr(p.base + 15000);
  }, () => { rebuild(); setShot('hero', true); });
  buttons($('metals'), METALS, 'metal', (b, m) => { b.style.setProperty('--sw', m.color); b.title = m.name; b.setAttribute('aria-label', m.name); }, () => update(false));
  buttons($('gems'), GEMS, 'gem', (b, g) => { b.textContent = g.name; }, () => update(false));
  buttons($('shapes'), SHAPES, 'shape', (b, s) => { b.textContent = s.name; }, () => update(true));
  buttons($('tones'), TONES, 'tone', (b, t) => { b.style.setProperty('--sw', t.color || 'var(--stage)'); b.title = t.name; b.setAttribute('aria-label', t.name); }, () => {
    if (state.light === 'phone') state.light = 'studio';
    update(false);
  });
  buttons($('shots'), SHOTS, 'shot', (b, s) => {
    b.innerHTML = `<i></i><span></span>`;
    b.children[0].textContent = String(SHOTS.indexOf(s) + 1).padStart(2, '0');
    b.children[1].textContent = s.name;
  }, (s) => setShot(s.id));
  $('carat').addEventListener('input', (e) => { state.carat = Number(e.target.value); update(true); });
  $('light-studio').addEventListener('click', () => { state.light = 'studio'; update(false); });
  $('light-phone').addEventListener('click', () => { state.light = 'phone'; update(false); });
  $('buy').addEventListener('click', () => { $('toast').textContent = 'Added. This is a sample store, so nothing is charged or shipped.'; });
}

/* Small pictures for the collection row, rendered once from the same 3D pieces. */
function renderThumbs() {
  const keep = { ...state };
  renderer.setSize(320, 320, false);
  camera.aspect = 1;
  camera.updateProjectionMatrix();
  for (const b of $('rail').children) {
    Object.assign(state, { product: b.dataset.id, shape: 'round', carat: 1.2, shot: 'hero', tone: 'none', light: 'studio' });
    rebuild();
    applyLook();
    goToShot('hero', true);
    camera.lookAt(controls.target);
    renderer.render(scene, camera);
    const img = new Image();
    img.alt = '';
    img.src = canvas.toDataURL('image/jpeg', 0.86);
    b.querySelector('.ph').replaceWith(img);
  }
  Object.assign(state, keep);
}

function start() {
  buildInterface();
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  } catch (err) {
    $('fallback').hidden = false;
    canvas.hidden = true;
    $('hint').hidden = true;
    return;
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(28, 1, 0.5, 2000);
  controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.autoRotateSpeed = 0.9;
  controls.addEventListener('start', () => { idleSince = Infinity; tween = null; });
  controls.addEventListener('end', () => { idleSince = performance.now(); });
  envs = { studio: makeEnv('studio'), phone: makeEnv('phone'), gem: makeEnv('gem') };
  mats = makeMaterials();
  shadowMesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: shadowTexture(), transparent: true, depthWrite: false }));
  shadowMesh.rotation.x = -Math.PI / 2;
  scene.add(shadowMesh);

  renderThumbs();
  rebuild();
  resize();
  setShot('hero', true);

  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(canvas);
  const themeChanged = () => { if (scene) applyLook(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChanged);
  new MutationObserver(themeChanged).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  requestAnimationFrame(frame);
}

start();
