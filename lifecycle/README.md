# LDSO-Lifecycle: Legal Document Lifecycle and Amendment Ontology

**Namespace:** `https://w3id.org/ldso/lifecycle#`
**Prefix:** `life:`
**Version:** 1.0.0
**Status:** Community Specification

> **Disclaimer:** This ontology is not an official W3C or OASIS specification.
> It is a community/project specification produced for legal knowledge graph
> engineering purposes, using W3C ReSpec formatting conventions.

---

## Overview

LDSO-Lifecycle is an RDF/OWL ontology module that models how legal documents
evolve over time. It is part of the **Legal Document Structure Ontology (LDSO)**
family and extends **LDSO-Core** — the generic legal document structure layer.

It is intentionally scoped to lifecycle concerns only. Legal obligations,
permissions, and operational trade rules belong in LDSO-Semantics and domain
ontologies respectively.

---

## Files

| File | Description |
|---|---|
| `ontology.ttl` | OWL ontology — all classes, properties, and SKOS vocabularies |
| `shapes.ttl` | SHACL validation shapes |
| `examples/example.ttl` | Turtle examples (USMCA amendment, insurance endorsement, treaty repeal) |
| `examples/example.jsonld` | JSON-LD examples with full context |
| `index.html` | ReSpec specification |

---

## Lifecycle Model

LDSO-Lifecycle organises lifecycle concepts into four strata:

```
1. Lifecycle Events        — things that happen to documents and provisions
2. Modification Layer      — amendment instructions and their legal effects
3. Versioning Layer        — immutable provision versions and their chains
4. State Layer             — named legal states and transitions between them
```

### Lifecycle Events

Every significant occurrence affecting a legal instrument is a
`life:LifecycleEvent` with a dated `life:eventDate`. Subclasses cover the
full event vocabulary:

| Class | Meaning |
|---|---|
| `life:Commencement` | Document formally comes into existence |
| `life:EntryIntoForce` | Document becomes legally operative |
| `life:Suspension` | Legal effectiveness temporarily halted |
| `life:Expiration` | Automatic end by sunset clause |
| `life:Termination` | Deliberate act ending effectiveness |

---

## Amendment Model

### The Instruction / Effect Distinction

LDSO-Lifecycle rigorously separates two things that are often conflated:

**Amendment Instruction** (`life:AmendmentInstruction`)
: The textual directive in an amending instrument. Example: *"Article 2.5,
  paragraph 3 is hereby replaced by the following…"*

**Legal Effect** (`life:LegalEffect`)
: The resulting change in legal state. Example: a `life:Substitution` that
  closes version 1 and opens version 2 of the provision.

```turtle
# The instruction — what the amending document says
:Instr_2028_Art2_5_Para3
    a life:AmendmentInstruction ;
    life:modifies :USMCA_Art2_5_Para3_v1 ;
    life:modificationDate "2028-01-15"^^xsd:date .

# The effect — what legally results
:Sub_2028_Art2_5_Para3
    a life:Substitution ;
    life:derivedFromInstruction :Instr_2028_Art2_5_Para3 ;
    life:replaces :USMCA_Art2_5_Para3_v1 ;
    life:createsVersion :USMCA_Art2_5_Para3_v2 ;
    life:eventDate "2028-03-01"^^xsd:date .
```

### Effect Types

| Class | Meaning |
|---|---|
| `life:Insertion` | New content added to existing instrument |
| `life:Deletion` | Existing content removed |
| `life:Substitution` | Existing content replaced by new content |
| `life:Repeal` | Entire instrument or major unit abrogated |
| `life:Renumbering` | Structural renumbering without content change |
| `life:Consolidation` | Editorial integration of amendments into unified text |

---

## Versioning Strategy

### Immutability Principle

Old provision versions are **never deleted or overwritten**. Every amendment
creates a new `life:VersionedProvision` instance. Historical state is always
recoverable for any point in time.

### Version Chain

Versions form a doubly-linked chain:

```turtle
:Art2_5_Para3_v1
    life:effectiveFrom  "2020-07-01"^^xsd:date ;
    life:effectiveTo    "2028-02-28"^^xsd:date ;
    life:versionNumber  "1" ;
    life:nextVersion    :Art2_5_Para3_v2 .

:Art2_5_Para3_v2
    life:effectiveFrom  "2028-03-01"^^xsd:date ;
    life:versionNumber  "2" ;
    life:supersedes     :Art2_5_Para3_v1 ;
    life:previousVersion :Art2_5_Para3_v1 .
```

### Stable Identity

The article (`ex:USMCA_Art2_5`) has a stable IRI across all versions.
Individual versioned provisions carry the temporal metadata. This design
supports point-in-time queries without SPARQL temporal extensions:

```sparql
SELECT ?provision ?text
WHERE {
    ?provision a life:VersionedProvision ;
               dct:isPartOf ex:USMCA_Art2_5 ;
               life:effectiveFrom ?from .
    OPTIONAL { ?provision life:effectiveTo ?to }
    FILTER (?from <= "2025-01-01"^^xsd:date)
    FILTER (!BOUND(?to) || ?to >= "2025-01-01"^^xsd:date)
}
```

---

## Temporal Reasoning

### Validity vs Applicability

