import * as THREE from './vendor/three.module.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';

/* ---------- catalogue data ---------- */

/* Two lines on one page: fine jewellery and a lower-priced demi-fine line. */
const TIERS = [
  { id: 'fine', name: 'Fine', label: 'Fine jewellery' },
  { id: 'demi', name: 'Demi-fine', label: 'Demi-fine' },
];
const METALS = [
  { id: 'yellow', name: '18k yellow gold', demi: 'Gold vermeil', color: '#EDBE5F', factor: 1 },
  { id: 'rose', name: '18k rose gold', demi: 'Rose gold vermeil', color: '#E6A48B', factor: 1 },
  { id: 'white', name: '18k white gold', demi: 'Sterling silver', color: '#E9E7E1', factor: 1.03 },
  { id: 'platinum', name: 'Platinum', demi: 'Rhodium on silver', color: '#D5D9DD', factor: 1.12 },
];
const GEMS = [
  { id: 'diamond', name: 'Lab diamond', demi: 'Moissanite', tint: '#FFFFFF', core: '#F4F7FF', rate: 45000, demiRate: 1800 },
  { id: 'sapphire', name: 'Sapphire', demi: 'Lab sapphire', tint: '#2550D8', core: '#3F6CFF', rate: 30000, demiRate: 600 },
  { id: 'emerald', name: 'Emerald', demi: 'Lab emerald', tint: '#0C9A58', core: '#22C07A', rate: 35000, demiRate: 700 },
  { id: 'ruby', name: 'Ruby', demi: 'Lab ruby', tint: '#CF1340', core: '#FF3A5E', rate: 38000, demiRate: 650 },
];
/* Width is the stone's width in mm at 1 carat. Ratio is length over width. Prongs are angles in degrees. */
const SHAPES = [
  { id: 'round', name: 'Round', width: 6.5, ratio: 1, outline: 'circle' },
  { id: 'oval', name: 'Oval', width: 5.7, ratio: 1.36, outline: 'circle' },
  { id: 'cushion', name: 'Cushion', width: 5.8, ratio: 1.05, outline: 'cushion' },
  { id: 'princess', name: 'Princess', width: 5.5, ratio: 1, outline: 'square' },
  { id: 'emerald', name: 'Emerald cut', width: 5.0, ratio: 1.38, outline: 'octagon', corner: 0.16, step: true },
  { id: 'asscher', name: 'Asscher', width: 5.5, ratio: 1, outline: 'octagon', corner: 0.21, step: true },
  { id: 'radiant', name: 'Radiant', width: 5.3, ratio: 1.25, outline: 'octagon', corner: 0.09 },
  { id: 'pear', name: 'Pear', width: 5.5, ratio: 1.55, outline: 'pear', prongs: [0, 105, 155, 205, 255], upright: true },
  { id: 'marquise', name: 'Marquise', width: 5.0, ratio: 2, outline: 'marquise', prongs: [0, 65, 115, 180, 245, 295], upright: true },
  { id: 'heart', name: 'Heart', width: 6.5, ratio: 1, outline: 'heart', prongs: [180, 50, 310], upright: true },
];
const AGES = [
  { id: '20s', name: '20s', i: 0 },
  { id: '30s', name: '30s', i: 1 },
  { id: '45+', name: '45+', i: 2 },
];
const LIGHTS = [
  { id: 'studio', name: 'Studio', env: 'studio', exposure: 1.05, tint: '#FFFFFF' },
  { id: 'day', name: 'Daylight', env: 'day', exposure: 1.0, tint: '#F3F7FF', bg: '#DDE5EC' },
  { id: 'golden', name: 'Golden hour', env: 'golden', exposure: 1.02, tint: '#FFE9CC', bg: '#E8D0B0' },
  { id: 'candle', name: 'Candlelight', env: 'candle', exposure: 1.05, tint: '#FFD6A8', bg: '#3A2A1E', dark: true },
  { id: 'phone', name: 'Phone snap', env: 'phone', exposure: 0.78, tint: '#FFFFFF', bg: '#B5A88F', rough: 0.3 },
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
const FINGER = { label: 'Finger size', options: ['Slim, 15.3 mm', 'Medium, 16.5 mm', 'Broad, 18.4 mm'] };
const FITS = {
  solitaire: FINGER, halo: FINGER, eternity: FINGER,
  pendant: { label: 'Chain length', options: ['16 inch', '18 inch', '20 inch'] },
  bracelet: { label: 'Wrist size', options: ['15 cm', '16.5 cm', '18 cm'] },
};
const INNER_R = [7.65, 8.25, 9.2];
const PRODUCTS = [
  { id: 'solitaire', kind: 'Ring', name: 'Aria Solitaire', base: 28000, demi: 2400, shapes: true, build: buildSolitaire,
    caratLabel: 'Carat', setting: 'Four prong', blurb: 'One stone, four prongs, a plain band. The stone sits high so light gets in from the sides.' },
  { id: 'halo', kind: 'Ring', name: 'Noor Halo', base: 42000, demi: 3200, shapes: true, build: buildHalo,
    caratLabel: 'Centre carat', setting: 'Halo, four prong', blurb: 'A ring of small stones around the centre makes it look about half a carat larger.' },
  { id: 'eternity', kind: 'Band', name: 'Eternity Band', base: 36000, demi: 3600, shapes: false, build: buildEternity,
    caratLabel: 'Total carat', setting: 'Shared prong, 24 stones', blurb: 'Twenty four matched stones all the way round. Worn alone or stacked.' },
  { id: 'studs', kind: 'Earrings', name: 'Tara Studs', base: 18000, demi: 1800, shapes: true, build: buildStuds,
    caratLabel: 'Carat per ear', setting: 'Four prong basket', blurb: 'A matched pair in low baskets, so they sit close to the ear.' },
  { id: 'pendant', kind: 'Pendant', name: 'Drop Pendant', base: 16000, demi: 1900, shapes: true, build: buildPendant,
    caratLabel: 'Carat', setting: 'Four prong, fixed bail', blurb: 'A single stone on a fine chain. Sits just below the collarbone.' },
  { id: 'bracelet', kind: 'Bracelet', name: 'Line Bracelet', base: 85000, demi: 5500, shapes: false, build: buildBracelet,
    caratLabel: 'Carat', setting: 'Cup set, 46 stones', blurb: 'One unbroken line of stones. Total weight is three times the figure shown on the slider.' },
];

const state = { tier: 'fine', age: '30s', fit: 1, product: 'solitaire', metal: 'yellow', gem: 'diamond', shape: 'round', carat: 1.2, tone: 'none', shot: 'hero', light: 'studio' };
const $ = (id) => document.getElementById(id);
const find = (list, id) => list.find((x) => x.id === id);
const inr = (n) => 'Rs ' + new Intl.NumberFormat('en-IN').format(Math.round(n / 100) * 100);
const isDemi = () => state.tier === 'demi';
const metalName = (m) => (isDemi() ? m.demi : m.name);
const gemName = (g) => (isDemi() ? g.demi : g.name);
const ageIndex = () => find(AGES, state.age).i;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- geometry helpers ---------- */

const UP = new THREE.Vector3(0, 1, 0);
const V = (x, y, z) => new THREE.Vector3(x, y, z);

/* Girdle outline seen from above, fitted to a 1 by 1 box. */
const outlineCache = {};
function outlineOf(shapeId) {
  if (outlineCache[shapeId]) return outlineCache[shapeId];
  const def = find(SHAPES, shapeId);
  const ring = (n, f) => Array.from({ length: n }, (_, i) => f((i / n) * Math.PI * 2));
  const pointy = (t) => Math.sin(t) * Math.sqrt(Math.max(0, 1 - Math.pow(Math.abs(Math.cos(t)), 3)));
  let pts;
  if (def.outline === 'square') {
    pts = ring(16, (t) => { const k = 1 / Math.max(Math.abs(Math.cos(t)), Math.abs(Math.sin(t))); return [Math.cos(t) * k, Math.sin(t) * k]; });
  } else if (def.outline === 'octagon') {
    const c = def.corner * 2;
    const v = [[1 - c, 1], [-1 + c, 1], [-1, 1 - c], [-1, -1 + c], [-1 + c, -1], [1 - c, -1], [1, -1 + c], [1, 1 - c]];
    pts = v.flatMap((p, i) => { const q = v[(i + 1) % 8]; return [p, [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]]; });
  } else if (def.outline === 'cushion') {
    const e = (x) => Math.sign(x) * Math.pow(Math.abs(x), 2 / 3.2);
    pts = ring(24, (t) => [e(Math.cos(t)), e(Math.sin(t))]);
  } else if (def.outline === 'marquise') {
    pts = ring(24, (t) => [Math.cos(t), pointy(t)]);
  } else if (def.outline === 'pear') {
    pts = ring(24, (t) => [Math.cos(t), Math.cos(t) > 0 ? pointy(t) : Math.sin(t)]);
  } else if (def.outline === 'heart') {
    pts = ring(32, (t) => [13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t), 16 * Math.pow(Math.sin(t), 3)]);
  } else {
    pts = ring(16, (t) => [Math.cos(t), Math.sin(t)]);
  }
  const xs = pts.map((p) => p[0]), zs = pts.map((p) => p[1]);
  const [x0, x1, z0, z1] = [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)];
  outlineCache[shapeId] = pts.map(([x, z]) => [(x - (x0 + x1) / 2) / (x1 - x0), (z - (z0 + z1) / 2) / (z1 - z0)]);
  return outlineCache[shapeId];
}

