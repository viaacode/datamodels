#!/usr/bin/env python3
"""Render the migration manifest as a standalone, offline HTML report."""

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit


def link(uri):
    text = escape(uri)
    if urlsplit(uri).scheme in {"http", "https"}:
        return f'<a href="{escape(uri, quote=True)}">{text}</a>'
    return text


def bars(counts):
    maximum = max(counts.values(), default=1) or 1
    return "".join(
        f'<div class="bar"><span>{escape(name)}</span><b>{count:,}</b>'
        f'<i style="width:{100 * count / maximum:.2f}%"></i></div>'
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )


def triple_text(triple):
    if triple is None:
        return "—"
    parts = []
    for term in triple:
        if "uri" in term:
            parts.append(f"<{term['uri']}>")
        elif "bnode" in term:
            parts.append("_:" + term["bnode"])
        else:
            value = json.dumps(term["literal"], ensure_ascii=False)
            if term.get("language"):
                value += "@" + term["language"]
            if term.get("datatype"):
                value += f"^^<{term['datatype']}>"
            parts.append(value)
    return escape(" ".join(parts))


def render(data):
    terms = data["terms"]
    kinds = Counter(term["kind"] for term in terms.values())
    sources = data["selected"]
    changes = data.get("changes", [])
    rows = []
    for original, term in sorted(
        terms.items(), key=lambda item: (item[1]["english_label"].casefold(), item[0])
    ):
        unchanged = term["target"] == original
        rows.append(
            f'<tr data-unchanged="{str(unchanged).lower()}"{" hidden" if unchanged else ""} '
            f'data-kind="{escape(term["kind"], quote=True)}" '
            f'data-sources="{escape(json.dumps(term["sources"]), quote=True)}">'
            f"<td><strong>{escape(term['english_label'])}</strong>{link(original)}</td>"
            f"<td>{link(term['target'])}</td>"
            f'<td><span class="badge">{escape(term["kind"])}</span></td>'
            f"<td>{'<br>'.join(escape(source) for source in term['sources'])}</td></tr>"
        )
    options = lambda values: "".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in sorted(values)
    )
    change_rows = "".join(
        f"<tr><td><strong>{escape(change['reason'])}</strong>{escape(change['source'])}</td>"
        f"<td><code>{triple_text(change['before'])}</code></td>"
        f"<td><code>{triple_text(change['after'])}</code></td></tr>"
        for change in changes
    )
    stats = "".join(
        f"<div><b>{count:,}</b><span>{label}</span></div>"
        for label, count in [
            ("URI mappings", len(terms)),
            ("Source files", len(sources)),
            ("Selected triples", sum(sources.values())),
            ("Recorded changes", len(changes)),
        ]
    )
    return (
        PAGE.replace("<!-- NAMESPACE -->", escape(data["namespace"]))
        .replace("<!-- STATS -->", stats)
        .replace("<!-- KINDS -->", bars(kinds))
        .replace("<!-- SOURCES -->", bars(sources))
        .replace(
            "<!-- REASONS -->", bars(Counter(change["reason"] for change in changes))
        )
        .replace("<!-- KIND OPTIONS -->", options(kinds))
        .replace("<!-- SOURCE OPTIONS -->", options(sources))
        .replace("<!-- ROWS -->", "".join(rows))
        .replace("<!-- CHANGES -->", change_rows)
    )


