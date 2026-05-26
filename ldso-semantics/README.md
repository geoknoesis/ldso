# LDSO-Semantics — Legal Semantic Annotation Ontology

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL and SHACL technologies.

## Overview

LDSO-Semantics provides a vocabulary for annotating the deontic and definitional
content of legal provisions. It records what provisions **oblige**, **permit**,
**prohibit**, **define**, and **scope** — without encoding structural form (LDSO-Core)
or lifecycle state (LDSO-Lifecycle).

Annotations are first-class nodes that point to LDSO-Core structural elements via
`leg:annotates`, keeping structure and meaning cleanly separated.

## Namespace

```turtle
@prefix leg: <https://w3id.org/ldso/semantics#> .
```

Ontology IRI: `https://w3id.org/ldso/semantics`

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL validation shapes |
| `competency-questions.md` | SPARQL competency questions |
| `examples/example.ttl` | Article 2.5 (ATA Agreement) annotated example |
| `examples/example.jsonld` | JSON-LD context |

## Module Position

```
Layer 5 — Domain            (trade rules, HS triggers, origin rules)
Layer 4 — LDSO-Semantics    ← THIS MODULE (obligations, permissions, definitions)
Layer 3 — LDSO-Lifecycle    (amendments, versions, consolidation)
Layer 2b — LDSO-Entities    (named entity annotation)
Layer 1 — LDSO-Core         (document structure)
```

LDSO-Semantics imports LDSO-Core. It is independent of LDSO-Lifecycle and
LDSO-Entities, though it pairs naturally with both.

## Design Principle

Structure is independent from meaning. `ldso:Article` is a structural class.
`leg:Obligation` annotates that article. The two are linked by `leg:annotates`
in one direction only (annotation → element), never the reverse. This allows:

- The same provision to carry multiple annotations of different types
- Independent SPARQL queries over structure or meaning
- Semantic annotations to be loaded as a separate named graph

## Class Hierarchy

```
leg:LegalAnnotation
├── leg:NormativeStatement
│   ├── leg:Obligation      (SHALL / MUST)
│   ├── leg:Permission      (MAY / IS PERMITTED TO)
│   ├── leg:Prohibition     (SHALL NOT / MUST NOT)
│   ├── leg:Right           (IS ENTITLED TO / HAS THE RIGHT TO)
│   └── leg:Discretion      (MAY AT ITS DISCRETION)
├── leg:Definition          (defined term + definition text)
├── leg:Exception           (carve-out from a norm)
│   └── leg:Exemption       (named-subject exception)
└── leg:Scope               (range of applicability)

leg:Condition               (standalone prerequisite, referenced by norms)
```

## Core Properties

### Object Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `leg:annotates` | `LegalAnnotation` | `ldso:LegalElement` | Source provision being annotated |
| `leg:normativeSubject` | `NormativeStatement` | any | Who bears the duty or right |
| `leg:normativeObject` | `NormativeStatement` | any | Subject matter of the norm |
| `leg:conditionedBy` | `NormativeStatement` | `Condition` | Prerequisite for the norm |
| `leg:conditionOf` | `Condition` | `NormativeStatement` | Inverse of conditionedBy |
| `leg:exceptedBy` | `NormativeStatement` | `Exception` | Exception that qualifies the norm |
| `leg:exceptionOf` | `Exception` | `NormativeStatement` | Inverse of exceptedBy |
| `leg:scopeOf` | `Scope` | `LegalAnnotation` | Norm(s) whose applicability is delimited |
| `leg:hasScopeAnnotation` | `LegalAnnotation` | `Scope` | Inverse of scopeOf |
| `leg:statedIn` | `Condition` / `Exception` | `ldso:LegalElement` | Where the condition/exception is stated |
| `leg:correlatesTo` | `Right` | `Obligation` | Hohfeldian correlate obligation |
| `leg:definesEntity` | `Definition` | `ent:NamedEntity` | Entity represented by the defined term |