/* Stacks scaled copies of the outline into a faceted stone. Each row is [height, scale]; scale 0 is a point. */
function facetted(outline, rows) {
  const pos = [];
  const at = ([y, k], i) => { const [x, z] = outline[i % outline.length]; return [x * k, y, z * k]; };
  for (let r = 0; r < rows.length - 1; r++) {
    for (let i = 0; i < outline.length; i++) {
      const a0 = at(rows[r], i), a1 = at(rows[r], i + 1), b0 = at(rows[r + 1], i), b1 = at(rows[r + 1], i + 1);
      if (rows[r][1] > 0) pos.push(...a0, ...a1, ...b1);
      if (rows[r + 1][1] > 0) pos.push(...a0, ...b1, ...b0);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.computeVertexNormals();
  return g;
}
const BRILLIANT = [[-0.43, 0], [-0.2, 0.54], [-0.015, 1], [0.015, 1], [0.09, 0.8], [0.15, 0.56], [0.15, 0]];
const STEP = [[-0.42, 0], [-0.33, 0.4], [-0.18, 0.76], [-0.02, 1], [0.02, 1], [0.09, 0.84], [0.15, 0.66], [0.15, 0]];
const geoCache = {};
function stoneGeometry(shapeId) {
  if (!geoCache[shapeId]) {
    const rows = find(SHAPES, shapeId).step ? STEP : BRILLIANT;
    const o = outlineOf(shapeId);
    geoCache[shapeId] = { shell: facetted(o, rows), core: facetted(o, rows.slice(0, 3)) };
  }
  return geoCache[shapeId];
}
/* Point on the girdle in the direction of an angle, in mm. */
function rimPoint(shapeId, deg, l, w) {
  const a = (deg * Math.PI) / 180;
  let best = [l / 2, 0], bd = Infinity;
  for (const [x, z] of outlineOf(shapeId)) {
    const d = Math.abs(((Math.atan2(z * w, x * l) - a) % (2 * Math.PI) + 3 * Math.PI) % (2 * Math.PI) - Math.PI);
    if (d < bd) { bd = d; best = [x * l, z * w]; }
  }
  return best;
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
  core.rotation.y = 0.12;
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
  const pr = w * 0.045 + 0.13;
  for (const deg of find(SHAPES, shape).prongs || [45, 135, 225, 315]) {
    const [rx, rz] = rimPoint(shape, deg, l, w);
    const px = rx * 0.97, pz = rz * 0.97;
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

/* ---------- display forms: the body the piece is shown on in shot six ---------- */

function lathe(pts, mat, seg = 48) {
  return new THREE.Mesh(new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), seg), mat);
}
function handForm(r, mats, age = 1) {
  const g = new THREE.Group();
  const geo = lathe([[0, -47], [r * 1.14, -46], [r * 1.1, -30], [r * 1.02, -12], [r, 0], [r, 5], [r * [1.06, 1.09, 1.15][age], 13], [r, 21],
    [r * 0.93, 32], [r * 0.8, 40], [r * 0.55, 44.5], [0, 46]], mats.skin, 40).geometry;
  const finger = (x, y, z, s) => {
    const m = new THREE.Mesh(geo, mats.skin);
    m.rotation.x = Math.PI / 2;
    m.position.set(x, y, z);
    m.scale.setScalar(s);
    g.add(m);
  };
  const off = 2.05 * r + 4.5;
  finger(0, 0, 0, 1);
  finger(-off, -0.6, 7, 1.04);
  finger(off, -1, -11, 0.88);
  const palm = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), mats.skin);
  palm.scale.set(r * 4.7, r * 1.2, 30);
  palm.position.set(0, -r * 0.3, -66);
  g.add(palm);
  return { group: g, center: V(0, r * 0.5, 3), radius: 25, dir: V(0.22, 1, -0.6), hide: [] };
}
function armForm(rw, mats) {
  const g = new THREE.Group();
  const arm = lathe([[0, -98], [1.45, -94], [1.3, -60], [1.1, -25], [1, 0], [1.02, 10], [1.14, 24], [1.22, 38], [1.12, 54], [0.8, 64], [0, 68]]
    .map(([f, y]) => [f * rw, y]), mats.skin);
  arm.scale.set(1.12, 1, 0.86);
  g.add(arm);
  return { group: g, center: V(0, 2, 0), radius: 40, dir: V(0.3, 0.32, 1), hide: [] };
}
const BUST = [[-150, 96], [-110, 94], [-70, 88], [-35, 78], [-12, 66], [0, 58], [10, 52], [22, 47], [45, 44], [75, 45], [92, 47]];
function bustR(y) {
  if (y <= BUST[0][0]) return BUST[0][1];
  for (let i = 1; i < BUST.length; i++) {
    if (y <= BUST[i][0]) {
      const [y0, r0] = BUST[i - 1], [y1, r1] = BUST[i];
      return r0 + ((r1 - r0) * (y - y0)) / (y1 - y0);
    }
  }
  return BUST[BUST.length - 1][1];
}
function bustForm(drop, w, chainTopY, mats) {
  const g = new THREE.Group();
  const zc = -bustR(-drop) - w * 0.55;
  const bust = lathe(BUST.map(([y, r]) => [r, y]), mats.skin, 64);
  bust.scale.x = 1.3;
  bust.position.set(0, drop, zc);
  g.add(bust);
  const yF = chainTopY - drop, pts = [];
  for (let i = 0; i < 120; i++) {
    const th = (i / 120) * Math.PI * 2, k = Math.abs(Math.sin(th / 2));
    const yb = yF + (26 - yF) * Math.pow(k, 1.1);
    const rho = bustR(yb) + 0.5 + w * 0.55 * Math.pow(1 - k, 6);
    pts.push(V(1.3 * rho * Math.sin(th), yb + drop, zc + rho * Math.cos(th)));
  }
  g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 360, 0.42, 8, true), mats.metal));
  return { group: g, center: V(0, drop * 0.55, 0), radius: drop * 0.75 + 34, dir: V(0.1, 0.04, 1), hide: [] };
}
function earForm(gap, w, mats, age = 1) {
  const g = new THREE.Group();
  const blob = (sx, sy, sz, x, y, z, tilt = 0) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), mats.skin);
    m.scale.set(sx, sy, sz);
    m.position.set(x, y, z);
    m.rotation.z = tilt;
    g.add(m);
  };
  const lz = -w * 0.5 - 4.2;
  blob(7.6 + age * 0.7, 8.4 + age * 1.1, 4, gap, -age * 0.7, lz); // lobe, fuller with age
  blob(14, 30, 4.5, gap + 3, 24, lz - 0.5, -0.2);     // ear
  blob(92, 112, 74, gap - 11, 32, lz - 73);           // head
  blob(50, 120, 45, gap + 2, -150, lz - 78);          // neck
  return { group: g, center: V(gap - 2, 12, 0), radius: 40, dir: V(0.3, 0.08, 1), hide: [] };
}

