/* Same-origin archive shell. Reads archive/index.json only; it does not fetch reports. */
(function () {
  var script = document.currentScript;
  if (!script || window.__aiDailyArchive) return;
  window.__aiDailyArchive = true;
  var root = new URL("./", script.src);

  var css = document.createElement("style");
  css.textContent = [
    ".arc-nav{box-sizing:border-box;position:fixed;top:0;bottom:0;left:0;width:min(300px,86vw);padding:18px 16px 28px;background:#f3f1ec;color:#1c1b19;border-right:1px solid #e4e1da;overflow:auto;overscroll-behavior:contain;z-index:40;transform:translateX(-100%);pointer-events:none;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC','Noto Sans SC','Source Han Sans SC','WenQuanYi Micro Hei',sans-serif;font-size:14px;line-height:1.45}",
    ".arc-nav *{box-sizing:border-box}",
    ".arc-nav a{color:inherit;text-decoration:none}",
    ".arc-backdrop{position:fixed;inset:0;background:rgba(28,27,25,.42);z-index:35;border:0;padding:0}",
    ".arc-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 14px;position:sticky;top:0;z-index:15;background:rgba(251,250,247,.94);border-bottom:1px solid #e4e1da;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans SC','WenQuanYi Micro Hei',sans-serif}",
    ".arc-open,.arc-close,.arc-go{font:inherit;color:#1c1b19;background:#fff;border:1px solid #d6d2c9;border-radius:8px;min-height:44px;padding:8px 12px;cursor:pointer}",
    ".arc-open{font-weight:600}",
    ".arc-close{padding:6px 10px;min-height:36px}",
    ".arc-pager{display:flex;gap:8px;margin-left:auto;min-width:0}",
    ".arc-pager a,.arc-edge{display:flex;flex-direction:column;justify-content:center;min-height:44px;min-width:0;padding:4px 10px;border:1px solid #e4e1da;border-radius:8px;background:#fff;color:#1c1b19;text-decoration:none;font-size:13px;line-height:1.3}",
    ".arc-pager a:hover{border-color:#1c1b19}",
    ".arc-edge{color:#8a857d;background:#f6f5f1}",
    ".arc-pager small{color:#57534e;font-size:12px}",
    ".arc-head{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}",
    ".arc-brand{font-size:15px;font-weight:700;letter-spacing:.04em}",
    ".arc-kicker{margin:4px 0 0;color:#8a857d;font-size:12px;letter-spacing:.08em}",
    ".arc-label{display:block;margin:14px 0 6px;color:#57534e;font-size:12px}",
    ".arc-q,.arc-date{width:100%;min-height:40px;border:1px solid #d6d2c9;border-radius:8px;background:#fff;color:#1c1b19;font:inherit;font-size:14px;padding:8px 10px}",
    ".arc-date-row{display:flex;gap:8px}",
    ".arc-date{min-width:0;flex:1}",
    ".arc-go{flex:none}",
    ".arc-msg{min-height:1.2em;margin:6px 0 0;color:#8a857d;font-size:12.5px}",
    ".arc-count{margin:12px 0 6px;color:#8a857d;font-size:12px}",
    ".arc-year,.arc-month{margin:0}",
    ".arc-year>summary,.arc-month>summary{cursor:pointer;list-style:none;font-weight:650}",
    ".arc-year>summary::-webkit-details-marker,.arc-month>summary::-webkit-details-marker{display:none}",
    ".arc-year>summary::before,.arc-month>summary::before{content:'';display:inline-block;width:0;height:0;margin-right:7px;border-top:4px solid transparent;border-bottom:4px solid transparent;border-left:5px solid currentColor;vertical-align:1px}",
    ".arc-year[open]>summary::before,.arc-month[open]>summary::before{border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid currentColor;border-bottom:0;vertical-align:2px}",
    ".arc-hit b,.arc-day{overflow-wrap:anywhere}",
    ".arc-year{margin-top:8px}",
    ".arc-year>summary{font-size:13px;letter-spacing:.12em;color:#57534e;padding:6px 0}",
    ".arc-month{margin:0 0 4px 2px}",
    ".arc-month>summary{font-size:14px;padding:6px 2px}",
    ".arc-day{display:grid;grid-template-columns:auto auto 1fr;gap:6px;align-items:baseline;padding:7px 8px;border-radius:8px;margin:1px 0}",
    ".arc-day[hidden],.arc-month[hidden],.arc-year[hidden],.arc-hit[hidden]{display:none !important}",
    ".arc-day:hover{background:#e8e4db}",
    ".arc-day.is-current{background:#1c1b19;color:#fbfaf7}",
    ".arc-day .num{font-variant-numeric:tabular-nums;font-weight:700}",
    ".arc-day .wk{color:#57534e;font-size:12px}",
    ".arc-day.is-current .wk,.arc-day.is-current .no{color:#d9d4ca}",
    ".arc-day .no{font-size:12.5px;color:#57534e}",
    ".arc-hits{margin-top:8px}",
    ".arc-hit{display:block;padding:8px;border-top:1px solid #e4e1da}",
    ".arc-hit:hover{background:#e8e4db}",
    ".arc-hit b{display:block;font-weight:600;font-size:13.5px}",
    ".arc-hit span{display:block;color:#57534e;font-size:12px;margin-bottom:2px}",
    ".arc-empty{margin:8px 0;color:#57534e;font-size:13px}",
    ".arc-nav :focus-visible,.arc-bar :focus-visible{outline:2px solid #3b6fd8;outline-offset:2px}",
    "@media (min-width:960px){",
    "body.arc-on{padding-left:292px}",
    ".arc-nav{width:292px;transform:none;pointer-events:auto;z-index:20}",
    ".arc-open,.arc-close,.arc-backdrop{display:none !important}",
    ".arc-bar.arc-home{display:none}",
    "}",
    "@media (max-width:959px){",
    "body.arc-open .arc-nav{transform:none;pointer-events:auto}",
    "}",
    "@media (max-width:420px){",
    ".arc-bar{flex-wrap:wrap;padding:8px 10px}",
    ".arc-pager{width:100%;margin-left:0}",
    ".arc-pager a,.arc-edge{flex:1}",
    "}",
    "@media print{.arc-nav,.arc-bar,.arc-backdrop{display:none !important}body.arc-on{padding-left:0}}",
    "html.arc-lock,html.arc-lock body{overflow:hidden}"
  ].join("");
  document.head.appendChild(css);
  document.body.classList.add("arc-on");

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function url(path) {
    return new URL(path, root).href;
  }
  function norm(value) {
    return String(value || "").toLowerCase().replace(/\s+/g, "").replace(/[年月日./_\-]/g, "");
  }
  function shortWeek(value) {
    return String(value || "").replace("星期", "周");
  }
  function focusable(container) {
    var nodes = container.querySelectorAll("a[href],button:not([disabled]),input:not([disabled]),summary");
    return Array.prototype.filter.call(nodes, function (node) {
      return node.getClientRects().length > 0;
    });
  }

  fetch(new URL("archive/index.json", script.src))
    .then(function (response) {
      if (!response.ok) throw new Error("index");
      return response.json();
    })
    .then(function (data) {
      var issues = (data.issues || []).slice().sort(function (a, b) {
        if (a.date === b.date) return a.path < b.path ? 1 : -1;
        return a.date < b.date ? 1 : -1;
      });
      var path = location.pathname;
      var current = null;
      issues.forEach(function (issue) {
        if (path.endsWith("/" + issue.path) || path.endsWith(issue.path)) current = issue;
      });
      var chrono = issues.slice().sort(function (a, b) {
        return a.date < b.date ? -1 : 1;
      });
      var index = -1;
      chrono.forEach(function (issue, i) {
        if (current && issue.date === current.date) index = i;
      });
      var prev = index > 0 ? chrono[index - 1] : null;
      var next = index >= 0 && index < chrono.length - 1 ? chrono[index + 1] : null;
      var openKey = (current || issues[0]).year + "-" + (current || issues[0]).month;
      var desktopQuery = window.matchMedia("(min-width:960px)");
      var lastFocus = null;

      var backdrop = el("button", "arc-backdrop");
      backdrop.type = "button";
      backdrop.setAttribute("aria-label", "关闭历史日报");
      backdrop.hidden = true;
      document.body.appendChild(backdrop);

      var nav = el("nav", "arc-nav");
      nav.id = "arc-nav";
      nav.setAttribute("aria-label", "历史日报");
      var head = el("div", "arc-head");
      var brandWrap = el("div");
      var brand = el("a", "arc-brand", data.publication || "AI 科技日报");
      brand.href = url("index.html");
      if (!current) brand.setAttribute("aria-current", "page");
      var kicker = el("p", "arc-kicker", "历史日报");
      brandWrap.appendChild(brand);
      brandWrap.appendChild(kicker);
      var closeBtn = el("button", "arc-close", "关闭");
      closeBtn.type = "button";
      closeBtn.setAttribute("aria-label", "关闭历史日报");
      head.appendChild(brandWrap);
      head.appendChild(closeBtn);
      nav.appendChild(head);

      var qLabel = el("label", "arc-label", "搜索");
      qLabel.htmlFor = "arc-q";
      var query = el("input", "arc-q");
      query.id = "arc-q";
      query.type = "search";
      query.placeholder = "日期、期号、标题或要点";
      query.setAttribute("aria-label", "搜索日期、期号、标题或今日要点");
      query.autocomplete = "off";
      nav.appendChild(qLabel);
      nav.appendChild(query);

      var dLabel = el("label", "arc-label", "跳到日期");
      dLabel.htmlFor = "arc-date";
      var dateRow = el("div", "arc-date-row");
      var dateInput = el("input", "arc-date");
      dateInput.id = "arc-date";
      dateInput.type = "date";
      if (issues.length) {
        var span = [];
        issues.forEach(function (issue) {
          (issue.jump || [issue.date]).forEach(function (day) { span.push(day); });
        });
        span.sort();
        dateInput.min = span[0];
        dateInput.max = span[span.length - 1];
      }
      if (current) dateInput.value = current.date;
      dateInput.setAttribute("aria-label", "选择已发布的日期");
      var go = el("button", "arc-go", "打开");
      go.type = "button";
      go.id = "arc-go";
      dateRow.appendChild(dateInput);
      dateRow.appendChild(go);
      var jumpMsg = el("p", "arc-msg");
      jumpMsg.id = "arc-jump-msg";
      jumpMsg.setAttribute("role", "status");
      nav.appendChild(dLabel);
      nav.appendChild(dateRow);
      nav.appendChild(jumpMsg);

      var count = el("p", "arc-count");
      count.setAttribute("role", "status");
      nav.appendChild(count);
      var tree = el("div", "arc-tree");
      nav.appendChild(tree);
      var hits = el("div", "arc-hits");
      nav.appendChild(hits);
      var empty = el("p", "arc-empty");
      empty.hidden = true;
      nav.appendChild(empty);
      document.body.appendChild(nav);

      var bar = el("div", "arc-bar");
      var openBtn = el("button", "arc-open", "历史日报");
      openBtn.type = "button";
      openBtn.setAttribute("aria-expanded", "false");
      openBtn.setAttribute("aria-controls", "arc-nav");
      bar.appendChild(openBtn);
      var pager = el("div", "arc-pager");
      pager.setAttribute("aria-label", "前后期");
      if (current) {
        pager.appendChild(edge("上一期", prev, "已是最早", "prev"));
        pager.appendChild(edge("下一期", next, "已是最新", "next"));
      } else {
        bar.classList.add("arc-home");
      }
      bar.appendChild(pager);
      document.body.insertBefore(bar, document.body.firstChild);

      var groups = {};
      var yearOrder = [];
      issues.forEach(function (issue) {
        var key = issue.year + "-" + issue.month;
        if (!groups[key]) {
          groups[key] = { year: issue.year, month: issue.month, items: [] };
          yearOrder.push(key);
        }
        groups[key].items.push(issue);
      });
      var years = {};
      yearOrder.forEach(function (key) {
        var group = groups[key];
        if (!years[group.year]) {
          var year = el("details", "arc-year");
          var ySum = el("summary", null, String(group.year));
          year.appendChild(ySum);
          years[group.year] = year;
          tree.appendChild(year);
        }
        var month = el("details", "arc-month");
        month.dataset.key = key;
        if (key === openKey) month.open = true;
        var mSum = el("summary", null, group.month + "月");
        month.appendChild(mSum);
        group.items.forEach(function (issue) {
          var link = el("a", "arc-day");
          link.href = url(issue.path);
          link.dataset.id = issue.id || issue.date;
          link.appendChild(el("span", "num", issue.label || String(issue.day)));
          link.appendChild(el("span", "wk", issue.issue ? shortWeek(issue.weekday) : ""));
          link.appendChild(el("span", "no", issue.issue ? ("第" + issue.issue + "期") : (issue.kicker || "")));
          if (current && issue.path === current.path) {
            link.classList.add("is-current");
            link.setAttribute("aria-current", "page");
          }
          month.appendChild(link);
        });
        if (key === openKey) years[group.year].open = true;
        years[group.year].appendChild(month);
      });

      function edge(label, issue, boundary, rel) {
        if (!issue) {
          var span = el("span", "arc-edge");
          span.setAttribute("aria-disabled", "true");
          span.appendChild(document.createTextNode(label));
          span.appendChild(el("small", null, boundary));
          return span;
        }
        var link = el("a");
        link.href = url(issue.path);
        link.rel = rel;
        link.appendChild(document.createTextNode(label));
        link.appendChild(el("small", null, issue.coverage || (issue.month + "月" + issue.day + "日")));
        return link;
      }

      function haystack(issue) {
        var parts = [issue.date, issue.title, issue.weekday, issue.kicker, issue.coverage, issue.label, issue.issue ? ("第" + issue.issue + "期") : "", issue.summary, issue.window];
        (issue.highlights || []).forEach(function (item) {
          parts.push(item.n, item.title);
        });
        return norm(parts.join(" "));
      }

      function applyFilter(raw) {
        var q = norm(raw);
        var visibleIssues = 0;
        var hitCount = 0;
        hits.textContent = "";
        issues.forEach(function (issue) {
          var matched = !q || haystack(issue).indexOf(q) !== -1;
          var link = tree.querySelector('.arc-day[data-id="' + (issue.id || issue.date) + '"]');
          if (link) link.hidden = !matched;
          if (matched) visibleIssues += 1;
          if (!q) return;
          (issue.highlights || []).forEach(function (item) {
            var blob = norm(item.title + item.n);
            if (blob.indexOf(q) === -1 && norm(issue.title + issue.date).indexOf(q) === -1) return;
            if (blob.indexOf(q) === -1) return;
            hitCount += 1;
            var hit = el("a", "arc-hit");
            hit.href = url(issue.path) + "#" + item.id;
            hit.appendChild(el("span", null, (issue.coverage || (issue.month + "月" + issue.day + "日")) + " · 要点 " + item.n));
            hit.appendChild(el("b", null, item.title));
            hits.appendChild(hit);
          });
        });
        Object.keys(groups).forEach(function (key) {
          var month = tree.querySelector('.arc-month[data-key="' + key + '"]');
          if (!month) return;
          var any = month.querySelector(".arc-day:not([hidden])");
          month.hidden = !any;
          if (q && any) month.open = true;
          if (!q) month.open = key === openKey;
        });
        Object.keys(years).forEach(function (year) {
          var node = years[year];
          var any = node.querySelector(".arc-month:not([hidden])");
          node.hidden = !any;
          if (q && any) node.open = true;
          if (!q) node.open = !!node.querySelector('.arc-month[data-key="' + openKey + '"]');
        });
        empty.hidden = !q || visibleIssues > 0 || hitCount > 0;
        empty.textContent = "没有匹配的日报";
        count.textContent = q
          ? "匹配 " + visibleIssues + " 期" + (hitCount ? " · " + hitCount + " 条要点" : "")
          : "已发布 " + issues.length + " 期";
      }

      function findDate(value) {
        var found = null;
        issues.forEach(function (issue) {
          var days = issue.jump || [issue.date];
          if (days.indexOf(value) !== -1 && (!found || issue.date === value)) found = issue;
        });
        return found;
      }
      function jump() {
        var value = dateInput.value;
        jumpMsg.textContent = "";
        if (!value) {
          jumpMsg.textContent = "请选择日期";
          return;
        }
        var found = findDate(value);
        if (!found) {
          jumpMsg.textContent = "这一天还没有日报";
          return;
        }
        location.href = url(found.path);
      }

      function isDesktop() {
        return desktopQuery.matches;
      }
      function contentNode() {
        return document.getElementById("content") || document.querySelector(".wrap");
      }
      function closeDrawer(restore) {
        var target = openBtn;
        if (restore && lastFocus && lastFocus.focus && !nav.contains(lastFocus)) target = lastFocus;
        if (restore) target.focus();
        document.body.classList.remove("arc-open");
        document.documentElement.classList.remove("arc-lock");
        backdrop.hidden = true;
        openBtn.setAttribute("aria-expanded", "false");
        nav.removeAttribute("role");
        nav.removeAttribute("aria-modal");
        if (!isDesktop()) nav.setAttribute("aria-hidden", "true");
        else nav.removeAttribute("aria-hidden");
        var content = contentNode();
        if (content) content.inert = false;
      }
      function openDrawer() {
        if (isDesktop()) return;
        lastFocus = document.activeElement && document.activeElement !== document.body ? document.activeElement : openBtn;
        document.body.classList.add("arc-open");
        document.documentElement.classList.add("arc-lock");
        backdrop.hidden = false;
        openBtn.setAttribute("aria-expanded", "true");
        nav.setAttribute("role", "dialog");
        nav.setAttribute("aria-modal", "true");
        nav.removeAttribute("aria-hidden");
        var content = contentNode();
        if (content) content.inert = true;
        closeBtn.focus();
      }
      function onKey(event) {
        if (event.key === "Escape") {
          if (document.body.classList.contains("arc-open")) {
            event.preventDefault();
            closeDrawer(true);
            return;
          }
          if (document.activeElement === query && query.value) {
            query.value = "";
            applyFilter("");
          }
          return;
        }
        if (event.key !== "Tab" || !document.body.classList.contains("arc-open")) return;
        var nodes = focusable(nav);
        if (!nodes.length) return;
        var first = nodes[0];
        var last = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }

      openBtn.addEventListener("click", function () {
        lastFocus = openBtn;
        openDrawer();
      });
      closeBtn.addEventListener("click", function () { closeDrawer(true); });
      backdrop.addEventListener("click", function () { closeDrawer(true); });
      document.addEventListener("keydown", onKey);
      query.addEventListener("input", function () { applyFilter(query.value); });
      go.addEventListener("click", jump);
      dateInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") jump();
      });
      nav.addEventListener("click", function (event) {
        var link = event.target.closest ? event.target.closest("a") : null;
        if (link && !isDesktop()) closeDrawer(false);
      });
      function syncMode() {
        if (isDesktop()) closeDrawer(false);
        else if (!document.body.classList.contains("arc-open")) nav.setAttribute("aria-hidden", "true");
      }
      if (desktopQuery.addEventListener) desktopQuery.addEventListener("change", syncMode);
      syncMode();
      applyFilter("");

      var hashId = location.hash.replace(/^#/, "");
      if (hashId) {
        var target = document.getElementById(hashId);
        if (target) {
          if (target.tagName === "DETAILS") target.open = true;
          var parent = target.parentNode;
          while (parent) {
            if (parent.tagName === "DETAILS") parent.open = true;
            parent = parent.parentNode;
          }
        }
      }
    })
    .catch(function () {
      document.body.classList.remove("arc-on");
    });
})();
