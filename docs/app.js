/* Language switch for the pages: Vietnamese by default, ?lang=en or the saved choice for English. */
(function () {
  "use strict";
  var KEY = "exomaly-how-lang";

  /** @returns {string} "vi" or "en" */
  function pick() {
    var fromUrl = /[?&]lang=(vi|en)\b/.exec(location.search);
    if (fromUrl) return fromUrl[1];
    try {
      var saved = localStorage.getItem(KEY);
      if (saved === "vi" || saved === "en") return saved;
    } catch (e) { /* storage blocked: fall through to the default */ }
    return "vi";
  }

  /** @param {string} lang "vi" or "en" */
  function apply(lang) {
    document.documentElement.setAttribute("data-lang", lang);
    document.documentElement.setAttribute("lang", lang);
  }

  apply(pick());

  document.addEventListener("DOMContentLoaded", function () {
    var buttons = document.querySelectorAll("[data-set-lang]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function (ev) {
        var lang = ev.currentTarget.getAttribute("data-set-lang");
        apply(lang);
        try { localStorage.setItem(KEY, lang); } catch (e) { /* ignore */ }
      });
    }
  });
})();
