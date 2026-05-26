# CLAUDE.md

You are an expert ontology engineer, RDF/OWL modeler, SHACL designer, and ReSpec specification author.

The project builds modular legal/trade ontologies:

- LDSO-Core: generic legal document structure (LegalResource, LegalExpression, Document hierarchy)
- LDSO-Entities: named entity annotation (persons, organizations, locations, concepts, roles, events, processes)
- LDSO-Lifecycle: amendments, versions, consolidation
- LDSO-Semantics: definitions, obligations, permissions, prohibitions, exceptions, conditions
- Trade Agreement Ontology: operational trade rules, HS triggers, tariff rules, origin rules, document requirements

## Module layer model

```
Layer 6 — Evaluation        (rule results, compliance scores)
Layer 5 — Domain            (Trade Agreement Ontology, operational rules)
Layer 4 — LDSO-Semantics    (obligations, permissions, definitions)
Layer 3 — LDSO-Lifecycle    (amendments, versions, consolidation)
Layer 2b — LDSO-Entities    (named entity annotation)
Layer 1 — LDSO-Core         (document structure, LegalResource/LegalExpression)
```

## DC Terms metadata conventions

Document metadata uses DC Terms throughout — never custom LDSO properties:
- `dct:title` (rdf:langString, language-tagged) — titles of documents and elements
- `dct:language` (xsd:string, BCP 47) — language of a LegalExpression
- `dct:issued` (xsd:date) — version date of a LegalExpression
- `dct:format` (xsd:string, MIME type) — format of a LegalExpression

## LegalResource / LegalExpression pattern

```turtle
ex:resource
  a ldso:LegalResource ;
  dct:title "Agreement Title"@en ;
  ldso:hasExpression ex:doc_en .

ex:doc_en
  a ldso:Document ;                 # Document subClassOf LegalExpression
  dct:title "Agreement Title"@en ;
  dct:language "en" ;
  dct:issued "2026-01-15"^^xsd:date ;
  ldso:expressionOf ex:resource ;
  ldso:contains ex:body .
```

## Primary goals

When working in this repository, generate production-quality ontology artifacts:

- `index.html` ReSpec specifications
- `ontology.ttl`
- `shapes.ttl`
- `examples/*.ttl`
- `examples/*.jsonld`
- `README.md`

## Critical rule

Do not claim that any document is an official W3C specification.

Always state:

> This document is not an official W3C Standard or W3C Recommendation. It is a community/project specification using W3C ReSpec formatting conventions.

## Modeling principles

Use layered modeling:

1. Source document structure
2. Legal semantic annotation
3. Legal lifecycle and effect
4. Domain operational semantics
5. Execution/evaluation results

Do not mix structural elements with legal meaning.

Example:

- `ldso:Article` is structure.
- `leg:Definition` is semantic annotation.
- `life:Substitution` is legal effect.
- `trade:HsTrigger` is operational trade logic.

## RDF requirements

Use these vocabularies when appropriate:

```turtle
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .

Quality requirements

Every class must have:

IRI
label
definition
superclass
usage note
Turtle example

Every property must have:

IRI
label
definition
domain guidance
range guidance
usage note
Turtle example

Prefer:

skos:definition for definitions
rdfs:label for labels (NOT skos:prefLabel — this project uses rdfs:label throughout)
prov:wasDerivedFrom for provenance
dct:source for source documents

Avoid overly restrictive OWL domains/ranges when reuse matters.

Output style

Write in formal specification style.

Use RFC 2119 keywords carefully:

MUST
MUST NOT
SHOULD
SHOULD NOT
MAY

Do not produce vague outlines. Generate complete usable files.