### Datatype Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `leg:deonticModal` | `NormativeStatement` | `xsd:string` | Verbatim modal verb ('shall', 'may', etc.) |
| `leg:normativeText` | `NormativeStatement` | `rdf:langString` | Verbatim normative sentence |
| `leg:definedTerm` | `Definition` | `rdf:langString` | The term being defined |
| `leg:definitionText` | `Definition` | `rdf:langString` | The definition text |
| `leg:conditionText` | `Condition` | `rdf:langString` | Natural-language condition |
| `leg:scopeText` | `Scope` | `rdf:langString` | Scope description |
| `leg:exceptionText` | `Exception` | `rdf:langString` | Exception text |

## Usage Pattern

```turtle
# 1. Declare entities (from LDSO-Entities)
ex:contracting_party
  a ent:Role ;
  ent:showAs "Contracting Party"@en .

# 2. Annotate the structural element (from LDSO-Core)
# ex:para_1  a ldso:Paragraph — declared in structural graph

# 3. Declare the condition
ex:Cond_ReExport
  a leg:Condition ;
  leg:conditionText "Goods intended for re-exportation within the specified period."@en ;
  leg:statedIn ex:para_1 .

# 4. Declare the normative statement
ex:Oblig_Para1_Admit
  a leg:Obligation ;
  leg:annotates ex:para_1 ;
  leg:normativeSubject ex:contracting_party ;
  leg:deonticModal "shall" ;
  leg:conditionedBy ex:Cond_ReExport .

# 5. Assert the inverse
ex:Cond_ReExport leg:conditionOf ex:Oblig_Para1_Admit .
```

## SHACL Validation

```bash
pyshacl -s shapes.ttl -sf turtle -df turtle examples/example.ttl
```

| Shape | Target | Validates |
|-------|--------|-----------|
| `leg:LegalAnnotationShape` | `leg:LegalAnnotation` | `leg:annotates` minCount 1 |
| `leg:NormativeStatementShape` | `leg:NormativeStatement` | `leg:deonticModal` present; `leg:normativeSubject` (Warning) |
| `leg:ObligationShape` | `leg:Obligation` | modal matches obligatory pattern (Warning) |
| `leg:PermissionShape` | `leg:Permission` | modal matches permissive pattern (Warning) |
| `leg:ProhibitionShape` | `leg:Prohibition` | modal matches prohibitive pattern (Warning) |
| `leg:DefinitionShape` | `leg:Definition` | `leg:definedTerm` and `leg:definitionText` present |
| `leg:ExceptionShape` | `leg:Exception` | `leg:exceptionOf` present (Warning) |
| `leg:ConditionShape` | `leg:Condition` | `leg:conditionText` present |
| `leg:ScopeShape` | `leg:Scope` | `leg:scopeText` present (Warning) |
| `leg:ExceptionInverseShape` | subjects of `leg:exceptedBy` | B.exceptionOf = A check |
| `leg:ConditionInverseShape` | subjects of `leg:conditionedBy` | B.conditionOf = A check |

## Alignment with External Standards

| Standard | Relationship |
|----------|-------------|
| LegalRuleML | `leg:Obligation` ≈ `lrml:Obligation`; `leg:Permission` ≈ `lrml:Permission`; `leg:Prohibition` ≈ `lrml:Prohibition` |
| ODRL | `leg:Permission` ≈ `odrl:Permission`; `leg:Prohibition` ≈ `odrl:Prohibition`; `leg:Obligation` ≈ `odrl:Duty` |
| LKG / Metalex | `leg:Definition` ≈ metalex:Definition; `leg:Condition` ≈ metalex:Condition |
| Hohfeld | `leg:Right` ↔ `leg:Obligation` via `leg:correlatesTo` follows Hohfeldian correlate structure |

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Stephane Fellah — Geoknoesis LLC
