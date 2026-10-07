const state = {
  edition: "gen",
  reference: "John 3:16",
  sourceVisible: false,
  minimalMode: localStorage.getItem("verse-minimal") === "1",
  neighbors: { previous: null, next: null },
  requestNumber: 0,
};

const elements = {
  root: document.documentElement,
  stage: document.querySelector("#reading-stage"),
  form: document.querySelector("#reference-form"),
  input: document.querySelector("#reference-input"),
  suggestions: document.querySelector("#book-suggestions"),
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
  previousBottom: document.querySelector("#previous-button-bottom"),
  previousLabelBottom: document.querySelector("#previous-label-bottom"),
  next: document.querySelector("#next-button"),
  nextLabel: document.querySelector("#next-label"),
  nextBottom: document.querySelector("#next-button-bottom"),
  nextLabelBottom: document.querySelector("#next-label-bottom"),
  sourceButton: document.querySelector("#source-button"),
  sourceStatus: document.querySelector("#source-status"),
  minimalButton: document.querySelector("#minimal-button"),
  minimalStatus: document.querySelector("#minimal-status"),
  themeButton: document.querySelector("#theme-button"),
  themeMeta: document.querySelector('meta[name="theme-color"]'),
};

let suggestionRequest = 0;
let suggestionTimer = null;
let activeSuggestion = -1;

function bookQuery(value) {
  const trimmed = value.trimStart();
  if (!trimmed || /\s\d+[:.\s]*\d*$/.test(trimmed)) return null;
  return trimmed.slice(0, 40);
}

function closeSuggestions() {
  elements.suggestions.hidden = true;
  elements.suggestions.replaceChildren();
  elements.input.setAttribute("aria-expanded", "false");
  elements.input.removeAttribute("aria-activedescendant");
  activeSuggestion = -1;
}

function selectSuggestion(book) {
  elements.input.value = `${book} `;
  closeSuggestions();
  elements.input.focus();
}

function setActiveSuggestion(index) {
  const options = [...elements.suggestions.querySelectorAll("[role='option']")];
  if (!options.length) return;
  activeSuggestion = (index + options.length) % options.length;
  options.forEach((option, optionIndex) => {
    const selected = optionIndex === activeSuggestion;
    option.setAttribute("aria-selected", String(selected));
    option.classList.toggle("active", selected);
  });
  elements.input.setAttribute("aria-activedescendant", options[activeSuggestion].id);
  options[activeSuggestion].scrollIntoView({ block: "nearest" });
}

function renderSuggestions(books) {
  if (!books.length) {
    closeSuggestions();
    return;
  }
  elements.suggestions.replaceChildren(
    ...books.map((book, index) => {
      const option = document.createElement("li");
      option.id = `book-suggestion-${index}`;
      option.role = "option";
      option.dataset.book = book;
      option.textContent = book;
      option.setAttribute("aria-selected", "false");
      option.addEventListener("mousedown", (event) => event.preventDefault());
      option.addEventListener("click", () => selectSuggestion(book));
      return option;
    }),
  );
  elements.suggestions.hidden = false;
  elements.input.setAttribute("aria-expanded", "true");
  activeSuggestion = -1;
}

