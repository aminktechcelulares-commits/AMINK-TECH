
/* ================= AMINK · Sedes independientes (Chapinero / Modelia) + Gerencia consolidada ================= */
/* Cada sede guarda todo aparte en Supabase (store/<sede>/<sección>): inventario, caja, facturas, clientes, servicios y numeración.
   Gerencia puede entrar a una sede (opera con todos los permisos) o a la vista Consolidada (suma ambas; solo lectura). */
var AMK_PIN = '3sdthmiu';   /* shortcut: PIN único fijo en el código (pedido del cliente); para PIN por perfil, leerlo de S.config.users */
var AMK_USERS = [
  { id: 'us_ger', nombre: 'Gerencia', perfil: 'gerencia', desc: 'Resume y maneja ambas sedes · pide PIN' },
  { id: 'us_cha', nombre: 'Chapinero', perfil: 'sede', sede: 'chapinero', desc: 'Inventario, caja y facturas de Chapinero · pide PIN' },
  { id: 'us_mod', nombre: 'Modelia', perfil: 'sede', sede: 'modelia', desc: 'Inventario, caja y facturas de Modelia · pide PIN' }
];
var AMK_NOMBRE = { chapinero: 'Chapinero', modelia: 'Modelia', todas: 'Consolidado (ambas sedes)' };

/* perfil "sede": opera su sede completa, sin costos, configuración ni anulaciones (eso queda en Gerencia) */
PERFILES.sede = '🏬 Sede';
MENU_PERFIL.sede = MENU_DEF.map(m => m.id).filter(id => !['config', 'finanzas', 'campanas', 'comisiones'].includes(id));
Object.keys(PERM).forEach(k => { if (PERM[k].includes('comercial') || PERM[k].includes('bodega') || k === 'editar_inventario') PERM[k].push('sede'); });

