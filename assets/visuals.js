(() => {
  'use strict';
  const root = document.querySelector('#network');
  if (!root) return;
  const views = [...root.querySelectorAll('.network-view')];
  const tabs = [...root.querySelectorAll('[data-network-view]')];
  const panels = [...root.querySelectorAll('[data-relation-detail]')];
  let currentView = views[0];
  function selectRelation(id) {
    panels.forEach(p => { p.hidden = p.dataset.relationDetail !== id; });
    root.querySelectorAll('[data-select-relation]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.selectRelation === id)));
    root.querySelectorAll('[data-relation]').forEach(e => e.classList.toggle('selected', e.dataset.relation === id));
  }
  function selectView(id, relation) {
    currentView = views.find(v => v.dataset.view === id) || views[0];
    views.forEach(v => { v.hidden = v !== currentView; });
    tabs.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.networkView === currentView.dataset.view)));
    selectRelation(relation || currentView.querySelector('[data-select-relation]').dataset.selectRelation);
  }
  tabs.forEach(b => b.addEventListener('click', () => selectView(b.dataset.networkView)));
  root.querySelectorAll('[data-select-relation]').forEach(b => b.addEventListener('click', () => selectRelation(b.dataset.selectRelation)));
  root.querySelectorAll('[data-relation]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); selectRelation(a.dataset.relation); }));
  function openAnchor() {
    const id = location.hash.replace('#relation-', '');
    if (!location.hash.startsWith('#relation-')) return;
    const view = views.find(v => [...v.querySelectorAll('[data-select-relation]')].some(b => b.dataset.selectRelation === id));
    if (view) { selectView(view.dataset.view, id); requestAnimationFrame(() => document.getElementById('relation-' + id).scrollIntoView()); }
  }
  selectView(currentView.dataset.view);
  addEventListener('hashchange', openAnchor);
  openAnchor();
})();
