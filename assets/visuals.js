(() => {
  'use strict';
  const root = document.querySelector('#network');
  if (!root) return;
  const cards = [...root.querySelectorAll('[data-relationship]')];
  const choices = [...root.querySelectorAll('[data-actor]')];
  const select = root.querySelector('#actorSelect');
  const actorName = root.querySelector('#actorName');
  const actorRole = root.querySelector('#actorRole');
  const status = root.querySelector('#actorResult');
  const focus = root.querySelector('.actor-focus');
  let activeActor = 'huang';

  function showActor(id, updateHash = false) {
    const option = [...select.options].find(o => o.value === id);
    if (!option) return;
    activeActor = id;
    let count = 0;
    cards.forEach(card => {
      card.hidden = id !== 'all' && card.dataset.subject !== id && card.dataset.object !== id;
      if (!card.hidden) count++;
    });
    choices.forEach(button => {
      const selected = button.dataset.actor === id;
      if (button.classList.contains('actor-choice')) button.setAttribute('aria-pressed', String(selected));
      else button.hidden = selected;
    });
    select.value = id;
    actorName.textContent = id === 'all' ? '全部直接关系' : option.dataset.label;
    actorRole.textContent = id === 'all' ? '按记录逐段查看；保留各自的来源与限定' : option.dataset.role;
    focus.classList.toggle('unverified', option.dataset.kind === 'unverified');
    status.textContent = `${actorName.textContent} · ${count} 段关系`;
    if (updateHash) history.replaceState(null, '', '#actor-' + id);
  }
  choices.forEach(button => button.addEventListener('click', () => {
    showActor(button.dataset.actor, true);
    if (!button.classList.contains('actor-choice')) {
      actorName.setAttribute('tabindex', '-1');
      actorName.focus({preventScroll:true});
      focus.scrollIntoView({block:'start', behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
    }
  }));
  select.addEventListener('change', () => showActor(select.value, true));
  function openAnchor() {
    let hash;
    try { hash = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    if (hash.startsWith('actor-')) {
      showActor(hash.slice(6));
      requestAnimationFrame(() => root.scrollIntoView({block:'start'}));
    } else if (hash.startsWith('relation-')) {
      const card = cards.find(c => c.id === hash);
      if (!card) return;
      if (activeActor !== 'all' && ![card.dataset.subject, card.dataset.object].includes(activeActor)) showActor(card.dataset.subject);
      card.querySelector('details').open = true;
      requestAnimationFrame(() => card.scrollIntoView({block:'start'}));
    }
  }
  showActor(activeActor);
  addEventListener('hashchange', openAnchor);
  openAnchor();
})();
