(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (s, p = document) => p.querySelector(s);
  const $$ = (s, p = document) => Array.from(p.querySelectorAll(s));
  const list = $('#eventList');
  if (list) {
    const events = $$('.event', list);
    const input = $('#timelineSearch');
    const result = $('#timelineResult');
    const more = $('#timelineMore');
    const all = $('#timelineAll');
    const clear = $('#timelineReset');
    const sort = $('#timelineSort');
    let grade = 'all';
    let limit = 16;
    let matches = [];
    const setGrade = (g) => {
      grade = g;
      $$('[data-filter-grade]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filterGrade === g)));
    };
    function render() {
      const query = input.value.trim().toLocaleLowerCase();
      const words = query.split(/\s+/).filter(Boolean);
      matches = events.filter(e => (grade === 'all' || e.dataset.grade === grade) && words.every(w => e.dataset.search.includes(w)));
      matches.sort((a, b) => sort.value === 'asc' ? a.dataset.date.localeCompare(b.dataset.date) || +a.dataset.order - +b.dataset.order : b.dataset.date.localeCompare(a.dataset.date) || +b.dataset.order - +a.dataset.order);
      events.forEach(e => { e.hidden = true; });
      matches.forEach((e, i) => { list.append(e); e.hidden = i >= limit; });
      const shown = Math.min(limit, matches.length);
      result.textContent = `找到 ${matches.length} 条，显示 ${shown} 条。${grade === 'all' ? '' : `当前筛选 ${grade}。`}`;
      more.hidden = shown >= matches.length;
      all.hidden = shown >= matches.length;
      more.textContent = `再显示 ${Math.min(24, matches.length - shown)} 条`;
      $('#timelineEmpty').hidden = matches.length > 0;
    }
    input.addEventListener('input', () => { limit = 16; render(); });
    sort.addEventListener('change', () => { limit = 16; render(); });
    $$('[data-filter-grade]').forEach(b => b.addEventListener('click', () => { setGrade(b.dataset.filterGrade); limit = 16; render(); }));
    more.addEventListener('click', () => { limit += 24; render(); });
    all.addEventListener('click', () => { limit = events.length; render(); });
    clear.addEventListener('click', () => { input.value = ''; setGrade('all'); limit = 16; render(); input.focus(); });
    $$('[data-show-grade]').forEach(b => b.addEventListener('click', () => {
      input.value = ''; setGrade(b.dataset.showGrade); limit = 16; render();
      $('#timeline').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
    }));
    function showAnchor() {
      const id = decodeURIComponent(location.hash.slice(1));
      const target = id && document.getElementById(id);
      const event = target && target.closest('.event');
      if (!event || !list.contains(event)) return;
      input.value = ''; setGrade('all'); limit = events.length; render();
      requestAnimationFrame(() => event.scrollIntoView());
    }
    render();
    window.addEventListener('hashchange', showAnchor);
    if (location.hash) showAnchor();
    window.addEventListener('beforeprint', () => events.forEach(e => { e.hidden = false; }));
    window.addEventListener('afterprint', render);
  }
  const sourceSearch = $('#sourceSearch');
  if (sourceSearch) {
    const rows = $$('#sourceTable tbody tr');
    sourceSearch.addEventListener('input', () => {
      const q = sourceSearch.value.trim().toLocaleLowerCase();
      let n = 0;
      rows.forEach(row => { row.hidden = !row.textContent.toLocaleLowerCase().includes(q); if (!row.hidden) n++; });
      $('#sourceResult').textContent = `显示 ${n} / ${rows.length} 条来源记录`;
    });
  }
  const backTop = $('#backTop');
  if (backTop) {
    const update = () => { backTop.hidden = scrollY < 600; };
    addEventListener('scroll', update, {passive:true});
    backTop.addEventListener('click', () => scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'}));
    update();
  }
  const nav = $$('.section-nav a[href^="#"]');
  const sections = nav.map(a => ({a, node:document.getElementById(a.hash.slice(1))})).filter(s => s.node);
  let navFrame = false;
  const updateNav = () => {
    navFrame = false;
    const cutoff = Math.max(100, innerHeight * .2);
    const passed = sections.map(s => ({...s, top:s.node.getBoundingClientRect().top})).filter(s => s.top <= cutoff);
    const active = passed.sort((a,b) => b.top - a.top)[0] || sections[0];
    nav.forEach(a => a.setAttribute('aria-current', String(active && a === active.a)));
  };
  const scheduleNav = () => { if (!navFrame) { navFrame = true; requestAnimationFrame(updateNav); } };
  addEventListener('scroll', scheduleNav, {passive:true});
  addEventListener('resize', scheduleNav);
  document.addEventListener('toggle', scheduleNav, true);
  updateNav();
})();
