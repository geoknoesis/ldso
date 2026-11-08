# LDSO-Deontic — Formal Deontic Norm Layer

> **Disclaimer:** This ontology is not an official W3C Standard or W3C Recommendation.
> It is a community/project specification using W3C RDF/OWL and SHACL technologies.
> **Status: draft 0.1.0.**

## Overview

LDSO-Deontic is the vocabulary for **formal, executable norms**: rules with a
strength (strict, defeasible, defeater), formal conditions, deontic conclusions
(obligation, prohibition, permission, right) with bearers, actions, targets and
deadlines, reparation chains, and explicit overrides with their legal basis.
Norms also compute with **values**: predicates declare typed signatures
(quantities and relations over numbers, instants, durations and texts),
conditions compare, assign and aggregate values with exact arithmetic,
rounding and calendar expressions, and an obligation may be over an amount
("pay at least the fee").

It covers the deontic and defeasible constructs of **OASIS LegalRuleML Core 1.0**
and of the **W3C ODRL 2.2** Information Model, and it is designed so that a
normative system expressed in it compiles to the defeasible deontic engine of
**HydraDL** (`hydradl-deontic`).

Where it sits:

| Layer | Module | Says |
|---|---|---|
| 4 | LDSO-Semantics (`leg:`) | *what a provision says*: "Clause 8 states an obligation of the insurer" |
| 5 | LDSO-Operations (`ops:`) | *how it is operated*: triggers, criteria, procedures, schedules |
| 5a | **LDSO-Deontic (`deo:`)** | *how it is formalised*: `O[insurer](paid(claim))` within 30 days of approval, ⊗ late fee; defeated by the flood exclusion |

Two analysts can annotate a clause identically in `leg:` and still formalise it
differently in `deo:` — hence a separate layer. `deo:formalizes` links each rule,
condition or statement back to the annotation it formalises, so a reasoner's
explanation can cite the source provision.

## Namespace

```turtle
@prefix deo: <https://w3id.org/ldso/deontic#> .
```

Ontology IRI: `https://w3id.org/ldso/deontic` — imports LDSO Core, Entities,
Semantics and Operations (it reuses `ops:Deadline`, `ops:Schedule` and the
`ops:Comparator` individuals rather than redefining them).

## Files

| File | Description |
|------|-------------|
| `ontology.ttl` | OWL ontology in Turtle |
| `shapes.ttl` | SHACL shapes: structural well-formedness of any LDSO-Deontic data |
| `hydradl-profile-shapes.ttl` | SHACL shapes: the subset HydraDL executes (gaps G2–G5, G7–G9) |
| `alignments.ttl` | SKOS mappings to LegalRuleML and ODRL |
| `competency-questions.md` | Competency questions with SPARQL, run by `tests/test_deontic.py` |
| `index.html` | ReSpec specification |
| `examples/example.ttl` / `.jsonld` | Household insurance policy — executable (passes both shape sets) |
| `examples/licence.ttl` / `.jsonld` | Dataset licence — ODRL / LegalRuleML constructs outside the HydraDL profile |

## Class Hierarchy

