const state = {
  edition: "kjv",
  reference: "John 3:16",
  sourceVisible: false,
  neighbors: { previous: null, next: null },
  requestNumber: 0,
};

const elements = {
  root: document.documentElement,
  stage: document.querySelector("#reading-stage"),
  form: document.querySelector("#reference-form"),
  input: document.querySelector("#reference-input"),
  editionSelect: document.querySelector("#edition-select"),
  referenceTitle: document.querySelector("#reference-title"),
  editionName: document.querySelector("#edition-name"),
  verseText: document.querySelector("#verse-text"),
  sourceCard: document.querySelector("#source-card"),
  sourceLabel: document.querySelector("#source-label"),
  sourceText: document.querySelector("#source-text"),
  transliteration: document.querySelector("#source-transliteration"),
  errorCard: document.querySelector("#error-card"),
  errorMessage: document.querySelector("#error-message"),
  retry: document.querySelector("#error-retry"),
  previous: document.querySelector("#previous-button"),
  previousLabel: document.querySelector("#previous-label"),
  next: document.querySelector("#next-button"),
  nextLabel: document.querySelector("#next-label"),
  sourceButton: document.querySelector("#source-button"),
  sourceStatus: document.querySelector("#source-status"),
  themeButton: document.querySelector("#theme-button"),
  themeMeta: document.querySelector('meta[name="theme-color"]'),
};

function preferredTheme() {
  const saved = localStorage.getItem("verse-theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function setTheme(theme) {
  elements.root.dataset.theme = theme;
  elements.themeButton.setAttribute("aria-label", `Use ${theme === "dark" ? "light" : "dark"} theme`);
  elements.themeMeta.content = theme === "dark" ? "#15130f" : "#f4efe4";
  localStorage.setItem("verse-theme", theme);
}

function urlState() {
  const params = new URLSearchParams(window.location.search);
  return {
    edition: params.get("v") || "kjv",
    reference: params.get("ref") || "John 3:16",
    sourceVisible: params.get("source") === "1",
  };
}

function updateUrl(mode = "replace") {
  const params = new URLSearchParams({ v: state.edition, ref: state.reference });
  if (state.sourceVisible) params.set("source", "1");
  const method = mode === "push" ? "pushState" : "replaceState";
  window.history[method]({}, "", `${window.location.pathname}?${params}`);
}

async function loadEditions() {
  const response = await fetch("api/editions");
  if (!response.ok) throw new Error("Edition list could not be loaded.");
  const data = await response.json();
  elements.editionSelect.replaceChildren(
    ...data.editions.map((edition) => {
      const option = document.createElement("option");
      option.value = edition.id;
      option.textContent = `${edition.id.toUpperCase()} — ${edition.name}`;
      return option;
    }),
  );
  if (!data.editions.some((edition) => edition.id === state.edition)) {
    state.edition = data.editions[0]?.id || "kjv";
  }
  elements.editionSelect.value = state.edition;
}

function setLoading(loading) {
  elements.stage.setAttribute("aria-busy", String(loading));
  elements.form.querySelector("button").disabled = loading;
  elements.editionSelect.disabled = loading;
}

function showError(message) {
  elements.errorMessage.textContent = message;
  elements.errorCard.hidden = false;
  document.querySelector(".verse-card").hidden = true;
  elements.sourceCard.hidden = true;
}

function neighborLabel(neighbor) {
  return neighbor ? neighbor.display : "End of text";
}

function render(data) {
  const reference = data.reference;
  state.reference = reference.display;
  state.edition = data.edition.id;
  state.neighbors = data.neighbors;

  elements.input.value = reference.display;
  elements.editionSelect.value = state.edition;
  elements.referenceTitle.textContent = reference.display;
  elements.editionName.textContent = data.edition.name;
  elements.verseText.textContent = data.text;
  elements.previousLabel.textContent = neighborLabel(data.neighbors.previous);
  elements.nextLabel.textContent = neighborLabel(data.neighbors.next);
  elements.previous.disabled = !data.neighbors.previous;
  elements.next.disabled = !data.neighbors.next;
  elements.errorCard.hidden = true;
  document.querySelector(".verse-card").hidden = false;

  if (state.sourceVisible && data.source) {
    elements.sourceLabel.textContent = data.source.label;
    elements.sourceText.textContent = data.source.text;
    elements.sourceText.lang = data.source.language === "hebrew" ? "he" : "grc";
    elements.sourceText.dir = data.source.language === "hebrew" ? "rtl" : "ltr";
    elements.transliteration.textContent = data.source.transliteration;
    elements.sourceCard.hidden = false;
    elements.sourceStatus.textContent = data.source.label;
  } else {
    elements.sourceCard.hidden = true;
    elements.sourceStatus.textContent = state.sourceVisible ? "Unavailable" : "Hidden";
  }

  elements.sourceButton.setAttribute("aria-pressed", String(state.sourceVisible));
  document.title = `${reference.display} (${state.edition.toUpperCase()}) — Verse`;
}

async function loadVerse({ historyMode = "replace", restoreEdition = null } = {}) {
  const requestNumber = ++state.requestNumber;
  setLoading(true);
  const params = new URLSearchParams({
    edition: state.edition,
    reference: state.reference,
    source: state.sourceVisible ? "1" : "0",
  });

  try {
    const response = await fetch(`api/verse?${params}`);
    const data = await response.json();
    if (requestNumber !== state.requestNumber) return;
    if (!response.ok) throw new Error(data.error || "That verse could not be loaded.");
    render(data);
    updateUrl(historyMode);
  } catch (error) {
    if (requestNumber !== state.requestNumber) return;
    if (restoreEdition) {
      state.edition = restoreEdition;
      elements.editionSelect.value = restoreEdition;
    }
    showError(error.message || "The reader could not connect to the verse library.");
  } finally {
    if (requestNumber === state.requestNumber) setLoading(false);
  }
}

function navigate(direction) {
  const neighbor = state.neighbors[direction];
  if (!neighbor) return;
  state.reference = neighbor.display;
  loadVerse({ historyMode: "push" });
}

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  state.reference = elements.input.value;
  loadVerse({ historyMode: "push" });
});

elements.editionSelect.addEventListener("change", () => {
  const previousEdition = state.edition;
  state.edition = elements.editionSelect.value;
  loadVerse({ historyMode: "push", restoreEdition: previousEdition });
});

elements.previous.addEventListener("click", () => navigate("previous"));
elements.next.addEventListener("click", () => navigate("next"));
elements.retry.addEventListener("click", () => loadVerse());

elements.sourceButton.addEventListener("click", () => {
  state.sourceVisible = !state.sourceVisible;
  loadVerse();
});

elements.themeButton.addEventListener("click", () => {
  setTheme(elements.root.dataset.theme === "dark" ? "light" : "dark");
});

document.addEventListener("keydown", (event) => {
  if (event.target.matches("input, select, button")) return;
  if (event.key === "ArrowLeft") navigate("previous");
  if (event.key === "ArrowRight") navigate("next");
  if (event.key.toLowerCase() === "s") elements.sourceButton.click();
  if (event.key.toLowerCase() === "t") elements.themeButton.click();
  if (event.key === "/") {
    event.preventDefault();
    elements.input.focus();
    elements.input.select();
  }
});

window.addEventListener("popstate", () => {
  Object.assign(state, urlState());
  loadVerse();
});

async function init() {
  Object.assign(state, urlState());
  setTheme(preferredTheme());
  try {
    await loadEditions();
    await loadVerse();
  } catch (error) {
    setLoading(false);
    showError(error.message || "Verse could not start.");
  }
}

init();
