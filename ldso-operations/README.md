# LDSO-Operations — Operational Rule Layer

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL and SHACL technologies.

## Overview

LDSO-Operations provides a domain-agnostic vocabulary for expressing the operational
machinery of legal rules — the triggers, qualifying criteria, procedures, schedules,
measurements, and documentary requirements that transform abstract normative statements
into machine-executable logic.

It bridges LDSO-Semantics (Layer 4, abstract normative statements) and domain-specific
vertical ontologies (Layer 5+). Each `ops:OperativeRule` operationalizes one or more
`leg:NormativeStatement` instances from LDSO-Semantics.

## Namespace

```turtle
@prefix ops: <https://w3id.org/ldso/operations#> .
```

Ontology IRI: `https://w3id.org/ldso/operations`

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL validation shapes |
| `index.html` | ReSpec specification |
| `examples/example.ttl` | ATA Convention temporary admission example in Turtle |
| `examples/example.jsonld` | Same example in JSON-LD |

## Class Hierarchy

```
ops:OperativeRule

ops:Trigger
├── ops:EventTrigger       (fired by a named real-world event)
├── ops:ThresholdTrigger   (fired when a measured value crosses a boundary)
├── ops:StatusTrigger      (fired on an entity's status transition)
├── ops:TemporalTrigger    (fired at a date or after a duration)
└── ops:RequestTrigger     (fired by submission of an application or declaration)

ops:Criterion
├── ops:EligibilityCriterion    (subject must hold a status or qualification)
├── ops:ClassificationCriterion (subject must fall in a specified category)
├── ops:ThresholdCriterion      (a measurement must meet a numeric bound)
├── ops:DocumentaryCriterion    (specified documentary evidence must be present)
└── ops:TemporalCriterion       (rule must be invoked within a time window)

ops:Procedure
ops:Step
ops:Schedule
ops:Measurement
ops:DocumentaryRequirement
```

## Core Properties

| Property | Description |
|----------|-------------|
| `ops:operativizes` | Links an OperativeRule to the NormativeStatement it implements |
| `ops:hasTrigger` | Links a rule to its activation condition |
| `ops:hasCriterion` | Links a rule to a qualifying condition |
| `ops:hasProcedure` | Links a rule to its ordered procedural steps |
| `ops:hasSchedule` | Links a rule to its temporal constraints |
| `ops:hasMeasurement` | Links a ThresholdTrigger/Criterion to its measurement |
| `ops:hasDocumentaryRequirement` | Links a rule or criterion to a documentary requirement |
| `ops:hasStep` | Links a Procedure to an ordered Step |
| `ops:triggerDescription` | Human-readable description of a trigger |
| `ops:periodStart` / `ops:periodEnd` | Start/end dates of a Schedule |

## Usage Pattern

```turtle
# Operative rule binding trigger, criteria, procedure, schedule
ex:Rule_TemporaryAdmission
  a ops:OperativeRule ;
  rdfs:label "Temporary admission rule — ATA carnet"@en ;
  ops:operativizes ex:Oblig_AdmitGoods ;
  ops:hasTrigger ex:Trigger_CarnetPresented ;
  ops:hasCriterion ex:Crit_ValidCarnet, ex:Crit_WithinPeriod ;
  ops:hasProcedure ex:Proc_CarnetAdmission ;
  ops:hasSchedule ex:Sched_6MonthDeadline .

# Trigger
ex:Trigger_CarnetPresented
  a ops:RequestTrigger ;
  ops:triggerDescription "Fires when a holder presents a valid ATA carnet at a customs post."@en .

# Criterion with documentary requirement
ex:Crit_ValidCarnet
  a ops:DocumentaryCriterion ;
  ops:hasDocumentaryRequirement ex:Req_ATACarnet .

# Documentary requirement
ex:Req_ATACarnet
  a ops:DocumentaryRequirement ;
  rdfs:label "ATA carnet"@en .

# Temporal schedule
ex:Sched_6MonthDeadline
  a ops:Schedule ;
  ops:periodEnd "P6M"^^xsd:duration .

# Ordered procedure
ex:Proc_CarnetAdmission
  a ops:Procedure ;
  ops:hasStep ex:Step_InspectGoods, ex:Step_StampCarnet, ex:Step_GrantAdmission .

ex:Step_InspectGoods  a ops:Step ; ops:orderIndex 1 ;
  rdfs:label "Inspect goods against carnet description"@en .
ex:Step_StampCarnet   a ops:Step ; ops:orderIndex 2 ;
  rdfs:label "Stamp and endorse the ATA carnet"@en .
ex:Step_GrantAdmission a ops:Step ; ops:orderIndex 3 ;
  rdfs:label "Record temporary admission in national system"@en .
```

## SPARQL Query — All operative rules for a normative statement

```sparql
PREFIX ops:  <https://w3id.org/ldso/operations#>
PREFIX leg:  <https://w3id.org/ldso/semantics#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?rule ?label WHERE {
  ?rule ops:operativizes ?stmt ;
        rdfs:label ?label .
  ?stmt rdfs:label "Obligation to admit goods temporarily"@en .
}
ORDER BY ?label
```

## SPARQL Query — All documentary requirements across rules

```sparql
PREFIX ops: <https://w3id.org/ldso/operations#>

SELECT DISTINCT ?rule ?doc WHERE {
  { ?rule ops:hasCriterion ?c . ?c ops:hasDocumentaryRequirement ?doc . }
  UNION
  { ?rule ops:hasDocumentaryRequirement ?doc . }
}
ORDER BY ?rule
```

## SHACL Validation

```bash
pyshacl -s shapes.ttl -sf turtle -df turtle examples/example.ttl
```

| Shape | Target | Validates |
|-------|--------|-----------|
| `ops:OperativeRuleShape` | `ops:OperativeRule` | `operativizes` and `hasTrigger` required |
| `ops:TriggerShape` | `ops:Trigger` | `triggerDescription` required |
| `ops:StepShape` | `ops:Step` | `orderIndex` required, ≥ 1 |
| `ops:ScheduleShape` | `ops:Schedule` | `periodEnd` > `periodStart` when both asserted |
| `ops:ThresholdTriggerShape` | `ops:ThresholdTrigger` | `hasMeasurement` required |
| `ops:DocumentaryCriterionShape` | `ops:DocumentaryCriterion` | `hasDocumentaryRequirement` required |

## Module Position

```
Layer 5  — Domain Vertical       (Trade Agreement Ontology, etc.)
Layer 4b — LDSO-Operations  ← THIS MODULE (operational rule machinery)
Layer 4  — LDSO-Semantics        (obligations, permissions, definitions)
Layer 3  — LDSO-Lifecycle        (amendments, versions)
Layer 2  — LDSO-Entities         (named entity catalogue)
Layer 1  — LDSO-Core             (document structure)
```

LDSO-Operations imports LDSO-Semantics (which transitively imports LDSO-Core and LDSO-Entities).

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Stephane Fellah — Geoknoesis LLC
