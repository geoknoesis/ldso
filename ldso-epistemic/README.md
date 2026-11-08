# LDSO-Epistemic — Claims, Sources, Trust and Conflict Resolution

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL technologies.
> **Status: draft 0.1.0.**

## Overview

LDSO-Epistemic is the vocabulary for **what sources claim**, as opposed to what is true:
claims (one asserted triple, possibly denied) with a source, a confidence and a time;
corrections (`epi:supersedes`) and retractions; the trust a source carries (a tier, an
admission floor); the policy that settles conflicts between claims (an ordered list of
criteria, optionally per property or class); and the result of an assessment (a status per
claim, the conflicts found, the decisions taken).

It reuses **PROV-O** (a claim is a `prov:Entity`, `epi:claimedBy` is a sub-property of
`prov:wasAttributedTo`) and is designed so that claims, sources and a policy map to the
belief-revision engine of **HydraDL** (`hydradl-epistemic`). The engine decides, against a
trusted OWL 2 DL ontology, which claims to accept, reject or leave contested, and explains
each status.

| Layer | Module | Says |
|---|---|---|
| 2b | LDSO-Entities / LDSO-Annotations (`ent:`, `ann:`) | *what a text mentions*, with the score of the extractor |
| 6 | **LDSO-Epistemic (`epi:`)** | *who claims what*, how far each source is trusted, and *which claims survive* when they conflict |

A claim derived from an `ann:EntityMention` uses `prov:wasDerivedFrom` that mention and
copies its confidence when the mention states one. A mention with no score gives a claim
with no `epi:confidence` (not stated), not 1.0.

## Namespace

```turtle
@prefix epi: <https://w3id.org/ldso/epistemic#> .
```