```
deo:NormativeSystem                 (ODRL Policy · LegalRuleML Statements · HydraDL NormSystem)

deo:Rule
├── deo:PrescriptiveRule            (concludes a deontic statement or a reparation chain)
└── deo:ConstitutiveRule            (concludes a fact: counts-as, definitions)
deo:FactualStatement                (an unconditional fact stated by the system)

deo:DeonticStatement
├── deo:Obligation                  (O; ODRL Duty)
├── deo:Prohibition                 (F = O¬)
├── deo:Permission                  (P, strong)
└── deo:Right                       (P of the bearer + correlative duties of others)

deo:ReparationChain ── deo:ChainElement     (⊗; LegalRuleML SuborderList)
deo:Reparation                      (a violation's consequence, remedy or penalty, stated separately)
deo:Override                        (rule ≻ rule, with deo:overrideBasis)
deo:Alternatives                    (competing interpretations)
deo:TemporalCharacteristic          (a rule's legal status changing at a time)

deo:Literal ── deo:Argument         (predicate(arg0, arg1, …), possibly negated)
├── deo:Action                      (what a statement requires, forbids or permits)
└── deo:FactCondition               (also a deo:Condition)
deo:Variable

deo:Condition
├── deo:FactCondition               (a recorded fact)
├── deo:ClassCondition              (OWL class membership, via the DL reasoner)
├── deo:PropertyCondition           (OWL object property, via the DL reasoner)
├── deo:NormCondition               (a statement in force / violated / fulfilled)
├── deo:ComparisonCondition         (ODRL Constraint: compare, is any of, is a)
├── deo:LogicalCondition            (ODRL LogicalConstraint) ── deo:SequencedOperand
├── deo:AssignmentCondition         (?x = expression; HydraDL Let)
└── deo:AggregateCondition          (?x = sum / count / min / max over a pattern)

deo:PredicateSignature ── deo:ArgumentSlot   (argument types, key length, quantity or relation)
deo:Expression ── deo:ExpressionOperand      (an operation over ordered operands)

deo:Collection
├── deo:AssetCollection
└── deo:PartyCollection
deo:SetOperator                     (isA, hasPart, isPartOf, isAllOf, isAnyOf, isNoneOf)
```

SKOS schemes: strengths, obligation types (achievement, maintenance, punctual),
reparation kinds (consequence, remedy, penalty), override bases (lex specialis,
lex posterior, lex superior, explicit clause, conflict strategy), conflict
strategies (ambiguity blocking, permission prevails, prohibition prevails,
invalidate), policy types (set, offer, agreement + assertion, privacy, request,
ticket), norm states (in force, violated, fulfilled), logical operators, legal
statuses and status developments; for values: value types (individual,
number, instant, duration, text), operations (the arithmetic, rounding and
calendar functions of HydraDL `Expr`), rounding modes (half up, half even,
down, up) and aggregate operators (sum, count, min, max).

## Usage Pattern

```turtle
ex:r_pay
  a deo:PrescriptiveRule ;
  deo:strength deo:DefeasibleStrength ;
  deo:hasCondition ex:c_covered , ex:c_insurer_of , ex:c_approved ;
  deo:activatedBy ex:c_approved ;                       # the clock starts at approval
  deo:hasConsequent [
    a deo:ReparationChain ;
    deo:hasChainElement
      [ a deo:ChainElement ; deo:position 1 ; deo:statement ex:obl_pay ] ,      # pay within 30 days
      [ a deo:ChainElement ; deo:position 2 ; deo:statement ex:obl_late_fee ]   # else a late fee
  ] ;
  deo:formalizes ex:Oblig_Clause8 .                     # → leg:annotates → Clause 8

ex:ov_flood
  a deo:Override ;
  deo:overriding ex:r_flood_endorsement ;
  deo:overridden ex:r_flood_exclusion ;
  deo:overrideBasis deo:LexSpecialis ;
  deo:basisProvision ex:endorsement_3 .
```

A computed value: the late fee is 1.5% of the claim amount, to the cent, and the
insurer must pay at least that fee.

