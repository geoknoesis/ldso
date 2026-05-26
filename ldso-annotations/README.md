# LDSO-Annotations — Document Annotation Module

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL and SHACL technologies.

## Overview

LDSO-Annotations provides a vocabulary for linking named entities to their occurrences
in legal document elements. It operates at two complementary granularities:

- **Coarse** — `ann:refersToEntity` links a document element directly to a canonical
  `ent:NamedEntity`. Used for human-curated annotation or simple entity indexing.
- **Fine** — `ann:EntityMention` represents one specific occurrence of a named entity
  in one document location, carrying the exact surface form, character offsets, and
  an optional NER confidence score. This is the primary output unit of NLP pipelines.

LDSO-Annotations sits above both LDSO-Core (document structure) and LDSO-Entities
(canonical entity catalogue) in the LDSO module stack.

## Namespace

```turtle
@prefix ann: <https://w3id.org/ldso/annotations#> .
```

Ontology IRI: `https://w3id.org/ldso/annotations`

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL validation shapes |
| `examples/example.ttl` | Full two-level annotation example in Turtle |
| `examples/example.jsonld` | Same example in JSON-LD |

## Term Summary

### Class

| Class | Description |
|-------|-------------|
| `ann:EntityMention` | One occurrence of a named entity in a specific document location |

### Object Properties

| Property | Description |
|----------|-------------|
| `ann:refersToEntity` | Coarse link from a document element to a canonical named entity |
| `ann:mentionOf` | Links an EntityMention to its canonical NamedEntity (functional) |
| `ann:inElement` | Links an EntityMention to its containing document element (functional) |
| `ann:hasMention` | Inverse of `ann:inElement` — element to its mentions |

### Datatype Properties

| Property | Range | Description |
|----------|-------|-------------|
| `ann:surfaceForm` | `rdf:langString` | Exact text of the mention as found in the source |
| `ann:startChar` | `xsd:nonNegativeInteger` | Zero-based start offset into the element's text |
| `ann:endChar` | `xsd:nonNegativeInteger` | Exclusive end offset (exclusive upper bound) |
| `ann:confidence` | `xsd:decimal` [0.0, 1.0] | NER model confidence score |

## Usage Patterns

### Coarse annotation (human-curated)

```turtle
ex:art_5
  ann:refersToEntity ex:wco, ex:temporary_admission, ex:customs_territory .
```

### Fine annotation (NLP pipeline output)

```turtle
ex:para_2
  ann:hasMention ex:m_wco_para2, ex:m_authority_para2 .

ex:m_wco_para2
  a ann:EntityMention ;
  ann:mentionOf   ex:wco ;
  ann:inElement   ex:para_2 ;
  ann:surfaceForm "World Customs Organization"@en ;
  ann:startChar   23 ;
  ann:endChar     51 ;
  ann:confidence  0.98 .

ex:m_authority_para2
  a ann:EntityMention ;
  ann:mentionOf   ex:competent_authority ;
  ann:inElement   ex:para_2 ;
  ann:surfaceForm "competent authority"@en ;
  ann:confidence  0.91 .
```

### Both levels together (index + provenance)

```turtle
ex:para_2
  ann:refersToEntity ex:wco ;         # coarse index
  ann:hasMention     ex:m_wco_para2 . # fine provenance
```

## SPARQL Query — Find all paragraphs mentioning an entity

```sparql
PREFIX ann: <https://w3id.org/ldso/annotations#>
PREFIX ent: <https://w3id.org/ldso/entities#>
PREFIX ldso: <https://w3id.org/ldso/core#>

SELECT ?element ?citation ?surfaceForm WHERE {
  ?entity ent:showAs "World Customs Organization"@en .
  ?element ann:hasMention ?mention ;
           ldso:citation ?citation .
  ?mention ann:mentionOf ?entity ;
           ann:surfaceForm ?surfaceForm .
}
ORDER BY ?citation
```

## SPARQL Query — Surface form variants for a canonical entity

```sparql
PREFIX ann: <https://w3id.org/ldso/annotations#>
PREFIX ent: <https://w3id.org/ldso/entities#>

SELECT DISTINCT ?surfaceForm WHERE {
  ?entity ent:showAs "World Customs Organization"@en .
  ?m ann:mentionOf ?entity ;
     ann:surfaceForm ?surfaceForm .
}
ORDER BY ?surfaceForm
```

## SHACL Validation

```bash
pyshacl -s shapes.ttl -sf turtle -df turtle examples/example.ttl
```

| Shape | Target | Validates |
|-------|--------|-----------|
| `ann:EntityMentionShape` | `ann:EntityMention` | `mentionOf`, `inElement`, `surfaceForm` required; datatype and range checks |
| `ann:EntityMentionOffsetShape` | `ann:EntityMention` | `startChar` and `endChar` co-presence; `endChar > startChar` |
| `ann:RefersToEntityShape` | Objects of `ann:refersToEntity` | SHOULD be typed as `ent:NamedEntity` |
| `ann:MentionCoarseConsistencyShape` | Elements with `ann:hasMention` | SHOULD carry `ann:refersToEntity` for the same entity |

## Module Position

```
Layer 2c — LDSO-Annotations  ← THIS MODULE (entity mentions, NLP output)
Layer 2b — LDSO-Entities         (canonical entity catalogue)
Layer 1  — LDSO-Core             (document structure)
```

LDSO-Annotations imports both LDSO-Core and LDSO-Entities.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Stephane Fellah — Geoknoesis LLC
