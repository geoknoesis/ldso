# LDSO-Core — Legal Document Structure Ontology: Core Module

> **Disclaimer:** This ontology is not an official W3C, OASIS, or any other
> standards body specification. It is a community and project ontology using
> W3C RDF/OWL and SHACL technologies.

## Overview

LDSO-Core provides a generic, modular RDF/OWL vocabulary for representing the
structural hierarchy, ordering, and identity of legal documents. It is the
foundation layer of the Legal Document Structure Ontology (LDSO) family.

LDSO-Core covers **structure only**:

- Legal resource and expression identity (LegalResource, LegalExpression)
- Document hierarchy (Body, Part, Chapter, Section, Article, Paragraph …)
- List structure (BlockList, Item, Point …)
- Table structure (Table, Row, Cell)
- Annexes and attachments
- Structural references and citations
- Element ordering

Legal semantics (obligations, permissions, definitions), lifecycle (amendments,
versioning), and domain rules (tariff, origin) belong to separate LDSO modules.

## Namespace

```turtle
@prefix ldso: <https://w3id.org/ldso/core#> .
```

Ontology IRI: `https://w3id.org/ldso/core`

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL validation shapes |
| `index.html` | ReSpec specification |
| `examples/example.ttl` | Article 2.5 example in Turtle |
| `examples/example.jsonld` | Article 2.5 example in JSON-LD |

## Scope

LDSO-Core supports any legal instrument where structural representation matters:

- Treaties and trade agreements
- National and supranational laws and regulations
- Contracts and commercial agreements
- Insurance policies
- Technical standards
- Judicial decisions
- Parliamentary documents

## Module Architecture

LDSO is organised in layers. Each layer imports the ones below it.

```
Layer 6 — Evaluation        (rule results, compliance scores)
Layer 5 — Domain            (trade, insurance, contracts — operational rules)
Layer 4 — LDSO-Semantics    (obligations, permissions, definitions)
Layer 3 — LDSO-Lifecycle    (amendments, versions, consolidation)
Layer 2b — LDSO-Entities    (named entity annotation)
Layer 1 — LDSO-Core         ← THIS MODULE
```

Do not mix layers. Never place obligations or trade rules in LDSO-Core.

## Design Principles

1. **Structure is independent from meaning.** `ldso:Article` is a structural
   class. Legal meaning (obligation, permission) is annotated by LDSO-Semantics.

2. **Graph-native identity.** Every element's IRI is its primary identifier.
   `ldso:citation` carries the dot-concatenated citation path (e.g., `2.5.1.a`)
   for querying and display. `ldso:notation` carries the local label as printed
   in the source (e.g., `5`, `a`).

3. **Ordering without RDF Collections.** Legal order is expressed with
   `ldso:next`, `ldso:previous`, and `ldso:orderIndex`. Never use `rdf:List`.

4. **Minimal OWL.** Domains and ranges are advisory. Avoid OWL restrictions that
   would break open-world reasoning for large corpora.

5. **DC Terms for metadata.** Document identity and bibliographic metadata use
   `dct:title` (language-tagged), `dct:language`, `dct:issued`, and
   `dct:format`. No custom metadata properties are defined in Core.

6. **Resource / Expression separation.** `ldso:LegalResource` is the abstract
   legal instrument (language-independent). `ldso:LegalExpression` is a specific
   language-version of it. `ldso:Document` is a concrete structural encoding of
   a LegalExpression.

## Class Hierarchy

```
ldso:LegalResource
├── ldso:LegalExpression
│   └── ldso:Document
└── ldso:LegalElement
    ├── ldso:Preface
    ├── ldso:Preamble
    ├── ldso:Body
    ├── ldso:Conclusions
    ├── ldso:Part
    ├── ldso:Title
    ├── ldso:Chapter
    ├── ldso:Section              (a Section partOf Section = "subsection" position)
    ├── ldso:Article
    ├── ldso:Paragraph        (a Paragraph partOf Paragraph = "subparagraph" position)
    ├── ldso:Clause
    ├── ldso:Point            (a Point partOf Point = "subpoint" position)
    ├── ldso:BlockList
    ├── ldso:Item
    ├── ldso:Annex
    ├── ldso:Schedule
    ├── ldso:Appendix
    ├── ldso:Attachment
    ├── ldso:Table
    ├── ldso:Row
    ├── ldso:Cell
    └── ldso:Reference
        ├── ldso:InternalReference
        ├── ldso:ExternalReference
        └── ldso:Citation
```

## Resource / Expression Pattern

```turtle
# Abstract legal instrument (language-independent)
ex:resource_ata
  a ldso:LegalResource ;
  dct:title "Agreement on Temporary Admission of Goods"@en ;
  ldso:hasExpression ex:doc_ata_en .

# Specific language version
ex:doc_ata_en
  a ldso:Document ;
  dct:title "Agreement on Temporary Admission of Goods"@en ;
  dct:language "en" ;
  dct:issued "2026-01-15"^^xsd:date ;
  dct:format "text/turtle" ;
  ldso:expressionOf ex:resource_ata ;
  ldso:contains ex:body_ata .
```

## Ordering Pattern

Use the doubly-linked list pattern. Never use `rdf:List`.

```turtle
:para_1
  ldso:orderIndex 1 ;
  ldso:next :para_2 .

:para_2
  ldso:orderIndex 2 ;
  ldso:previous :para_1 ;
  ldso:next :para_3 .

:para_3
  ldso:orderIndex 3 ;
  ldso:previous :para_2 .
```

This pattern supports:

- Linear traversal in both directions
- Amendment insertion (insert a node between two siblings)
- SPARQL ordering via `ldso:orderIndex`

## SHACL Validation

### Run with Apache Jena SHACL

