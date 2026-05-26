# LDSO-Semantics — Competency Questions

Competency questions define what the module must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against `examples/example.ttl`.

Prefixes used throughout:

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX ent:  <https://w3id.org/ldso/entities#>
PREFIX leg:  <https://w3id.org/ldso/semantics#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

---

## Normative Statement Discovery

### CQ-S-01 — What normative statements annotate a specific provision?

```sparql
SELECT ?annotation ?type ?modal WHERE {
  ?annotation leg:annotates <https://example.org/ata/para_1> ;
              a ?type .
  OPTIONAL { ?annotation leg:deonticModal ?modal }
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/semantics#"))
  FILTER(?type != leg:LegalAnnotation)
}
```

---

### CQ-S-02 — What are all obligations in an article?

```sparql
SELECT ?obligation ?modal ?normativeText WHERE {
  ?obligation a leg:Obligation ;
              leg:annotates ?element .
  ?element ldso:partOf+ <https://example.org/ata/art_5> .
  OPTIONAL { ?obligation leg:deonticModal ?modal }
  OPTIONAL { ?obligation leg:normativeText ?normativeText }
}
ORDER BY ?modal
```

---

### CQ-S-03 — What are all permissions in the document?

```sparql
SELECT ?permission ?element ?modal WHERE {
  ?permission a leg:Permission ;
              leg:annotates ?element .
  OPTIONAL { ?permission leg:deonticModal ?modal }
}
ORDER BY ?element
```

---

### CQ-S-04 — What are all prohibitions in the document?

```sparql
SELECT ?prohibition ?element ?text WHERE {
  ?prohibition a leg:Prohibition ;
               leg:annotates ?element .
  OPTIONAL { ?prohibition leg:normativeText ?text }
}
```

---

### CQ-S-05 — What norms apply to a specific subject (e.g., competent authority)?

```sparql
SELECT ?norm ?type ?modal ?element WHERE {
  ?norm leg:normativeSubject <https://example.org/ata/competent_authority> ;
        a ?type ;
        leg:annotates ?element .
  OPTIONAL { ?norm leg:deonticModal ?modal }
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/semantics#"))
  FILTER(?type != leg:LegalAnnotation)
  FILTER(?type != leg:NormativeStatement)
}
ORDER BY ?element
```

---

### CQ-S-06 — List all norms by deontic type across the document.

```sparql
SELECT ?type (COUNT(?norm) AS ?count) WHERE {
  ?norm a ?type ;
        leg:annotates ?element .
  VALUES ?type {
    leg:Obligation leg:Permission leg:Prohibition leg:Right leg:Discretion
  }
}
GROUP BY ?type
ORDER BY DESC(?count)
```

---

## Conditions and Exceptions

### CQ-S-07 — What conditions govern a specific obligation?

```sparql
SELECT ?condition ?conditionText WHERE {
  <https://example.org/ata/Oblig_Para1_Admit>
    leg:conditionedBy ?condition .
  ?condition leg:conditionText ?conditionText .
}
```

---

### CQ-S-08 — Are there norms that apply without any conditions?

```sparql
SELECT ?norm ?type WHERE {
  ?norm a ?type ;
        leg:annotates ?element .
  VALUES ?type { leg:Obligation leg:Prohibition }
  FILTER NOT EXISTS { ?norm leg:conditionedBy ?cond }
}
```

---

### CQ-S-09 — What exceptions qualify a specific obligation?

```sparql
SELECT ?exception ?exceptionText WHERE {
  <https://example.org/ata/Oblig_Para2_Present>
    leg:exceptedBy ?exception .
  OPTIONAL { ?exception leg:exceptionText ?exceptionText }
}
```

---

### CQ-S-10 — Which norms have at least one exception?

```sparql
SELECT ?norm ?type (COUNT(?exc) AS ?exceptionCount) WHERE {
  ?norm a ?type ;
        leg:exceptedBy ?exc .
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/semantics#"))
}
GROUP BY ?norm ?type
ORDER BY DESC(?exceptionCount)
```

---

## Definitions

### CQ-S-11 — What terms are defined in the document?

```sparql
SELECT ?definition ?term ?definitionText WHERE {
  ?definition a leg:Definition ;
              leg:definedTerm ?term ;
              leg:definitionText ?definitionText .
  FILTER(LANG(?term) = "en")
}
ORDER BY ?term
```

