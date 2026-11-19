"use strict";

const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const START = "/* __WAKELOCK_START__ */";
const END = "/* __WAKELOCK_END__ */";

function extract(rel) {
  const file = path.join(ROOT, rel);
  const text = fs.readFileSync(file, "utf8");
  const start = text.indexOf(START);
  const end = text.indexOf(END);
  if (start < 0 || end < 0) throw new Error("wake lock markers missing in " + rel);
  const lineStart = text.lastIndexOf("\n", start) + 1;
  const lineEnd = text.indexOf("\n", end);
  const block = text.slice(lineStart, lineEnd === -1 ? text.length : lineEnd);
  const lines = block.split("\n");
  const indents = lines.filter((l) => l.trim()).map((l) => l.match(/^ */)[0].length);
  const n = Math.min(...indents);
  return lines.map((l) => (l.length >= n ? l.slice(n) : l)).join("\n");
}

const staticBlock = extract("static/app.js");
const offlineBlock = extract("offline/app.js");

function makeDocument(hidden = false) {
  const listeners = {};
  return {
    get hidden() { return hidden; },
    set hidden(v) { hidden = Boolean(v); },
    addEventListener(type, fn) {
      (listeners[type] || (listeners[type] = [])).push(fn);
    },
    dispatchEvent(ev) {
      const type = typeof ev === "string" ? ev : ev.type;
      for (const fn of listeners[type] || []) fn();
    },
  };
}

function mockSentinel() {
  const s = {
    released: false,
    releaseCalls: 0,
    release() {
      s.releaseCalls += 1;
      return Promise.resolve().then(() => {
        s.released = true;
        if (s._onRelease) s._onRelease();
      });
    },
    addEventListener(type, fn) {
      if (type === "release") s._onRelease = fn;
    },
  };
  return s;
}

function loadApi(opts = {}) {
  const document = makeDocument(Boolean(opts.hidden));
  const sentinel = mockSentinel();
  const calls = [];
  const requestImpl = opts.requestImpl || (async (type) => {
    calls.push(type);
    return sentinel;
  });
  const navigator = Object.prototype.hasOwnProperty.call(opts, "navigator")
    ? opts.navigator
    : { wakeLock: { request: requestImpl } };
  const sandbox = { navigator, document, Promise };
  vm.runInNewContext(staticBlock, sandbox, { filename: "wakelock.js" });
  return {
    init: sandbox.initWakeLock,
    request: sandbox.requestWakeLock,
    release: sandbox.releaseWakeLock,
    document,
    calls,
    sentinel,
  };
}

describe("wake lock helper is shared", () => {
  it("uses the same helper in the online and offline app JS", () => {
    assert.equal(offlineBlock, staticBlock);
  });
});

describe("wakelock", () => {
  it("requests a screen lock while a verse is on screen", async () => {
    const api = loadApi();
    api.init();
    await api.request();
    assert.deepEqual(api.calls, ["screen"]);
    assert.equal(typeof api.sentinel._onRelease, "function");
  });

  it("is a no-op when wakeLock is missing", async () => {
    const api = loadApi({ navigator: {} });
    api.init();
    await api.request();
    assert.deepEqual(api.calls, []);
  });

  it("is a no-op when the tab is hidden", async () => {
    const api = loadApi({ hidden: true });
    api.init();
    await api.request();
    assert.deepEqual(api.calls, []);
  });

  it("swallows request errors", async () => {
    const api = loadApi({
      requestImpl: async () => { throw new Error("denied"); },
    });
    api.init();
    await api.request();
  });

  it("does not request twice while the lock is held", async () => {
    const api = loadApi();
    api.init();
    await api.request();
    await api.request();
    assert.deepEqual(api.calls, ["screen"]);
  });

  it("releases the lock on error / stop", async () => {
    const api = loadApi();
    api.init();
    await api.request();
    await api.release();
    assert.equal(api.sentinel.releaseCalls, 1);
    assert.equal(api.sentinel.released, true);
  });

  it("swallows release errors", async () => {
    const api = loadApi();
    api.sentinel.release = () => Promise.reject(new Error("gone"));
    api.init();
    await api.request();
    await api.release();
  });

  it("re-requests on visibilitychange when the tab is visible again", async () => {
    const api = loadApi();
    api.init();
    await api.request();
    assert.deepEqual(api.calls, ["screen"]);
    api.document.hidden = true;
    api.sentinel.released = true;
    api.sentinel._onRelease();
    api.document.hidden = false;
    api.document.dispatchEvent({ type: "visibilitychange" });
    await Promise.resolve();
    await Promise.resolve();
    assert.deepEqual(api.calls, ["screen", "screen"]);
  });

  it("does not re-request on visibilitychange after release", async () => {
    const api = loadApi();
    api.init();
    await api.request();
    await api.release();
    api.document.dispatchEvent({ type: "visibilitychange" });
    await Promise.resolve();
    assert.deepEqual(api.calls, ["screen"]);
  });

  it("init is safe to call more than once", async () => {
    const api = loadApi();
    api.init();
    api.init();
    await api.request();
    api.document.hidden = true;
    api.sentinel.released = true;
    api.sentinel._onRelease();
    api.document.hidden = false;
    api.document.dispatchEvent({ type: "visibilitychange" });
    await Promise.resolve();
    await Promise.resolve();
    assert.deepEqual(api.calls, ["screen", "screen"]);
  });
});