```turtle
ex:r_late_fee_amount
  a deo:ConstitutiveRule ;
  deo:strength deo:StrictStrength ;
  deo:hasCondition ex:c_claim_amount ,                  # claimAmount(?claim, ?amount)
                   [ a deo:AssignmentCondition ;         # ?fee = round(0.015 × ?amount, 2, half even)
                     deo:assigns ex:var_fee ;
                     deo:expression [
                       a deo:Expression ; deo:operation deo:Round ;
                       deo:places 2 ; deo:roundingMode deo:HalfEven ;
                       deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue [
                         a deo:Expression ; deo:operation deo:Mul ;
                         deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue 0.015 ] ,
                                        [ a deo:ExpressionOperand ; deo:position 2 ; deo:operandValue ex:var_amount ] ] ] ] ] ;
  deo:concludes ex:lit_late_fee_amount .                # lateFeeAmount(?claim, ?fee)

ex:obl_late_fee
  a deo:Obligation ;
  deo:bearer ex:var_insurer ;
  deo:action ex:act_pay_late_fee ;                      # paidLateFee(?claim, ?fee)
  deo:fulfilmentComparator ops:GreaterThanOrEqual .     # a payment ≥ the fee fulfils it
```

`claimAmount` and `lateFeeAmount` are declared quantities (one value per
claim) and `paidLateFee` a relation (any number of payments), each with a
`deo:PredicateSignature` on the normative system.

Modelling rules the shapes enforce:

- Priority is never implicit: every `deo:Override` records its basis, and
  overrides form no cycle.
- Reparation chains are ordered by `deo:position` (LDSO never uses `rdf:List`);
  only the last element may be a permission.
- A record is open unless the system declares it complete
  (`deo:declaresComplete`): without that, a missing payment record never proves
  a payment was not made.
- Variables are scoped to their rule, and (in the HydraDL profile) every
  variable must be bound by a positive fact, class or property condition, or
  by an assignment or aggregate, whose variable is fresh.
- Signatures are well formed: argument slots indexed 0..n-1, a key no longer
  than the arguments, and exactly one value after the key for a quantity; one
  signature per predicate.
- Expressions have operands at positions 1..n, as many as their operation
  takes; `deo:Round` and only it has `deo:places` and `deo:roundingMode`; an
  expression never contains itself.
- Sets are repeated values, not lists: `deo:IsAnyOf` and `deo:IsNoneOf` take
  one `deo:rightOperand` per member, every other operator exactly one.

---

## Coverage: LegalRuleML Core 1.0

LegalRuleML is XML-first; terms are its element and attribute names. Its
deontic sub-kinds and legal statuses are not elements: documents name them by
`@iri`, and LDSO-Deontic gives them concepts.

