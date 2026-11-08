# LDSO-Deontic — Competency Questions

Competency questions define what the module must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against the example named on its `Against:` line
(`tests/test_deontic.py` runs every query and requires a non-empty answer).

Questions about what is *in force, violated or fulfilled in a situation* are
not SPARQL questions: they need defeasible reasoning over the facts of a case,
which is the reasoner's job (HydraDL). These questions are about the norms
themselves — what a reasoner is given, and what an explanation cites.

Prefixes used throughout:

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX leg:  <https://w3id.org/ldso/semantics#>
PREFIX ops:  <https://w3id.org/ldso/operations#>
PREFIX deo:  <https://w3id.org/ldso/deontic#>
```

---

## Norms and their parties

### CQ-D-01 — Who must, must not, or may do what, under which rule?

Against: `examples/example.ttl`

```sparql
SELECT ?rule ?kind ?bearer ?act WHERE {
  ?rule deo:hasConsequent ?c .
  { ?c a deo:DeonticStatement . BIND (?c AS ?s) }
  UNION { ?c deo:hasChainElement/deo:statement ?s }
  ?s a ?kind ; deo:bearer ?bearer ; deo:action/deo:predicate ?act .
  FILTER (?kind IN (deo:Obligation, deo:Prohibition, deo:Permission, deo:Right))
}
ORDER BY ?rule
```

---

### CQ-D-02 — Which rights does the system grant, and which duties do they impose on others?

Against: `examples/example.ttl`

```sparql
SELECT ?right ?holder ?duty ?dutyBearer ?dutyAct WHERE {
  ?right a deo:Right ; deo:bearer ?holder ; deo:correlative ?duty .
  ?duty deo:bearer ?dutyBearer ; deo:action/deo:predicate ?dutyAct .
}
```

---

## Priority and exceptions

### CQ-D-03 — Which rule prevails over which, on what legal basis, and which provision says so?

Against: `examples/example.ttl`

```sparql
SELECT ?stronger ?weaker ?basis ?provision WHERE {
  ?ov a deo:Override ; deo:overriding ?stronger ; deo:overridden ?weaker ;
      deo:overrideBasis ?basis .
  OPTIONAL { ?ov deo:basisProvision ?provision }
}
```

---

### CQ-D-04 — Which exceptions only block a norm, without imposing the opposite?

Against: `examples/example.ttl`

```sparql
SELECT ?defeater ?blocked ?rule WHERE {
  ?defeater deo:strength deo:DefeaterStrength ;
            deo:hasConsequent/deo:action/deo:predicate ?act .
  ?rule deo:hasConsequent ?c .
  { ?c deo:action/deo:predicate ?act . BIND (?c AS ?blocked) }
  UNION { ?c deo:hasChainElement/deo:statement ?blocked . ?blocked deo:action/deo:predicate ?act }
  FILTER (?rule != ?defeater)
}
```

---

### CQ-D-05 — Where do rules compete over the deadline of the same duty, and what decides?

Against: `examples/example.ttl`

```sparql
SELECT ?r1 ?d1 ?r2 ?d2 ?prevails ?basis WHERE {
  ?r1 deo:hasConsequent ?c1 . ?r2 deo:hasConsequent ?c2 .
  { ?c1 a deo:Obligation . BIND (?c1 AS ?s1) } UNION { ?c1 deo:hasChainElement/deo:statement ?s1 }
  { ?c2 a deo:Obligation . BIND (?c2 AS ?s2) } UNION { ?c2 deo:hasChainElement/deo:statement ?s2 }
  ?s1 deo:action ?act ; deo:deadline/ops:deadlineDuration ?d1 .
  ?s2 deo:action ?act ; deo:deadline/ops:deadlineDuration ?d2 .
  FILTER (?d1 != ?d2 && STR(?r1) < STR(?r2))
  OPTIONAL {
    ?ov deo:overriding ?prevails ; deo:overridden ?yields ; deo:overrideBasis ?basis .
    FILTER ((?prevails = ?r1 && ?yields = ?r2) || (?prevails = ?r2 && ?yields = ?r1))
  }
}
```

---

## Time and violation

### CQ-D-06 — By when must each obligation be met, and what starts the clock?

Against: `examples/example.ttl`

```sparql
SELECT ?rule ?s ?within ?by ?activation WHERE {
  ?rule deo:hasConsequent ?c .
  { ?c a deo:Obligation . BIND (?c AS ?s) } UNION { ?c deo:hasChainElement/deo:statement ?s }
  ?s deo:deadline ?dl .
  OPTIONAL { ?dl ops:deadlineDuration ?within }
  OPTIONAL { ?dl ops:deadlineDate ?by }
  OPTIONAL { ?rule deo:activatedBy/deo:predicate ?activation }
}
ORDER BY ?rule
```

---

### CQ-D-07 — What does the violation of an obligation lead to?

Against: `examples/example.ttl`

```sparql
SELECT ?violated ?next ?how WHERE {
  {
    ?chain deo:hasChainElement ?e1 , ?e2 .
    ?e1 deo:position ?p ; deo:statement ?violated .
    ?e2 deo:position ?q ; deo:statement ?next .
    FILTER (?q = ?p + 1)
    BIND ("reparation chain" AS ?how)
  } UNION {
    ?rep deo:repairs ?violated ; deo:imposes ?next ; deo:reparationKind ?kind .
    BIND (STR(?kind) AS ?how)
  }
}
```

---

### CQ-D-08 — Which rules depend on another norm being in force or violated?

Against: `examples/example.ttl`

```sparql
SELECT ?rule ?state ?norm WHERE {
  ?rule deo:hasCondition ?c .
  ?c a deo:NormCondition ; deo:normState ?state ; deo:aboutStatement ?norm .
}
```

---

### CQ-D-09 — Which records are complete, so that a missing fact counts as false?

Against: `examples/example.ttl`

```sparql
SELECT ?system ?predicate WHERE {
  ?system deo:declaresComplete ?predicate .
}
```

---

## Provenance

### CQ-D-10 — Which provision does each rule formalise?

Against: `examples/example.ttl`

```sparql
SELECT ?rule ?annotation ?provision ?label WHERE {
  ?rule deo:strength ?strength ; deo:formalizes ?annotation .
  ?annotation leg:annotates ?provision .
  OPTIONAL { ?provision rdfs:label ?label }
}
ORDER BY ?rule
```

---

## ODRL and LegalRuleML constructs

### CQ-D-11 — Which permissions require a duty first, and which constraints narrow their action?

Against: `examples/licence.ttl`

```sparql
SELECT ?permission ?duty ?constraint ?left ?op WHERE {
  ?permission a deo:Permission .
  OPTIONAL { ?permission deo:requiresDuty ?duty }
  OPTIONAL { ?permission deo:action/deo:refinement ?constraint .
             ?constraint deo:leftOperand ?left ; deo:operator ?op }
  FILTER (BOUND(?duty) || BOUND(?constraint))
}
```

---

### CQ-D-12 — Which provisions have competing interpretations, and is one adopted?

Against: `examples/licence.ttl`

```sparql
SELECT ?set ?alternative ?adopted WHERE {
  ?set a deo:Alternatives ; deo:alternative ?alternative .
  OPTIONAL { ?set deo:adopted ?adopted }
}
```

---

### CQ-D-13 — Which systems does a policy inherit rules from, and under which conflict strategy?

Against: `examples/licence.ttl`

```sparql
SELECT ?policy ?type ?strategy ?parent ?inheritedRule WHERE {
  ?policy deo:inheritsFrom ?parent ; deo:policyType ?type .
  OPTIONAL { ?policy deo:conflictStrategy ?strategy }
  ?parent deo:hasRule ?inheritedRule .
}
```

---

### CQ-D-14 — Which obligations are of a kind other than achievement, or survive their violation?

Against: `examples/licence.ttl`

```sparql
SELECT ?s ?type ?perdurant WHERE {
  ?s a deo:Obligation .
  OPTIONAL { ?s deo:obligationType ?type }
  OPTIONAL { ?s deo:perdurant ?perdurant }
  FILTER ((BOUND(?type) && ?type != deo:Achievement) || ?perdurant = true)
}
```

---

## Values

### CQ-D-15 — Which quantities does the system compute, and from what?

Against: `examples/example.ttl`

```sparql
SELECT ?quantity ?rule ?operation ?input ?inputPredicate WHERE {
  ?system deo:declaresSignature ?sig .
  ?sig deo:signaturePredicate ?quantity ; deo:isQuantity true .
  ?rule deo:concludes/deo:predicate ?quantity ;
        deo:hasCondition ?computation .
  { ?computation a deo:AssignmentCondition } UNION { ?computation a deo:AggregateCondition }
  ?computation deo:expression ?e .
  OPTIONAL { ?e deo:operation ?operation }
  ?e (deo:hasOperand/deo:operandValue)* ?input .
  ?input a deo:Variable .
  OPTIONAL {
    { ?rule deo:hasCondition ?c } UNION { ?computation deo:pattern ?c }
    ?c deo:predicate ?inputPredicate ; deo:hasArgument/deo:argumentValue ?input .
  }
}
ORDER BY ?quantity
```
