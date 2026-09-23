/* Minimal Streamlit Components v1 protocol. No build step or external CDN. */
"use strict";
const Bridge = (() => {
  let active = null,
    timer = null;
  const post = (type, data = {}) =>
    window.parent.postMessage({ isStreamlitMessage: true, type, ...data }, "*");
  const height = () => {
    let h;
    try {
      h = window.parent.visualViewport?.height || window.parent.innerHeight;
    } catch {
      h = window.visualViewport?.height || window.innerHeight;
    }
    post("streamlit:setFrameHeight", {
      height: Math.max(240, h || window.innerHeight),
    });
  };
  function transmit() {
    if (!active) return;
    post("streamlit:setComponentValue", {
      value: active.event,
      dataType: "json",
    });
    clearTimeout(timer);
    timer = setTimeout(() => {
      document.querySelector("#connection").classList.remove("hidden");
      window.FS?.releaseInput();
    }, 15000);
  }
  window.addEventListener("message", (e) => {
    if (e.source !== window.parent || e.data?.type !== "streamlit:render")
      return;
    height();
    const reply = e.data.args?.reply;
    if (active && reply?.id === active.event.id) {
      clearTimeout(timer);
      document.querySelector("#connection").classList.add("hidden");
      const resolve = active.resolve;
      active = null;
      resolve(reply);
    }
  });
  document.querySelector("#retry").onclick = transmit;
  window.addEventListener("resize", height);
  window.addEventListener("orientationchange", height);
  try {
    window.parent.addEventListener("resize", height);
    window.parent.visualViewport?.addEventListener("resize", height);
  } catch {}
  post("streamlit:componentReady", { apiVersion: 1 });
  height();
  return {
    get busy() {
      return !!active;
    },
    request(action, data = {}) {
      if (active) return Promise.reject(new Error("Espera a Python"));
      return new Promise((resolve) => {
        active = {
          event: {
            id: crypto.randomUUID
              ? crypto.randomUUID()
              : Date.now() + "-" + Math.random(),
            action,
            data,
          },
          resolve,
        };
        transmit();
      });
    },
  };
})();
