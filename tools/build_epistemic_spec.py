"""Build ldso-epistemic/index.html (ReSpec) from ontology.ttl, README.md and competency-questions.md.

The term reference is generated from the ontology and the narrative from the Markdown, so the
specification cannot drift from either. Needs the `markdown` package (dev only).
Usage: python tools/build_epistemic_spec.py [output-path]
"""
from html import escape
from pathlib import Path
import re
import sys
import markdown
from rdflib import Graph, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'ldso-epistemic'
DEO='https://w3id.org/ldso/epistemic#'
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else MOD/'index.html'
g=Graph().parse(MOD/'ontology.ttl')
PREFIXES={str(iri):p for p,iri in g.namespaces()}

def curie(term):
    s=str(term)
    for iri,p in sorted(PREFIXES.items(),key=lambda x:-len(x[0])):
        if p and s.startswith(iri):return f'{p}:{s[len(iri):]}'
    return s

def local(term):return str(term)[len(DEO):]
def text(term,p):
    v=g.value(term,p)
    return '' if v is None else str(v)
def para(s):return escape(re.sub(r'\s*\n\s*',' ',s.strip()))
def ours(t):return isinstance(t,URIRef) and str(t).startswith(DEO)
def md(s):return markdown.markdown(s,extensions=['tables','fenced_code'])

def shown(term):
    """A domain or range: a class, or the members of an owl:unionOf joined by ' or '."""
    if term is None:return '—'
    members=g.value(term,OWL.unionOf)
    if members is not None:return ' or '.join(curie(m) for m in Collection(g,members))
    return curie(term)

def by_label(terms):return sorted(terms,key=lambda t:local(t).lower())

def class_section(c):
    supers=[curie(s) for s in g.objects(c,RDFS.subClassOf)]
    rows=[('IRI',f'<code>{escape(str(c))}</code>'),('Label',escape(text(c,RDFS.label))),
          ('Subclass of',escape(', '.join(supers)) or '—'),('Definition',para(text(c,SKOS.definition)))]
    if text(c,SKOS.scopeNote):rows.append(('Usage',para(text(c,SKOS.scopeNote))))
    table=''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k,v in rows)
    ex=text(c,SKOS.example).strip()
    pre=f'\n    <pre class="example" title="{escape(local(c))}">{escape(ex)}</pre>' if ex else ''
    return (f'  <section id="{local(c)}">\n    <h3><span class="ont-term">{curie(c)}</span></h3>\n'
            f'    <table class="ont-table">{table}</table>{pre}\n  </section>\n')

def property_table(kind):
    rows=[]
    for p in by_label(t for t in g.subjects(RDF.type,kind) if ours(t)):
        chars=[curie(t) .split(':')[1] for t in g.objects(p,RDF.type) if t!=kind]
        chars+=[f'⊑ {curie(s)}' for s in g.objects(p,RDFS.subPropertyOf)]
        rows.append(f'<tr id="{local(p)}"><td><code>{curie(p)}</code></td>'
                    f'<td>{escape(shown(g.value(p,RDFS.domain)))}</td>'
                    f'<td>{escape(shown(g.value(p,RDFS.range)))}</td>'
                    f'<td>{escape(", ".join(chars)) or "—"}</td>'
                    f'<td>{para(text(p,SKOS.definition))}'
                    + (f'<br/><small>{para(text(p,SKOS.scopeNote))}</small>' if text(p,SKOS.scopeNote) else '')
                    + '</td></tr>')
    return ('<table class="ont-table"><thead><tr><th>Property</th><th>Domain</th><th>Range</th>'
            '<th>Characteristics</th><th>Definition</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>')

def individuals(cls):
    rows=''.join(f'<tr id="{local(i)}"><td><code>{curie(i)}</code></td><td>{escape(text(i,RDFS.label))}</td>'
                 f'<td>{para(text(i,SKOS.definition))}</td></tr>'
                 for i in by_label(g.subjects(RDF.type,URIRef(DEO+cls))))
    return ('<table class="ont-table"><thead><tr><th>Individual</th><th>Label</th><th>Definition</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')

def readme_sections():
    """README `## ` sections as ReSpec sections, minus the ones this page renders itself."""
    readme=(MOD/'README.md').read_text(encoding='utf-8')
    parts=re.split(r'^## ',readme,flags=re.M)[1:]
    skip={'Namespace','Files','Class Hierarchy','Validation'}
    out=[]
    for part in parts:
        title,body=part.split('\n',1)
        title=title.strip()
        if title in skip:continue
        body=body.replace('\n---\n','\n')
        sid=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
        out.append(f'<section id="{sid}">\n<h2>{escape(title)}</h2>\n{md(body)}\n</section>\n')
    return ''.join(out)

def competency_questions():
    cq=(MOD/'competency-questions.md').read_text(encoding='utf-8')
    body=cq.split('\n',1)[1]
    body=re.sub(r'^## ',r'### ',re.sub(r'^### ',r'#### ',body,flags=re.M),flags=re.M)
    return md(body)

classes=by_label(t for t in g.subjects(RDF.type,OWL.Class) if ours(t))
version=text(URIRef('https://w3id.org/ldso/epistemic'),OWL.versionInfo)
date=text(URIRef('https://w3id.org/ldso/epistemic'),URIRef('http://purl.org/dc/terms/modified'))

