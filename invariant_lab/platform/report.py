from __future__ import annotations

import html
import json
from pathlib import Path

from .types import ScanResult

def markdown_report(result: ScanResult) -> str:
    lines = [
        "# Security Invariant Lab — Security Intelligence Report",
        "",
        f"Target: {result.root}",
        "",
        "## Metrics",
        "",
    ]
    for key, value in result.metrics.items():
        lines.append(f"- **{key}**: {value}")
    lines += ["", "## Findings", ""]
    if not result.findings:
        lines.append("No heuristic findings were produced.")
    for f in result.findings:
        lines += [
            f"### {f.id} — {f.title}",
            "",
            f"- Kind: {f.kind}",
            f"- Severity heuristic: {f.severity}",
            f"- Confidence: {f.confidence}",
            f"- Location: {f.file}:{f.line}",
            f"- Evidence: {f.evidence}",
            f"- Recommendation: {f.recommendation}",
            "",
        ]
    lines += ["## Candidate Properties", ""]
    for p in result.invariants:
        lines.append(f"- {p.name} → {p.expression} ({p.confidence})")
    lines += ["", "## Contracts", ""]
    for c in result.contracts:
        lines.append(f"- **{c.name}**: {len(c.functions)} functions, {len(c.state_variables)} state variables")
    return "\n".join(lines) + "\n"

def html_report(result: ScanResult) -> str:
    data = json.dumps(result.to_dict(), indent=2)
    findings = "".join(
        "<article><h3>{} — {}</h3><p><b>{}</b> / {} — {}:{}</p><pre>{}</pre><p>{}</p></article>".format(
            html.escape(f.id), html.escape(f.title), html.escape(f.severity),
            html.escape(f.confidence), html.escape(f.file), f.line,
            html.escape(f.evidence), html.escape(f.recommendation)
        )
        for f in result.findings
    )
    invs = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(p.name), html.escape(p.expression), html.escape(p.confidence)
        ) for p in result.invariants
    )
    metric_cards = "".join(
        "<div class='card'><span>{}</span><strong>{}</strong></div>".format(
            html.escape(str(k)), html.escape(str(v))
        ) for k, v in result.metrics.items()
    )
    data_html = html.escape(data)
    findings_html = findings or "<p>No heuristic findings.</p>"
    invs_html = invs or "<tr><td colspan='3'>No candidates.</td></tr>"
    return """<!doctype html>
<html><head><meta charset="utf-8"><title>SIL Security Report</title>
<style>
body{font-family:Inter,Segoe UI,Arial,sans-serif;background:#0b1020;color:#e9eefc;margin:0}
main{max-width:1180px;margin:auto;padding:36px}h1{font-size:32px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.card,article{background:#121a2f;border:1px solid #253252;border-radius:14px;padding:16px;margin:12px 0}
.card span{display:block;color:#93a4c7;font-size:12px}.card strong{font-size:24px}
table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid #253252;text-align:left}
pre{white-space:pre-wrap;background:#0a0f1d;padding:12px;border-radius:10px;overflow:auto}
small{color:#93a4c7}
</style></head><body><main>
<h1>Security Invariant Lab</h1><small>{root}</small>
<h2>Security Intelligence</h2><div class="grid">{cards}</div>
<h2>Findings</h2>{findings_html}
<h2>Candidate Security Properties</h2>
<table><tr><th>Name</th><th>Expression</th><th>Confidence</th></tr>{invs_html}</table>
<h2>Machine-readable snapshot</h2><pre>{data_html}</pre>
</main></body></html>""".format(
        root=html.escape(result.root), cards=metric_cards,
        findings_html=findings_html, invs_html=invs_html, data_html=data_html
    )

def write_reports(result: ScanResult, out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md = out / "report.md"
    html_path = out / "report.html"
    md.write_text(markdown_report(result), encoding="utf-8")
    html_path.write_text(html_report(result), encoding="utf-8")
    return md, html_path
