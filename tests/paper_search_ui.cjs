/* Offline checks of the shipped paper-search module and DOM interactions. */
const assert = require("node:assert/strict");
const search = require("../site/paper-search.js");

const papers = [
  {id: "paper-game", title: "Game State Reconstruction", title_zh: "游戏状态重建", authors: ["Ada Example"], doi: "10.1234/game", arxiv_id: "2601.01234", year: 2026, publication_status: "preprint", targets: ["game", "website"]},
  {id: "paper-app", title: "All Android Interfaces", title_zh: "全部安卓界面", authors: ["Bo Researcher"], doi: "10.2345/app", arxiv_id: null, year: 2025, publication_status: "conference-accepted", targets: ["app"]},
  {id: "paper-published", title: "Protocol Formats", title_zh: "协议格式", authors: ["Chen Reviewer"], doi: null, arxiv_id: null, year: 2025, publication_status: "conference-paper", targets: ["protocol"]}
];
const records = search.readRecords({schema_version: 1, papers});
const allowed = search.allowedValues(records);
const state = query => search.readState(new URLSearchParams(query), allowed);
for (const query of ["reconstruction", "游戏状态", "Ada", "10.1234/game", "2601.01234"]) {
  assert.deepEqual(records.filter(paper => search.matches(paper, state("q=" + encodeURIComponent(query)))).map(paper => paper.id), ["paper-game"]);
}
assert(search.matches(records[0], state("target=website&status=preprint&year=2026&q=game")));
assert(!search.matches(records[0], state("target=website&status=conference-paper&year=2026")));
assert.deepEqual(records.filter(paper => search.matches(paper, state("status=conference-accepted"))).map(paper => paper.id), ["paper-app"]);
assert.deepEqual(state("target=javascript:bad&status=published&year=2025.0"), {q: "", target: "all", status: "all", year: "all"});
assert.equal(state("q=" + "a".repeat(300)).q.length, 240);
assert.equal(search.stateURL("https://awesomerea.org/papers/?q=bad&q=duplicate&utm_source=fixture#paper-app", state("q=all&year=2025")).href,
  "https://awesomerea.org/papers/?utm_source=fixture&q=all&year=2025#paper-app");
for (const invalid of [{schema_version: 2, papers}, {schema_version: 1, papers: [...papers, papers[0]]}, {schema_version: 1, papers: [{...papers[0], targets: ["unknown"]}]}]) {
  assert.throws(() => search.readRecords(invalid));
}

class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.hidden = false; this.value = ""; this.textContent = ""; this.handlers = {}; this.children = []; }
  addEventListener(type, callback) { this.handlers[type] = callback; }
  emit(type, extra = {}) { this.handlers[type]?.({target: this, preventDefault() {}, ...extra}); }
  querySelectorAll(selector) { return selector === "[data-paper-id]" ? this.children : []; }
  querySelector() { return this.label; }
  focus() { this.focused = true; }
}
function setup(lang = "en", query = "", invalidData = false) {
  const ids = new Map(["paper-search", "paper-search-data", "paper-query", "paper-target", "paper-status", "paper-year", "paper-results", "paper-empty", "paper-clear", "paper-empty-reset"].map(id => [id, new Element()]));
  ids.get("paper-search").hidden = true;
  ids.get("paper-search-data").textContent = JSON.stringify({schema_version: invalidData ? 2 : 1, papers});
  const cards = papers.map(paper => new Element({paperId: paper.id}));
  const sections = papers.map((paper, i) => { const section = new Element({paperSection: paper.targets[0]}); section.children = [cards[i]]; section.label = new Element(); return section; });
  const topics = papers.map(paper => { const topic = new Element({paperTopic: paper.targets[0]}); topic.label = new Element(); return topic; });
  const language = new Element(); language.href = lang === "zh" ? "/papers/" : "/zh/papers/";
  const document = {documentElement: {lang: lang === "zh" ? "zh-CN" : "en"}, getElementById: id => ids.get(id),
    querySelector: selector => selector === ".papers-language" ? language : null,
    querySelectorAll: selector => ({"[data-paper-id]": cards, "[data-paper-section]": sections, "[data-paper-topic]": topics}[selector] || [])};
  const browser = {location: new URL("https://awesomerea.org" + (lang === "zh" ? "/zh/papers/" : "/papers/") + query), handlers: {}, calls: [],
    addEventListener(type, callback) { this.handlers[type] = callback; }};
  browser.history = Object.fromEntries(["replaceState", "pushState"].map(method => [method, (_, __, url) => { browser.location = new URL(url); browser.calls.push(method); }]));
  const initialized = search.initialize(document, browser);
  return {ids, cards, sections, topics, language, browser, initialized, visible: () => cards.filter(card => !card.hidden).map(card => card.dataset.paperId)};
}
for (const lang of ["en", "zh"]) {
  const app = setup(lang, "?target=website&year=2026#paper-game");
  assert(app.initialized); assert.equal(app.ids.get("paper-search").hidden, false);
  assert.deepEqual(app.visible(), ["paper-game"]);
  assert.equal(app.ids.get("paper-results").textContent, lang === "zh" ? "显示 1 / 3 篇论文" : "Showing 1 of 3 papers");
  assert.equal(new URL(app.language.href).hash, "#paper-game");
  assert.equal(new URL(app.language.href).searchParams.get("target"), "website");
  app.ids.get("paper-clear").emit("click"); assert.equal(app.visible().length, 3); assert(app.ids.get("paper-query").focused);
  const input = app.ids.get("paper-query"); const before = app.browser.location.href;
  input.emit("compositionstart"); input.value = "游戏"; input.emit("input", {isComposing: true});
  assert.equal(app.visible().length, 3); assert.equal(app.browser.location.href, before);
  input.emit("compositionend"); assert.deepEqual(app.visible(), ["paper-game"]);
  input.value = "no matching paper"; input.emit("input"); assert.equal(app.visible().length, 0); assert.equal(app.ids.get("paper-empty").hidden, false);
  assert(app.sections.every(section => section.hidden)); assert(app.topics.every(topic => topic.hidden));
  app.ids.get("paper-empty-reset").emit("click"); assert.equal(app.visible().length, 3); assert.equal(app.ids.get("paper-empty").hidden, true);
  assert(app.sections.every(section => !section.hidden));
  app.ids.get("paper-status").value = "conference-accepted"; app.ids.get("paper-status").emit("change");
  assert.deepEqual(app.visible(), ["paper-app"]); assert.equal(app.browser.calls.at(-1), "pushState");
  app.browser.location = new URL("https://awesomerea.org/papers/?q=protocol"); app.browser.handlers.popstate();
  assert.deepEqual(app.visible(), ["paper-published"]); assert.equal(app.ids.get("paper-status").value, "all");
}
const invalid = setup("en", "?status=bad&year=0&target=bad");
assert.equal(invalid.browser.location.search, ""); assert.equal(invalid.visible().length, 3);
const broken = setup("en", "?q=no-match", true);
assert.equal(broken.initialized, false); assert.equal(broken.ids.get("paper-search").hidden, true); assert.equal(broken.visible().length, 3);
console.log("Paper search: bilingual matching, facets, URLs, IME, history, reset and static fallback passed.");