page=f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>LDSO-Epistemic: Claims, Sources, Trust and Conflict Resolution</title>
  <!-- Generated by tools/build_epistemic_spec.py from ontology.ttl, README.md and competency-questions.md. Do not edit by hand. -->
  <script src="https://www.w3.org/Tools/respec/respec-w3c" class="remove" defer></script>
  <script class="remove">
    var respecConfig = {{
      specStatus: "unofficial",
      shortName: "ldso-epistemic",
      latestVersion: "https://w3id.org/ldso/epistemic",
      edDraftURI:    "https://w3id.org/ldso/epistemic",
      publishDate: "{date}",
      editors: [{{
        name: "Stephane Fellah",
        company: "Geoknoesis LLC",
        url: "https://www.geoknoesis.com"
      }}],
      license: "cc-by",
      doJsonLd: true,
      github: "https://github.com/geoknoesis/ldso",
      lint: {{ "no-headingless-sections": false }},
      localBiblio: {{
        "LDSO-CORE": {{ title: "LDSO-Core: Legal Document Structure Ontology", href: "https://w3id.org/ldso/core", publisher: "Geoknoesis LLC" }},
        "SHACL": {{ title: "Shapes Constraint Language (SHACL)", href: "https://www.w3.org/TR/shacl/", publisher: "W3C" }},
        "SKOS": {{ title: "SKOS Simple Knowledge Organization System Reference", href: "https://www.w3.org/TR/skos-reference/", publisher: "W3C" }}
      }}
    }};
  </script>
  <style>
    .ont-term {{ font-family: monospace; font-weight: bold; }}
    .ont-table {{ width: 100%; border-collapse: collapse; margin: 1em 0; }}
    .ont-table th, .ont-table td {{ border: 1px solid #ccc; padding: 6px 10px; vertical-align: top; }}
    .ont-table th {{ background: #f0f0f0; }}
    pre.example {{ background: #f8f8f8; border-left: 3px solid #aaa; padding: 0.8em 1em; overflow-x: auto; }}
    .note {{ background: #fffbe6; border-left: 3px solid #e6b800; padding: 0.6em 1em; margin: 0.8em 0; }}
    table {{ border-collapse: collapse; }}
    td, th {{ border: 1px solid #ccc; padding: 4px 8px; vertical-align: top; }}
  </style>
</head>
<body>

<h1>LDSO-Epistemic: Claims, Sources, Trust and Conflict Resolution</h1>

<section id="abstract">
  <h2>Abstract</h2>
  <p>
    <strong>LDSO-Epistemic</strong> is an RDF/OWL vocabulary for what sources claim, as opposed to what is
    true: claims (one asserted triple, possibly denied) with a source, a confidence and a time;
    corrections and retractions; the trust a source carries; the resolution policy that settles
    conflicts between claims; and the stored result of an assessment (accepted, rejected, contested,
    undetermined or not admitted), with the decisions that explain it. It compiles to the
    <code>hydradl-epistemic</code> engine and builds on [[LDSO-CORE]].
  </p>
  <p class="note">
    <strong>Status notice:</strong> This document is not an official W3C Standard or W3C
    Recommendation. It is a community/project specification using W3C ReSpec formatting conventions.
  </p>
</section>

<section id="sotd">
  <p class="note">This document is not an official W3C Standard or W3C Recommendation. It is a community/project specification using W3C ReSpec formatting conventions.</p>
  <p>
    This is draft {version}, produced by Geoknoesis LLC.
    Ontology IRI: <code>https://w3id.org/ldso/epistemic</code> — version IRI
    <code>https://w3id.org/ldso/epistemic/{version}</code> — preferred prefix <code>epi:</code>.
    Feedback is welcome via the <a href="https://github.com/geoknoesis/ldso/issues">GitHub issue tracker</a>.
  </p>
</section>

{readme_sections()}
<section id="class-reference">
  <h2>Class Reference</h2>
{''.join(class_section(c) for c in classes)}</section>

<section id="individuals">
  <h2>Named Individuals</h2>
  <section id="criteria">
    <h3>Resolution criteria (<span class="ont-term">epi:Criterion</span>)</h3>
    {individuals('Criterion')}
  </section>
  <section id="claim-statuses">
    <h3>Claim statuses (<span class="ont-term">epi:ClaimStatus</span>)</h3>
    {individuals('ClaimStatus')}
  </section>
</section>

<section id="object-properties">
  <h2>Object Properties</h2>
  {property_table(OWL.ObjectProperty)}
</section>

<section id="datatype-properties">
  <h2>Datatype Properties</h2>
  {property_table(OWL.DatatypeProperty)}
</section>

<section id="shacl-validation">
  <h2>SHACL Validation</h2>
  <p>
    <code>shapes.ttl</code> checks the structural well-formedness of any LDSO-Epistemic data.
    <code>hydradl-profile-shapes.ttl</code> restricts it to what the HydraDL epistemic engine
    executes. Validate data merged with its imported ontologies; see the RDF → Rust mapping section.
  </p>
</section>

<section id="competency-questions">
  <h2>Competency Questions</h2>
{competency_questions()}
</section>

<section id="conformance"></section>

</body>
</html>
'''
OUT.write_text(page,encoding='utf-8',newline='\n')
print(OUT,len(page),'chars;',len(classes),'classes')