/* ---------- pieces ---------- */

function buildSolitaire(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  const BAND_R = INNER_R[c.fit] + 0.9;
  g.add(new THREE.Mesh(new THREE.TorusGeometry(BAND_R, 0.9, 24, 120), mats.metal));
  const h = head(c.shape, size, mats);
  h.position.y = BAND_R + 0.5 + size.w * 0.47;
  g.add(h);
  return { form: handForm(INNER_R[c.fit] - 0.05, mats, c.age), group: g, focus: h.position.clone(), focusSize: size.l, size, top: V(0, 1, 0.001), profile: V(1, 0.14, 0.1), hero: V(0.75, 0.62, 1.25), shadow: true };
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
  const BAND_R = INNER_R[c.fit] + 1.05;
  g.add(new THREE.Mesh(new THREE.TorusGeometry(BAND_R, 1.05, 24, 120), mats.metal));
  g.add(ringOfStones(n, d, (t) => {
    const nrm = V(Math.cos(t), Math.sin(t), 0);
    return { pos: nrm.clone().multiplyScalar(BAND_R + 0.72 + d * 0.2), normal: nrm };
  }, mats));
  return { form: handForm(INNER_R[c.fit] - 0.05, mats, c.age), group: g, focus: V(0, BAND_R + 1, 0), focusSize: 9, size: { w: d, l: d }, top: V(0, 1, 0.001), profile: V(1, 0.14, 0.1), hero: V(0.8, 0.55, 1.2), shadow: true };
}