async function fetchBookSuggestions(query) {
  const requestNumber = ++suggestionRequest;
  try {
    const response = await fetch(`api/books?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error("Book suggestions unavailable.");
    const data = await response.json();
    if (requestNumber === suggestionRequest && bookQuery(elements.input.value) === query) {
      renderSuggestions(data.books);
    }
  } catch (_error) {
    if (requestNumber === suggestionRequest) closeSuggestions();
  }
}

function preferredTheme() {
  const saved = localStorage.getItem("verse-theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function setTheme(theme) {
  elements.root.dataset.theme = theme;
  elements.themeButton.setAttribute("aria-label", `Use ${theme === "dark" ? "light" : "dark"} theme`);
  elements.themeMeta.content = theme === "dark" ? "#15130f" : "#ffffff";
  localStorage.setItem("verse-theme", theme);
}

function setMinimalMode(enabled) {
  state.minimalMode = enabled;
  elements.root.classList.toggle("minimal-mode", enabled);
  elements.minimalButton.setAttribute("aria-pressed", String(enabled));
  elements.minimalStatus.textContent = enabled ? "On" : "Off";
  localStorage.setItem("verse-minimal", enabled ? "1" : "0");
  if (enabled) closeSuggestions();
}

const KNOWN_EDITIONS = ["esv", "gen", "kj16", "kjv", "nasb"];

function mountPrefix() {
  const pathname = window.location.pathname;
  const mountEnd = pathname.indexOf("/verse/");
  if (mountEnd >= 0) return pathname.slice(0, mountEnd + "/verse/".length);
  if (pathname === "/verse") return "/verse/";
  return "/";
}

function prettyRef(reference) {
  const match = reference.trim().match(/^(.+?)\s+(\d+)\s*[:.\s]\s*(\d+)\s*$/);
  if (!match) return null;
  return `${match[1].trim().replace(/\s+/g, "-")}-${match[2]}-${match[3]}`;
}

function parsePrettyRef(slug) {
  const match = slug.match(/^(.+)-(\d+)-(\d+)$/);
  if (!match || !match[1]) return null;
  const book = match[1].replace(/-/g, " ");
  return `${book} ${match[2]}:${match[3]}`;
}

function urlState() {
  const params = new URLSearchParams(window.location.search);
  const sourceVisible = params.get("source") === "1";
  // Legacy share links (?v=&ref=) keep working and canonicalize on load.
  if (params.get("v") || params.get("ref")) {
    return {
      edition: params.get("v") || "gen",
      reference: params.get("ref") || "John 3:16",
      sourceVisible,
    };
  }
  // Pretty paths: /verse/John-3-16 or /verse/kjv/Ps-23-1
  const segs = window.location.pathname.replace(/\/+$/, "").split("/").filter(Boolean);
  if (segs[0] === "verse") segs.shift();
  let edition = "gen";
  let slug = segs.length ? segs[segs.length - 1] : "";
  if (segs.length >= 2 && KNOWN_EDITIONS.includes(segs[segs.length - 2].toLowerCase())) {
    edition = segs[segs.length - 2].toLowerCase();
  }
  const reference = parsePrettyRef(slug);
  return {
    edition,
    reference: reference || "John 3:16",
    sourceVisible,
  };
}

function updateUrl(mode = "replace") {
  const slug = prettyRef(state.reference) || "John-3-16";
  const source = state.sourceVisible ? "?source=1" : "";
  const url = `${mountPrefix()}${state.edition}/${slug}${source}`;
  const method = mode === "push" ? "pushState" : "replaceState";
  window.history[method]({}, "", url);
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
    state.edition = data.editions.some((edition) => edition.id === "gen") ? "gen" : data.editions[0]?.id;
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
  elements.previous.disabled = true;
  elements.previousBottom.disabled = true;
  elements.next.disabled = true;
  elements.nextBottom.disabled = true;
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
  elements.previousLabelBottom.textContent = neighborLabel(data.neighbors.previous);
  elements.nextLabel.textContent = neighborLabel(data.neighbors.next);
  elements.nextLabelBottom.textContent = neighborLabel(data.neighbors.next);
  elements.previous.disabled = !data.neighbors.previous;
  elements.previousBottom.disabled = !data.neighbors.previous;
  elements.next.disabled = !data.neighbors.next;
  elements.nextBottom.disabled = !data.neighbors.next;
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
  closeSuggestions();
  state.reference = elements.input.value;
  loadVerse({ historyMode: "push" });
});

elements.input.addEventListener("input", () => {
  window.clearTimeout(suggestionTimer);
  const query = bookQuery(elements.input.value);
  if (!query) {
    suggestionRequest += 1;
    closeSuggestions();
    return;
  }
  suggestionTimer = window.setTimeout(() => fetchBookSuggestions(query), 120);
});

elements.input.addEventListener("keydown", (event) => {
  if (elements.suggestions.hidden) return;
  const options = [...elements.suggestions.querySelectorAll("[role='option']")];
  if (event.key === "ArrowDown") {
    event.preventDefault();
    setActiveSuggestion(activeSuggestion + 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    setActiveSuggestion(activeSuggestion - 1);
  } else if (event.key === "Enter" && activeSuggestion >= 0) {
    event.preventDefault();
    selectSuggestion(options[activeSuggestion].dataset.book);
  } else if (event.key === "Escape") {
    closeSuggestions();
  }
});

elements.input.addEventListener("blur", () => {
  window.setTimeout(closeSuggestions, 100);
});

elements.editionSelect.addEventListener("change", () => {
  const previousEdition = state.edition;
  state.edition = elements.editionSelect.value;
  loadVerse({ historyMode: "push", restoreEdition: previousEdition });
});

elements.previous.addEventListener("click", () => navigate("previous"));
elements.previousBottom.addEventListener("click", () => navigate("previous"));
elements.next.addEventListener("click", () => navigate("next"));
elements.nextBottom.addEventListener("click", () => navigate("next"));
elements.retry.addEventListener("click", () => loadVerse());

// Match the comic reader's touch navigation: swipe left/right by 40px.
let touchStartX = null;
document.addEventListener("touchstart", (event) => {
  touchStartX = event.changedTouches[0].clientX;
}, { passive: true });
document.addEventListener("touchend", (event) => {
  if (touchStartX === null) return;
  const deltaX = event.changedTouches[0].clientX - touchStartX;
  if (deltaX < -40) navigate("next");
  else if (deltaX > 40) navigate("previous");
  touchStartX = null;
}, { passive: true });

elements.sourceButton.addEventListener("click", () => {
  state.sourceVisible = !state.sourceVisible;
  loadVerse();
});

elements.minimalButton.addEventListener("click", () => {
  setMinimalMode(!state.minimalMode);
});

elements.themeButton.addEventListener("click", () => {
  setTheme(elements.root.dataset.theme === "dark" ? "light" : "dark");
});

document.addEventListener("keydown", (event) => {
  const typing = event.target.matches("input, select, textarea, [contenteditable='true']");
  if (typing) return;
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    navigate("previous");
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    navigate("next");
  }
  if (event.key.toLowerCase() === "s") elements.sourceButton.click();
  if (event.key.toLowerCase() === "m") elements.minimalButton.click();
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
  setMinimalMode(state.minimalMode);
  try {
    await loadEditions();
    await loadVerse();
  } catch (error) {
    setLoading(false);
    showError(error.message || "Verse could not start.");
  }
}

init();
