# LDSO — Legal Document Structure Ontology

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://w3id.org/ldso)

A modular RDF/OWL vocabulary stack for representing legal documents in machine-readable form — from raw structural hierarchy through named entity annotation, legal lifecycle management, deontic semantic annotation, and operational rule execution.

**Landing page:** [index.html](index.html)

---

## Overview

LDSO is organized as six independent but composable modules. Each layer builds on those below it. Consume only the layers you need.

| Layer | Module | Prefix | Namespace |
|-------|--------|--------|-----------|
| 1 | [LDSO-Core](ldso-core/) | `ldso:` | `https://w3id.org/ldso/core#` |
| 2b | [LDSO-Entities](ldso-entities/) | `ent:` | `https://w3id.org/ldso/entities#` |
| 2c | [LDSO-Annotations](ldso-annotations/) | `ann:` | `https://w3id.org/ldso/annotations#` |
| 3 | [LDSO-Lifecycle](lifecycle/) | `life:` | `https://w3id.org/ldso/lifecycle#` |
| 4 | [LDSO-Semantics](ldso-semantics/) | `leg:` | `https://w3id.org/ldso/semantics#` |
| 5 | [LDSO-Operations](ldso-operations/) | `ops:` | `https://w3id.org/ldso/operations#` |

### Layer stack

```
Layer 6  — Evaluation          (rule results, compliance scores)
Layer 5b — Domain Verticals    (Trade Agreement Ontology, Environment, Finance, …)
Layer 5  — LDSO-Operations     (operative rules, triggers, criteria, procedures)
Layer 4  — LDSO-Semantics      (obligations, permissions, definitions, conditions)
Layer 3  — LDSO-Lifecycle      (amendments, versions, consolidation)
Layer 2c — LDSO-Annotations    (entity mentions, surface forms, NER output)
Layer 2b — LDSO-Entities       (named entity catalogue)
Layer 1  — LDSO-Core           (document structure, LegalResource/LegalExpression)
```

---

## Module Summaries

### LDSO-Core (Layer 1)
Generic vocabulary for the structural hierarchy of legal documents. Covers `LegalResource`, `LegalExpression`, `Document`, and 20+ element types (Chapter, Article, Paragraph, Item, Annex, Table, …). Includes sibling ordering (`ldso:next`, `ldso:previous`), citation paths, and the FRBR-inspired resource/expression identity model.

### LDSO-Entities (Layer 2b)
Named entity catalogue for legal documents. A single `ent:NamedEntity` OWL class with a SKOS-based type taxonomy (Person, Organization, Location, Concept, Role, Event, Process). Entity type is expressed as SKOS concepts — not OWL subclasses — enabling multi-dimensional classification and open-ended domain extension.

### LDSO-Annotations (Layer 2c)
Document annotation module. Supports coarse annotation (`ann:refersToEntity` — a direct link from element to entity) and fine-grained NER output (`ann:EntityMention` — with surface form, character offsets, and confidence score). Imports LDSO-Core and LDSO-Entities.

### LDSO-Lifecycle (Layer 3)
Legal document lifecycle and amendment ontology. Models lifecycle events (Entry, Suspension, Repeal, Expiry), amendment instructions and their effects, version chains (`life:supersedes`/`life:supersededBy`), temporal applicability intervals (`life:validFrom`/`life:validTo`), and consolidated text provenance via PROV-O.

### LDSO-Semantics (Layer 4)
Legal semantic annotation ontology. Provides first-class RDF nodes for deontic norms — `leg:Obligation`, `leg:Permission`, `leg:Prohibition`, `leg:Right`, `leg:Discretion` — plus `leg:Definition`, `leg:Scope`, `leg:Condition`, `leg:Exception`, and `leg:Exemption`. All annotations link to their source document element via `leg:annotates`.

### LDSO-Operations (Layer 5)
Domain-agnostic operational rule layer. Defines `ops:OperativeRule` binding a trigger, criteria, procedure, schedule, and documentary requirements into a machine-executable rule. Includes five Trigger subtypes, five Criterion subtypes, ordered procedural Steps, three Schedule types, Measurement with Comparators, and DocumentaryRequirement.

---

## Repository Structure

