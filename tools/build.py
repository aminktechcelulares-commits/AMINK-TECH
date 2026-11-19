"""Genera site/admin.html y site/index.html de AMINK TECH a partir de la plantilla Tecno Phone.
Uso: python build.py <anon_key> [correo_admin]"""
import base64, re, sys, pathlib

ROOT = pathlib.Path(__file__).parent
SRC = pathlib.Path(r"C:/Users/USUARIO/Downloads")
KEY = sys.argv[1] if len(sys.argv) > 1 else ''
MAIL = sys.argv[2] if len(sys.argv) > 2 else ''
URL = 'https://qgnmoeyrbicdwjxnbfwd.supabase.co'
OLD_URL = 'https://ksfabuzurjxofapqoonc.supabase.co'

b64 = lambda p: 'data:image/png;base64,' + base64.b64encode((ROOT / 'brand' / p).read_bytes()).decode()
MARK, MARK128, WORD, WORD_L = b64('mark256.png'), b64('mark128.png'), b64('wordmark.png'), b64('wordmark-light.png')


def sub(txt, pat, rep, count=0, flags=0, expect=None):
    new, n = re.subn(pat, rep, txt, count=count, flags=flags)
    if n == 0 or (expect is not None and n != expect):
        raise SystemExit(f'patrón {pat[:70]!r}: {n} coincidencias (esperadas {expect or ">0"})')
    return new


def rep(txt, old, new, expect=None):
    n = txt.count(old)
    if n == 0 or (expect is not None and n != expect):
        raise SystemExit(f'texto {old[:70]!r}: {n} coincidencias (esperadas {expect or ">0"})')
    return txt.replace(old, new)


COLORS = [  # plantilla (teal Tecno Phone) -> AMINK TECH
    ('#1B2126', '#0D1B2A'), ('#0B7C8C', '#1B3A5C'), ('#0E93A5', '#2563EB'), ('#19C1D6', '#3B82F6'),
    ('#A3E4EE', '#93C5FD'), ('#E7F8FB', '#DBEAFE'), ('#F3FBFD', '#EFF6FF'),
    ('#0E3940', '#132B55'), ('#0B2A30', '#0E1C36'), ('#1E8595', '#1E4FB8'), ('#12262B', '#131F35'), ('#0F1C20', '#0E1726'),
    ('#0B8091', '#1D4ED8'), ('#13A6B9', '#2F6FED'), ('#0D5562', '#1E3A8A'), ('#173540', '#16294A'), ('#24414B', '#22355A'),
    ('#2A3A42', '#253247'), ('#121C22', '#0B1422'), ('#EDF2F4', '#EEF3FA'), ('#EEF3F5', '#EFF4FB'), ('#E9F0F3', '#E8EFFA'),
    ('14,147,165', '37,99,235'), ('25,193,214', '59,130,246'), ('11,128,145', '29,78,216'), ('27,33,38', '13,27,42'), ('12,48,58', '13,27,42'), ('8,20,26', '6,14,26'),
]


def recolor(t):
    for a, b in COLORS:
        t = re.sub(re.escape(a), b, t, flags=re.I)
    return t


# ------------------------------------------------------------------ admin.html
a = (SRC / 'admin.html').read_text(encoding='utf-8')
a = recolor(a)
a = sub(a, r'<link rel="icon" href="favicon\.ico"[^>]*>', f'<link rel="icon" href="{MARK128}">', expect=1)
a = sub(a, r'(<link rel="apple-touch-icon" href=")data:image/png;base64,[^"]*', r'\g<1>' + MARK, expect=1)
a = sub(a, r'<img src="data:image/png;base64,[^"]*"( alt="Logo" data-logo)', f'<img src="{MARK}"' + r'\1', expect=2)
a = sub(a, r'const LOGO_DEF = "data:image/png;base64,[^"]*"', f'const LOGO_DEF = "{MARK}"', expect=1)
a = rep(a, OLD_URL, URL, expect=1)
a = sub(a, r"(const SUPA = \{ url: '[^']*', key: ')[^']*'", r"\g<1>" + KEY + "'", expect=1)
a = rep(a, '<meta name="description" content="PubliFuturo Gestión — ERP', '<meta name="description" content="AMINK TECH Gestión — ERP')
for old in ('tecnophoneapplestore@gmail.com',):
    a = a.replace(old, MAIL)
