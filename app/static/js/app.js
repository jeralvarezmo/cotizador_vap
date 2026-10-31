// JavaScript básico: agregar/quitar elementos, filtrar perfiles por producto y confirmar acciones.
// NO contiene fórmulas: todos los cálculos se hacen en Python (servidor).
document.addEventListener('DOMContentLoaded', () => {
  const cont = document.getElementById('filas-items');
  const plantilla = document.getElementById('plantilla-fila');

  function filtrarPerfiles(fila) {
    const prod = fila.querySelector('.sel-producto');
    const perfil = fila.querySelector('.sel-perfil');
    if (!prod || !perfil) return;
    const cats = ((prod.selectedOptions[0] || {}).dataset || {}).cats || '';
    const permitidas = cats.split(',').filter(Boolean);
    Array.from(perfil.options).forEach(o => {
      if (!o.value) return;
      const ok = permitidas.length === 0 || permitidas.includes(o.dataset.cat);
      o.hidden = !ok; o.disabled = !ok;
    });
    if (perfil.selectedOptions[0] && perfil.selectedOptions[0].disabled) perfil.value = '';
  }

  function enlazar(fila) {
    const prod = fila.querySelector('.sel-producto');
    if (prod) prod.addEventListener('change', () => filtrarPerfiles(fila));
    const quitar = fila.querySelector('.quitar-fila');
    if (quitar) quitar.addEventListener('click', () => {
      if (cont.querySelectorAll('.fila-item').length > 1) fila.remove();
    });
    filtrarPerfiles(fila);
  }

  if (cont && plantilla) {
    cont.querySelectorAll('.fila-item').forEach(enlazar);
    document.getElementById('agregar-fila').addEventListener('click', () => {
      const nodo = plantilla.content.firstElementChild.cloneNode(true);
      cont.appendChild(nodo); enlazar(nodo);
      const primero = nodo.querySelector('input'); if (primero) primero.focus();
    });
  }
  document.querySelectorAll('[data-confirmar]').forEach(f =>
    f.addEventListener('submit', e => { if (!confirm(f.dataset.confirmar)) e.preventDefault(); }));
  const vista = document.getElementById('vista-previa');
  if (vista) vista.scrollIntoView({behavior: 'smooth'});
});