PAGE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Model map · Migration explorer</title>
<style>
:root{color-scheme:light;--ink:#193440;--muted:#526973;--line:#dce5e8;--teal:#087e82}
*{box-sizing:border-box}body{margin:0;background:#f3f6f7;color:var(--ink);font:15px/1.55 system-ui,sans-serif}
header{background:#143541;color:white;padding:44px max(24px,calc((100vw - 1400px)/2)) 38px}
header p{margin:0;color:#b8d8df}h1{font-size:clamp(30px,4vw,46px);letter-spacing:-1.5px;margin:5px 0 12px}
header small{display:block;overflow-wrap:anywhere;color:#9edbd6}main{max-width:1448px;margin:auto;padding:28px 24px 50px}
h2{font-size:20px;margin:0 0 16px}a{color:var(--teal);text-decoration:none;overflow-wrap:anywhere}a:hover{text-decoration:underline}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stats>div,.panel{background:white;border:1px solid var(--line);border-radius:12px;padding:22px}
.stats b{display:block;font-size:30px;letter-spacing:-1px}.stats span,.hint{color:var(--muted)}
.overview{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px}
.bar{display:grid;grid-template-columns:1fr auto;position:relative;gap:12px;padding:7px 0 11px;margin-bottom:5px;font-size:13px}
.bar span{overflow-wrap:anywhere}.bar i{position:absolute;bottom:2px;height:4px;background:#29aaa4;border-radius:3px}
summary{cursor:pointer;font-weight:650}details.panel>summary{font-size:20px}details[open]>summary{margin-bottom:18px}
.toolbar{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;align-items:end}
label{display:grid;gap:5px;font-size:12px;font-weight:650}label:first-child{flex:1;min-width:220px}
.toggle{display:flex;align-items:center;gap:8px}
input,select{font:inherit;font-size:14px;padding:10px 12px;border:1px solid #a9bcc4;border-radius:7px;background:white;color:var(--ink);max-width:100%}
select{max-width:300px}input:focus-visible,select:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #e0a335;outline-offset:3px}
.table-wrap{overflow:auto;max-height:72vh;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13px}th{text-align:left;background:#edf3f4;position:sticky;top:0;z-index:1;font-size:11px;text-transform:uppercase;letter-spacing:.7px}
td,th{padding:14px 16px;border-bottom:1px solid var(--line);vertical-align:top}td{min-width:105px;max-width:430px;overflow-wrap:anywhere}
td strong{display:block;color:var(--ink);font-size:14px;margin-bottom:5px}tbody tr:hover{background:#f4faf9}
.badge{display:inline-block;background:#e2f3ef;color:#17665e;padding:3px 9px;border-radius:20px;font-size:12px}
.hint{font-size:13px;margin:8px 0 16px}.empty{text-align:center;padding:32px;color:var(--muted)}
.changes{margin-top:24px}.changes code{font-size:12px;white-space:pre-wrap}footer{font-size:12px;color:var(--muted);margin-top:22px}
@media(max-width:760px){.stats{grid-template-columns:repeat(2,1fr)}.overview{grid-template-columns:1fr}main{padding:20px 12px}.panel{padding:16px}header{padding:30px 20px}td{min-width:160px}}
</style>
<header><p>CONSOLIDATED MODEL / MIGRATION MANIFEST</p><h1>Model map explorer</h1>
<small><!-- NAMESPACE --></small></header>
<main>
<section class="stats" aria-label="Model summary"><!-- STATS --></section>
<div class="overview">
<section class="panel"><h2>Terms by kind</h2><!-- KINDS --></section>
<section class="panel"><h2>Changes by reason</h2><!-- REASONS --></section>
</div>
<details class="panel"><summary>Source contributions</summary>
<p class="hint">Selected triples per source file, before consolidation.</p><!-- SOURCES --></details>
<section class="panel" style="margin-top:24px"><h2>URI mappings</h2>
<p class="hint">Follow each original identifier into the consolidated namespace.</p>
<div class="toolbar">
<label>Search mappings<input id="search" type="search" placeholder="Label, URI, or source file…"></label>
<label>Kind<select id="kind"><option value="">All kinds</option><!-- KIND OPTIONS --></select></label>
<label>Source file<select id="source"><option value="">All sources</option><!-- SOURCE OPTIONS --></select></label>
<label class="toggle"><input id="show-unchanged" type="checkbox" aria-controls="mappings">Show unchanged mappings</label>
</div>
<p class="hint" id="count" role="status"></p>
<noscript><p>Changed mappings are shown. Enable JavaScript to show unchanged mappings, search, and filter.</p></noscript>
<div class="table-wrap"><table id="mappings" aria-label="Original to consolidated URI mappings">
<thead><tr><th scope="col">Label / original URI</th><th scope="col">Target URI</th><th scope="col">Kind</th><th scope="col">Defined in</th></tr></thead>
<tbody><!-- ROWS --></tbody></table><p class="empty" id="empty" hidden>No mappings match these filters.</p></div>
</section>
<details class="panel changes"><summary>Annotation and header changes</summary>
<div class="table-wrap"><table aria-label="Recorded changes"><thead><tr><th scope="col">Reason / source</th><th scope="col">Before</th><th scope="col">After</th></tr></thead>
<tbody><!-- CHANGES --></tbody></table></div></details>
<footer>Generated from model-map.json. This report describes URI migration and provenance; it does not contain class or property relationships.</footer>
</main>
<script>
const search = document.querySelector('#search');
const kind = document.querySelector('#kind');
const source = document.querySelector('#source');
const showUnchanged = document.querySelector('#show-unchanged');
const rows = Array.from(document.querySelectorAll('#mappings tbody tr'), row => ({
  row, text: row.textContent.toLowerCase(), sources: JSON.parse(row.dataset.sources)
}));
function filter() {
  const query = search.value.trim().toLowerCase();
  let count = 0;
  for (const item of rows) {
    const visible = item.text.includes(query) && (!kind.value || item.row.dataset.kind === kind.value)
      && (!source.value || item.sources.includes(source.value))
      && (showUnchanged.checked || item.row.dataset.unchanged !== 'true');
    item.row.hidden = !visible;
    if (visible) count++;
  }
  document.querySelector('#count').textContent = `${count.toLocaleString()} of ${rows.length.toLocaleString()} mappings`;
  document.querySelector('#empty').hidden = count !== 0;
}
search.addEventListener('input', filter);
kind.addEventListener('change', filter);
source.addEventListener('change', filter);
showUnchanged.addEventListener('change', filter);
filter();
</script>
</html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("model-map.json"),
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="HTML path (default: alongside input)"
    )
    args = parser.parse_args(argv)
    output = args.output or args.input.with_suffix(".html")
    if output.resolve() == args.input.resolve():
        parser.error("output must differ from input")
    try:
        document = render(json.loads(args.input.read_text(encoding="utf-8")))
        output.write_text(document, encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Could not generate report: {error}\n")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