function buildStuds(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  const gap = size.l / 2 + 3.2;
  for (const sx of [-1, 1]) {
    const h = head(c.shape, size, mats);
    h.add(rod(V(0, -size.w * 0.5, 0), V(0, -size.w * 0.5 - 8, 0), 0.38, mats.metal));
    h.rotation.set(Math.PI / 2, find(SHAPES, c.shape).upright ? Math.PI / 2 : 0, 0);
    h.position.x = sx * gap;
    g.add(h);
  }
  const form = earForm(gap, size.w, mats, c.age);
  form.hide.push(g.children[0]);
  return { form, group: g, focus: V(gap, 0, 0), focusSize: size.l, size, top: V(0, 0.001, 1), profile: V(1, 0.18, 0.3), hero: V(0.45, 0.3, 1.3), shadow: false };
}

function buildPendant(c, mats) {
  const size = stoneSize(c.carat, c.shape);
  const g = new THREE.Group();
  const h = head(c.shape, size, mats);
  const upright = find(SHAPES, c.shape).upright;
  h.rotation.set(Math.PI / 2, upright ? Math.PI / 2 : 0, 0);
  g.add(h);
  const bailY = (upright ? size.l : size.w) / 2 + 1.5;
  const bail = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.32, 12, 32), mats.metal);
  bail.position.y = bailY;
  bail.rotation.y = Math.PI / 2;
  g.add(bail);
  const pts = [V(-24, 32, -5), V(-13, 15, -1.5), V(0, bailY + 0.75, 0), V(13, 15, -1.5), V(24, 32, -5)];
  const chain = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 120, 0.3, 8), mats.metal);
  g.add(chain);
  const form = bustForm([38, 62, 88][c.fit], size.w, bailY + 0.75, mats);
  form.hide.push(chain);
  return { form, group: g, focus: V(0, 0, 0), focusSize: size.l, size, top: V(0, 0.001, 1), profile: V(1, 0.1, 0.45), hero: V(0.35, 0.05, 1.3), shadow: false, frame: { center: V(0, 9, 0), radius: 17 } };
}