a = rep(a, "<div class=\"brand-sub\" id=\"bizSub\">Ibagué</div>", "<div class=\"brand-sub\" id=\"bizSub\">Tecnology</div>", expect=1)
a = rep(a, "ciudad: 'Ibagué, Tolima', regimen", "ciudad: '', regimen", expect=1)
a = rep(a, "sub: 'Tecnología · Accesorios · Servicio técnico', nit", "sub: 'Tu mundo en buenas manos', nit", expect=1)
a = rep(a, "c.sub = 'Tecnología · Accesorios · Servicio técnico'", "c.sub = 'Tu mundo en buenas manos'", expect=1)
a = rep(a, "categorias: ['Accesorios', 'Cargadores y cables', 'Audífonos y parlantes', 'Power bank y tomas', 'Relojes smart', 'Herramientas y repuestos', 'Pantallas', 'Baterías', 'Computación']",
        "categorias: ['Celulares', 'Accesorios', 'Forros y protectores', 'Cargadores y cables', 'Audífonos y parlantes', 'Relojes smart', 'Repuestos', 'Servicio técnico']", expect=1)
# catálogo inicial y datos de la tienda anterior: fuera
a = sub(a, r'var TP_SEED = \[.*?\];\n', 'var TP_SEED = [];\n', count=1, flags=re.S)
a = rep(a, "var TP_CATS = ['Audífonos', 'Apple Pencil', 'Cables', 'Baterías', 'Fundas'];", "var TP_CATS = ['Celulares', 'Accesorios', 'Forros y protectores', 'Cargadores y cables', 'Audífonos y parlantes', 'Relojes smart', 'Repuestos', 'Servicio técnico'];", expect=1)
a = sub(a, r"var TP_DATA = \{[^}]*\};", "var TP_DATA = { nit: '', tel: '3207021124', wa: '3169041345', dir: 'Manzana 107 Casa 13, Local 3, Barrio Modelia', ciudad: 'Ibagué, Tolima', email: 'aminktechcelulares@gmail.com' };", expect=1)
a = rep(a, "c.prefijoSKU = 'TP';", "c.prefijoSKU = 'AT';", expect=1)
a = rep(a, "prefijoSKU: 'EP'", "prefijoSKU: 'AT'", expect=1)
a = rep(a, "TECNO PHONE", "AMINK TECH")
a = rep(a, "Tecno Phone", "AMINK TECH")
# --- servicio técnico: factura al entregar (sin doble conteo en caja/bancos), ticket, arrastre táctil
a = sub(a, r"function finalizarServicio\(s, method, banco, ref\) \{\n.*?\n\}\n", lambda m: (ROOT / 'patches/finalizar.js').read_text(encoding='utf-8'), count=1, flags=re.S)
a = rep(a, "S.services.filter(s => s.deliveredAt && String(s.deliveredAt).slice(0, 10) === d).forEach(s => {",
        "S.services.filter(s => s.deliveredAt && !s.invoiceId && String(s.deliveredAt).slice(0, 10) === d).forEach(s => {", expect=1)
a = rep(a, "S.services.filter(s => s.deliveredAt && String(s.deliveredAt).slice(0, 10) === c.id && s.payMethod",
        "S.services.filter(s => s.deliveredAt && !s.invoiceId && String(s.deliveredAt).slice(0, 10) === c.id && s.payMethod", expect=1)
a = rep(a, "S.services.filter(s => s.payBank).forEach(s =>", "S.services.filter(s => s.payBank && !s.invoiceId).forEach(s =>", expect=1)
a = rep(a, """<button class="btn" onclick="window.print()">🖨️ Imprimir</button>
      ${idx >= 0""", """<button class="btn" onclick="printOrden('${s.id}')">🖨️ ${s.invoiceNum ? 'Imprimir factura ' + esc(s.invoiceNum) : 'Imprimir orden'}</button>
      ${idx >= 0""", expect=1)
