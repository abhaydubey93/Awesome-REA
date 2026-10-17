/* Exercise actual browser functions with offline payloads and a minimal DOM. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'site/index.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'site/app.js'), 'utf8');

class Element {
  constructor(tag = 'div') { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.handlers = {}; this.value = ''; this.className = ''; this.classList = {toggle() {}, add() {}, remove() {}}; }
  append(...nodes) { for (const node of nodes) this.children.push(...(node.tag === 'fragment' ? node.children : [node])); }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(event, callback) { this.handlers[event] = callback; }
  emit(event) { this.handlers[event]?.({target: this}); }
  get options() { return this.children; }
  focus() {}
  scrollIntoView() {}
}
function setup(query, {curatedProtocol = true, sourceProtocol = true, pathname = "/"} = {}) {
  const elements = new Map();
  const buttons = [...html.matchAll(/<button[^>]+data-(source-target|target)="([^"]+)"[^>]*>/g)].map(match => {
    const node = new Element('button');
    node.dataset[match[1] === 'source-target' ? 'sourceTarget' : 'target'] = match[2];
    node.hidden = /\bhidden\b/.test(match[0]);
    return node;
  });
  const protocolLabels = [new Element('span'), new Element('span')];
  protocolLabels.forEach(node => node.dataset.i18n = 'targetProtocol');
  const document = {baseURI: 'https://awesomerea.org/', documentElement: {dataset: {}}, activeElement: {tagName: 'BODY'},
    querySelector(selector) {
      if (selector === '[data-target="protocol"]') return buttons.find(node => node.dataset.target === 'protocol');
      if (selector === '[data-source-target="protocol"]') return buttons.find(node => node.dataset.sourceTarget === 'protocol');
      if (!elements.has(selector)) elements.set(selector, new Element()); return elements.get(selector); },
    querySelectorAll(selector) {
      if (selector === '[data-target]') return buttons.filter(node => node.dataset.target);
      if (selector === '[data-source-target]') return buttons.filter(node => node.dataset.sourceTarget);
      if (selector === '[data-i18n]') return protocolLabels;
      return [];
    }, createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag),
    createDocumentFragment: () => new Element('fragment'), addEventListener() {}};
  const rows = ['protocol', 'app'].map((target, index) => ({id: 'fixture-' + index, name: 'Fixture ' + index, name_zh: '测试 ' + index,
    full_name: 'Fixture/project' + index, url: 'https://github.com/Fixture/project' + index,
    evidence_url: 'https://github.com/Fixture/project' + index, description_en: '', description_zh: '',
    targets: [target], topics: [], category: 'dynamic-analysis', group: 'tools', kind: 'tool', relationship: 'foundation',
    requirements: ['A fixture'], requirements_zh: ['测试条件'], verified_at: '2026-01-01', scan_status: 'readme-scanned', stars: index}));
  const browser = {meta: {schema_version: 1, status: 'complete', full_export: 'source-index.json', full_export_sha256: 'a'.repeat(64),
    scope: {scanned_count: 2, excluded_count: 0, browse_count: 2}}, resources: rows.map((row, i) => ({...row, targets: !i && !sourceProtocol ? ['app'] : row.targets}))};
  const curatedRows = rows.map((row, i) => ({...row, targets: !i && !curatedProtocol ? ['app'] : row.targets}));
  const location = new URL('https://awesomerea.org' + pathname + query);
  const requests = [];
  location.assign = next => { location.lastNavigation = String(next); };
  const context = {document, location, URL, URLSearchParams, console,
    history: {replaceState(_, __, next) { location.href = String(next); location.search = new URL(next).search; }},
    fetch: async url => { requests.push(String(url)); return {ok: true, json: async () => new URL(url).pathname.endsWith('catalog.json') ? {resources: curatedRows, meta: {source_index: {resource_count: 2}}} : browser}; }};
  vm.createContext(context);
  vm.runInContext(script.replace('applyLanguage(); load();', '') + '\nglobalThis.audit = {state,sourceState,load,loadSources,filtered,sourceFiltered,applyLanguage,reset,resetSources,setIndexMode};', context);
  return {api: context.audit, context, elements, buttons, protocolLabels, requests};
}
(async () => {
  for (const lang of ['en', 'zh']) {
    const app = setup(`?view=curated&target=protocol&source-target=protocol&lang=${lang}`);
    await app.api.load();
    await app.api.loadSources();
    assert.equal(app.api.state.error, false);
    assert.equal(app.api.sourceState.error, false);
    assert.equal(app.api.state.target, 'protocol');
    assert.equal(app.api.sourceState.target, 'protocol');
    app.api.applyLanguage();
    assert(app.protocolLabels.every(node => node.innerHTML === (lang === 'zh' ? '协议' : 'Protocol')));
    for (const query of ['protocol', '协议']) {
      app.api.state.q = query; app.api.sourceState.q = query;
      assert.equal(app.api.filtered().length, 1);
      assert.equal(app.api.sourceFiltered().length, 1);
    }
    app.api.state.q = ''; app.api.sourceState.q = '';
    app.api.sourceState.visible = 96;
    const sourceButton = app.buttons.find(node => node.dataset.sourceTarget === 'protocol');
    app.api.setIndexMode('source-index'); sourceButton.emit('click');
    assert.equal(app.api.sourceState.visible, 24);
    assert.equal(sourceButton.attrs['aria-pressed'], 'true');
    assert.equal(new URL(app.context.location.href).searchParams.get('source-target'), 'protocol');
    app.api.resetSources();
    assert.equal(app.api.sourceState.target, 'all');
    assert.equal(new URL(app.context.location.href).searchParams.has('source-target'), false);
    app.api.setIndexMode('curated'); app.api.state.visible = 45;
    app.buttons.find(node => node.dataset.target === 'protocol').emit('click');
    assert.equal(app.api.state.visible, 15);
    assert.equal(new URL(app.context.location.href).searchParams.get('target'), 'protocol');
    app.api.reset();
    assert.equal(app.api.state.target, 'all');
    assert.equal(new URL(app.context.location.href).searchParams.has('target'), false);
    app.api.state.q = '应用'; app.api.sourceState.q = '应用';
    assert.equal(app.api.filtered()[0].targets[0], 'app');
    assert.equal(app.api.sourceFiltered()[0].targets[0], 'app');
  }
  for (const [curatedProtocol, sourceProtocol] of [[false, false], [true, false], [false, true]]) {
    const app = setup('?view=curated&target=protocol&source-target=protocol', {curatedProtocol, sourceProtocol});
    await app.api.load(); await app.api.loadSources();
    const curatedButton = app.buttons.find(node => node.dataset.target === 'protocol');
    const sourceButton = app.buttons.find(node => node.dataset.sourceTarget === 'protocol');
    assert.equal(curatedButton.hidden, !curatedProtocol);
    assert.equal(sourceButton.hidden, !sourceProtocol);
    assert.equal(app.api.state.target, 'protocol');
    assert.equal(app.api.sourceState.target, 'protocol');
    app.api.state.q = 'no matching fixture'; app.api.sourceState.q = 'no matching fixture';
    app.api.applyLanguage();
    assert.equal(app.api.filtered().length, 0);
    assert.equal(app.api.sourceFiltered().length, 0);
    assert.equal(curatedButton.hidden, !curatedProtocol);
    assert.equal(sourceButton.hidden, !sourceProtocol);
    assert.equal(app.elements.get('#clear-filters').hidden, false);
    assert.equal(app.elements.get('#source-clear').hidden, false);
  }
  const chinese = setup('?view=curated&target=protocol#catalog', {pathname: '/zh/'});
  await chinese.api.load();
  assert.equal(chinese.api.state.lang, 'zh');
  assert(chinese.requests.every(url => !new URL(url).pathname.startsWith('/zh/')));
  const picker = chinese.elements.get('#language-select');
  picker.value = 'en'; picker.emit('change');
  const switched = new URL(chinese.context.location.lastNavigation);
  assert.equal(switched.pathname, '/');
  assert.equal(switched.searchParams.get('target'), 'protocol');
  assert.equal(switched.hash, '#catalog');
  assert.equal(switched.searchParams.has('lang'), false);
  const home = setup(''); await home.api.load();
  assert.equal(home.api.state.lang, 'en');
  assert.equal(home.api.sourceState.mode, 'curated');
  const invalid = setup('?view=curated&target=unrecognized&source-target=unrecognized');
  await invalid.api.load();
  assert.equal(invalid.api.state.target, 'all');
  assert.equal(invalid.api.sourceState.target, 'all');
  process.stdout.write('Protocol UI boundaries passed\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
