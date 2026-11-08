# LDSO-Epistemic — Competency Questions

Competency questions define what the module must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against the example named on its `Against:` line
(`tests/test_epistemic.py` runs every query and requires a non-empty answer).

Questions about *which claims win* are not answered by SPARQL: they need the
belief-revision engine (HydraDL, `hydradl-epistemic`), which decides against the
trusted ontology. CQ-E-5 to CQ-E-7 read the **stored** result (Layer 6) that the
engine produced; CQ-E-1 to CQ-E-4 read the inputs. A stored decision names a winner and a
loser only when a criterion decided it (it then has an `epi:decidedBy`); every decision,
decided or not, names its two claims with `epi:compares`.

This document is not an official W3C Standard or W3C Recommendation. It is a
community/project specification using W3C ReSpec formatting conventions.

Prefixes used throughout:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX epi: <https://w3id.org/ldso/epistemic#>
PREFIX ex:  <https://example.org/kyc/>
```

---

## Claims and sources

### CQ-E-1 — Which claims did a given source make?

Against: `examples/kyc.ttl`

```sparql
SELECT ?claim ?subject ?predicate ?object WHERE {
  ?claim a epi:Claim ;
         epi:claimedBy ex:newsA ;
         rdf:subject ?subject ;
         rdf:predicate ?predicate ;
         rdf:object ?object .
}
ORDER BY ?claim
```

Expected on `kyc.ttl`: four claims of `ex:newsA`: `ex:nerDoi`, `ex:nerShell`,
`ex:newsControl` and `ex:newsUk`.

---

### CQ-E-2 — Which claims correct another claim, and what do they correct?

Against: `examples/kyc.ttl`

```sparql
SELECT ?correction ?corrected WHERE {
  ?correction epi:supersedes ?corrected .
}
ORDER BY ?correction
```

Expected on `kyc.ttl`: one row, `ex:formAddrNew` corrects `ex:formAddrOld`.

---

## Resolution policy

### CQ-E-3 — Which chain of criteria settles conflicts about `registeredAddress`, in order?

Against: `examples/kyc.ttl`

```sparql
SELECT ?position ?criterion WHERE {
  {
    SELECT ?criterion (COUNT(?before) AS ?position) WHERE {
      ?policy epi:hasScopedChain ?chain .
      ?chain epi:appliesTo ex:registeredAddress ;
             epi:criteria ?list .
      ?list rdf:rest* ?before .
      ?before rdf:rest* ?cell .
      ?cell rdf:first ?criterion .
    }
    GROUP BY ?criterion
  }
}
ORDER BY ?position
```

Expected on `kyc.ttl`: position 1 `epi:ByRecency`, position 2 `epi:ByTier`.
A conflict about any other property uses the policy's default chain: `epi:ByTier`,
`epi:ByConfidence`, `epi:ByRecency`.

---

### CQ-E-4 — Which claims are below the admission floor, computed from their confidence?

The floor of a source applies to its own claims; otherwise the floor of the policy
does. A claim with no confidence is never below a floor.

Against: `examples/kyc.ttl`

```sparql
SELECT ?claim ?confidence ?floor WHERE {
  ?claim a epi:Claim ;
         epi:confidence ?confidence ;
         epi:claimedBy ?source .
  ?policy a epi:ResolutionPolicy ;
          epi:admissionFloor ?policyFloor .
  OPTIONAL { ?source epi:admissionFloor ?sourceFloor }
  BIND (COALESCE(?sourceFloor, ?policyFloor) AS ?floor)
  FILTER (?confidence < ?floor)
}
ORDER BY ?claim
```

Expected on `kyc.ttl`: one row, `ex:nerShell` (confidence 0.4, floor 0.5).

---

## Results

### CQ-E-5 — Which claims are contested, according to the stored assessment?

Against: `examples/kyc.ttl`

```sparql
SELECT ?claim ?reason WHERE {
  ?assessment a epi:Assessment ;
              epi:assesses ?claim ;
              epi:status epi:Contested ;
              epi:reason ?reason .
}
ORDER BY ?claim
```

Expected on `kyc.ttl`: `ex:newsCy` and `ex:newsUk`, both in conflict 3: the policy
cannot choose between them (same tier, confidences 0.91 and 0.88 within the margin,
no claim time).

---

### CQ-E-6 — Which decision rejected `ex:newsControl`, and by which criterion?

Against: `examples/kyc.ttl`

Only a decided pair has a loser; the query also requires the criterion.

```sparql
SELECT ?decision ?winner ?criterion ?values WHERE {
  ?decision a epi:Decision ;
            epi:loser ex:newsControl ;
            epi:winner ?winner ;
            epi:decidedBy ?criterion ;
            epi:comparedValues ?values .
}
ORDER BY ?decision
```

Expected on `kyc.ttl`: two decisions, both by `epi:ByTier`: `ex:formCleared` over it
("tier 2 over tier 1") and `ex:sancIvan` over it ("tier 3 over tier 1"). The claim is
rejected because the sanctioned person's claim outranks it as well.

---

### CQ-E-7 — Which pairs of claims did no criterion decide, and what was tried?

An undecided decision has no `epi:winner`, `epi:loser` or `epi:decidedBy`; its two claims
are read from `epi:compares`.

Against: `examples/kyc.ttl`

```sparql
SELECT ?decision ?first ?second ?values WHERE {
  ?decision a epi:Decision ;
            epi:compares ?first , ?second ;
            epi:comparedValues ?values .
  FILTER (STR(?first) < STR(?second))
  FILTER NOT EXISTS { ?decision epi:decidedBy ?criterion }
}
ORDER BY ?decision
```

Expected on `kyc.ttl`: one row, `ex:d_country` comparing `ex:newsCy` and `ex:newsUk`
("undecided after tier, confidence, recency"), the decision behind their contested status
(CQ-E-5).