| LegalRuleML | LDSO-Deontic |
|---|---|
| `LegalRuleMLDocument`, `Statements`, `hasStatement` | `deo:NormativeSystem`, `deo:hasRule` (+ `deo:hasFactualStatement`, `deo:hasOverride`, `deo:hasReparation`) |
| `PrescriptiveStatement` | `deo:PrescriptiveRule` |
| `ConstitutiveStatement` | `deo:ConstitutiveRule` (shape: no deontic consequent) |
| `FactualStatement` | `deo:FactualStatement` + `deo:asserts` |
| `ruleml:Rule` `if` / `then` | `deo:hasCondition` / `deo:hasConsequent` or `deo:concludes` |
| `ruleml:Neg` | `deo:negated true` |
| `ruleml:Naf` | no per-condition operator: declare the predicate complete (`deo:declaresComplete`), so absence counts as false |
| `ruleml:Var`, `ruleml:Ind`, `ruleml:Atom` | `deo:Variable`, individual IRIs, `deo:Literal` + `deo:Argument` |
| `ruleml:Data` (typed values), `ruleml:Expr` + `ruleml:Fun` (built-in functions) | typed literals; `deo:Expression` with `deo:operation` and ordered `deo:ExpressionOperand` nodes |
| *(none: predicate typing)* | `deo:PredicateSignature`, `deo:declaresSignature` |
| `hasStrength`, `appliesStrength` | `deo:strength` |
| `StrictStrength`, `DefeasibleStrength`, `Defeater` | `deo:StrictStrength`, `deo:DefeasibleStrength`, `deo:DefeaterStrength` |
| `Obligation`, `Prohibition`, `Permission`, `Right` | `deo:Obligation`, `deo:Prohibition`, `deo:Permission`, `deo:Right` |
| recursive deontics (an Obligation containing a Permission) | `deo:deonticContent` |
| `Bearer`, `AuxiliaryParty` | `deo:bearer`, `deo:auxiliaryParty` (+ `deo:beneficiary`) |
| achievement / maintenance / punctual (`@iri`) | `deo:obligationType` → `deo:Achievement`, `deo:Maintenance`, `deo:Punctual` |
| preemptive / non-preemptive, perdurant / non-perdurant (`@iri`) | `deo:preemptive`, `deo:perdurant` (booleans) |
| `SuborderList` (⊗) | `deo:ReparationChain`, `deo:ChainElement`, `deo:position` (its last element may be a permission) |
| `ReparationStatement`, `Reparation` | `deo:hasReparation`, `deo:Reparation` |
| `toPrescriptiveStatement`, `appliesPenalty` | `deo:repairs`, `deo:imposes` |
| `PenaltyStatement`, `Penalty` | `deo:reparationKind deo:Penalty`, `deo:imposes` |
| Violation, Compliance (as premises) | `deo:NormCondition` with `deo:Violated` / `deo:Fulfilled` (both executable) |
| `OverrideStatement`, `Override` `@over` `@under`, `hasQualification` | `deo:hasOverride`, `deo:Override`, `deo:overriding`, `deo:overridden` |
| *(none: priority's justification)* | `deo:overrideBasis`, `deo:basisProvision` |
| `Alternatives`, `hasAlternative`, `fromLegalSources` | `deo:Alternatives`, `deo:alternative`, `deo:legalSource`; `deo:adopted` picks one |
| `TemporalCharacteristic`, `hasTemporalCharacteristic` | `deo:TemporalCharacteristic`, `deo:temporalCharacteristic` |
| `forStatus`, `hasStatusDevelopment`, `atTime` | `deo:forStatus`, `deo:statusDevelopment`, `deo:atTime` |
| InForce, Efficacious, Applicability, Enforceability; Starts, Ends | `deo:StatusInForce`, `deo:StatusEfficacious`, `deo:StatusApplicable`, `deo:StatusEnforceable`; `deo:Starts`, `deo:Ends` |
| `Authority`, `Jurisdiction`, `LegalSource` (+ collections) | `deo:authority`, `deo:jurisdiction`, `deo:legalSource` (repeat the property) |
| `Paraphrase` | `deo:paraphrase` |
| `Comment` | `rdfs:comment` |
| `Agent`, `Figure`, `Role` | `ent:NamedEntity` with `ent:entityType ent:Role` (LDSO-Entities), as bearer / auxiliary party |
| `Reference`, `LegalReference` | LDSO Core legal elements, cited by `deo:legalSource` / `deo:basisProvision` |
| `Context`, `Association`, `appliesAssociation`, `appliesSource`… | not reified: the metadata goes on the rule itself (`deo:legalSource`, `deo:authority`, `deo:jurisdiction`, `deo:temporalCharacteristic`), and `deo:formalizes` links the rule to its annotation |

## Coverage: ODRL 2.2

| ODRL | LDSO-Deontic |
|---|---|
| `Policy`, `uid` | `deo:NormativeSystem` (its IRI is the uid) |
| `Set`, `Offer`, `Agreement` | `deo:policyType` → `deo:Set`, `deo:Offer`, `deo:Agreement` |
| Common Vocabulary `Assertion`, `Privacy`, `Request`, `Ticket` | `deo:Assertion`, `deo:Privacy`, `deo:Request`, `deo:Ticket` (narrower concepts) |
| `permission`, `prohibition`, `obligation` | `deo:hasRule` → a `deo:PrescriptiveRule` concluding a `deo:Permission`, `deo:Prohibition`, `deo:Obligation` |
| `Rule`, `Permission`, `Prohibition`, `Duty` | `deo:Rule` + `deo:Permission`, `deo:Prohibition`, `deo:Obligation` |
| `duty` (on a Permission) | `deo:requiresDuty` (executable: a `Fulfilled` condition on the duty) |
| `consequence` (on a Duty), `remedy` (on a Prohibition), `failure` | `deo:Reparation` with `deo:reparationKind deo:Consequence` / `deo:Remedy`, `deo:imposes` |
| `action`, `Action` | `deo:action` → `deo:Action` (its `deo:predicate` is the ODRL action IRI) |
| `includedIn`, `implies` | `deo:includedIn`, `deo:implies` (between act-type IRIs) |
| `refinement` | `deo:refinement` (on an action or a collection) |
| `target`, `Asset`, `AssetCollection`, `partOf` | `deo:target`, any IRI, `deo:AssetCollection`, `deo:memberOf` |
| `assigner`, `assignee`, `Party`, `PartyCollection` | `deo:assigner`, `deo:assignee`, `ent:NamedEntity`, `deo:PartyCollection` |
| other party functions (`attributedParty`, `consentingParty`, …) | sub-properties of `deo:auxiliaryParty` in an ODRL profile |
| `constraint`, `Constraint` | `deo:hasCondition`, `deo:ComparisonCondition` |
| `leftOperand`, `operator`, `rightOperand`, `rightOperandReference`, `unit`, `dataType`, `status` | `deo:leftOperand`, `deo:operator`, `deo:rightOperand`, `deo:rightOperandReference`, `deo:unit`, `deo:dataType`, `deo:status` |
| `rightOperand` as a list (for `isAnyOf`, `isNoneOf`) | `deo:rightOperand` repeated, one value per member |
| a left operand that carries a value (`count`, `payAmount`, `purpose`, a domain measure) | its predicate's `deo:PredicateSignature`, so the comparison compiles to a typed value fact |
| a duty to pay an amount (`compensate` refined by `payAmount` with `gteq`) | an obligation whose action carries the amount, with `deo:fulfilmentComparator ops:GreaterThanOrEqual` |
| `eq`, `neq`, `lt`, `lteq`, `gt`, `gteq` | `ops:Equal`, `ops:NotEqual`, `ops:LessThan`, `ops:LessThanOrEqual`, `ops:GreaterThan`, `ops:GreaterThanOrEqual` |
| `isA`, `hasPart`, `isPartOf`, `isAllOf`, `isAnyOf`, `isNoneOf` | `deo:IsA`, `deo:HasPart`, `deo:IsPartOf`, `deo:IsAllOf`, `deo:IsAnyOf`, `deo:IsNoneOf` |
| left operands (`dateTime`, `count`, `spatial`, `purpose`, …) | used as-is: `deo:leftOperand odrl:count` |
| `LogicalConstraint`, `and`, `or`, `xone`, `andSequence` | `deo:LogicalCondition`, `deo:And`, `deo:Or`, `deo:Xone`, `deo:AndSequence` |
| `conflict`: `perm`, `prohibit`, `invalid` | `deo:conflictStrategy`: `deo:PermissionPrevails`, `deo:ProhibitionPrevails`, `deo:Invalidate` (+ `deo:AmbiguityBlocking`) |
| `inheritFrom`, `profile` | `deo:inheritsFrom`, `deo:profile` |
| states: satisfied, exercised, fulfilled, infringed, void | evaluation results, not vocabulary — see *Statuses* below |

---

## Compiling to HydraDL

Data that conforms to `shapes.ttl` **and** `hydradl-profile-shapes.ttl`
compiles to a `hydradl_deontic::NormSystem` that passes
`NormSystem::validate()`. The compiler still calls `validate()`, which also
catches violation cycles through `Violated` conditions (beyond SPARQL's reach).

| LDSO-Deontic | `hydradl-deontic` |
|---|---|
| `deo:NormativeSystem` | `NormSystem` |
| `deo:hasRule` (with `deo:inheritsFrom*`) | `NormSystem.rules` (the union) |
| `deo:Override` | `NormSystem.superiority` pair `(overriding, overridden)` |
| `deo:declaresComplete` | `NormSystem.closed` (fact predicates, named classes, roles) |
| `deo:Rule` IRI, `deo:formalizes` → citation | `Rule.id`, `Rule.source` |
| `deo:strength` | `RuleKind::Strict` / `Defeasible` / `Defeater` |
| `deo:hasCondition` | `Rule.body` |
| `deo:activatedBy` | `Rule.activated_by` (index of that condition) |
| `deo:FactCondition` | `Condition::Fact(Literal)` |
| `deo:ClassCondition` | `Condition::Class { class, term, positive }` |
| `deo:PropertyCondition` | `Condition::Role { role, subject, object, positive }` |
| `deo:NormCondition` `deo:InForce` / `deo:Violated` / `deo:Fulfilled` | `Condition::InForce` / `Condition::Violated` / `Condition::Fulfilled` |
| `deo:declaresSignature` → `deo:PredicateSignature` | `NormSystem.signatures`: `Signature { args, key, quantity }` from the slots' `deo:valueType` in `deo:argumentIndex` order, `deo:keyLength` and `deo:isQuantity` |
| `deo:ValueTypeScheme` concepts | `ValueType::Individual` / `Number` / `Instant` / `Duration` / `Text` |
| `deo:utcOffset` | `NormSystem.utc_offset` (seconds; absent: 0) |
| `deo:Expression` + `deo:operation` + operands in `deo:position` order | `Expr::…` (`deo:Mul` → `Expr::Mul`, `deo:Lesser` / `deo:Greater` → `Expr::Min` / `Max`, `deo:Round` → `Expr::Round(e, deo:places, Rounding)`) |
| `deo:operandValue` / `deo:expression` a literal, an individual, a variable | `Expr::Term(Term::Value(…))` (xsd:decimal/integer → `Number`, xsd:dateTime → `Instant`, xsd:duration → `Duration`, xsd:string → `Text`) / `Term::Individual` / `Term::Variable` |
| `deo:AssignmentCondition` | `Condition::Let { var: deo:assigns, expr: deo:expression }` |
| `deo:AggregateCondition` | `Condition::Aggregate { var, op: deo:aggregateOperator (Sum / Count / Min / Max), expr, pattern: deo:pattern }` |
| `deo:ConstitutiveRule` concluding a literal whose value argument is an assigned variable | `Head::Fact` of a computed value (a quantity competes with other values of its key) |
| `deo:ComparisonCondition` with an `ops:Comparator` | `Condition::Fact(leftOperand(key, ?v))` + `Condition::Compare { left: ?v, op, right: rightOperand }` |
| `deo:ComparisonCondition` with `deo:IsAnyOf` / `deo:IsNoneOf` | that fact condition + `Condition::In { expr: ?v, values: every deo:rightOperand, positive: true / false }` |
| `deo:ComparisonCondition` with `deo:IsA` | that fact condition + `Condition::Class { class: rightOperand, term: ?v }` |
| `ops:Equal`, `ops:NotEqual`, `ops:LessThan`, `ops:LessThanOrEqual`, `ops:GreaterThan`, `ops:GreaterThanOrEqual` | `Cmp::Eq`, `Ne`, `Lt`, `Le`, `Gt`, `Ge` |
| `deo:fulfilmentComparator` | `Deontic::fulfilled_when(Cmp)` (absent: `Cmp::Eq`) |
| `deo:PrescriptiveRule` + one statement | `Head::Norm(Deontic)` |
| `deo:PrescriptiveRule` + `deo:ReparationChain` | `Head::Chain(Vec<Deontic>)` in `deo:position` order; the last element may be `permitted` |
| `deo:ConstitutiveRule` | `Head::Fact(Literal)` |
| `deo:FactualStatement` | a strict rule with an empty body and `Head::Fact` |
| `deo:Obligation` / `deo:Prohibition` / `deo:Permission` | `Deontic::obliged` / `forbidden` (= obliged of the negated action) / `permitted` |
| `deo:bearer` | `Deontic.bearer` (a `Term`) |
| `deo:action` (+ `deo:target` as a trailing argument when the action does not name it) | `Deontic.action` |
| `deo:deadline` → `ops:deadlineDuration` | `Deadline::Within(seconds)` |
| `deo:deadline` → `ops:deadlineDate` | `Deadline::At(timestamp)` |
| `deo:Variable` / individual IRI | `Term::Variable` / `Term::Individual` |

Constructs the compiler rewrites (no HydraDL counterpart needed):

| Construct | Compiled as |
|---|---|
| `deo:Right` | the bearer's permission plus each `deo:correlative` statement, all concluded by the same rule body |
| `deo:Reparation` | the imposed statement appended to the chain of every rule concluding the repaired statement (the profile requires it to be that chain's last element; one imposing a permission must be the statement's only reparation, so the permission ends the chain) |
| `deo:requiresDuty` | a rule with the permission's conditions concluding the duty, and `Condition::Fulfilled { duty }` added to the permission's rule |
| the key of a `deo:ComparisonCondition` | the target of the refined statement (whose action or target collection the comparison refines), else the subject of the rule's only positive class condition; with neither, or with positive class conditions on several subjects, the profile reports that the compiler cannot place the key |
| `deo:LogicalCondition` `And` / `Or` / `Xone` | inlined conjunction / one rule per operand / one rule per operand with the others negated (disjunctive normal form, nested operands expanded) |
| `deo:refinement` | added to the conditions of each rule using the refined action or collection |
| `deo:AssetCollection` / `deo:PartyCollection` as target / bearer | a fresh variable with a `deo:memberOf` fact condition |
| `deo:includedIn` | strict constitutive rules: doing the narrower act is doing the broader one |
| `deo:implies` | a defeater against prohibitions of the implied act when the implying act is permitted |
| `deo:conflictStrategy deo:PermissionPrevails` / `ProhibitionPrevails` | overrides (basis `deo:ConflictStrategyBasis`) of each permission rule over each contrary prohibition rule, or the reverse |
| `deo:conflictStrategy deo:Invalidate` | ambiguity blocking; any reported `Conflict` makes the whole system void |
| `deo:policyType deo:Offer` / `deo:Request` | nothing in force (the profile warns) |
| `deo:Alternatives` | the adopted alternative; with none adopted, one `NormSystem` per alternative |

**Time.** HydraDL counts time in `i64` seconds. A duration compiles to its
length in seconds, which is only defined for weeks, days, hours, minutes and
seconds (G8). A date compiles to a timestamp; the proposed convention is the
end of that day at the system's `deo:utcOffset` (UTC when absent) — this is an
open choice for the compiler, recorded here so it is made once. The calendar
operations (`deo:YearsBetween`, `deo:AddMonths`…) count civil dates at the same
offset, so an age or a date "six months after filing" can be computed and
compared, even though a deadline cannot yet be stated in months (G8).

**Values.** Numbers are exact rationals: `0.015 × 1234.56` is exactly
`18.5184`, and only `deo:Round`, `deo:Floor` and `deo:Ceil` round. A missing
value of an open recorded predicate is unknown, and so is whatever is computed
from it (an obligation over it has status `Unknown`, never `NotApplicable`).
Aggregates have set semantics: records that must count separately carry an
identifying argument (`wage(?person, ?month, ?amount)`). See the
`hydradl-deontic` README, "Values".

### Gaps: valid LDSO-Deontic that HydraDL does not yet execute

Each is a Violation of `hydradl-profile-shapes.ttl`; `examples/licence.ttl` has
one instance of each, and the test suite checks that exactly these seven are
reported. The numbering is kept stable: G1 (fulfilled conditions and ODRL duty
preconditions) and G6 (a permission ending a reparation chain) are closed, and
G4 is narrowed from every comparison to the part-of and set operands.

| Gap | Construct | Source | What it needs in the engine |
|---|---|---|---|
| G2 | `deo:temporalCharacteristic` (rule validity windows) | LegalRuleML TemporalCharacteristic | a validity interval per rule, checked against the evaluation time |
| G3 | maintenance and punctual obligations; preemptive and perdurant ones | LegalRuleML deontic `@iri` kinds | status rules per obligation type |
| G4 (part-of and set operands) | `deo:IsPartOf`, `deo:HasPart`, `deo:IsAllOf`; `deo:rightOperandReference`; `deo:status` | ODRL isPartOf, hasPart, isAllOf, rightOperandReference, status | containment between individuals (a spatial or mereological relation), sets as values, right operands looked up at evaluation time, and status values generated from the exercised action |
| G5 | `deo:AndSequence` | ODRL andSequence | order in time between condition facts |
| G7 | recurring and period schedules | LDSO-Operations schedules | one obligation instance per period |
| G8 | calendar durations (months, years) as deadlines | legal text ("within six months") | a deadline computed with calendar arithmetic from the activation date |
| G9 | `deo:deonticContent` (a norm about a norm) | LegalRuleML recursive deontics | nested modalities |

Until G4 is closed, record a part-of comparison's outcome as a fact
(`inEU(?dataset)`) and use a `deo:FactCondition`. Comparisons with stated
values — `=`, `≠`, `<`, `≤`, `>`, `≥`, `deo:IsAnyOf`, `deo:IsNoneOf` and
`deo:IsA` — are executable.

### Statuses

HydraDL reports, for each obligation instance, one of NotApplicable, Active,
Fulfilled, Violated or Unknown (the last when an open record leaves it
undecided). The standards' state terms read off these:

| Standard term | HydraDL result |
|---|---|
| LegalRuleML Violation; ODRL *infringed* (prohibition), duty *not fulfilled* | `Status::Violated` |
| LegalRuleML Compliance; ODRL *fulfilled* | `Status::Fulfilled` |
| ODRL *satisfied* (constraint) | the condition is proved (+∂) |
| ODRL *exercised* (permission) | a fact of the permitted action is recorded |
| ODRL *void* (policy, under `invalid`) | some `Conflict` is reported |
| strong permission / weak permission | +∂ P concluded / no prohibition concluded |

---

## Validation

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -p "test_deontic.py" -v
```

The suite parses every artifact, meta-validates both shape sets, parses every
embedded `skos:example`, checks the JSON-LD examples are isomorphic to the
Turtle ones, runs every competency question, checks the insurance example
passes both shape sets and the licence example reports exactly gaps G2–G5 and
G7–G9 (and no other violation), adds one defect at a time to the insurance
example to check that each shape fires, and adds the constructs of the closed
gaps (a duty precondition, a `Fulfilled` condition, a reparation ending a chain
in a permission, comparisons, set membership, an aggregate) to check that they
pass both shape sets.

Validate data merged with its imports (ontology graphs included in the data
graph) rather than through pyshacl's `ont_graph` option: pyshacl does not show
`ont_graph` triples to shapes nested in `sh:or`.

## Open Questions

1. **Date convention** — which instant `ops:deadlineDate` denotes. The time
   zone is now stated per system (`deo:utcOffset`); proposed: the end of that
   day at that offset.
2. **Strict deontic rules** — HydraDL lets a superior rule beat a strict
   deontic rule (only factual conclusions have a strict tier). LegalRuleML
   leaves this open; documented on `deo:StrictStrength`.
3. **Root README** — the LDSO layer table should gain a row for Layer 5a
   (LDSO-Deontic) once this module is accepted.