```bash
shacl validate \
  --shapes shapes.ttl \
  --data examples/example.ttl
```

### Run with PySHACL

```bash
pyshacl \
  -s shapes.ttl \
  -sf turtle \
  -df turtle \
  examples/example.ttl
```

### Shapes provided

| Shape | Target | Validates |
|-------|--------|-----------|
| `ldso:LegalExpressionShape` | `ldso:LegalExpression` | `dct:language` present; `ldso:expressionOf` present (Warning if absent) |
| `ldso:DocumentShape` | `ldso:Document` | `dct:title` (language-tagged) present |
| `ldso:ArticleShape` | `ldso:Article` | notation present |
| `ldso:ParagraphShape` | `ldso:Paragraph` | orderIndex >= 1 |
| `ldso:BlockListShape` | `ldso:BlockList` | contains >= 1 Item |
| `ldso:ItemShape` | `ldso:Item` | notation and orderIndex present |
| `ldso:TableShape` | `ldso:Table` | hasRow >= 1 |
| `ldso:RowShape` | `ldso:Row` | orderIndex and hasCell >= 1 |
| `ldso:CellShape` | `ldso:Cell` | orderIndex present |
| `ldso:NextRequiresOrderShape` | subjects of `ldso:next` | orderIndex present |
| `ldso:PreviousRequiresOrderShape` | subjects of `ldso:previous` | orderIndex present |
| `ldso:OrderingChainIntegrityShape` | subjects of `ldso:next` | B.previous = A check |
| `ldso:ReferenceShape` | `ldso:Reference` | `ldso:refersTo` present |
| `ldso:InternalReferenceShape` | `ldso:InternalReference` | `ldso:anchorText` (langString) present |
| `ldso:ExternalReferenceShape` | `ldso:ExternalReference` | `ldso:anchorText` (langString) present |
| `ldso:AnnexShape` | `ldso:Annex` | notation and `dct:title` present |
| `ldso:ClauseShape` | `ldso:Clause` | notation present |
| `ldso:NoRdfCollectionsShape` | `ldso:LegalElement` | no rdf:first |
| `ldso:CitationChainShape` | subjects of `ldso:citation` | child citation starts with parent citation + "." |

## JSON-LD Publication

Load the JSON-LD context from `examples/example.jsonld` for publishing
LDSO-Core data as JSON-LD. The context maps compact terms to full IRIs:

```json
{
  "@context": {
    "ldso":         "https://w3id.org/ldso/core#",
    "dct":          "http://purl.org/dc/terms/",
    "xsd":          "http://www.w3.org/2001/XMLSchema#",
    "LegalResource":    "ldso:LegalResource",
    "LegalExpression":  "ldso:LegalExpression",
    "Document":         "ldso:Document",
    "title":        { "@id": "dct:title", "@container": "@language" },
    "language":     { "@id": "dct:language" },
    "issued":       { "@id": "dct:issued", "@type": "xsd:date" },
    "format":       { "@id": "dct:format" },
    "expressionOf": { "@id": "ldso:expressionOf", "@type": "@id" },
    "hasExpression":{ "@id": "ldso:hasExpression", "@type": "@id", "@container": "@set" },
    "notation":     { "@id": "ldso:notation" },
    "citation":     { "@id": "ldso:citation" },
    "orderIndex":   { "@id": "ldso:orderIndex", "@type": "xsd:integer" },
    "contains":     { "@id": "ldso:contains", "@type": "@id", "@container": "@set" },
    "next":         { "@id": "ldso:next", "@type": "@id" },
    "previous":     { "@id": "ldso:previous", "@type": "@id" }
  }
}
```

## SPARQL Queries

### List all language expressions of a legal resource

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX dct:  <http://purl.org/dc/terms/>

SELECT ?expression ?language ?issued WHERE {
  <https://example.org/resource/temporary-admission>
    ldso:hasExpression ?expression .
  ?expression dct:language ?language .
  OPTIONAL { ?expression dct:issued ?issued }
}
ORDER BY ?language
```

### Retrieve Article 2.5 in document order

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>

SELECT ?notation ?text WHERE {
  <https://example.org/doc/temporary-admission/EN/body/chp_2/art_5>
    ldso:contains ?para .
  ?para a ldso:Paragraph ;
        ldso:notation ?notation ;
        ldso:text ?text ;
        ldso:orderIndex ?idx .
}
ORDER BY ?idx
```

### Walk a BlockList in order

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>

SELECT ?notation ?text WHERE {
  ?list a ldso:BlockList ;
        ldso:contains ?item .
  ?item ldso:notation ?notation ;
        ldso:text ?text ;
        ldso:orderIndex ?idx .
}
ORDER BY ?idx
```

### Find all Articles in a document

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX dct:  <http://purl.org/dc/terms/>

SELECT ?article ?notation ?title WHERE {
  ?article a ldso:Article ;
           ldso:notation ?notation .
  OPTIONAL { ?article dct:title ?title }
}
ORDER BY ?notation
```

## Alignment with Existing Standards

| Standard | Relationship |
|----------|-------------|
| FRBR / IFLA LRM | `ldso:LegalResource` ≈ Work; `ldso:LegalExpression` ≈ Expression; `ldso:Document` ≈ Manifestation |
| ELI (European Legislation Identifier) | ELI IRIs can be used as `ldso:LegalResource` or `ldso:LegalExpression` identifiers |
| Dublin Core / DCTerms | `dct:title`, `dct:language`, `dct:issued`, `dct:format` used on Document and LegalExpression |
| SKOS | `skos:definition` and `skos:scopeNote` used throughout the ontology |
| Akoma Ntoso (AKN) | Structural hierarchy inspired by AKN element taxonomy; not an AKN ontology |

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Stephane Fellah — Geoknoesis LLC
