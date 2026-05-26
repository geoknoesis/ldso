# LDSO-Lifecycle — Competency Questions

Competency questions define what the module must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against `examples/example.ttl`.

Prefixes used throughout:

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX life: <https://w3id.org/ldso/lifecycle#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
```

---

## Amendment Tracking

### CQ-L-01 — Which instruments has document X formally amended?

```sparql
SELECT ?amending ?amended ?issued WHERE {
  ?amending a ldso:Document ;
            life:amends ?amended .
  OPTIONAL { ?amending dct:issued ?issued }
}
ORDER BY ?issued
```

---

### CQ-L-02 — What amendment instructions target a specific provision?

```sparql
SELECT ?instruction ?changeDescription WHERE {
  ?instruction a life:AmendmentInstruction ;
               life:modifies <https://w3id.org/ldso/lifecycle/example#USMCA_Art2_5_Para3_v1> .
  OPTIONAL { ?instruction life:changeDescription ?changeDescription }
}
```

---

### CQ-L-03 — What legal effects resulted from a given amendment instruction?

```sparql
SELECT ?instruction ?effect ?effectType WHERE {
  ?instruction a life:AmendmentInstruction ;
               life:resultsIn ?effect .
  ?effect a ?effectType .
  FILTER(?effectType != life:LegalEffect)
  FILTER(STRSTARTS(STR(?effectType), "https://w3id.org/ldso/lifecycle#"))
}
```

---

### CQ-L-04 — What is the full instruction–effect provenance chain for a provision substitution?

```sparql
SELECT ?instruction ?substitution ?replacedVersion ?newVersion WHERE {
  ?substitution a life:Substitution ;
                life:derivedFromInstruction ?instruction ;
                life:replaces ?replacedVersion ;
                life:createsVersion ?newVersion .
}
```

---

## Version History

### CQ-L-05 — What versions exist for a provision, ordered chronologically?

```sparql
SELECT ?version ?versionNumber ?effectiveFrom ?effectiveTo WHERE {
  ?version a life:VersionedProvision ;
           ldso:partOf+ <https://w3id.org/ldso/lifecycle/example#USMCA_Art2_5> .
  OPTIONAL { ?version life:versionNumber ?versionNumber }
  OPTIONAL { ?version life:effectiveFrom ?effectiveFrom }
  OPTIONAL { ?version life:effectiveTo   ?effectiveTo }
}
ORDER BY ?effectiveFrom
```

---

### CQ-L-06 — What is the current (open-ended) version of a provision?

A version with no `life:effectiveTo` is presumed current.

```sparql
SELECT ?version ?effectiveFrom WHERE {
  ?version a life:VersionedProvision ;
           ldso:partOf+ <https://w3id.org/ldso/lifecycle/example#USMCA_Art2_5> ;
           life:effectiveFrom ?effectiveFrom .
  FILTER NOT EXISTS { ?version life:effectiveTo ?effectiveTo }
}
```

---

### CQ-L-07 — Which provision supersedes another in the version chain?

```sparql
SELECT ?newer ?older WHERE {
  ?newer a life:VersionedProvision ;
         life:supersedes ?older .
}
ORDER BY ?older
```

---

### CQ-L-08 — Walk the full version chain of a provision from oldest to newest.

```sparql
SELECT ?version ?effectiveFrom WHERE {
  ?version a life:VersionedProvision ;
           ldso:partOf+ <https://w3id.org/ldso/lifecycle/example#USMCA_Art2_5> ;
           life:effectiveFrom ?effectiveFrom .
}
ORDER BY ?effectiveFrom
```

---

## Point-in-Time Validity

### CQ-L-09 — Which provisions were valid on a specific date?

Replaces the date literal with the query date to retrieve the applicable law at that moment.

```sparql
SELECT ?provision ?effectiveFrom ?effectiveTo WHERE {
  ?provision a life:VersionedProvision ;
             life:effectiveFrom ?effectiveFrom .
  OPTIONAL { ?provision life:effectiveTo ?effectiveTo }
  BIND("2026-01-01"^^xsd:date AS ?queryDate)
  FILTER(?effectiveFrom <= ?queryDate)
  FILTER(!BOUND(?effectiveTo) || ?effectiveTo > ?queryDate)
}
ORDER BY ?effectiveFrom
```

---

### CQ-L-10 — Which provisions have expired (effectiveTo is in the past)?

```sparql
SELECT ?provision ?effectiveTo WHERE {
  ?provision a life:VersionedProvision ;
             life:effectiveTo ?effectiveTo .
  BIND(NOW() AS ?today)
  FILTER(?effectiveTo < ?today)
}
ORDER BY ?effectiveTo
```

---

### CQ-L-11 — Which instruments are currently suspended?

```sparql
SELECT ?resource ?stateLabel WHERE {
  ?resource life:stateLabel ?stateLabel .
  FILTER(?stateLabel = "Suspended")
}
```

---

## Lifecycle Events

### CQ-L-12 — What lifecycle events are recorded for a legal instrument, ordered by date?

```sparql
SELECT ?event ?type ?eventDate ?changeDescription WHERE {
  ?event life:affects <https://w3id.org/ldso/lifecycle/example#USMCA_Original> ;
         a ?type .
  OPTIONAL { ?event life:eventDate ?eventDate }
  OPTIONAL { ?event life:changeDescription ?changeDescription }
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/lifecycle#"))
  FILTER(?type != life:LifecycleEvent)
}
ORDER BY ?eventDate
```

---

### CQ-L-13 — What is the entry-into-force date of an instrument?

```sparql
SELECT ?instrument ?eventDate WHERE {
  ?eif a life:EntryIntoForce ;
       life:eventDate ?eventDate ;
       life:affects ?instrument .
}
ORDER BY ?instrument
```

---

### CQ-L-14 — Which provisions were created by insertions?

```sparql
SELECT ?insertion ?newProvision ?effectiveFrom WHERE {
  ?insertion a life:Insertion ;
             life:createsVersion ?newProvision .
  OPTIONAL { ?newProvision life:effectiveFrom ?effectiveFrom }
}
ORDER BY ?effectiveFrom
```

---

## Consolidation

### CQ-L-15 — Which consolidated provisions exist and what source versions do they derive from?

```sparql
SELECT ?consolidated ?source ?consolidationDate WHERE {
  ?consolidated a life:ConsolidatedProvision ;
                life:derivedFromProvision ?source .
  OPTIONAL {
    ?consolidation a life:Consolidation ;
                   life:createsVersion ?consolidated ;
                   life:consolidationDate ?consolidationDate .
  }
}
ORDER BY ?consolidationDate
```

---

### CQ-L-16 — What is the consolidated text of a provision as of a consolidation date?

```sparql
SELECT ?consolidated ?consolidationDate ?text WHERE {
  ?consolidated a life:ConsolidatedProvision ;
                ldso:partOf+ <https://w3id.org/ldso/lifecycle/example#USMCA_Art2_5> .
  OPTIONAL {
    ?consolidation a life:Consolidation ;
                   life:createsVersion ?consolidated ;
                   life:consolidationDate ?consolidationDate .
  }
  OPTIONAL { ?consolidated ldso:text ?text }
}
ORDER BY ?consolidationDate
```

---

## Deprecated and Repealed Provisions

### CQ-L-17 — Which provisions have been deprecated?

```sparql
SELECT ?provision ?effectiveTo WHERE {
  ?provision a life:DeprecatedProvision ;
             life:effectiveTo ?effectiveTo .
}
ORDER BY ?effectiveTo
```

---

### CQ-L-18 — Which instruments or provisions have been repealed, and by what repealing act?

```sparql
SELECT ?repeal ?repealed ?effectiveTo WHERE {
  ?repeal a life:Repeal ;
          life:repeals ?repealed .
  OPTIONAL { ?repealed life:effectiveTo ?effectiveTo }
}
```

---

## Validation Support

### CQ-L-19 — Which amendment instructions have no linked legal effect?

*Detected by `life:AmendmentInstructionShape`.*

```sparql
SELECT ?instruction ?changeDescription WHERE {
  ?instruction a life:AmendmentInstruction .
  OPTIONAL { ?instruction life:changeDescription ?changeDescription }
  FILTER NOT EXISTS { ?instruction life:resultsIn ?effect }
}
```

*Expected result: no rows in a well-formed dataset.*

---

### CQ-L-20 — Which legal effects have no derivedFromInstruction (broken provenance)?

```sparql
SELECT ?effect ?type WHERE {
  ?effect a life:LegalEffect ;
          a ?type .
  FILTER(?type != life:LegalEffect)
  FILTER NOT EXISTS { ?effect life:derivedFromInstruction ?instruction }
}
```

*Expected result: no rows in a well-formed dataset.*

---

### CQ-L-21 — Which versioned provisions lack an effectiveFrom date?

*Detected by `life:VersionedProvisionShape`.*

```sparql
SELECT ?provision WHERE {
  ?provision a life:VersionedProvision .
  FILTER NOT EXISTS { ?provision life:effectiveFrom ?date }
}
```

*Expected result: no rows.*

---

### CQ-L-22 — Are there ordering chain breaks in the lifecycle graph?
*(Analogous to the LDSO-Core ordering check — detects A.next = B but B.previous ≠ A.)*

```sparql
SELECT ?a ?b WHERE {
  ?a ldso:next ?b .
  FILTER NOT EXISTS { ?b ldso:previous ?a }
}
```

*Expected result: no rows.*

---

### CQ-L-23 — Which DeprecatedProvisions are missing an effectiveTo date?

```sparql
SELECT ?provision WHERE {
  ?provision a life:DeprecatedProvision .
  FILTER NOT EXISTS { ?provision life:effectiveTo ?date }
}
```

*Expected result: no rows.*