```
ldso/
├── index.html                  ← Landing page (overview of all modules)
├── README.md
│
├── ldso-core/
│   ├── index.html              ← ReSpec specification
│   ├── ontology.ttl            ← OWL ontology (Turtle)
│   └── shapes.ttl              ← SHACL validation shapes
│
├── ldso-entities/
│   ├── index.html
│   ├── ontology.ttl
│   ├── shapes.ttl
│   └── examples/
│       ├── example.ttl
│       └── example.jsonld
│
├── ldso-annotations/
│   ├── index.html
│   ├── ontology.ttl
│   └── shapes.ttl
│
├── lifecycle/
│   ├── index.html
│   ├── ontology.ttl
│   └── shapes.ttl
│
├── ldso-semantics/
│   ├── index.html
│   ├── ontology.ttl
│   └── shapes.ttl
│
└── ldso-operations/
    ├── index.html
    ├── ontology.ttl
    └── shapes.ttl
```

---

## Quick Start

```turtle
@prefix ldso: <https://w3id.org/ldso/core#> .
@prefix ent:  <https://w3id.org/ldso/entities#> .
@prefix ann:  <https://w3id.org/ldso/annotations#> .
@prefix life: <https://w3id.org/ldso/lifecycle#> .
@prefix leg:  <https://w3id.org/ldso/semantics#> .
@prefix ops:  <https://w3id.org/ldso/operations#> .
@prefix dct:  <http://purl.org/dc/terms/> .

# Layer 1 — Document Structure
ex:ata
  a ldso:LegalResource ;
  dct:title "ATA Convention"@en ;
  ldso:hasExpression ex:ata_en .

ex:ata_en
  a ldso:Document ;
  dct:language "en" ;
  dct:issued "1961-12-06"^^xsd:date ;
  ldso:expressionOf ex:ata .

# Layer 2b — Named Entity
ex:wco
  a ent:NamedEntity ;
  ent:entityType ent:Organization ;
  ent:showAs "World Customs Organization"@en ;
  ent:href <https://www.wikidata.org/entity/Q186049> .

# Layer 4 — Legal Semantic Annotation
ex:oblig_1
  a leg:Obligation ;
  leg:annotates ex:ata_art1 ;
  rdfs:label "Obligation to present carnet"@en .

# Layer 5 — Operative Rule
ex:rule_ta
  a ops:OperativeRule ;
  ops:operativizes ex:oblig_1 ;
  ops:hasTrigger ex:trig_carnet .
```

To import the full stack:

```turtle
<https://example.org/my-ontology>
  a owl:Ontology ;
  owl:imports <https://w3id.org/ldso/core>,
              <https://w3id.org/ldso/entities>,
              <https://w3id.org/ldso/annotations>,
              <https://w3id.org/ldso/lifecycle>,
              <https://w3id.org/ldso/semantics>,
              <https://w3id.org/ldso/operations> .
```

---

## Design Principles

1. **Strict layer separation.** Structure, semantics, lifecycle, and operational rules are in separate modules. No module mixes concerns from another layer.
2. **DC Terms for metadata.** All document-level metadata uses Dublin Core Terms (`dct:title`, `dct:language`, `dct:issued`, `dct:format`). No custom LDSO metadata properties.
3. **SKOS for taxonomies.** Entity type classification uses a SKOS `ConceptScheme` — not OWL subclasses — enabling multi-dimensional typing and domain extension.
4. **SHACL for validation.** Every module ships a companion `shapes.ttl` with NodeShapes, property constraints, and SPARQL-based integrity checks.
5. **IRI-first identity.** Every meaningful resource is identified by an IRI. Blank nodes are not used for primary entities.
6. **Modular adoption.** Each layer can be deployed independently. A system using only Layer 1 has no dependency on Layers 2–5.

---

## Versioning

All modules follow [Semantic Versioning](https://semver.org/). The current release is **v1.0.0** (2026-05-25).

Version IRIs follow the pattern `https://w3id.org/ldso/{module}/1.0.0`.

---

## Contributing

Bug reports, feature requests, and pull requests are welcome via the [issue tracker](https://github.com/geoknoesis/ldso/issues).

When contributing ontology terms, every class and property must have:
- `rdfs:label` (language-tagged)
- `skos:definition`
- `skos:scopeNote`
- `skos:example` (Turtle)
- `rdfs:isDefinedBy`

---

## License

Copyright 2026 Stephane Fellah, Geoknoesis LLC.

All files in this repository are published under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

---

## Disclaimer

This is not an official W3C Standard or W3C Recommendation. It is a community/project specification produced by Geoknoesis LLC using W3C ReSpec formatting conventions.