a = rep(a, "const ticketHTML = s => `<div class=\"ticket\" onclick=", "const ticketHTML = s => `<div class=\"ticket\" data-order-id=\"${s.id}\" onclick=", expect=1)
a = rep(a, "<div class=\"col-b\">${it.map(ticketHTML)", "<div class=\"col-b\" data-status=\"${k}\">${it.map(ticketHTML)", expect=1)
a = rep(a, ".col-b{padding:10px;display:flex;flex-direction:column;gap:9px}",
        ".col-b{padding:10px;display:flex;flex-direction:column;gap:9px}\n.ticket[data-order-id]{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}", expect=1)
a = sub(a, r"/\* --- 3\. Drag & drop en kanban de servicios --- \*/.*?(?=/\* --- 5\. )", lambda m: (ROOT / 'patches/servicios.js').read_text(encoding='utf-8'), count=1, flags=re.S)
# Perfiles AMINK: Gerencia + sedes Chapinero y Modelia, todos con el mismo PIN
a = rep(a, "{ id: 'us_ger', nombre: 'Gerencia', perfil: 'gerencia', pin: 'g3r3nc14'", "{ id: 'us_ger', nombre: 'Gerencia', perfil: 'gerencia', pin: '3sdthmiu'", expect=1)
a = rep(a, "{ id: 'us_com', nombre: 'Comercial', perfil: 'comercial', pin: 'c0m3rc14l'", "{ id: 'us_cha', nombre: 'Chapinero', perfil: 'sede', sede: 'chapinero', pin: '3sdthmiu'", expect=1)
a = rep(a, "{ id: 'us_bod', nombre: 'Bodega', perfil: 'bodega', pin: 'b0d3g4'", "{ id: 'us_mod', nombre: 'Modelia', perfil: 'sede', sede: 'modelia', pin: '3sdthmiu'", expect=1)
a = rep(a, "const GER_PIN_EXTRA = 'g3r3nc1a';", "const GER_PIN_EXTRA = '3sdthmiu';", expect=1)
# --- sedes: almacenamiento separado por sede (store/<sede>/<sección>, localStorage por sede)
a = rep(a, "/* ---- persistencia ---- */\nlet DBX = null", """/* ---- persistencia ---- */
/* AMINK: cada sede guarda sus datos aparte; 'todas' = vista consolidada de Gerencia (solo lectura) */
const SEDES = { chapinero: 'Chapinero', modelia: 'Modelia' };
let SEDE = (() => { try { const s = localStorage.getItem('amk_sede'); return (SEDES[s] || s === 'todas') ? s : 'chapinero'; } catch (e) { return 'chapinero'; } })();
const NS = () => 'store/' + SEDE + '/';
let DBX = null""", expect=1)
a = rep(a, "localStorage.getItem('yt_syn')", "localStorage.getItem('yt_syn_' + SEDE)", expect=1)
a = rep(a, "localStorage.setItem('yt_syn', JSON.stringify(SYN))", "localStorage.setItem('yt_syn_' + SEDE, JSON.stringify(SYN))", expect=1)
a = rep(a, "const LS = 'ef_gestion_v1';", "let LS = 'ef_gestion_v1_' + SEDE;", expect=1)
a = rep(a, "'store/' + k", "NS() + k", expect=3)
a = rep(a, "async function supaStart() {\n", "async function supaStart() {\n  if (SEDE === 'todas' && SUPA_ON && (await supaToken())) return amkConsolidar();\n", expect=1)
a = rep(a, "supaReq('GET', '?path=like.store%2F*&select=path,data');\n    const kept", "supaReq('GET', '?path=like.' + encodeURIComponent(NS()) + '*&select=path,data');\n    const kept", expect=1)
a = rep(a, "const k = r.path.slice(6);", "const k = r.path.slice(NS().length);", expect=1)
a = rep(a, "SUPA_DB.doc('public/catalog').set(d)", "if (SEDES[SEDE]) SUPA_DB.doc('public/catalog_' + SEDE).set(d)", expect=1)
a = rep(a, "for (const path of ['public/catalog', 'public/logo'])", "for (const path of ['public/catalog', 'public/catalog_chapinero', 'public/catalog_modelia', 'public/logo'])", expect=1)
# --- acceso: 3 perfiles fijos, todos con PIN; Gerencia elige Consolidado o una sede
a = rep(a, "const users = () => (S.config.users || []).filter(u => !u.inactivo);", "const users = () => AMK_USERS;", expect=1)
a = rep(a, "try { await supaStart(); } catch (e) { }\n    pinTries = 0; drawProfiles();", "pinTries = 0; drawProfiles();", expect=1)
a = rep(a, "${esc(PDESC[u.perfil] || '')}${u.perfil === 'gerencia' ? ' · pide PIN' : ''}", "${esc(u.desc || '')}", expect=1)
a = rep(a, "    if (u.perfil !== 'gerencia') return enter(u);\n", "", expect=1)
a = rep(a, "if (c !== String(u.pin || '') && c !== GER_PIN_EXTRA) {", "if (c !== AMK_PIN) {", expect=1)
a = rep(a, "    enter(u);\n  }\n  function enter(us) {", """    if (u.perfil === 'gerencia') return drawSedes();
    goSede(u, u.sede);
  }
  function drawSedes() {
    v10Shell(`<div id="v11Box"><div style="font-weight:700;font-size:1.05rem;margin:2px 0 12px">👑 Gerencia · ¿qué quieres ver?</div>
      <div class="opt-grid" style="grid-template-columns:1fr;gap:10px">${['todas', 'chapinero', 'modelia'].map(s => `<button class="opt" type="button" style="display:flex;align-items:center;gap:14px;padding:16px" onclick="ytV11.sede('${s}')"><span class="em" style="font-size:28px;margin:0">${s === 'todas' ? '📊' : '🏬'}</span><span><b style="font-size:1.05rem">${AMK_NOMBRE[s]}</b><span class="d" style="font-size:12.5px;display:block">${s === 'todas' ? 'Suma de ambas sedes: ventas, caja, inventario, reportes y estados financieros' : 'Operar la sede con permisos de Gerencia'}</span></span></button>`).join('')}</div>
      <div id="v11Msg" class="tiny" style="margin-top:10px;min-height:1em"></div></div>`);
  }
  async function goSede(u, sede) {
    v10Shell(`<div id="v11Box"><div class="alertbox g"><span class="em">☁️</span><div>Cargando ${esc(AMK_NOMBRE[sede] || sede)}…</div></div></div>`);
    try { await amkUsar(sede); } catch (e) { console.warn('sede', e); }
    enter(u);
  }
  function enter(us) {""", expect=1)
