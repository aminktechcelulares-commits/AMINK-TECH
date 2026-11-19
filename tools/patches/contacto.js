/* ---------------- contactos por persona y redes sociales (AMINK TECH) ---------------- */
const SOC_IC = {
  Instagram: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/></svg>',
  Facebook: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h-2.5A4.5 4.5 0 0 0 8 7.5V10H5.5v3.5H8V21h3.5v-7.5H14l.8-3.5h-3.3V7.8c0-.8.5-1.3 1.3-1.3H15z"/></svg>',
  TikTok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.4 2.6 2.2 4.4 5 4.7"/></svg>'
};
const waTo = (t, msg) => 'https://wa.me/57' + digits(t) + '?text=' + encodeURIComponent(msg);
const contactosHTML = () => (BRAND.contactos || []).map(c => `<a class="wa-call" href="${esc(waTo(c.t, 'Hola ' + c.n + ', vengo del catálogo web de ' + bizName() + '.'))}" target="_blank" rel="noopener">${IC.chat}WhatsApp ${esc(c.n)} · ${esc(prettyPhone(c.t))}</a>`).join('');
const redesHTML = () => (BRAND.redes || []).length ? `<div class="redes">${BRAND.redes.map(r => `<a href="${esc(r.u)}" target="_blank" rel="noopener">${SOC_IC[r.n] || ''}<span>${esc(r.n)}</span></a>`).join('')}</div>` : '';
const footContactoHTML = () => (BRAND.contactos || []).map(c => `<div style="margin-top:6px"><a href="${esc(waTo(c.t, 'Hola ' + c.n + ', vengo del catálogo web de ' + bizName() + '.'))}" target="_blank" rel="noopener">WhatsApp ${esc(c.n)} ${esc(prettyPhone(c.t))}</a></div>`).join('')
  + (BRAND.redes || []).map(r => `<div style="margin-top:6px"><a href="${esc(r.u)}" target="_blank" rel="noopener">${esc(r.n)}</a></div>`).join('');
