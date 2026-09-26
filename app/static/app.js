// Tapwise front-end: landing page (+ explore) -> intro -> questions about your day -> results.
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const state = { questions: [], step: 0, answers: {}, lastResult: null };

const LABELS = {
  cost: { under_5_eur: "Under €5", "5_to_50_eur": "€5–50", over_50_eur: "€50+" },
  phone: { any: "Any phone", iphone_only: "iPhone", android_only: "Android" },
  model: { one_time_sale: "One-time sale", subscription_or_lease: "Subscription / lease", service: "Service", custom_product: "Custom product" },
  kind: { business: "For business", maker: "Build project" },
};

// ---------------------------------------------------------------- which questions/options to show
// show_if: ["drive", "travel_often"] -> only if one of these was ticked in "about you"
const facts = () => new Set(state.answers.about || []);
const visible = (item) => !item.show_if || item.show_if.some((f) => facts().has(f));
const optionsFor = (q) => (q.options || []).filter(visible);
const activeQuestions = () => state.questions.filter((q) => visible(q) && (q.type !== "multi" || optionsFor(q).length));

// ---------------------------------------------------------------- navigation
function show(view) {
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + view));
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (view === "quiz") renderQuestion();
}
document.addEventListener("click", (e) => {
  const go = e.target.closest("[data-go]");
  if (go) { e.preventDefault(); if (go.dataset.go === "quiz") state.step = 0; show(go.dataset.go); }
  const open = e.target.closest("[data-open]");
  if (open) openSuggest(!!open.dataset.withContext);
});

// ---------------------------------------------------------------- startup
async function init() {
  const [meta, explore] = await Promise.all([fetch("/api/meta").then((r) => r.json()), fetch("/api/explore").then((r) => r.json())]);
  state.questions = meta.questions;
  $("#stats").innerHTML = `
    <div class="stat"><b>${meta.stats.ideas}</b><span>NFC ideas</span></div>
    <div class="stat"><b>${meta.stats.creators}</b><span>creators credited</span></div>
    <div class="stat"><b>${meta.stats.sources}</b><span>videos & books</span></div>`;
  $("#engine").innerHTML = meta.engines.map((e) =>
    `<option value="${e.name}" ${e.available ? "" : "disabled"}>${esc(e.label)}${e.available ? "" : " (not set up)"}</option>`).join("");
  $("#engine").addEventListener("change", () => { if (state.lastResult) submit(); });
  renderExplore(explore);
}

function renderExplore(groups) {
  const pick = (key) => {
    const g = groups.find((x) => x.key === key);
    document.querySelectorAll(".tab").forEach((t) => t.setAttribute("aria-selected", t.dataset.key === key));
    $("#explore-grid").innerHTML = g.ideas.map((i) => `
      <div class="ex-card"><b>${esc(i.title)}</b><p>${esc(i.summary)}</p>
        <small>Setup: ${esc(i.setup_time)} · shown by ${i.creators} creator${i.creators > 1 ? "s" : ""}</small></div>`).join("");
  };
  $("#explore-tabs").innerHTML = groups.map((g) => `<button class="tab" role="tab" data-key="${g.key}">${esc(g.label)}</button>`).join("");
  $("#explore-tabs").addEventListener("click", (e) => { const t = e.target.closest(".tab"); if (t) pick(t.dataset.key); });
  pick(groups[0].key);
}