a = rep(a, "window.ytV11 = { signin, verify, resend: () => sendCode(true), pick, pin, forget, profiles: drawProfiles };",
        "window.ytV11 = { signin, verify, resend: () => sendCode(true), pick, pin, forget, profiles: drawProfiles, sede: s => goSede(AMK_USERS[0], s) };", expect=1)
a = sub(a, r'<script src="assets/js/[^"]*"></script>\n?', '', expect=8)   # scripts de la plantilla que no existen (404)
_end = a.rfind('</script>')
a = a[:_end] + (ROOT / 'patches/sedes.js').read_text(encoding='utf-8') + a[_end:]
assert 'Tecno Phone' not in a and 'tecnophone' not in a.lower() and OLD_URL not in a
(ROOT / 'site/admin.html').write_text(a, encoding='utf-8')

# ------------------------------------------------------------------ index.html
i = (SRC / 'index.html').read_text(encoding='utf-8')
i = recolor(i)
i = sub(i, r'window\.TP_LOGO = "[^"]*"', f'window.TP_LOGO = "{WORD}"', expect=1)
i = sub(i, r'window\.TP_ICON = "[^"]*"', f'window.TP_ICON = "{MARK128}";\nwindow.TP_LOGO_LIGHT = "{WORD_L}"', expect=1)
i = rep(i, '<img class="hero-logo" alt="" width="440" height="186"><script>document.currentScript.previousElementSibling.src = TP_LOGO;</script>',
        '<img class="hero-logo" alt="" width="440" height="149"><script>document.currentScript.previousElementSibling.src = TP_LOGO_LIGHT;</script>', expect=1)
