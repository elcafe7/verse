/* Verse Offline — dependency-free reader over local data shards.
 * Same reading experience as the hosted app, minus the network:
 * verses load from data/<edition>/<book>.js, source text from data/src/.
 * Share state lives in the URL hash (#/kjv/Ps-23-1) so file:// links work.
 */
(function () {
  "use strict";

  var EDITIONS = ["kjv", "kj16", "gen"];

  var TSK_BOOK_ABBR = {
    "Genesis": "Ge.", "Exodus": "Ex.", "Leviticus": "Le.", "Numbers": "Nu.",
    "Deuteronomy": "De.", "Joshua": "Jos.", "Judges": "Jdg.", "Ruth": "Ru.",
    "1 Samuel": "1Sa.", "2 Samuel": "2Sa.", "1 Kings": "1Ki.", "2 Kings": "2Ki.",
    "1 Chronicles": "1Ch.", "2 Chronicles": "2Ch.", "Ezra": "Ezr.", "Nehemiah": "Neh.",
    "Esther": "Est.", "Job": "Job.", "Psalm": "Ps.", "Proverbs": "Pr.",
    "Ecclesiastes": "Ec.", "Song of Solomon": "So.", "Isaiah": "Is.", "Jeremiah": "Jer.",
    "Lamentations": "La.", "Ezekiel": "Eze.", "Daniel": "Da.", "Hosea": "Hos.",
    "Joel": "Joe.", "Amos": "Am.", "Obadiah": "Ob.", "Jonah": "Jon.",
    "Micah": "Mic.", "Nahum": "Nah.", "Habakkuk": "Hab.", "Zephaniah": "Zep.",
    "Haggai": "Hag.", "Zechariah": "Zec.", "Malachi": "Mal.",
    "Matthew": "Mt.", "Mark": "Mk.", "Luke": "Lk.", "John": "Jn.",
    "Acts": "Ac.", "Romans": "Ro.", "1 Corinthians": "1Co.", "2 Corinthians": "2Co.",
    "Galatians": "Ga.", "Ephesians": "Eph.", "Philippians": "Php.", "Colossians": "Col.",
    "1 Thessalonians": "1Th.", "2 Thessalonians": "2Th.",
    "1 Timothy": "1Ti.", "2 Timothy": "2Ti.", "Titus": "Tit.", "Philemon": "Phm.",
    "Hebrews": "Heb.", "James": "Jas.", "1 Peter": "1Pe.", "2 Peter": "2Pe.",
    "1 John": "1Jn.", "2 John": "2Jn.", "3 John": "3Jn.", "Jude": "Jude.",
    "Revelation": "Re."
  };

  var BIBLE_BOOKS = Object.keys(TSK_BOOK_ABBR).concat(
    ["Tobit", "Judith", "Wisdom of Solomon", "Ecclesiasticus", "Baruch",
     "1 Maccabees", "2 Maccabees", "1 Esdras", "2 Esdras",
     "Letter of Jeremiah", "Prayer of Azariah", "Susanna",
     "Bel and the Dragon", "Prayer of Manasseh"]
  );

  function normKey(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, ""); }

  var BOOK_ALIASES = {};
  BIBLE_BOOKS.forEach(function (book) {
    var low = book.toLowerCase();
    BOOK_ALIASES[low.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")] = book;
    BOOK_ALIASES[low.replace(/[^a-z0-9]+/g, "")] = book;
    var abbr = (TSK_BOOK_ABBR[book] || "").replace(/\.$/, "").toLowerCase();
    if (abbr) {
      BOOK_ALIASES[abbr.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")] = book;
      BOOK_ALIASES[abbr.replace(/[^a-z0-9]+/g, "")] = book;
    }
  });
  // Extra aliases mirroring the hosted reader (subset covering every book).
  var EXTRA = {
    "ge": "Genesis", "gn": "Genesis", "gen": "Genesis", "ex": "Exodus", "exo": "Exodus",
    "lev": "Leviticus", "num": "Numbers", "deut": "Deuteronomy", "dt": "Deuteronomy",
    "josh": "Joshua", "judg": "Judges", "1sam": "1 Samuel", "2sam": "2 Samuel",
    "1kgs": "1 Kings", "2kgs": "2 Kings", "1chr": "1 Chronicles", "2chr": "2 Chronicles",
    "ezr": "Ezra", "neh": "Nehemiah", "est": "Esther", "psa": "Psalm", "psalms": "Psalm",
    "prov": "Proverbs", "ecc": "Ecclesiastes", "eccl": "Ecclesiastes", "sos": "Song of Solomon",
    "canticles": "Song of Solomon", "isa": "Isaiah", "jer": "Jeremiah", "lam": "Lamentations",
    "ezek": "Ezekiel", "dan": "Daniel", "hos": "Hosea", "obad": "Obadiah", "jon": "Jonah",
    "mic": "Micah", "nah": "Nahum", "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai",
    "zech": "Zechariah", "mal": "Malachi", "matt": "Matthew", "mrk": "Mark", "lu": "Luke",
    "jhn": "John", "joh": "John", "ac": "Acts", "rom": "Romans", "1cor": "1 Corinthians",
    "2cor": "2 Corinthians", "gal": "Galatians", "eph": "Ephesians", "phil": "Philippians",
    "col": "Colossians", "1thess": "1 Thessalonians", "2thess": "2 Thessalonians",
    "1tim": "1 Timothy", "2tim": "2 Timothy", "tit": "Titus", "phlm": "Philemon",
    "heb": "Hebrews", "jam": "James", "1pet": "1 Peter", "2pet": "2 Peter",
    "1jhn": "1 John", "2jhn": "2 John", "3jhn": "3 John", "rev": "Revelation", "rv": "Revelation",
    "revelations": "Revelation", "psalm": "Psalm", "song": "Song of Solomon",
    "tob": "Tobit", "tobit": "Tobit", "jdt": "Judith", "judith": "Judith",
    "wis": "Wisdom of Solomon", "wisdomofsolomon": "Wisdom of Solomon",
    "sir": "Ecclesiasticus", "ecclesiasticus": "Ecclesiasticus", "sirach": "Ecclesiasticus",
    "bar": "Baruch", "baruch": "Baruch",
    "1macc": "1 Maccabees", "1maccabees": "1 Maccabees",
    "2macc": "2 Maccabees", "2maccabees": "2 Maccabees",
    "1esdras": "1 Esdras", "2esdras": "2 Esdras",
    "letterofjeremiah": "Letter of Jeremiah",
    "prayerofazariah": "Prayer of Azariah", "susanna": "Susanna",
    "belandthedragon": "Bel and the Dragon", "bel": "Bel and the Dragon",
    "prayerofmanasseh": "Prayer of Manasseh"
  };
  Object.keys(EXTRA).forEach(function (k) { BOOK_ALIASES[k] = EXTRA[k]; });

  function normalizeBook(book) {
    return BOOK_ALIASES[normKey(book)] || book.replace(/\s+/g, " ").replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); });
  }

  function slug(book) {
    return book.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  }

  function storeGet(key) {
    try { return window.localStorage.getItem(key); } catch (_e) { return null; }
  }
  function storeSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (_e) { /* file:// may deny storage */ }
  }

  var state = {
    edition: storeGet("verse-offline-edition") || "gen",
    reference: "John 3:16",
    sourceVisible: false,
    minimalMode: storeGet("verse-offline-minimal") === "1",
    neighbors: { previous: null, next: null },
    requestNumber: 0
  };
  if (EDITIONS.indexOf(state.edition) < 0) state.edition = "gen";

  var elements = {};
  ["stage", "form", "input", "suggestions", "editionSelect", "referenceTitle",
   "editionName", "verseText", "sourceCard", "sourceLabel", "sourceText",
   "transliteration", "errorCard", "errorMessage", "retry", "previous",
   "previousLabel", "previousBottom", "previousLabelBottom", "next", "nextLabel",
   "nextBottom", "nextLabelBottom", "sourceButton", "sourceStatus", "minimalButton",
   "minimalStatus", "themeButton", "themeMeta"].forEach(function (name) { elements[name] = null; });

  function $(id) { return document.getElementById(id); }

  function collect() {
    elements.root = document.documentElement;
    elements.stage = $("reading-stage");
    elements.form = $("reference-form");
    elements.input = $("reference-input");
    elements.suggestions = $("book-suggestions");
    elements.editionSelect = $("edition-select");
    elements.referenceTitle = $("reference-title");
    elements.editionName = $("edition-name");
    elements.verseText = $("verse-text");
    elements.sourceCard = $("source-card");
    elements.sourceLabel = $("source-label");
    elements.sourceText = $("source-text");
    elements.transliteration = $("source-transliteration");
    elements.errorCard = $("error-card");
    elements.errorMessage = $("error-message");
    elements.retry = $("error-retry");
    elements.previous = $("previous-button");
    elements.previousLabel = $("previous-label");
    elements.previousBottom = $("previous-button-bottom");
    elements.previousLabelBottom = $("previous-label-bottom");
    elements.next = $("next-button");
    elements.nextLabel = $("next-label");
    elements.nextBottom = $("next-button-bottom");
    elements.nextLabelBottom = $("next-label-bottom");
    elements.sourceButton = $("source-button");
    elements.sourceStatus = $("source-status");
    elements.minimalButton = $("minimal-button");
    elements.minimalStatus = $("minimal-status");
    elements.themeButton = $("theme-button");
    elements.themeMeta = document.querySelector('meta[name="theme-color"]');
  }

  /* ---------- data loading (<script> tags work over file://) ---------- */

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("Data file missing: " + src)); };
      document.head.appendChild(s);
    });
  }

  function editionBooks(ed) { return window.VERSE_INDEX.editions[ed]; }

  function ensureBook(ed, book) {
    var data = window.VERSE_DATA || {};
    if (data[ed] && data[ed][book]) return Promise.resolve();
    return loadScript("data/" + ed + "/" + slug(book) + ".js").then(function () {
      if (!(window.VERSE_DATA[ed] && window.VERSE_DATA[ed][book])) {
        throw new Error("“" + book + "” is not in this edition.");
      }
    });
  }

  function ensureSource(book) {
    var data = window.VERSE_DATA || {};
    if (data.src && data.src[book]) return Promise.resolve(data.src[book]);
    return loadScript("data/src/" + slug(book) + ".js").then(function () {
      return (window.VERSE_DATA.src || {})[book] || null;
    }, function () { return null; });
  }

  function parseReference(raw) {
    var match = String(raw).trim().match(/^(.+?)\s+(\d+)(?:[:.\s]+)(\d+)\s*$/);
    if (!match) throw new Error("Use a reference such as John 3:16.");
    var book = normalizeBook(match[1].trim());
    var chapter = parseInt(match[2], 10), verse = parseInt(match[3], 10);
    if (!(chapter >= 1 && verse >= 1)) throw new Error("Chapter and verse must be greater than zero.");
    return { book: book, chapter: chapter, verse: verse };
  }

  function displayRef(book, chapter, verse) { return book + " " + chapter + ":" + verse; }

  function chapterList(ed, book) {
    var chapters = editionBooks(ed).books[book] || {};
    return Object.keys(chapters).map(Number).sort(function (a, b) { return a - b; });
  }

  function neighborOf(ed, book, chapter, verse, direction) {
    var E = editionBooks(ed);
    var chapters = chapterList(ed, book);
    var idx = chapters.indexOf(chapter);
    var maxV = (E.books[book] || {})[String(chapter)] || 0;
    if (direction > 0) {
      if (verse < maxV) return { book: book, chapter: chapter, verse: verse + 1 };
      for (var i = idx + 1; i < chapters.length; i++) {
        return { book: book, chapter: chapters[i], verse: 1 };
      }
      var order = E.order, oi = order.indexOf(book);
      for (var j = oi + 1; j < order.length; j++) {
        var chs = chapterList(ed, order[j]);
        if (chs.length) return { book: order[j], chapter: chs[0], verse: 1 };
      }
      return null;
    }
    if (verse > 1) return { book: book, chapter: chapter, verse: verse - 1 };
    for (var k = idx - 1; k >= 0; k--) {
      var prevMax = (E.books[book] || {})[String(chapters[k])] || 0;
      if (prevMax) return { book: book, chapter: chapters[k], verse: prevMax };
    }
    var ord = E.order, oi2 = ord.indexOf(book);
    for (var m = oi2 - 1; m >= 0; m--) {
      var pchs = chapterList(ed, ord[m]);
      if (pchs.length) {
        var lastCh = pchs[pchs.length - 1];
        var lastV = (E.books[ord[m]] || {})[String(lastCh)] || 0;
        if (lastV) return { book: ord[m], chapter: lastCh, verse: lastV };
      }
    }
    return null;
  }

  /* ---------- hash URLs (#/kjv/Ps-23-1) ---------- */

  function prettySlug(book, chapter, verse) {
    return book.replace(/\s+/g, "-") + "-" + chapter + "-" + verse;
  }

  function parseSlug(sl) {
    var match = sl.match(/^(.+)-(\d+)-(\d+)$/);
    if (!match || !match[1]) return null;
    return { book: normalizeBook(match[1].replace(/-/g, " ")), chapter: parseInt(match[2], 10), verse: parseInt(match[3], 10) };
  }

  function hashState() {
    var hash = (window.location.hash || "").replace(/^#\/?/, "");
    var sourceVisible = false;
    var sm = hash.match(/[?&]source=1$/);
    if (sm) { sourceVisible = true; hash = hash.slice(0, sm.index); }
    var parts = hash.split("/").filter(Boolean);
    if (!parts.length) return { edition: state.edition, ref: null, sourceVisible: sourceVisible };
    var edition = state.edition, refSlug = parts[parts.length - 1];
    if (parts.length >= 2 && EDITIONS.indexOf(parts[parts.length - 2].toLowerCase()) >= 0) {
      edition = parts[parts.length - 2].toLowerCase();
    }
    return { edition: edition, ref: parseSlug(refSlug), sourceVisible: sourceVisible };
  }

  function updateHash(mode) {
    var parsed;
    try { parsed = parseReference(state.reference); }
    catch (_e) { return; }
    var url = "#/" + state.edition + "/" + prettySlug(parsed.book, parsed.chapter, parsed.verse) +
      (state.sourceVisible ? "?source=1" : "");
    if (mode === "push") window.history.pushState({}, "", url);
    else window.history.replaceState({}, "", url);
  }

  /* ---------- rendering ---------- */

  var suggestionRequest = 0, suggestionTimer = null, activeSuggestion = -1;

  function bookQuery(value) {
    var trimmed = String(value).replace(/^\s+/, "");
    if (!trimmed || /\s\d+[:.\s]*\d*$/.test(trimmed)) return null;
    return trimmed.slice(0, 40);
  }

  function closeSuggestions() {
    elements.suggestions.hidden = true;
    while (elements.suggestions.firstChild) elements.suggestions.removeChild(elements.suggestions.firstChild);
    elements.input.setAttribute("aria-expanded", "false");
    elements.input.removeAttribute("aria-activedescendant");
    activeSuggestion = -1;
  }

  function selectSuggestion(book) {
    elements.input.value = book + " ";
    closeSuggestions();
    elements.input.focus();
  }

  function setActiveSuggestion(index) {
    var options = Array.prototype.slice.call(elements.suggestions.querySelectorAll("[role='option']"));
    if (!options.length) return;
    activeSuggestion = (index + options.length) % options.length;
    options.forEach(function (option, optionIndex) {
      var selected = optionIndex === activeSuggestion;
      option.setAttribute("aria-selected", String(selected));
      if (selected) option.classList.add("active"); else option.classList.remove("active");
    });
    elements.input.setAttribute("aria-activedescendant", options[activeSuggestion].id);
    if (options[activeSuggestion].scrollIntoView) options[activeSuggestion].scrollIntoView({ block: "nearest" });
  }

  function renderSuggestions(books) {
    if (!books.length) { closeSuggestions(); return; }
    while (elements.suggestions.firstChild) elements.suggestions.removeChild(elements.suggestions.firstChild);
    books.forEach(function (book, index) {
      var option = document.createElement("li");
      option.id = "book-suggestion-" + index;
      option.setAttribute("role", "option");
      option.textContent = book;
      option.setAttribute("aria-selected", "false");
      option.addEventListener("mousedown", function (event) { event.preventDefault(); });
      option.addEventListener("click", function () { selectSuggestion(book); });
      elements.suggestions.appendChild(option);
    });
    elements.suggestions.hidden = false;
    elements.input.setAttribute("aria-expanded", "true");
    activeSuggestion = -1;
  }

  function normLower(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, ""); }

  function fetchBookSuggestions(query) {
    var requestNumber = ++suggestionRequest;
    window.setTimeout(function () {
      if (requestNumber !== suggestionRequest) return;
      if (bookQuery(elements.input.value) !== query) return;
      var nq = normLower(query);
      var scored = [];
      BIBLE_BOOKS.forEach(function (book) {
        var nb = normLower(book);
        if (nb.indexOf(nq) === 0) scored.push([0, book.length, book]);
        else if (nb.indexOf(nq) >= 0) scored.push([1, book.length, book]);
      });
      scored.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
      renderSuggestions(scored.slice(0, 8).map(function (s) { return s[2]; }));
    }, 120);
  }

  function preferredTheme() {
    var saved = storeGet("verse-offline-theme");
    if (saved === "light" || saved === "dark") return saved;
    try {
      if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) return "light";
    } catch (_e) { /* offline contexts may lack matchMedia */ }
    return "dark";
  }

  function setTheme(theme) {
    elements.root.setAttribute("data-theme", theme);
    elements.themeButton.setAttribute("aria-label", "Use " + (theme === "dark" ? "light" : "dark") + " theme");
    if (elements.themeMeta) elements.themeMeta.content = theme === "dark" ? "#15130f" : "#ffffff";
    storeSet("verse-offline-theme", theme);
  }

  function setMinimalMode(enabled) {
    state.minimalMode = enabled;
    if (enabled) elements.root.classList.add("minimal-mode");
    else elements.root.classList.remove("minimal-mode");
    elements.minimalButton.setAttribute("aria-pressed", String(enabled));
    elements.minimalStatus.textContent = enabled ? "On" : "Off";
    storeSet("verse-offline-minimal", enabled ? "1" : "0");
    if (enabled) closeSuggestions();
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
    return neighbor ? displayRef(neighbor.book, neighbor.chapter, neighbor.verse) : "End of text";
  }

  function render(book, chapter, verse, text, source) {
    state.reference = displayRef(book, chapter, verse);
    var prev = neighborOf(state.edition, book, chapter, verse, -1);
    var next = neighborOf(state.edition, book, chapter, verse, 1);
    state.neighbors = { previous: prev, next: next };

    elements.input.value = state.reference;
    elements.editionSelect.value = state.edition;
    elements.referenceTitle.textContent = state.reference;
    elements.editionName.textContent = editionBooks(state.edition).name;
    elements.verseText.textContent = text;
    elements.previousLabel.textContent = neighborLabel(prev);
    elements.previousLabelBottom.textContent = neighborLabel(prev);
    elements.nextLabel.textContent = neighborLabel(next);
    elements.nextLabelBottom.textContent = neighborLabel(next);
    elements.previous.disabled = !prev;
    elements.previousBottom.disabled = !prev;
    elements.next.disabled = !next;
    elements.nextBottom.disabled = !next;
    elements.errorCard.hidden = true;
    document.querySelector(".verse-card").hidden = false;

    if (state.sourceVisible && source) {
      elements.sourceLabel.textContent = source.label;
      elements.sourceText.textContent = source.text;
      try {
        elements.sourceText.lang = source.language === "hebrew" ? "he" : "grc";
        elements.sourceText.dir = source.language === "hebrew" ? "rtl" : "ltr";
      } catch (_e) { /* older engines */ }
      elements.transliteration.textContent = source.transliteration;
      elements.sourceCard.hidden = false;
      elements.sourceStatus.textContent = source.label;
    } else {
      elements.sourceCard.hidden = true;
      elements.sourceStatus.textContent = state.sourceVisible ? "Unavailable" : "Hidden";
    }

    elements.sourceButton.setAttribute("aria-pressed", String(state.sourceVisible));
    document.title = state.reference + " (" + state.edition.toUpperCase() + ") — Verse Offline";
  }

  function loadVerse(opts) {
    opts = opts || {};
    var requestNumber = ++state.requestNumber;
    setLoading(true);
    var restoreEdition = opts.restoreEdition || null;

    var parsed;
    try {
      parsed = parseReference(state.reference);
    } catch (error) {
      setLoading(false);
      showError(error.message);
      return Promise.resolve();
    }

    return ensureBook(state.edition, parsed.book).then(function () {
      if (requestNumber !== state.requestNumber) return null;
      var text = ((window.VERSE_DATA[state.edition][parsed.book] || {})[String(parsed.chapter)] || {})[String(parsed.verse)];
      if (!text) throw new Error("Verse not found in " + state.edition.toUpperCase() + ".");
      if (!state.sourceVisible) return { text: text, source: null };
      return ensureSource(parsed.book).then(function (src) {
        var source = null;
        if (src && src.v && src.v[String(parsed.chapter)] && src.v[String(parsed.chapter)][String(parsed.verse)]) {
          var pair = src.v[String(parsed.chapter)][String(parsed.verse)];
          source = {
            language: src.lang,
            label: src.lang.charAt(0).toUpperCase() + src.lang.slice(1),
            text: pair[0], transliteration: pair[1]
          };
        }
        return { text: text, source: source };
      });
    }).then(function (result) {
      if (!result || requestNumber !== state.requestNumber) return;
      render(parsed.book, parsed.chapter, parsed.verse, result.text, result.source);
      updateHash(opts.historyMode || "replace");
    }).catch(function (error) {
      if (requestNumber !== state.requestNumber) return;
      if (restoreEdition) {
        state.edition = restoreEdition;
        elements.editionSelect.value = restoreEdition;
      }
      showError(error.message || "That verse could not be loaded.");
    }).then(function () {
      if (requestNumber === state.requestNumber) setLoading(false);
    });
  }

  function navigate(direction) {
    var neighbor = state.neighbors[direction];
    if (!neighbor) return;
    state.reference = displayRef(neighbor.book, neighbor.chapter, neighbor.verse);
    loadVerse({ historyMode: "push" });
  }

  function loadEditions() {
    var names = EDITIONS.map(function (id) { return { id: id, name: editionBooks(id).name }; });
    names.forEach(function (edition) {
      var option = document.createElement("option");
      option.value = edition.id;
      option.textContent = edition.id.toUpperCase() + " — " + edition.name;
      elements.editionSelect.appendChild(option);
    });
    if (EDITIONS.indexOf(state.edition) < 0) state.edition = "gen";
    elements.editionSelect.value = state.edition;
  }

  function applyHash() {
    var hs = hashState();
    state.edition = hs.edition;
    storeSet("verse-offline-edition", state.edition);
    if (hs.ref) state.reference = displayRef(hs.ref.book, hs.ref.chapter, hs.ref.verse);
    state.sourceVisible = hs.sourceVisible;
    return loadVerse();
  }

  function init() {
    collect();
    setTheme(preferredTheme());
    setMinimalMode(state.minimalMode);
    loadEditions();

    elements.form.addEventListener("submit", function (event) {
      event.preventDefault();
      closeSuggestions();
      state.reference = elements.input.value;
      loadVerse({ historyMode: "push" });
    });

    elements.input.addEventListener("input", function () {
      window.clearTimeout(suggestionTimer);
      var query = bookQuery(elements.input.value);
      if (!query) { suggestionRequest += 1; closeSuggestions(); return; }
      suggestionTimer = window.setTimeout(function () { fetchBookSuggestions(query); }, 120);
    });

    elements.input.addEventListener("keydown", function (event) {
      if (elements.suggestions.hidden) return;
      var options = Array.prototype.slice.call(elements.suggestions.querySelectorAll("[role='option']"));
      if (event.key === "ArrowDown") { event.preventDefault(); setActiveSuggestion(activeSuggestion + 1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); setActiveSuggestion(activeSuggestion - 1); }
      else if (event.key === "Enter" && activeSuggestion >= 0) {
        event.preventDefault();
        selectSuggestion(options[activeSuggestion].textContent);
      } else if (event.key === "Escape") { closeSuggestions(); }
    });

    elements.input.addEventListener("blur", function () {
      window.setTimeout(closeSuggestions, 100);
    });

    elements.editionSelect.addEventListener("change", function () {
      var previousEdition = state.edition;
      state.edition = elements.editionSelect.value;
      storeSet("verse-offline-edition", state.edition);
      loadVerse({ historyMode: "push", restoreEdition: previousEdition });
    });

    elements.previous.addEventListener("click", function () { navigate("previous"); });
    elements.previousBottom.addEventListener("click", function () { navigate("previous"); });
    elements.next.addEventListener("click", function () { navigate("next"); });
    elements.nextBottom.addEventListener("click", function () { navigate("next"); });
    elements.retry.addEventListener("click", function () { loadVerse(); });

    elements.sourceButton.addEventListener("click", function () {
      state.sourceVisible = !state.sourceVisible;
      loadVerse();
    });

    elements.minimalButton.addEventListener("click", function () {
      setMinimalMode(!state.minimalMode);
    });

    elements.themeButton.addEventListener("click", function () {
      setTheme(elements.root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });

    document.addEventListener("keydown", function (event) {
      var target = event.target;
      var typing = target && (target.matches("input, select, textarea") || target.isContentEditable);
      if (typing) return;
      if (event.key === "ArrowLeft") { event.preventDefault(); navigate("previous"); }
      else if (event.key === "ArrowRight") { event.preventDefault(); navigate("next"); }
      else if (event.key === "/") {
        event.preventDefault();
        elements.input.focus();
        elements.input.select();
      } else if (event.key === "s" || event.key === "S") { elements.sourceButton.click(); }
      else if (event.key === "m" || event.key === "M") { elements.minimalButton.click(); }
      else if (event.key === "t" || event.key === "T") { elements.themeButton.click(); }
    });

    window.addEventListener("hashchange", function () { applyHash(); });

    setLoading(false);
    applyHash().catch(function (error) {
      setLoading(false);
      showError(error.message || "Verse could not start.");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