// ---------------------------------------------------------------- quiz
function renderQuestion() {
  const qs = activeQuestions();
  state.step = Math.min(state.step, qs.length - 1);
  const q = qs[state.step];
  $("#progress-bar").style.width = `${(state.step / qs.length) * 100}%`;
  $("#step-count").textContent = q.type === "intro" ? "Before we start" : `Step ${state.step} of ${qs.length - 1}`;
  $("#quiz-error").textContent = "";
  $("#btn-back").style.visibility = state.step === 0 ? "hidden" : "visible";
  const multiEmpty = q.type === "multi" && !(state.answers[q.id] || []).length;
  $("#btn-next").textContent = q.type === "intro" ? "Let's go" : state.step === qs.length - 1 ? "Show my ideas"
    : multiEmpty && q.id !== "about" ? "None of these, skip" : "Next";

  const val = state.answers[q.id];
  let body = "";
  if (q.type === "intro") {
    body = `<div class="intro-story"><span class="story-ico" aria-hidden="true">🚪</span><p>${esc(q.story)}</p></div>
      <div class="intro-points">${q.points.map((p) => `
      <div class="intro-point"><span class="ico">${p.icon}</span><div><b>${esc(p.title)}</b><span>${esc(p.text)}</span></div></div>`).join("")}</div>
      <div class="intro-rule"><span aria-hidden="true">📍</span><p>${esc(q.rule)}</p></div>
      <p class="intro-outro">${esc(q.outro)}</p>
      ${q.more ? `<a class="intro-more" href="${esc(q.more.url)}" target="_blank" rel="noopener">▶ ${esc(q.more.label)} ↗</a>` : ""}`;
  } else if (q.type === "text") {
    body = `<textarea id="q-text" placeholder="${esc(q.placeholder)}">${esc(val || "")}</textarea>`;
  } else {
    const opts = optionsFor(q);
    const chips = q.type === "multi" && q.id === "about";
    const tiles = q.type === "multi" && q.id !== "about";
    body = `<div class="options ${chips ? "chips" : ""} ${tiles ? "tiles" : ""}" role="${q.type === "multi" ? "group" : "radiogroup"}">` +
      opts.map((o) => {
        const sel = q.type === "multi" ? (val || []).includes(o.value) : val === o.value;
        return `<button type="button" class="option ${sel ? "selected" : ""}" data-value="${o.value}" aria-pressed="${sel}">
          ${o.icon ? `<span class="opt-ico" aria-hidden="true">${o.icon}</span>` : ""}<span class="opt-txt"><span class="label">${esc(o.label)}</span>${o.hint ? `<span class="hint">${esc(o.hint)}</span>` : ""}</span></button>`;
      }).join("") + "</div>";
  }
  $("#question").innerHTML = `<h2 class="q-title">${esc(q.title)}</h2>${q.subtitle ? `<p class="q-sub">${esc(q.subtitle)}</p>` : ""}${body}`;

  $("#question").querySelectorAll(".option").forEach((btn) => btn.addEventListener("click", () => {
    $("#quiz-error").textContent = "";
    if (q.type === "multi") {
      const set = new Set(state.answers[q.id] || []);
      set.has(btn.dataset.value) ? set.delete(btn.dataset.value) : set.add(btn.dataset.value);
      state.answers[q.id] = [...set];
      btn.classList.toggle("selected"); btn.setAttribute("aria-pressed", btn.classList.contains("selected"));
      const empty = !state.answers[q.id].length;
      if (q.id !== "about") $("#btn-next").textContent = state.step === activeQuestions().length - 1 ? "Show my ideas" : empty ? "None of these, skip" : "Next";
    } else {
      state.answers[q.id] = btn.dataset.value;
      $("#question").querySelectorAll(".option").forEach((b) => b.classList.toggle("selected", b === btn));
      setTimeout(next, 180);                       // single choice: move on automatically
    }
  }));
  const ta = $("#q-text");
  if (ta) { ta.addEventListener("input", () => (state.answers[q.id] = ta.value)); ta.focus(); }
}

function next() {
  const qs = activeQuestions();
  const q = qs[state.step];
  if (q.required && !state.answers[q.id]) { $("#quiz-error").textContent = "Pick one to continue."; return; }
  // drop answers to options that are no longer visible (e.g. un-ticked "I drive")
  if (q.id === "about") for (const other of state.questions) {
    if (other.type === "multi" && other.id !== "about" && state.answers[other.id]) {
      const ok = new Set(optionsFor(other).map((o) => o.value));
      state.answers[other.id] = visible(other) ? state.answers[other.id].filter((v) => ok.has(v)) : [];
    }
  }
  if (state.step < activeQuestions().length - 1) { state.step++; renderQuestion(); }
  else submit();
}
$("#btn-next").addEventListener("click", next);
$("#btn-back").addEventListener("click", () => { if (state.step > 0) { state.step--; renderQuestion(); } });
document.addEventListener("keydown", (e) => {
  if (!$("#view-quiz").classList.contains("active") || $("#suggest").open) return;
  if (e.key === "Enter" && !(e.target.tagName === "TEXTAREA" && !e.ctrlKey)) { e.preventDefault(); next(); }
});