i = rep(i, '<img class="wordmark" alt="Tecno Phone" width="440" height="186">', '<img class="wordmark" alt="AMINK TECH Tecnology" width="440" height="149">')
i = rep(i, '<title>Tecno Phone Ibagué · Catálogo</title>', '<title>AMINK TECH · Catálogo</title>', expect=1)
i = rep(i, 'content="Tecno Phone Ibagué · Catálogo"', 'content="AMINK TECH · Catálogo"', expect=1)
i = sub(i, r'<meta name="description" content="[^"]*">', '<meta name="description" content="AMINK TECH Tecnology: celulares de todas las marcas, accesorios originales y compatibles, y servicio técnico especializado. Consulta por WhatsApp.">', count=1)
i = sub(i, r"const BRAND = \{.*?\n\};", """const BRAND = {
  nombre: 'AMINK TECH',
  razon: 'AMINK TECH TECNOLOGY',
  nit: '',
  ciudad: 'Ibagué, Tolima',
  eslogan: 'Tu mundo en buenas manos',
  whatsapp: '3169041345',     /* número que recibe los pedidos del catálogo */
  telefono: '',
  correo: 'aminktechcelulares@gmail.com',
  contactos: [ { n: 'Estiwen', t: '3169041345' }, { n: 'María', t: '3207021124' } ],
  sedes: [ { n: 'AMINK TECH', d: 'Manzana 107 Casa 13, Local 3 · Barrio Modelia', q: 'Manzana 107 Casa 13 Local 3, Barrio Modelia, Ibagué, Tolima', url: 'https://maps.app.goo.gl/21yQpTZvTjicJLGa8' } ],
  redes: [
    { n: 'Instagram', u: 'https://www.instagram.com/celulares_aminktech' },
    { n: 'Facebook',  u: 'https://www.facebook.com/share/1FAhd5s5RG/' },
    { n: 'TikTok',    u: 'https://www.tiktok.com/@celulares.amink' }
  ]
};""", count=1, flags=re.S)
# contacto: WhatsApp por persona, redes sociales y enlace exacto de Maps
i = rep(i, "sedeMap = x => 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(x.q);",
        "sedeMap = x => x.url || 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(x.q);", expect=1)
i = rep(i, "function waCardHTML() {", (ROOT / 'patches/contacto.js').read_text(encoding='utf-8') + "function waCardHTML() {", expect=1)
i = rep(i, "Llamar al ${esc(prettyPhone(ST.site.tel))}</a>` : ''}</div>`;", "Llamar al ${esc(prettyPhone(ST.site.tel))}</a>` : ''}${contactosHTML()}${redesHTML()}</div>`;", expect=1)
i = rep(i, "<div><b>Contacto</b>${waNumber() ?", "<div><b>Contacto</b>${footContactoHTML()}${(BRAND.contactos || []).length ? '' : waNumber() ?", expect=1)
i = rep(i, "\n.wa-call{", "\n.redes{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.redes a{display:inline-flex;align-items:center;gap:7px;height:36px;padding:0 13px;border-radius:9999px;color:#fff;text-decoration:none;font-size:13.5px;font-weight:500;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22)}.redes svg,.wa-call svg{width:17px;height:17px;flex:none}\n.wa-call{", expect=1)
i = rep(i, OLD_URL, URL, expect=1)
i = sub(i, r"(const CFG = \{\n  url: '[^']*',\n  key: ')[^']*'", r"\g<1>" + KEY + "'", expect=1)
i = sub(i, r'const FALLBACK = \{"items": .*?\};\n', 'const FALLBACK = {"items": {}, "v": 3};\n', count=1, flags=re.S)
i = i.replace('Tecno Phone Ibagué', 'AMINK TECH').replace('Tecno Phone', 'AMINK TECH').replace('TECNOPHONELAB', 'AMINK TECH TECNOLOGY')