function buildBracelet(c, mats) {
  const n = 46, rw = [150, 165, 180][c.fit] / (2 * Math.PI), R = rw * 1.12 + 1.3;
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
  return { form: armForm(rw, mats), group: g, focus: V(0, 0, R), focusSize: 10, size: { w: d, l: d }, top: V(0, 1, 0.001), profile: V(0.2, 0.12, 1), hero: V(0.5, 0.75, 1.1), shadow: true };
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
  } else if (kind === 'day') {
    room('#8C99A6');
    panel(20, 0.2, 20, 0, 14, 0, '#EEF4FF', 5);        // sky
    panel(0.2, 16, 12, -14, 3, 0, '#F5F9FF', 9);       // window
    panel(10, 2, 0.2, 3, 0, 14, '#FFFFFF', 3);
    panel(18, 0.2, 18, 0, -14, 0, '#FFFFFF', 1.4);
    for (const [x, y, z] of [[-6, 9, -14], [11, 8, 14], [-14, 11, -8]]) panel(0.7, 0.7, 0.7, x, y, z, '#FFFFFF', 40);
  } else if (kind === 'golden') {
    room('#8E7A66');
    panel(0.2, 8, 14, -14, -1, 2, '#FFD2A0', 13);      // low sun
    panel(20, 0.2, 20, 0, 14, 0, '#FFF3E2', 4);        // open sky
    panel(0.2, 10, 3, 14, 3, -5, '#FFE6C8', 6);
    panel(10, 2, 0.2, 3, 0, 14, '#FFFFFF', 3);
    for (const [x, y, z] of [[-6, 6, -14], [11, 5, 14], [-14, 2, -8], [5, 9, -14]]) panel(0.7, 0.7, 0.7, x, y, z, '#FFD08A', 45);
  } else if (kind === 'candle') {
    room('#5A4636');
    for (const [x, z] of [[-9, 9], [8, 10], [-11, -7]]) panel(2, 3, 2, x, -3, z, '#FFC690', 30); // candles
    panel(20, 0.2, 20, 0, 14, 0, '#FFE8CF', 1.6);      // warm room light
    for (const [x, y, z] of [[-6, 9, -14], [5, 11, -14], [11, 8, 14], [-10, 10, 14], [14, 4, 8]]) panel(0.6, 0.6, 0.6, x, y, z, '#FFB262', 70);
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
    skin: new THREE.MeshStandardMaterial({ metalness: 0, roughness: 0.58, side: THREE.DoubleSide, envMapIntensity: 0.62 }),
    metal: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.13 }),
    shell: new THREE.MeshPhysicalMaterial({ metalness: 0, roughness: 0, transmission: 1, ior: 1.9, thickness: 0.25, dispersion: 2,
      flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.5, attenuationDistance: 6 }),
    core: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.04, flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.4 }),
    small: new THREE.MeshStandardMaterial({ metalness: 1, roughness: 0.03, flatShading: true, side: THREE.DoubleSide, envMapIntensity: 1.7 }),
  };
}