// ---------------------------------------------------------------- results
async function submit() {
  $("#progress-bar").style.width = "100%";
  show("results");
  $("#results").innerHTML = `<div class="loading">Finding your ideas…</div>`;
  ["#shopping", "#tips", "#also"].forEach((s) => ($(s).innerHTML = ""));
  const res = await fetch("/api/match", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: state.answers, engine: $("#engine").value }),
  });
  const data = await res.json();
  if (!res.ok) { $("#results").innerHTML = `<div class="empty">${esc(data.error || "Something went wrong.")}</div>`; return; }
  state.lastResult = data;
  renderResults(data);
}

// Source icon: the site's own favicon (YouTube, Reddit…), a book for books, a link icon otherwise
function sourceIcon(s) {
  if (s.type === "book") return `<span class="src-ico">📖</span>`;
  if (s.domain) return `<img class="src-ico" src="https://www.google.com/s2/favicons?domain=${s.domain}&sz=64" alt="${esc(s.platform)}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'src-ico',textContent:'▶'}))">`;
  return `<span class="src-ico">🔗</span>`;
}

// Turn the first mention of "a sticker" / "an NFC tag" in a pitch into a link to that tag in shops
function linkTag(text, tag) {
  const safe = esc(text);
  if (!tag || !tag.shop_url) return safe;
  const re = /\b((?:an?|the|each|your|one) (?:NFC )?(?:stickers?|tags?)|NFC (?:stickers?|tags?))\b/i;
  return safe.replace(re, (m) => `<a class="tag-link" href="${esc(tag.shop_url)}" target="_blank" rel="noopener" title="${esc(tag.name)}: see it in shops">${m}</a>`);
}