# catálogo = suma de las dos sedes (public/catalog_chapinero + public/catalog_modelia); usa Supabase, no el respaldo forzado
i = rep(i, """    const rows = await rest('?select=path,data&path=' + inList(['public/catalog']));
    cat = rows.find(r => r.path === 'public/catalog') || null;""", """    const rows = await rest('?select=path,data&path=' + inList(['public/catalog_chapinero', 'public/catalog_modelia']));
    const parts = rows.map(r => r.data).filter(d => d && d.items);
    cat = parts.length ? { data: mergeCatalogs(parts) } : null;""", expect=1)
i = rep(i, "existe la fila public/catalog. Ejecuta el SQL completo o entra una vez al admin.", "existe el catálogo de ninguna sede. Entra una vez al admin con Chapinero o Modelia.", expect=1)
i = rep(i, "    const data = FALLBACK; /* forzar fotos de Drive */", "    const data = cat ? cat.data : FALLBACK;", expect=1)
i = rep(i, "async function load(silent) {", """/* une los catálogos de las sedes: mismo código = un solo producto con el stock sumado */
function mergeCatalogs(list) {
  const items = {}; let at = '', site = null;
  list.forEach(d => {
    if (d.at && d.at > at) at = d.at; if (!site && d.site && d.site.biz) site = d.site;
    Object.entries(d.items || {}).forEach(([k, p]) => {
      const o = items[k];
      if (!o) { items[k] = Object.assign({}, p); return; }
      o.stock = (Number(o.stock) || 0) + (Number(p.stock) || 0);
      o.agotado = !!(o.agotado && p.agotado); o.hidden = !!(o.hidden && p.hidden); o.sinInv = !!(o.sinInv || p.sinInv);
      if (!o.hasImg && p.hasImg) { o.id = p.id; o.hasImg = true; }
      if (!(o.colores || []).length && (p.colores || []).length) o.colores = p.colores;
    });
  });
  return { at, site: site || {}, items };
}
async function load(silent) {""", expect=1)
# textos robustos cuando aún no hay sedes o NIT cargados
i = rep(i, "<p>${BRAND.sedes.length} puntos de atención en ${esc(BRAND.ciudad.split(',')[0])}.</p>",
        "<p>${BRAND.sedes.length ? BRAND.sedes.length + (BRAND.sedes.length === 1 ? ' punto' : ' puntos') + ' de atención' + (BRAND.ciudad ? ' en ' + esc(BRAND.ciudad.split(',')[0]) : '') + '.' : 'Celulares, accesorios y servicio técnico especializado.'}</p>", expect=1)
i = rep(i, "${esc(BRAND.razon)} · NIT ${esc(BRAND.nit)}", "${esc(BRAND.razon)}${BRAND.nit ? ' · NIT ' + esc(BRAND.nit) : ''}", expect=1)
i = rep(i, "${esc(BRAND.razon)}<br>NIT ${esc(BRAND.nit)}", "${esc(BRAND.razon)}${BRAND.nit ? '<br>NIT ' + esc(BRAND.nit) : ''}", expect=1)
i = rep(i, '<h3 class="sheet-h">Nuestras sedes</h3>', "${BRAND.sedes.length ? '<h3 class=\"sheet-h\">Nuestras sedes</h3>' : ''}", expect=1)
i = rep(i, "<div><b>Sedes en ${esc(BRAND.ciudad.split(',')[0])}</b>", "<div>${BRAND.sedes.length ? '<b>Sedes' + (BRAND.ciudad ? ' en ' + esc(BRAND.ciudad.split(',')[0]) : '') + '</b>' : ''}", expect=1)
(ROOT / 'site/index.html').write_text(i, encoding='utf-8')
print('ok', len(a), len(i))