function stageColor() {
  const L = find(LIGHTS, state.light);
  if (L.id === 'phone') return L.bg;
  const tone = find(TONES, state.tone);
  if (tone.color && state.shot !== 'model') return tone.color;
  if (L.bg) return L.bg;
  return getComputedStyle(document.documentElement).getPropertyValue('--stage').trim() || '#E3E7E9';
}

function applyLook() {
  const metal = find(METALS, state.metal), g = find(GEMS, state.gem);
  mats.metal.color.set(metal.color);
  mats.skin.color.set(find(TONES, state.tone).color || TONES[3].color);
  const worn = state.shot === 'model';
  current.form.group.visible = worn;
  for (const o of current.form.hide) o.visible = !worn;
  shadowMesh.visible = current.shadow && !worn;
  mats.shell.color.set(g.id === 'diamond' ? '#FFFFFF' : g.tint).lerp(new THREE.Color('#FFFFFF'), g.id === 'diamond' ? 0 : 0.45);
  mats.shell.attenuationColor.set(g.tint);
  mats.core.color.set(g.core);
  mats.small.color.set(g.core);
  const L = find(LIGHTS, state.light), tint = new THREE.Color(L.tint);
  mats.core.color.multiply(tint);
  mats.small.color.multiply(tint);
  scene.environment = envs[L.env];
  mats.core.envMap = mats.small.envMap = L.id === 'phone' ? envs.phone : envs.gem;
  renderer.toneMappingExposure = L.exposure;
  mats.metal.roughness = L.rough ?? 0.13;
  mats.skin.roughness = [0.5, 0.58, 0.68][ageIndex()];
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
  current = product.build({ carat: state.carat, shape: product.shapes ? state.shape : 'round', fit: state.fit, age: ageIndex() }, mats);
  scene.add(current.group);
  const box = new THREE.Box3().setFromObject(current.group);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  current.center = current.frame ? current.frame.center : sphere.center;
  current.radius = current.frame ? current.frame.radius : sphere.radius;
  shadowMesh.position.set(sphere.center.x, box.min.y - 0.05, sphere.center.z);
  shadowMesh.scale.set(Math.max(box.max.x - box.min.x, 6) * 1.7, Math.max(box.max.z - box.min.z, 6) * 1.7, 1);
  current.group.add(current.form.group);
}

/* Where the camera sits for each of the six shots. */
function shotPose(id) {
  const fit = (r) => (r / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2))) * 0.98;
  const c = current.center, r = current.radius;
  if (id === 'model') {
    const f = current.form;
    return { target: f.center.clone(), pos: f.center.clone().add(f.dir.clone().normalize().multiplyScalar(fit(f.radius))) };
  }
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
  controls.maxDistance = Math.max(current.radius, id === 'model' ? current.form.radius : 0) * 9;
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

