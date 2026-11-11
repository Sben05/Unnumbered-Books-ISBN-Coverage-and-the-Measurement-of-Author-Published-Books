"""Check bibliography keys, PDF links, typesetting warnings and key results."""
from pathlib import Path
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = (ROOT/'deliverables/UNNUMBERED_BOOKS.tex').read_text()
    pdf = PdfReader(ROOT/'deliverables/UNNUMBERED_BOOKS.pdf')
    keys = {key for group in re.findall(r'\\cite\w*\{([^}]+)\}', source)
            for key in group.split(',')}
    bibliography = set(re.findall(r'\\bibitem\[[^\n]+?\]\{([^}]+)\}', source))
    assert keys == bibliography, ('Citation/bibliography mismatch', keys ^ bibliography)
    destinations = pdf.named_destinations
    internal, citations, broken = [], [], []
    for index, page in enumerate(pdf.pages):
        for ref in page.get('/Annots', []):
            link = ref.get_object()
            target = link.get('/A', {}).get('/D', link.get('/Dest'))
            if link.get('/Subtype') == '/Link' and isinstance(target, str):
                internal.append(target)
                if target not in destinations:
                    broken.append([index+1, target])
                if target.startswith('cite.'):
                    citations.append(target)
    assert not broken, broken
    assert set(citations) == {'cite.'+key for key in keys}
    text = '\n\n'.join(page.extract_text() or '' for page in pdf.pages)
    assert '??' not in text and 'n.d.b,n' not in text
    for expected in ['60.6%', '1.53%', 'BNP, n.d.-b; BNP, n.d.-c']:
        assert expected in text, expected
    log = ROOT/'deliverables/UNNUMBERED_BOOKS.log'
    if log.exists():
        for warning in ['Overfull', 'Missing character', 'undefined citations', 'undefined references']:
            assert warning not in log.read_text(), warning
    report = dict(pages=len(pdf.pages), citation_keys=len(keys),
                  citation_hyperlinks=len(citations), internal_hyperlinks=len(internal),
                  broken_destinations=broken, bnp_citation='BNP, n.d.-b; BNP, n.d.-c',
                  producer_share_example='2014 actual 1.86%; fixed composition 1.53%; 2015 actual 1.29%')
    (ROOT/'results/manuscript_checks.json').write_text(json.dumps(report, indent=2)+'\n')
    (ROOT/'results/compiled_text.txt').write_text(text)
    print(f"PDF checks passed: {len(pdf.pages)} pages, {len(keys)} sources, "
          f"{len(citations)} citation links; no broken internal destinations.")


if __name__ == '__main__':
    main()
