# LDSO-Entities — Named Entity Reference Module

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL and SHACL technologies.

## Overview

LDSO-Entities (v1.2.0) provides a lightweight vocabulary for classifying and linking
named real-world entities referenced within legal documents — persons, organizations,
locations, concepts, roles, events, and processes.

Entity types are expressed as **SKOS concepts** in `ent:EntityTypeScheme`, not as OWL
subclasses. This keeps the class model flat while enabling open-ended, multi-dimensional
classification: domain verticals add `skos:narrower` concepts without touching this ontology.

Document-level annotation (entity mentions, surface forms, character offsets, NER confidence)
is handled by the **LDSO-Annotations module** (`https://w3id.org/ldso/annotations`).

## Namespace

```turtle
@prefix ent: <https://w3id.org/ldso/entities#> .
```

Ontology IRI: `https://w3id.org/ldso/entities`
Version: 1.2.0

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL validation shapes |
| `competency-questions.md` | SPARQL competency questions |
| `examples/example.ttl` | Article 2.5 example in Turtle |

## Class

```
ent:NamedEntity   (single OWL class — entity type via ent:entityType)
```

## Entity Type Vocabulary (SKOS)

`ent:EntityTypeScheme` defines seven top-level classification concepts:

| Concept | Definition |
|---------|-----------|
| `ent:Person` | Named natural person (signatories, authors, individual parties) |
| `ent:Organization` | Governmental body, intergovernmental organization, collective |
| `ent:Location` | Named geographic or jurisdictional location (country, territory) |
| `ent:Concept` | Legal concept or term of art (originating goods, temporary admission) |
| `ent:Role` | Legal or institutional role (customs officer, contracting party) |
| `ent:Event` | Named legal or historical event |
| `ent:Process` | Named legal or administrative process |

Domain verticals extend classification by adding `skos:narrower` concepts
(e.g., `trade:CustomsAdministration skos:broader ent:Organization`) without subclassing.

## Core Properties

| Property | Range | Description |
|----------|-------|-------------|
| `ent:entityType` | `skos:Concept` | Primary and secondary classification via SKOS concepts from `ent:EntityTypeScheme` |
| `ent:showAs` | `rdf:langString` | Human-readable surface form in the source text (language-tagged) |
| `ent:href` | `xsd:anyURI` | Canonical URI identifying the entity |

> **Note:** `ann:refersToEntity` (linking document elements to entities) is defined in
> the LDSO-Annotations module, not here.

## Usage Pattern

```turtle
# Declare named entities — always use ent:entityType, never OWL subclasses
ex:wco
  a ent:NamedEntity ;
  ent:entityType ent:Organization ;           # primary classification
  ent:href "https://www.wcoomd.org"^^xsd:anyURI ;
  ent:showAs "World Customs Organization"@en,
             "Organisation mondiale des douanes"@fr ;
  rdfs:label "World Customs Organization"@en .

ex:temporary_admission
  a ent:NamedEntity ;
  ent:entityType ent:Concept ;
  ent:href "https://example.org/legal/concepts/temporary-admission"^^xsd:anyURI ;
  ent:showAs "temporary admission"@en,
             "admission temporaire"@fr ;
  rdfs:label "temporary admission"@en .

# Multi-dimensional classification (primary + domain-specific)
ex:customs_administration
  a ent:NamedEntity ;
  ent:entityType ent:Organization ;           # primary: from core scheme
  ent:entityType trade:CustomsAdministration ; # secondary: from trade scheme
  ent:href "https://example.org/orgs/customs-admin"^^xsd:anyURI ;
  ent:showAs "national customs administration"@en .
```

## Annotating Document Elements

Entity-to-document linking is in LDSO-Annotations:

```turtle
# Coarse annotation (element refers to entity)
ex:art_5
  ann:refersToEntity ex:temporary_admission, ex:wco .

# Fine-grained annotation (entity mention with NER metadata)
ex:mention_1
  a ann:EntityMention ;
  ann:inElement ex:para_2 ;
  ann:refersToEntity ex:wco ;
  ann:surfaceForm "World Customs Organization"@en ;
  ann:charStart 42 ;
  ann:charEnd 68 ;
  ann:nerConfidence "0.98"^^xsd:decimal .
```

## SPARQL Query — Find all elements referencing a concept

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX ent:  <https://w3id.org/ldso/entities#>
PREFIX ann:  <https://w3id.org/ldso/annotations#>

SELECT ?element ?citation WHERE {
  ?concept ent:entityType ent:Concept ;
           ent:showAs ?label .
  FILTER(STR(?label) = "temporary admission")
  ?element ann:refersToEntity ?concept ;
           ldso:citation ?citation .
}
ORDER BY ?citation
```

## SPARQL Query — All entity types in a chapter

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX ent:  <https://w3id.org/ldso/entities#>
PREFIX ann:  <https://w3id.org/ldso/annotations#>

SELECT DISTINCT ?entity ?type ?showAs WHERE {
  ?chapter ldso:citation "2" ;
           ldso:contains+ ?element .
  ?element ann:refersToEntity ?entity .
  ?entity ent:entityType ?type ;
          ent:showAs ?showAs .
  ?type skos:inScheme ent:EntityTypeScheme .
}
ORDER BY ?type ?showAs
```

## SHACL Validation

```bash
pyshacl -s shapes.ttl -sf turtle -df turtle examples/example.ttl
```

| Shape | Target | Validates |
|-------|--------|-----------|
| `ent:NamedEntityShape` | `ent:NamedEntity` | `ent:href` (anyURI), `ent:showAs` (langString), `ent:entityType` required |
| `ent:EntityTypePrimaryCategoryShape` | `ent:NamedEntity` via SPARQL | At least one `ent:entityType` concept from `ent:EntityTypeScheme` present |
| `ent:EntityTypeSinglePrimaryShape` | `ent:NamedEntity` via SPARQL | At most one primary category concept from the core scheme |
| `ent:ConceptShowAsShape` | Entities with `ent:entityType ent:Concept` | `ent:showAs` required on named Concepts |
| `ent:EntityTypeSchemeShape` | `ent:EntityTypeScheme` (targetNode) | Seven `skos:hasTopConcept` assertions present |
| `ent:EntityTypeConceptShape` | Concepts in scheme via SPARQL | `skos:inScheme` and `rdfs:label` required |

## Module Position

```
Layer 4 — LDSO-Semantics    (obligations, definitions)
Layer 3 — LDSO-Lifecycle    (amendments, versions)
Layer 2c — LDSO-Annotations (entity mentions, span offsets, NER metadata)
Layer 2b — LDSO-Entities    ← THIS MODULE (named entity catalogue)
Layer 1 — LDSO-Core         (document structure)
```

LDSO-Entities imports LDSO-Core. LDSO-Annotations imports LDSO-Entities.

## Alignment with External Vocabularies

| Vocabulary | Relationship |
|------------|-------------|
| Schema.org | `ent:Person` ≈ `schema:Person`; `ent:Organization` ≈ `schema:Organization`; `ent:Location` ≈ `schema:Place` |
| SKOS | `ent:EntityTypeScheme` is a SKOS ConceptScheme; `ent:showAs` corresponds to `skos:altLabel` for display forms |
| Wikidata | `ent:href` may point to Wikidata entity URIs |
| GeoNames | `ent:href` may point to GeoNames URIs for `ent:Location` instances |

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Stephane Fellah — Geoknoesis LLC