`life:ValidityInterval` — when a provision *exists* in law.

`life:TemporalApplicability` — when a provision *applies* to transactions or
situations. Distinguishes retroactive, transitional, and prospective effect.

### Open-Ended Validity

Absent `life:effectiveTo` means indefinitely valid. Queries should treat no
`effectiveTo` as validity extending to the present and beyond.

### Temporal Overlap Detection

The SHACL shapes enforce that `effectiveTo >= effectiveFrom`. Application code
should additionally check for unintended overlaps: two versions of the same
provision with overlapping validity intervals indicate a data integrity issue.

### Future Amendments

Pending modifications (`life:PendingModification`) may be modeled before their
effective date. They transition to `life:EffectiveModification` when their
`effectiveFrom` is reached, traceable via `life:LegalStateTransition`.

---

## Consolidation

A `life:Consolidation` event integrates all amendments into a unified text as
of a given date. It produces `life:ConsolidatedProvision` instances that
replace the reading of multiple version instances for most use cases.

```turtle
:Consolidated_USMCA_2028
    a life:Consolidation ;
    life:consolidates :USMCA_Original ;
    life:consolidates :USMCA_AmendmentProtocol_2028 ;
    life:consolidationDate "2028-03-01"^^xsd:date .

:Consolidated_Art2_5_Para3
    a life:ConsolidatedProvision ;
    life:derivedFromConsolidation :Consolidated_USMCA_2028 ;
    life:derivedFromProvision :Art2_5_Para3_v1 ;
    life:derivedFromProvision :Art2_5_Para3_v2 .
```

Consolidations are editorial: they do not amend the law; they reflect it.

---

## Legal States

The `life:LegalStateScheme` SKOS concept scheme provides a controlled vocabulary
of named states. Use `life:stateLabel` for a human-readable string and
`life:LegalStateTransition` with `life:transitionsFrom` / `life:transitionsTo`
for machine-processable state transitions.

| State | Meaning |
|---|---|
| `life:StatePending` | Enacted but not yet operative |
| `life:StateEffective` | Currently operative |
| `life:StateSuspended` | Temporarily not operative |
| `life:StateExpired` | Naturally reached end of validity |
| `life:StateRepealed` | Formally abrogated |
| `life:StateDeprecated` | Superseded, retained for history |
| `life:StateConsolidated` | Present in consolidated text |

---

## Relationship to LDSO-Core and LDSO-Entities

**LDSO-Core** provides document structure: `ldso:LegalResource`,
`ldso:LegalExpression`, `ldso:Document`, `ldso:Article`, `ldso:Paragraph`, etc.
LDSO-Lifecycle uses these as the *targets* of amendment instructions and as
containers for versioned provisions.

**LDSO-Entities** provides named entity annotation. Entities referenced in
lifecycle events (signatories, depositary bodies) may be linked via
`ent:refersToEntity` at any structural level.

**LDSO-Semantics** (separate module) handles obligations, permissions,
prohibitions, and exceptions expressed within provisions. LDSO-Lifecycle does
not model legal meaning — only temporal and amendment structure.

---

## SHACL Validation

`shapes.ttl` validates:

- Every `VersionedProvision` has `effectiveFrom` and `versionNumber`
- `effectiveTo >= effectiveFrom` when both are present
- Every `AmendmentInstruction` has a target (`modifies`) and a `modificationDate`
- Every `Substitution` has `replaces` and `createsVersion`
- Every `Consolidation` integrates ≥ 2 instruments and has `consolidationDate`
- Every `ConsolidatedProvision` references its source consolidation and provisions
- Every `LegalStateTransition` has `transitionsFrom`, `transitionsTo`, `eventDate`
- No provision supersedes itself (cyclic supersession guard)
- Version lineage integrity (nextVersion / supersedes consistency)
- Every `DeprecatedProvision` has an `effectiveTo`

---

## Getting Started

### Load the ontology

```turtle
@prefix life: <https://w3id.org/ldso/lifecycle#> .

# Import in your ontology
<https://your-ontology>
    owl:imports <https://w3id.org/ldso/lifecycle> .
```

### Model an amendment

```turtle
# 1. Original provision (already exists)
:Art3_Para2_v1
    a life:VersionedProvision ;
    life:effectiveFrom "2020-01-01"^^xsd:date ;
    life:versionNumber "1" .

# 2. Amendment instruction (in the amending instrument)
:Instr_Amendment_2026
    a life:AmendmentInstruction ;
    life:modifies :Art3_Para2_v1 ;
    life:modificationDate "2026-06-01"^^xsd:date .

# 3. Legal effect
:Sub_2026_Art3_Para2
    a life:Substitution ;
    life:derivedFromInstruction :Instr_Amendment_2026 ;
    life:replaces :Art3_Para2_v1 ;
    life:createsVersion :Art3_Para2_v2 ;
    life:eventDate "2026-09-01"^^xsd:date .

# 4. New version
:Art3_Para2_v2
    a life:VersionedProvision ;
    life:effectiveFrom "2026-09-01"^^xsd:date ;
    life:versionNumber "2" ;
    life:supersedes :Art3_Para2_v1 .

# 5. Close old version
:Art3_Para2_v1 life:effectiveTo "2026-08-31"^^xsd:date .
```

---

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