function fromPrice(p) { return inr(isDemi() ? p.demi + 900 : p.base + 15000); }
function price() {
  const p = find(PRODUCTS, state.product), g = find(GEMS, state.gem), m = find(METALS, state.metal);
  const stones = p.id === 'studs' ? 2 : p.id === 'bracelet' ? 3 : 1;
  if (isDemi()) return p.demi + g.demiRate * Math.pow(state.carat, 1.3) * stones;
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
  $('metal-pick').textContent = metalName(m);
  $('gem-pick').textContent = gemName(g);
  $('age-pick').textContent = state.age;
  $('shape-pick').textContent = shape.name;
  $('carat-label').textContent = p.caratLabel;
  $('carat-pick').textContent = state.carat.toFixed(1) + ' ct';
  $('tone-pick').textContent = find(TONES, state.tone).name;
  $('shape-opt').hidden = !p.shapes;
  const mm = shape.ratio === 1 ? `${w.toFixed(1)} mm` : `${l.toFixed(1)} x ${w.toFixed(1)} mm`;
  const rows = [['Line', find(TIERS, state.tier).label], ['Stone', gemName(g)], ['Shape', shape.name], [p.caratLabel, state.carat.toFixed(2) + ' ct'],
    [p.shapes ? 'Stone size' : 'Each stone', mm], ['Metal', metalName(m)], ['Setting', p.setting]];
  if (FITS[p.id]) rows.push([FITS[p.id].label, FITS[p.id].options[state.fit]]);
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
  pressed($('lights'), state.light);
  pressed($('tiers'), state.tier);
  pressed($('ages'), state.age);
  for (const b of $('gems').children) b.textContent = gemName(find(GEMS, b.dataset.id));
  for (const b of $('metals').children) { const n = metalName(find(METALS, b.dataset.id)); b.title = n; b.setAttribute('aria-label', n); }
  for (const b of $('rail').children) b.lastElementChild.textContent = 'from ' + fromPrice(find(PRODUCTS, b.dataset.id));
  const L = find(LIGHTS, state.light);
  $('stage').dataset.dark = String(!!L.dark && (state.shot === 'model' || find(TONES, state.tone).id === 'none'));
  $('hint').textContent = state.shot === 'model'
    ? 'Display form, not a photo. The piece is exact.'
    : 'Drag to turn. Scroll or pinch to zoom.';
  const fit = FITS[p.id];
  $('fit-opt').hidden = !fit;
  if (fit) {
    $('fit-label').textContent = fit.label;
    $('fit-pick').textContent = fit.options[state.fit];
    [...$('fits').children].forEach((b, i) => { b.textContent = fit.options[i]; b.setAttribute('aria-pressed', String(i === state.fit)); });
  }
  $('toast').textContent = '';
}

function setShot(id, instant) {
  state.shot = id;
  if ((id === 'tone' || id === 'model') && state.tone === 'none') state.tone = 't3';
  applyLook();
  goToShot(id === 'tone' ? 'hero' : id, instant);
  refreshText();
}
function update(shapeChanged) {
  if (shapeChanged) { rebuild(); applyLook(); goToShot(state.shot === 'tone' ? 'hero' : state.shot, true); }
  applyLook();
  refreshText();
}

function buildInterface() {
  buttons($('rail'), PRODUCTS, 'product', (b, p) => {
    b.setAttribute('role', 'listitem');
    b.innerHTML = `<span class="ph"></span><b></b><span></span>`;
    b.children[1].textContent = p.name;
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
  for (let i = 0; i < 3; i++) {
    const b = document.createElement('button');
    b.type = 'button';
    b.addEventListener('click', () => { state.fit = i; update(true); });
    $('fits').append(b);
  }
  $('carat').addEventListener('input', (e) => { state.carat = Number(e.target.value); update(true); });
  $('see-model').addEventListener('click', () => { setShot('model'); $('stage').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' }); });
  buttons($('lights'), LIGHTS, 'light', (b, l) => { b.textContent = l.name; }, () => update(false));
  buttons($('tiers'), TIERS, 'tier', (b, t) => { b.textContent = t.name; }, () => update(false));
  buttons($('ages'), AGES, 'age', (b, a) => { b.textContent = a.name; }, () => { update(true); if (state.shot !== 'model') setShot('model'); });
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
  envs = Object.fromEntries(['studio', 'phone', 'gem', 'day', 'golden', 'candle'].map((k) => [k, makeEnv(k)]));
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
