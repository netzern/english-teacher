"""Wrap english-teacher.html in the same skeleton the Artifact publisher adds, for local testing."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
page = (root / "english-teacher.html").read_text(encoding="utf-8")
head = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" '
        'content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
(root / "_preview.html").write_text(head + page + "</body></html>", encoding="utf-8")
print("wrote _preview.html")