Ontology IRI: `https://w3id.org/ldso/epistemic` — imports LDSO Core and PROV-O.
Profile namespace (for the HydraDL profile shapes, `hydradl-profile-shapes.ttl`): `epix:` =
`https://w3id.org/ldso/epistemic/hydradl-profile#`.

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `alignments.ttl` | SKOS mappings to LDSO-Annotations, PROV-O and RDF 1.2 triple terms |
| `shapes.ttl` | SHACL shapes for valid LDSO-Epistemic data |
| `hydradl-profile-shapes.ttl` | SHACL shapes (`epix:`) for the executable profile: what `hydradl-epistemic` runs, and the gaps E1–E6 it reports |
| `examples/kyc.ttl`, `examples/kyc.jsonld` | The executable KYC example (see [The KYC example](#the-kyc-example)), in Turtle and JSON-LD |
| `examples/gaps.ttl`, `examples/gaps.jsonld` | Valid LDSO-Epistemic that the engine does not run, one case per gap |
| `competency-questions.md` | Competency questions with SPARQL queries over the examples |
| `index.html` | ReSpec specification, generated from `ontology.ttl`, this file and the competency questions |
| `README.md` | This file |

Outside the module directory, `tests/test_epistemic.py` checks the module (parsing, shapes,
profile, competency questions), and `tools/build_epistemic_spec.py` regenerates
`index.html`.

## Class Hierarchy

```
epi:Claim                      (rdf:Statement · prov:Entity; disjoint with epi:Retraction)
epi:Retraction                 (prov:Entity)
epi:Source                     (prov:Entity)

epi:ResolutionPolicy           (prov:Entity)
epi:ScopedChain
epi:Criterion                  (skos:Concept)
├── epi:ByTier
├── epi:ByConfidence
└── epi:ByRecency

epi:Assessment                 (prov:Entity)  ── epi:status ──> epi:ClaimStatus (skos:Concept)
                                                  ├── epi:Accepted
                                                  ├── epi:Rejected
                                                  ├── epi:Contested
                                                  ├── epi:Undetermined
                                                  └── epi:NotAdmitted
epi:Conflict                   (prov:Entity)
epi:Decision                   (prov:Entity)
```

## Properties

| Property | Domain → Range | Notes |
|---|---|---|
| `epi:negated` | Claim → `xsd:boolean` | the claim denies its triple; absent: false |
| `epi:claimedBy` | Claim or Retraction → Source | sub-property of `prov:wasAttributedTo`; pointing at a claim is nested attribution (gap E1) |
| `epi:confidence` | Claim → `xsd:decimal` [0,1] | absent means not stated; `skos:closeMatch` `ann:confidence` |
| `epi:claimedAt` | Claim or Retraction → `xsd:dateTime` | `skos:closeMatch` `prov:generatedAtTime` |
| `epi:supersedes` | Claim → Claim | correction |
| `epi:retracts` | Retraction → Claim | withdrawal |
| `epi:tier` | Source → `xsd:nonNegativeInteger` | higher is more trusted |
| `epi:admissionFloor` | Source or Policy → `xsd:decimal` [0,1] | |
| `epi:criteria` | Policy or ScopedChain → `rdf:List` of Criterion | ordered |
| `epi:appliesTo` | ScopedChain → property or class IRI | |
| `epi:confidenceMargin` | Policy → `xsd:decimal` [0,1] | |
| `epi:hasScopedChain` | Policy → ScopedChain | |
| `epi:assesses` | Assessment → Claim | |
| `epi:status` | Assessment → ClaimStatus | |
| `epi:reason` | Assessment → `xsd:string` | |
| `epi:involves` | Conflict → Claim | |
| `epi:compares` | Decision → Claim | exactly two per decision: the claims compared, decided or not |
| `epi:winner`, `epi:loser` | Decision → Claim | only when a criterion decided; sub-properties of `epi:compares` |
| `epi:decidedBy` | Decision → Criterion | only when a criterion decided |
| `epi:comparedValues` | Decision → `xsd:string` | |
| `epi:corroborates` | Claim → Claim | gap E2 |
| `epi:validFrom`, `epi:validUntil` | Claim → `xsd:dateTime` | gap E3 |
| `epi:trustedFor` | Source → any | gap E5 |
| `epi:trustLevel` | Source → `skos:Concept` | gap E6 |

### Dates

`epi:claimedAt` (and the gap properties `epi:validFrom` / `epi:validUntil`) take
`xsd:dateTime`, in UTC, for example `"2026-03-04T00:00:00Z"^^xsd:dateTime`. **`hydradl-dl`
supports `xsd:dateTime`, not `xsd:date`**: a claimed date written as `xsd:date` is not read
as an instant. The engine keeps whole seconds since the Unix epoch.

### Confidence and `ann:confidence`

`epi:confidence` is not declared equivalent to `ann:confidence`. LDSO-Annotations reads an
absent score as 1.0 (a human-curated annotation); the epistemic layer reads it as *not
stated*: such a claim is never below an admission floor and never decides a comparison by
confidence. The two are related by `skos:closeMatch` only. RDF 1.2 triple terms are noted
as a `skos:relatedMatch` of `epi:Claim`.

## RDF → Rust mapping

There is **no compiler yet**: the table is the contract for the one a builder will write.
Rust names are those of `crates/hydradl-epistemic/src`; `Query`, `Name` and `Ontology`
come from `hydradl-dl`.

| RDF | Rust |
|---|---|
| `epi:Source` + `epi:tier` / `epi:admissionFloor` | `Source { id, tier: Option<u32>, floor: Option<Confidence> }` |
| `epi:Claim` | `Claim { id, assertion: Query, source, confidence, at, supersedes }` |
| `rdf:subject` / `rdf:predicate` / `rdf:object` of a claim | `Claim::assertion`, a `Query` (rules below) |
| predicate `rdf:type` | `Query::ClassAssertion(individual, class)` |
| predicate `rdf:type` with `epi:negated true` | `Query::ClassAssertion(individual, Class::Not(class))` |
| predicate any other, object an IRI | `Query::ObjectPropertyAssertion(subject, role, object)` |
| predicate any other, object a literal | `Query::DataPropertyAssertion(subject, property, literal)` |
| `epi:negated true` on a property assertion | `Query::NegativeObjectPropertyAssertion` / `Query::NegativeDataPropertyAssertion` |
| predicate `owl:sameAs` (not negated) or `owl:differentFrom` with `epi:negated true` | `Query::SameIndividual(a, b)` |
| predicate `owl:differentFrom` (not negated) or `owl:sameAs` with `epi:negated true` | `Query::DifferentIndividuals(a, b)` |
| `epi:claimedBy` | `Claim::source` / `Retraction::source` (a `Name` naming a `Source`) |
| `epi:confidence` | `Claim::confidence: Option<Confidence>` (millionths in a `u32`, 0..=1_000_000) |
| `epi:claimedAt` | `Claim::at` / `Retraction::at: Option<i64>`, seconds, UTC |
| `epi:supersedes` | `Claim::supersedes: Vec<Name>` |
| `epi:Retraction` + `epi:retracts` | `Retraction { id, source, at, retracts: Vec<Name> }` |
| `epi:ResolutionPolicy` | `Policy { floor, margin, chain, overrides, max_calls, max_repairs }` |
| policy `epi:admissionFloor` | `Policy::floor` |
| `epi:confidenceMargin` | `Policy::margin` (default 0.05) |
| policy `epi:criteria` | `Policy::chain: Vec<Criterion>` (default tier, confidence, recency) |
| `epi:ByTier` / `epi:ByConfidence` / `epi:ByRecency` | `Criterion::Tier` / `Criterion::Confidence` / `Criterion::Recency` |
| `epi:ScopedChain` + `epi:appliesTo` + `epi:criteria` | one entry of `Policy::overrides: Vec<(Scope, Vec<Criterion>)>` |
| `epi:appliesTo` a property IRI | `Scope::Property(name)` |
| `epi:appliesTo` a class IRI | `Scope::Class(name)` |
| `epi:Assessment` | `Assessment { claim, status, reason }` |
| `epi:status` | `ClaimStatus::{Accepted, Rejected, Contested, Undetermined, NotAdmitted}` |
| `epi:reason` | `Reason::{NoConflict, Retracted, BelowFloor, Superseded, Conflicts, Undetermined}`, rendered by `Display` |
| `epi:Conflict` + `epi:involves` | `Conflict { id, claims, decisions }` |
| `epi:Decision` + `epi:compares` / `epi:winner` / `epi:loser` / `epi:decidedBy` / `epi:comparedValues` | `Decision { winner, loser, by: DecidedBy, chain: ChainUsed }`, rendered by `Display`: `epi:compares` is the pair `{winner, loser}`; `epi:winner`, `epi:loser` and `epi:decidedBy` are written only when `by` is not `DecidedBy::Undecided` |

A denied `rdf:type` claim is the assertion of the complement class. It is not looked up
under the class's scoped chain: an `epi:ScopedChain` that `epi:appliesTo` a class applies to
claims asserting that named class, so a claim denying it is compared by the default chain.

A `Belief` collects the sources, claims, retractions and policy over a trusted `Ontology`;
`Belief::validate()` reports the errors below as `EpistemicError`.

## Statuses and reasons

Five statuses, with the wording of the engine's `Display`:

| Status | Meaning | Reason shown |
|---|---|---|
| `epi:Accepted` | in every optimal repair | `no conflict`, or `in conflict N, M` when the claim won every conflict |
| `epi:Rejected` | in no optimal repair | `in conflict N, M` |
| `epi:Contested` | in some optimal repairs, not all | `in conflict N, M` |
| `epi:Undetermined` | the group could not be settled | `undetermined: <message>`, for example `more than 1024 optimal repairs` or `repair search exceeded 65536 repairs` |
| `epi:NotAdmitted` | left out before conflicts were considered | `retracted by R`, `confidence C below floor F` or `superseded by X` |

An assessment reads `c_news: rejected (in conflict 0)`. A decision reads
`c_registry outranks c_news: tier 3 over tier 1` (`tier 1 over no tier` when the loser's
source has no tier),
`... confidence 0.91 over 0.8 (margin 0.05)`, `... claimed at A, after B`, or
`a and b are undecided after tier, confidence, recency`, followed by
` [chain for P]` when a scoped chain was used. A conflict of one claim reads
`conflict N: c contradicts the trusted ontology`.

A stored `epi:Decision` always names its two claims with `epi:compares`. It names an
`epi:winner`, an `epi:loser` and an `epi:decidedBy`, each once, only when a criterion
decided the pair. An undecided pair has none of the three (the engine orders an undecided
pair by id internally, but that order is no preference and is not written), and its
`epi:comparedValues` reads `undecided after tier, confidence, recency`. `shapes.ttl`
enforces this: exactly two `epi:compares`, the three properties all present or all absent,
and the winner and the loser among the compared claims. A query for winners therefore
needs no filter on `epi:decidedBy`, but a query over all compared pairs must use
`epi:compares`, not `epi:winner`.

A claim failing several admission tests reports the first in this order: retracted, below
the floor, superseded. A claim whose replacement was itself retracted or fell below the
floor is not superseded.

## Gaps

Valid LDSO-Epistemic that the engine does not run (reported by the profile shapes,
`hydradl-profile-shapes.ttl`, and illustrated by `examples/gaps.ttl`): **E1** nested attribution (`epi:claimedBy` pointing at a claim), **E2**
`epi:corroborates`, **E3** `epi:validFrom` / `epi:validUntil`, **E4** claims about the
ontology (a claim whose triple is a TBox axiom), **E5** `epi:trustedFor`, **E6**
`epi:trustLevel` or a tier whose type is not an integer (graded trust). One source rating
another has no LDSO-Epistemic term and is outside the vocabulary for now.

## Usage Pattern

```turtle
ex:Ireland owl:differentFrom ex:Malta .   # in the trusted ontology

ex:src_registry a epi:Source ; epi:tier 3 .
ex:src_news     a epi:Source ; epi:tier 1 ; epi:admissionFloor 0.7 .

ex:c_registry a epi:Claim ;
  rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;
  epi:claimedBy ex:src_registry ;
  epi:claimedAt "2026-03-04T00:00:00Z"^^xsd:dateTime .

ex:c_news a epi:Claim ;
  rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Malta ;
  epi:claimedBy ex:src_news ; epi:confidence 0.91 .

ex:policy a epi:ResolutionPolicy ;
  epi:criteria ( epi:ByTier epi:ByConfidence epi:ByRecency ) .
```

With `ex:registeredIn` functional in the trusted ontology, the two claims conflict, the
registry's tier decides, and `ex:c_registry` is accepted while `ex:c_news` is rejected.
The `owl:differentFrom` is needed: OWL makes no unique name assumption, so without it a
functional `ex:registeredIn` only infers that `ex:Ireland` and `ex:Malta` are the same
country, and the two claims do not conflict (`examples/kyc.ttl` states
`ex:UK owl:differentFrom ex:CY` for the same reason).

## The KYC example

`examples/kyc.ttl` is the executable example and the scenario of the Rust test
`crates/hydradl-epistemic/tests/kyc.rs`: five sources (the registry and the sanctions list
at tier 3, the onboarding form at tier 2, two news sources at tier 1) make 13 claims about
the company `ex:acme`, with one retraction and one correction, under a policy with an
admission floor of 0.5, a confidence margin of 0.05, the default chain tier, confidence,
recency, and a scoped chain recency, tier for `ex:registeredAddress`. The engine finds four
conflicts and gives these statuses (the stored result at the end of `kyc.ttl`):

| Claim | Says | Status | Why |
|---|---|---|---|
| `ex:regDoi` | incorporated 2011-03-04 (registry) | accepted | conflict 2: tier 3 over tier 1 |
| `ex:nerDoi` | incorporated 2012-03-04 (news, 0.8) | rejected | conflict 2 |
| `ex:newsUk` | incorporated in the UK (news, 0.91) | contested | conflict 3: same tier, 0.91 against 0.88 is within the margin, no times |
| `ex:newsCy` | incorporated in Cyprus (news, 0.88) | contested | conflict 3 |
| `ex:formAddrOld` | address "1 Old St" (form) | not admitted | superseded by `ex:formAddrNew` |
| `ex:formAddrNew` | address "2 New St" (form, 2025) | accepted | conflict 0: claimed later, by the scoped chain |
| `ex:regAddr` | address "9 Registry Rd" (registry, 2023) | rejected | conflict 0 |
| `ex:regActive` | an active company (registry) | accepted | no conflict |
| `ex:newsDissolved` | a dissolved company (news, 0.7) | not admitted | retracted by `ex:newsBRetract` |
| `ex:nerShell` | a shell company (news, 0.4) | not admitted | confidence 0.4 below floor 0.5 |
| `ex:sancIvan` | Ivan is a sanctioned person (sanctions list) | accepted | conflict 1: tier 3 over both |
| `ex:formCleared` | Acme is cleared (form) | accepted | conflict 1: tier 2 over tier 1 |
| `ex:newsControl` | Acme is controlled by Ivan (news, 0.9) | rejected | conflict 1 |

Conflict 1 has three claims: control by a sanctioned person makes Acme sanctions-exposed,
which is disjoint from cleared. The only optimal repair keeps the two higher-tier claims and
drops the news item.

The stored decisions show both forms: `ex:d_address` and the three decisions of conflict 1
compare two claims and name the winner, the loser and the deciding criterion;
`ex:d_country`, the decision of conflict 3, compares `ex:newsCy` and `ex:newsUk` and names
no winner, loser or criterion (`undecided after tier, confidence, recency`).