function amkPrepSede() {
  const c = S.config; c.users = (c.users || []).filter(u => !['us_com', 'us_bod'].includes(u.id));
  AMK_USERS.forEach(u => { const x = c.users.find(y => y.id === u.id); if (x) Object.assign(x, { nombre: u.nombre, perfil: u.perfil, sede: u.sede, pin: AMK_PIN }); else c.users.push({ id: u.id, nombre: u.nombre, perfil: u.perfil, sede: u.sede, pin: AMK_PIN, creado: nowISO() }); });
  if (SEDES[SEDE] && c.amkSede !== SEDE) {   /* primera vez en la sede: numeración y caja propias */
    const pre = SEDE === 'chapinero' ? 'CH' : 'MO';
    if (!c.res.pos.actual) c.res.pos.prefijo = pre;
    if (!c.res.cont.actual) c.res.cont.prefijo = 'CT' + pre;
    (c.cajas || []).forEach((k, i) => { if (/^Caja \d+$/.test(k.nombre || '')) k.nombre = 'Caja ' + SEDES[SEDE] + (i ? ' ' + (i + 1) : ''); });
    c.amkSede = SEDE; save('config');
  }
}
let amkQuietUntil = 0;
async function amkUsar(sede) {
  clearTimeout(saveTimer); try { await flush(); } catch (e) { }   /* lo pendiente se guarda en la sede anterior */
  SEDE = sede; try { localStorage.setItem('amk_sede', sede); } catch (e) { }
  LS = 'ef_gestion_v1_' + sede;
  try { SYN = JSON.parse(localStorage.getItem('yt_syn_' + sede) || '{}'); } catch (e) { SYN = {}; }
  dirty.clear(); DBX = null; amkQuietUntil = Date.now() + 4000;
  S = JSON.parse(JSON.stringify(DEFAULTS));
  await initStore();
  await supaStart();
  amkPrepSede(); amkQuietUntil = Date.now() + 1500;
}
/* Consolidado: une las dos sedes en memoria (cada registro lleva _sede). No escribe en la nube. */
async function amkConsolidar() {
  supaState = 'sync'; supaBadge(); DBX = null;
  try {
    const rows = await supaReq('GET', '?path=like.store%2F*&select=path,data');
    const M = JSON.parse(JSON.stringify(DEFAULTS)); let cfg = null; const cats = new Set();
    Object.keys(SEDES).forEach(sd => {
      const pre = 'store/' + sd + '/';
      rows.filter(r => r.path.startsWith(pre)).forEach(r => {
        const k = r.path.slice(pre.length), v = r.data && r.data.v; if (!KEYS.includes(k) || v == null) return;
        if (Array.isArray(DEFAULTS[k]) && Array.isArray(v)) M[k] = M[k].concat(v.map(x => x && typeof x === 'object' ? Object.assign({}, x, { _sede: SEDES[sd] }) : x));
        else if (k === 'config') { if (!cfg) cfg = v; (v.categorias || []).forEach(c => cats.add(c)); }
      });
    });
    if (cfg) M.config = Object.assign({}, cfg, { categorias: [...cats] });
    try { localStorage.setItem(LS, JSON.stringify(M)); } catch (e) { }
    S = JSON.parse(JSON.stringify(DEFAULTS)); await initStore();
    S.products.forEach(v8Ensure);
    supaState = 'ok'; supaBadge();
  } catch (e) { console.warn(e); supaState = 'err'; supaBadge(); toast('No se pudo cargar el consolidado: ' + e.message, '⚠️'); }
  try { render(); } catch (e) { }
}
/* en Consolidado los cambios no se guardan: se avisa */
(function () {
  const _s = save; let warned = 0;
  save = function (...k) {
    if (SEDE === 'todas' && SESSION && Date.now() > amkQuietUntil && Date.now() - warned > 5000) { warned = Date.now(); toast('Vista consolidada: aquí no se guardan cambios. Toca la sede (arriba) y entra a Chapinero o Modelia para registrar.', '⚠️'); }
    return _s(...k);
  };
})();
/* indicador de sede en la barra superior; Gerencia lo usa para cambiar de sede */
function amkBadge() {
  if (!SESSION) return;
  let b = document.getElementById('amkBadge');
  if (!b) { b = document.createElement('button'); b.id = 'amkBadge'; b.type = 'button'; b.className = 'supa-b'; b.style.marginRight = '6px'; b.onclick = amkElegir; const tb = document.querySelector('.topbar .spacer'); if (!tb) return; tb.parentNode.insertBefore(b, tb.nextSibling); }
  b.innerHTML = (SEDE === 'todas' ? '📊 ' : '🏬 ') + '<span>' + esc(AMK_NOMBRE[SEDE] || SEDE) + '</span>' + (perfil() === 'gerencia' ? ' ▾' : '');
  b.style.cursor = perfil() === 'gerencia' ? 'pointer' : 'default';
}
function amkElegir() {
  if (perfil() !== 'gerencia') return;
  modal({ title: 'Cambiar de sede', em: '🏬', body: `<div class="opt-grid" style="grid-template-columns:1fr;gap:10px">${['todas', 'chapinero', 'modelia'].map(s => `<button class="opt" type="button" style="display:flex;align-items:center;gap:12px;padding:14px;${s === SEDE ? 'outline:2px solid var(--blue)' : ''}" onclick="amkIr('${s}')"><span class="em" style="font-size:26px;margin:0">${s === 'todas' ? '📊' : '🏬'}</span><span><b>${AMK_NOMBRE[s]}</b><span class="d" style="display:block;font-size:12.5px">${s === 'todas' ? 'Suma ventas, caja, inventario, reportes y estados financieros · solo lectura' : 'Operar la sede con permisos de Gerencia'}</span></span></button>`).join('')}</div>` });
}
async function amkIr(s) {
  closeModal(); if (s === SEDE) return;
  toast('Cargando ' + AMK_NOMBRE[s] + '…', '☁️');
  const uid0 = SESSION && SESSION.userId;
  await amkUsar(s); SESSION = { userId: uid0 || 'us_ger' };
  try { go('dashboard'); } catch (e) { render(); }
  toast('Estás en ' + AMK_NOMBRE[s], s === 'todas' ? '📊' : '🏬');
}
(function () { const _r = render; render = function () { const out = _r.apply(this, arguments); try { amkBadge(); } catch (e) { } return out; }; })();
