function finalizarServicio(s, method, banco, ref) {
  method = method || 'efectivo';
  if (!s.invoiceId && !openCash()) return toast('No hay sesión de caja abierta: ábrela para entregar y facturar la orden', '🚫');
  Object.assign(s, { status: 'entregado', deliveredAt: nowISO(), payMethod: method, payBank: banco, payRef: ref, warrantyUntil: s.warranty ? addDays(today(), s.warranty) : null });
  (s.history = s.history || []).push({ at: nowISO(), t: 'Entregada y cobrada (' + method + ')' });
  /* Factura POS de la entrega: el cobro entra a ventas, facturas, caja, dashboard, reportes y estados financieros.
     El anticipo ya se registró en caja el día que se recibió; aquí se descuenta para no contarlo dos veces. */
  const kind = S.config.fiscal.contingencia ? 'CONT' : 'POS';
  const inv = s.invoiceId ? null : nextInvoice(kind);
  if (inv) {
    const c = openCash();
    const line = (name, qty, price) => ({ productId: null, code: s.code, name, qty, price, cost: 0, tarifa: 'EXENTO', iva: 0, category: 'Servicio técnico', type: 'servicio' });
    const items = (s.items || []).filter(i => i.desc || i.price).map(i => line(i.desc || s.subject, Number(i.qty) || 1, Number(i.price) || 0));
    if (!items.length) items.push(line(s.subject || 'Servicio técnico', 1, s.total || 0));
    const sub = items.reduce((a, i) => a + i.qty * i.price, 0), adv = Math.min(s.advance || 0, sub), tot = Math.max(0, sub - adv);
    const v = { id: uid('vt'), code: consec('VT'), invoice: inv.number, invN: inv.n, docType: kind, docKind: 'FACTURA', resolucion: inv.resolucion, date: today(), at: nowISO(),
      sid: c.sid, cajaId: c.cajaId, caja: c.cajaNombre, user: curUser()?.nombre || S.config.user,
      items, subtotal: sub, discount: adv, dctoEfectivo: 0, anticipo: adv, base: tot, ivaTotal: 0, iva: 0, incTotal: 0, total: tot,
      payments: tot > 0 ? [{ method, amount: tot, bank: banco || '', ref: ref || '', denoms: {} }] : [], received: tot, change: 0, ajusteCentavo: 0,
      nit: s.doc || CF_ID, clientId: s.clientId || null, clientName: s.clientName || 'CONSUMIDOR FINAL', seller: s.assigned || curUser()?.nombre || '', metodo: 'CONTADO',
      obs: 'Orden de servicio ' + s.code, status: 'ok', type: 'servicio', serviceId: s.id, serviceCode: s.code };
    S.sales.unshift(v); s.invoiceId = v.id; s.invoiceNum = v.invoice;
    (s.history = s.history || []).push({ at: nowISO(), t: 'Facturada: ' + v.invoice });
    try { audit('VENTA_GRABADA', v.invoice + ' ' + money(tot) + ' · ' + s.code, v.invoice); } catch (e) { }
  }
  save('services', 'sales', 'counters', 'config'); closeModal(); render();
  if (inv) toast('Orden entregada y facturada: ' + s.invoiceNum, '🤝');
  else if (s.invoiceId) toast('Orden entregada', '🤝');
  else toast('Orden entregada SIN factura: la resolución POS está agotada o vencida', '⚠️');
}
