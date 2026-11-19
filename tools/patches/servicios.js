/* --- 3. Drag & drop en kanban de servicios: mouse (PC) y táctil (celular) --- */
function moverServ(id, newSt) {
  const s = S.services.find(x => x.id === id);
  if (!s || !EST_SERV[newSt] || s.status === newSt) return;
  if (newSt === 'entregado') return cambiarEstadoServ(id, 'entregado');   /* abre el cobro si hay saldo y factura */
  if (newSt === 'asignado' && !s.assigned) { const r = prompt('¿Quién será el responsable?\n' + responsables().join(', ')); if (r) s.assigned = r; }
  const prev = s.status; s.status = newSt;
  (s.history = s.history || []).push({ at: nowISO(), t: 'Estado: ' + ((EST_SERV[prev] || {}).t || prev) + ' → ' + EST_SERV[newSt].t + (s.assigned ? ' · ' + s.assigned : '') });
  save('services'); render(); toast('Orden movida a ' + EST_SERV[newSt].t, EST_SERV[newSt].e);
}
let svDrag = null;
const svColAt = (x, y) => [...document.querySelectorAll('.col-b[data-status]')].find(c => { const r = c.getBoundingClientRect(); return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom; }) || null;
const svHi = col => document.querySelectorAll('.col-b[data-status]').forEach(c => { c.style.background = c === col ? 'var(--blue-50)' : ''; c.style.outline = c === col ? '2px dashed var(--blue-400)' : ''; });
function svDragEnd(drop) {
  const d = svDrag; svDrag = null; if (!d) return;
  clearTimeout(d.timer); if (d.clone) d.clone.remove(); d.tk.style.opacity = ''; svHi(null);
  if (drop && d.active && d.col) moverServ(d.id, d.col.dataset.status);   /* fuera de una columna: la orden no cambia */
}
VIEWS.after_servicios = function () {
  keepFocus('#sq');
  document.querySelectorAll('.ticket[data-order-id]').forEach(tk => {
    const id = tk.dataset.orderId;
    tk.setAttribute('draggable', 'true');
    tk.ondragstart = e => { e.dataTransfer.setData('text/plain', id); tk.style.opacity = '.5'; };
    tk.ondragend = () => { tk.style.opacity = ''; };
    /* táctil: mantener presionado 0,3 s levanta la tarjeta; deslizar antes es scroll normal y un toque abre la orden */
    tk.addEventListener('touchstart', e => {
      if (e.touches.length !== 1) return svDragEnd(false);
      const t = e.touches[0]; svDragEnd(false);
      const d = svDrag = { tk, id, x: t.clientX, y: t.clientY, active: false, clone: null, col: null };
      d.timer = setTimeout(() => {
        if (svDrag !== d) return;
        const r = tk.getBoundingClientRect(); d.dx = d.x - r.left; d.dy = d.y - r.top; d.active = true;
        const c = tk.cloneNode(true); c.removeAttribute('onclick');
        c.style.cssText = `position:fixed;left:${r.left}px;top:${r.top}px;width:${r.width}px;margin:0;opacity:.9;z-index:9999;pointer-events:none;transform:rotate(2deg) scale(1.04);box-shadow:0 12px 40px rgba(0,0,0,.25)`;
        document.body.appendChild(c); d.clone = c; tk.style.opacity = '.3';
        if (navigator.vibrate) navigator.vibrate(30);
      }, 300);
    }, { passive: true });
    tk.addEventListener('touchmove', e => {
      const d = svDrag; if (!d || d.tk !== tk) return;
      const t = e.touches[0];
      if (!d.active) { if (Math.abs(t.clientX - d.x) > 10 || Math.abs(t.clientY - d.y) > 10) svDragEnd(false); return; }
      e.preventDefault();   /* bloquea el scroll mientras se arrastra */
      d.clone.style.left = (t.clientX - d.dx) + 'px'; d.clone.style.top = (t.clientY - d.dy) + 'px';
      d.col = svColAt(t.clientX, t.clientY); svHi(d.col);
    }, { passive: false });
    tk.addEventListener('touchend', e => { if (svDrag && svDrag.active) e.preventDefault(); svDragEnd(true); });
    tk.addEventListener('touchcancel', () => svDragEnd(false));
    tk.addEventListener('contextmenu', e => { if (svDrag) e.preventDefault(); });
  });
  document.querySelectorAll('.col-b[data-status]').forEach(col => {
    col.ondragover = e => { e.preventDefault(); col.style.background = 'var(--blue-50)'; };
    col.ondragleave = () => { col.style.background = ''; };
    col.ondrop = e => { e.preventDefault(); col.style.background = ''; const id = e.dataTransfer.getData('text/plain'); if (id) moverServ(id, col.dataset.status); };
  });
};