function renderIdea(idea, open) {
  const meta = [
    idea.setup_time ? `⏱ ${esc(idea.setup_time)}` : "",
    idea.tag ? `🏷️ ${esc(idea.tag.price_hint.replace(/^about /, ""))}` : "",
    idea.why.length ? `<span class="for-you">For you</span>` : "",
  ].filter(Boolean).join(`<span class="dot-sep">·</span>`);

  const why = idea.why.map((w) => `
      <div class="why-item"><span class="said-text">${esc(w.you_said)}</span><p>${linkTag(w.pitch, idea.tag)}</p></div>`).join("");

  const steps = idea.steps.length ? `<div class="steps">${idea.steps.map((st, n) => `
      <div class="step"><div class="step-ico">${st.icon}<span class="step-n">${n + 1}</span></div>
        <b>${esc(st.title)}</b><p>${esc(st.text)}</p>${(st.links || []).map((l) => `<a class="step-link" href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join("")}</div>`).join("")}</div>` : "";

  const warn = idea.warnings.length || idea.needs_review ? `<div class="badges">${idea.warnings.map((w) => `<span class="badge warn">${esc(w)}</span>`).join("")}
      ${idea.needs_review ? `<span class="badge review" title="${esc(idea.review_flags.join(" · "))}">unverified</span>` : ""}</div>` : "";

  const business = idea.business ? `<div class="business"><b>Business angle</b><br>
      ${esc(LABELS.model[idea.business.model] || idea.business.model)} · customers: ${esc(idea.business.who_pays)} · startup cost: ${esc(idea.business.startup_cost)}</div>` : "";

  const sources = idea.sources.map((s) => `
    <li>${sourceIcon(s)}<div><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.creator || "Unknown")}</a>
      <span class="quote">${esc(s.title)}${s.quotes.length ? ` · listen for: “${esc(s.quotes[0])}”` : ""}${s.is_search ? " · (search link)" : ""}</span></div></li>`).join("");

  return `<details class="idea" ${open ? "open" : ""}>
    <summary><div class="idea-head"><span class="hook">${esc(idea.hook || idea.title)}</span>
      <span class="meta">${meta}</span></div><span class="chev" aria-hidden="true"></span></summary>
    <div class="idea-body">
      ${why ? `<div class="why">${why}</div>` : `<p>${esc(idea.summary)}</p>`}
      ${warn}${business}
      <h4>How to set it up</h4>${steps}
      <details class="more"><summary>More details</summary><p>${esc(idea.how_it_works)}</p>${idea.setup ? `<p><b>Apps:</b> ${esc(idea.setup)}</p>` : ""}</details>
      <h4>See it explained by ${idea.sources.length} creator${idea.sources.length > 1 ? "s" : ""}</h4>
      <ul class="sources">${sources}</ul>
    </div></details>`;
}

function renderResults(d) {
  const n = d.results.length;
  const list = n ? d.results : d.also;
  $("#results-title").textContent = n ? "See how NFC tags can help you" : "Ideas for people like you";
  $("#results-sub").textContent = n
    ? `${n} idea${n > 1 ? "s" : ""} based on what you told us. Open the ones that make you curious.`
    : "You didn't pick any annoyances, so here are popular ideas that fit your life.";

  $("#results").innerHTML = list.length ? list.map((x) => renderIdea(x, false)).join("")
    : `<div class="empty">Nothing fits yet. Try ticking a few everyday annoyances, or suggest an idea below.</div>`;

  $("#shopping").innerHTML = d.shopping_list.length ? `<details class="shopping-box"><summary>🛒 Your tag shopping list <span class="muted">(${d.shopping_list.length} type${d.shopping_list.length > 1 ? "s" : ""} of tag)</span></summary>
      <p class="muted">Shops use technical names, so copy the search term and paste it into any online shop.</p>
      <div class="shop-items">${d.shopping_list.map((t) => `
        <div class="shop-item"><b>${esc(t.name)}</b>
          <small>${esc(t.price_hint)} · for: ${esc(t.ideas.slice(0, 3).join(", "))}${t.ideas.length > 3 ? "…" : ""}</small>
          <div class="search-term"><span class="muted" style="font-size:.8rem">Type this in the shop:</span><code>${esc(t.search_term)}</code>
            <button class="mini-btn" data-copy="${esc(t.search_term)}">Copy</button>
            <a class="mini-btn" target="_blank" rel="noopener" href="https://www.google.com/search?tbm=shop&q=${encodeURIComponent(t.search_term)}">Search</a>
          </div></div>`).join("")}</div></details>` : "";
  $("#tips").innerHTML = d.tips.length ? `<details class="tips-box"><summary>💡 Good to know before you start</summary>${d.tips.map((t) => `<div class="tip">${esc(t)}</div>`).join("")}</details>` : "";
  $("#also").innerHTML = n && d.also.length ? `<h3>Also popular with people like you</h3>
      <p class="muted">You didn't mention these, but they fit your life.</p>
      ${d.also.map((x) => renderIdea(x, false)).join("")}` : "";
}

document.addEventListener("click", async (e) => {
  const b = e.target.closest("[data-copy]");
  if (!b) return;
  try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = "Copied ✓"; }
  catch { b.textContent = "Select & copy"; }
  setTimeout(() => (b.textContent = "Copy"), 1500);
});

// ---------------------------------------------------------------- suggest dialog
let sendContext = false;
function openSuggest(withContext) {
  sendContext = withContext;
  $("#suggest-form").hidden = false; $("#suggest-thanks").hidden = true;
  $("#suggest-form").reset(); $("#suggest-error").textContent = "";
  $("#suggest").showModal();
  $("#suggest-form textarea").focus();
}
$("#suggest-form").addEventListener("submit", async (e) => {
  if (e.submitter && e.submitter.value === "cancel") return;       // Cancel closes the dialog
  e.preventDefault();
  const f = new FormData(e.target);
  const body = Object.fromEntries(f.entries());
  body.credit_ok = f.has("credit_ok");
  if ((body.description || "").trim().length < 10) { $("#suggest-error").textContent = "Describe the idea in a sentence or two."; return; }
  if (body.email && !e.target.email.checkValidity()) { $("#suggest-error").textContent = "That email doesn't look right."; return; }
  if (sendContext) body.context = state.answers;
  $("#suggest-send").disabled = true;
  const res = await fetch("/api/suggest", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  $("#suggest-send").disabled = false;
  if (!res.ok) { $("#suggest-error").textContent = (await res.json()).error || "Couldn't send. Try again."; return; }
  $("#suggest-form").hidden = true; $("#suggest-thanks").hidden = false;
});
$("#suggest-form textarea").addEventListener("input", () => ($("#suggest-error").textContent = ""));
$("#suggest-close").addEventListener("click", () => $("#suggest").close());

init();