---

### CQ-S-12 — Where is a specific term defined?

```sparql
SELECT ?definition ?element ?citation WHERE {
  ?definition a leg:Definition ;
              leg:definedTerm "temporary admission"@en ;
              leg:annotates ?element .
  OPTIONAL { ?element ldso:citation ?citation }
}
```

---

### CQ-S-13 — Which defined terms are linked to named entities?

```sparql
SELECT ?term ?entity ?href WHERE {
  ?def a leg:Definition ;
       leg:definedTerm ?term ;
       leg:definesEntity ?entity .
  OPTIONAL { ?entity ent:href ?href }
  FILTER(LANG(?term) = "en")
}
ORDER BY ?term
```

---

## Scope Analysis

### CQ-S-14 — What scope annotations cover a specific article?

```sparql
SELECT ?scope ?scopeText WHERE {
  ?scope a leg:Scope ;
         leg:annotates <https://example.org/ata/art_5> ;
         leg:scopeText ?scopeText .
}
```

---

### CQ-S-15 — Which obligations fall within a named scope?

```sparql
SELECT ?obligation ?element WHERE {
  <https://example.org/ata/Scope_Art2_5>
    leg:scopeOf ?obligation .
  ?obligation a leg:Obligation ;
              leg:annotates ?element .
}
```

---

## Cross-Provision Queries

### CQ-S-16 — What conditions are shared (referenced by more than one norm)?

```sparql
SELECT ?condition (COUNT(?norm) AS ?normCount) WHERE {
  ?norm leg:conditionedBy ?condition .
}
GROUP BY ?condition
HAVING (?normCount > 1)
ORDER BY DESC(?normCount)
```

---

### CQ-S-17 — Retrieve the full semantic profile of a provision.

Returns every annotation type for a given provision node.

```sparql
SELECT ?annotation ?type ?modal ?definedTerm ?conditionText WHERE {
  ?annotation leg:annotates <https://example.org/ata/para_1> ;
              a ?type .
  OPTIONAL { ?annotation leg:deonticModal ?modal }
  OPTIONAL { ?annotation leg:definedTerm ?definedTerm }
  OPTIONAL {
    ?annotation leg:conditionedBy ?cond .
    ?cond leg:conditionText ?conditionText .
  }
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/semantics#"))
  FILTER(?type != leg:LegalAnnotation)
}
```

---

## Validation Support

### CQ-S-18 — Which annotations have no leg:annotates link (orphaned)?

*Checked by `leg:LegalAnnotationShape`.*

```sparql
SELECT ?annotation ?type WHERE {
  ?annotation a ?type .
  VALUES ?type {
    leg:Obligation leg:Permission leg:Prohibition
    leg:Right leg:Discretion leg:Definition leg:Exception leg:Scope
  }
  FILTER NOT EXISTS { ?annotation leg:annotates ?element }
}
```

*Expected result: no rows.*

---

### CQ-S-19 — Which obligations lack a normative subject?

```sparql
SELECT ?obligation WHERE {
  ?obligation a leg:Obligation .
  FILTER NOT EXISTS { ?obligation leg:normativeSubject ?subject }
}
```

*Expected result: no rows in a well-formed dataset.*

---

### CQ-S-20 — Are there broken exception inverse chains?

*Checked by `leg:ExceptionInverseShape`.*

```sparql
SELECT ?norm ?exc WHERE {
  ?norm leg:exceptedBy ?exc .
  FILTER NOT EXISTS { ?exc leg:exceptionOf ?norm }
}
```

*Expected result: no rows.*

---

### CQ-S-21 — Are there broken condition inverse chains?

*Checked by `leg:ConditionInverseShape`.*

```sparql
SELECT ?norm ?cond WHERE {
  ?norm leg:conditionedBy ?cond .
  FILTER NOT EXISTS { ?cond leg:conditionOf ?norm }
}
```

*Expected result: no rows.*

---

### CQ-S-22 — Which definitions lack a definition text?

*Checked by `leg:DefinitionShape`.*

```sparql
SELECT ?definition ?term WHERE {
  ?definition a leg:Definition ;
              leg:definedTerm ?term .
  FILTER NOT EXISTS { ?definition leg:definitionText ?text }
}
```

*Expected result: no rows.*