/* --- 4. Ticket de orden de servicio (mismo formato 80 mm que la factura POS) --- */
function srvTicketHTML(s) {
  const [biz, sub] = bizHeader();
  const v = s.invoiceId ? S.sales.find(x => x.id === s.invoiceId) : null;
  const r = S.config.res[v && v.docType === 'FE' ? 'fe' : 'pos'];
  const items = (s.items || []).filter(i => i.desc || i.price);
  const saldo = Math.max(0, (s.total || 0) - (s.advance || 0)), entregada = s.status === 'entregado';
  const medio = m => esc(MEDIO_T[m] || m);
  return `<div class="tk">
    <div class="c"><img src="${LOGO_B64}" style="width:46px;height:46px;border-radius:10px"><br><b style="font-size:13px">${esc(biz)}</b><br>${esc(sub)}<br>
      ${v && r.resolucion ? `Res. DIAN ${esc(r.resolucion)} ${r.fecha ? 'del ' + dmy(r.fecha) : ''}<br>${esc(r.prefijo)} ${nfmt(r.desde)} al ${nfmt(r.hasta)}<br>` : ''}</div>
    <hr><div><b>ORDEN DE SERVICIO</b> <span class="r"><b>${esc(s.code)}</b></span></div>
    <div>Recibida: ${dmy(s.createdAt)} ${hm(s.createdAt)}</div>
    ${v ? `<div><b>${v.docType === 'FE' ? 'FACTURA ELECTRÓNICA' : 'FACTURA DE VENTA POS'}</b> <span class="r"><b>${esc(v.invoice)}</b></span></div><div>Entregada: ${dmy(v.date)} ${hm(v.at)}</div>`
      : entregada && s.deliveredAt ? `<div>Entregada: ${dmy(s.deliveredAt)} ${hm(s.deliveredAt)}</div>`
      : `<div>Estado: ${esc((EST_SERV[s.status] || {}).t || s.status)}</div>${s.promise ? `<div>Entrega estimada: ${dmy(s.promise)}</div>` : ''}`}
    <hr><div>Cliente: ${esc(s.clientName)}</div>${s.phone ? `<div>Tel: ${esc(s.phone)}</div>` : ''}${s.doc ? `<div>Doc: ${esc(s.doc)}</div>` : ''}
    <hr><div>Equipo: ${esc(s.subject || '')}</div>${s.desc ? `<div>Falla: ${esc(s.desc)}</div>` : ''}<div>Responsable: ${esc(s.assigned || 'Sin asignar')}</div>
    <hr><div class="c"><b>DETALLE DE SERVICIOS</b></div>
    <table>${items.map(i => `<tr><td colspan="3">${esc(i.desc || s.subject)}</td></tr><tr><td>${nfmt(i.qty)} × ${money(i.price)}</td><td></td><td class="r">${money(i.qty * i.price)}</td></tr>`).join('') || '<tr><td colspan="3">Sin detalle</td></tr>'}</table>
    <hr><table><tr><td>Subtotal</td><td class="r">${money(s.total)}</td></tr>
    ${s.advance ? `<tr><td>Anticipo${s.advMethod ? ' (' + medio(s.advMethod) + ')' : ''}</td><td class="r">-${money(s.advance)}</td></tr>` : ''}
    <tr><td><b>${entregada ? 'TOTAL COBRADO' : 'SALDO A PAGAR'}</b></td><td class="r"><b style="font-size:15px">${money(saldo)}</b></td></tr>
    ${entregada && s.payMethod && saldo ? `<tr><td>Medio: ${medio(s.payMethod)}${s.payBank ? ' ' + esc(s.payBank) : ''}${s.payRef ? ' #' + esc(s.payRef) : ''}</td><td class="r">${money(saldo)}</td></tr>` : ''}</table>
    <hr><div class="c">${s.warranty ? `Garantía: ${nfmt(s.warranty)} días${s.warrantyUntil ? ' (hasta ' + dmy(s.warrantyUntil) + ')' : ''}<br>` : ''}Gracias por su confianza${(S.config.wa || S.config.tel) ? '<br>WhatsApp: ' + esc(S.config.wa || S.config.tel) : ''}</div></div>`;
}
function printOrden(id) {
  const s = S.services.find(x => x.id === id); if (!s) return;
  const f = document.createElement('iframe'); f.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0';
  document.body.appendChild(f);
  f.contentDocument.write(`<html><head><meta charset="utf-8"><title>Orden ${esc(s.code)}</title><style>@page{size:80mm auto;margin:0}body{margin:0}${TICKET_CSS}</style></head><body>${srvTicketHTML(s)}</body></html>`);
  f.contentDocument.close();
  setTimeout(() => { f.contentWindow.focus(); f.contentWindow.print(); setTimeout(() => f.remove(), 3000); }, 250);
}
/* en la factura de una orden, el descuento es el anticipo ya recibido */
(function () { const _p = posTicketHTML; posTicketHTML = function (v) { const h = _p(v); return v && v.type === 'servicio' && v.discount ? h.replace('<td>Descuento</td>', '<td>Anticipo ' + esc(v.serviceCode || '') + '</td>') : h; }; })();

