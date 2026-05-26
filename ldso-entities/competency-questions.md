# LDSO-Entities — Competency Questions

Competency questions define what the module must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against `examples/example.ttl`.

Prefixes used throughout:

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX ent:  <https://w3id.org/ldso/entities#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

---

## Entity Catalogue

### CQ-E-01 — What named entities are declared in the graph?

```sparql
SELECT ?entity ?type ?showAs ?href WHERE {
  ?entity a ent:NamedEntity ;
          ent:showAs ?showAs ;
          ent:href ?href .
  ?entity a ?type .
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/entities#"))
  FILTER(?type != ent:NamedEntity)
}
ORDER BY ?type ?showAs
```

---

### CQ-E-02 — What organizations are declared?

```sparql
SELECT ?org ?showAs ?href WHERE {
  ?org a ent:Organization ;
       ent:showAs ?showAs ;
       ent:href ?href .
}
```

---

### CQ-E-03 — What legal concepts are declared?

```sparql
SELECT ?concept ?showAs ?href WHERE {
  ?concept a ent:Concept ;
           ent:showAs ?showAs ;
           ent:href ?href .
}
```

---

### CQ-E-04 — What roles are declared?

```sparql
SELECT ?role ?showAs ?href WHERE {
  ?role a ent:Role ;
        ent:showAs ?showAs ;
        ent:href ?href .
}
```

---

## Element-Level Entity References

### CQ-E-05 — Which articles reference a specific named entity?

```sparql
SELECT ?article ?citation WHERE {
  ?entity ent:showAs "temporary admission" .
  ?article a ldso:Article ;
           ent:refersToEntity ?entity ;
           ldso:citation ?citation .
}
ORDER BY ?citation
```

---

### CQ-E-06 — What named entities are referenced anywhere in chapter 2?

```sparql
SELECT DISTINCT ?entity ?type ?showAs WHERE {
  ?chapter ldso:citation "2" ;
           ldso:contains+ ?element .
  ?element ent:refersToEntity ?entity .
  ?entity a ?type ;
          ent:showAs ?showAs .
  FILTER(STRSTARTS(STR(?type), "https://w3id.org/ldso/entities#"))
  FILTER(?type != ent:NamedEntity)
}
ORDER BY ?type ?showAs
```

---

### CQ-E-07 — Which elements refer to entities of a given type throughout the document?

```sparql
SELECT ?element ?citation ?showAs WHERE {
  <https://example.org/ata/doc_ata_en>
    ldso:contains+ ?element .
  ?element ent:refersToEntity ?entity .
  ?entity a ent:Role ;
          ent:showAs ?showAs .
  OPTIONAL { ?element ldso:citation ?citation }
}
ORDER BY ?citation
```

---

### CQ-E-08 — Find all elements referencing a specific entity by its canonical href.

```sparql
SELECT ?element ?citation WHERE {
  ?entity ent:href "https://example.org/legal/concepts/temporary-admission"^^xsd:anyURI .
  ?element ent:refersToEntity ?entity ;
           ldso:citation ?citation .
}
ORDER BY ?citation
```

---

## Validation Support

### CQ-E-09 — Which named entities are missing a canonical href?

*Checked by `ent:NamedEntityShape`.*

```sparql
SELECT ?entity ?showAs WHERE {
  ?entity a ent:NamedEntity .
  OPTIONAL { ?entity ent:showAs ?showAs }
  FILTER NOT EXISTS { ?entity ent:href ?href }
}
```

*Expected result: no rows.*

---

### CQ-E-10 — Which named entities are typed as more than one disjoint subtype?

*Checked by `ent:EntityTypeConsistencyShape`.*

```sparql
SELECT ?entity (GROUP_CONCAT(?subtype ; separator=", ") AS ?types) WHERE {
  ?entity a ?subtype .
  VALUES ?subtype {
    ent:Person ent:Organization ent:Location
    ent:Concept ent:Role ent:Event ent:Process
  }
}
GROUP BY ?entity
HAVING (COUNT(DISTINCT ?subtype) > 1)
```

*Expected result: no rows in a well-formed dataset.*
