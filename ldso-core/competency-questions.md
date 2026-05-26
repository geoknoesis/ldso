# LDSO-Core — Competency Questions

Competency questions define what the ontology must be able to answer.
Each question is stated in natural language and paired with a SPARQL query
validated against `examples/example.ttl`.

Prefixes used throughout:

```sparql
PREFIX ldso: <https://w3id.org/ldso/core#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

---

## Legal Resource and Expression

### CQ-C-01 — What abstract legal instruments are in the knowledge graph?

```sparql
SELECT ?resource ?title WHERE {
  ?resource a ldso:LegalResource ;
            dct:title ?title .
  FILTER NOT EXISTS { ?resource a ldso:LegalExpression }
}
```

*Returns only abstract instruments (not Documents or LegalExpressions).*

---

### CQ-C-02 — What language expressions exist for a given instrument?

```sparql
SELECT ?expr ?lang ?issued WHERE {
  <https://example.org/resource/temporary-admission>
    ldso:hasExpression ?expr .
  ?expr dct:language ?lang .
  OPTIONAL { ?expr dct:issued ?issued }
}
ORDER BY ?lang
```

---

### CQ-C-03 — Retrieve the full instrument → expression → document chain.

```sparql
SELECT ?resource ?resourceTitle ?expr ?lang ?issued WHERE {
  ?resource a ldso:LegalResource ;
            dct:title ?resourceTitle .
  OPTIONAL {
    ?expr ldso:expressionOf ?resource ;
          dct:language ?lang .
    OPTIONAL { ?expr dct:issued ?issued }
  }
  FILTER NOT EXISTS { ?resource a ldso:LegalExpression }
}
ORDER BY ?resourceTitle ?lang
```

---

## Document Structure

### CQ-C-04 — What documents are in the knowledge graph?

```sparql
SELECT ?doc ?title ?lang WHERE {
  ?doc a ldso:Document ;
       dct:title ?title ;
       dct:language ?lang .
}
ORDER BY ?lang
```

---

### CQ-C-05 — What top-level structural elements does a document contain?

```sparql
SELECT ?element ?type WHERE {
  <https://example.org/doc/temporary-admission/EN> ldso:contains ?body .
  ?body ldso:contains ?element .
  ?element a ?type .
}
```

---

### CQ-C-06 — What is the text of the element with citation "2.5.1"?

```sparql
SELECT ?element ?text WHERE {
  ?element ldso:citation "2.5.1" ;
           ldso:text ?text .
}
```

---

### CQ-C-07 — What are all the chapters in a document, in order?

```sparql
SELECT ?chapter ?notation ?title WHERE {
  <https://example.org/doc/temporary-admission/EN>
    ldso:contains / ldso:contains ?chapter .
  ?chapter a ldso:Chapter ;
           ldso:notation ?notation .
  OPTIONAL { ?chapter dct:title ?title }
}
ORDER BY ?notation
```

---

### CQ-C-08 — What are all the articles in chapter 2, in document order?

```sparql
SELECT ?article ?notation ?citation WHERE {
  ?chapter ldso:notation "2" ;
           ldso:contains ?article .
  ?article a ldso:Article ;
           ldso:notation ?notation ;
           ldso:citation ?citation ;
           ldso:orderIndex ?idx .
}
ORDER BY ?idx
```

---

### CQ-C-09 — List all paragraphs of article 5 in document order, with their text.

```sparql
SELECT ?para ?citation ?text WHERE {
  <https://example.org/doc/temporary-admission/EN/body/chp_2/art_5>
    ldso:contains ?para .
  ?para a ldso:Paragraph ;
        ldso:citation ?citation ;
        ldso:orderIndex ?idx .
  OPTIONAL { ?para ldso:text ?text }
}
ORDER BY ?idx
```

---

### CQ-C-10 — What is the next sibling of paragraph "2.5.1"?

```sparql
SELECT ?next ?citation WHERE {
  ?para ldso:citation "2.5.1" ;
        ldso:next ?next .
  ?next ldso:citation ?citation .
}
```

---

### CQ-C-11 — What element directly contains paragraph "2.5.2"?

```sparql
SELECT ?parent ?type ?citation WHERE {
  ?para ldso:citation "2.5.2" ;
        ldso:partOf ?parent .
  ?parent a ?type .
  OPTIONAL { ?parent ldso:citation ?citation }
}
```

---

### CQ-C-12 — What is the full ancestor chain from item "2.5.2.a" to the document root?

```sparql
SELECT ?ancestor ?type ?citation WHERE {
  ?item ldso:citation "2.5.2.a" .
  ?item ldso:partOf+ ?ancestor .
  ?ancestor a ?type .
  OPTIONAL { ?ancestor ldso:citation ?citation }
}
```

*Uses `ldso:partOf` as a transitive property (`owl:TransitiveProperty`).
In SPARQL, use property path `ldso:partOf+` for transitivity.*

---

### CQ-C-13 — List all items in the block list under paragraph "2.5.2", in order.

```sparql
SELECT ?item ?notation ?text WHERE {
  ?para ldso:citation "2.5.2" ;
        ldso:contains ?list .
  ?list a ldso:BlockList ;
        ldso:contains ?item .
  ?item a ldso:Item ;
        ldso:notation ?notation ;
        ldso:orderIndex ?idx .
  OPTIONAL { ?item ldso:text ?text }
}
ORDER BY ?idx
```

---

### CQ-C-14 — Walk the sibling chain of items in a block list from first to last.

```sparql
SELECT ?item ?notation WHERE {
  ?list a ldso:BlockList ;
        ldso:contains ?item .
  ?item ldso:notation ?notation ;
        ldso:orderIndex ?idx .
  FILTER NOT EXISTS { ?item ldso:previous ?prev }
}
ORDER BY ?idx
```

*Start at the item with no `ldso:previous` (the head), then follow `ldso:next`.*

---

### CQ-C-15 — Which elements are referenced by inline cross-references within article 5?

```sparql
SELECT ?ref ?anchorText ?target WHERE {
  <https://example.org/doc/temporary-admission/EN/body/chp_2/art_5>
    ldso:contains+ ?ref .
  ?ref a ldso:InternalReference ;
       ldso:anchorText ?anchorText ;
       ldso:refersTo ?target .
}
```

---

### CQ-C-16 — What are all elements at a given structural type across the entire document?

```sparql
SELECT ?article ?citation ?title WHERE {
  <https://example.org/doc/temporary-admission/EN>
    ldso:contains+ ?article .
  ?article a ldso:Article ;
           ldso:citation ?citation .
  OPTIONAL { ?article dct:title ?title }
}
ORDER BY ?citation
```

*Uses `ldso:contains+` (transitive) to traverse the full document tree.*

---

### CQ-C-17 — Does the ordering chain for paragraphs in article 5 have no broken links?

```sparql
ASK {
  ?para a ldso:Paragraph ;
        ldso:next ?next .
  FILTER NOT EXISTS { ?next ldso:previous ?para }
}
```

*Returns `false` if the chain is intact (no broken `next`/`previous` pairs).*

---

## Tables

### CQ-C-18 — What are the header cells of table 1 in article 5?

```sparql
SELECT ?cell ?text WHERE {
  ?table a ldso:Table ;
         ldso:partOf <https://example.org/doc/temporary-admission/EN/body/chp_2/art_5> ;
         ldso:hasRow ?row .
  ?row ldso:isHeader true ;
       ldso:hasCell ?cell .
  ?cell ldso:text ?text ;
        ldso:orderIndex ?col .
}
ORDER BY ?col
```

---

### CQ-C-19 — Retrieve all data rows of table 1 with their cells in column order.

```sparql
SELECT ?rowIdx ?colIdx ?text WHERE {
  ?table a ldso:Table ;
         ldso:hasRow ?row .
  ?row ldso:orderIndex ?rowIdx ;
       ldso:hasCell ?cell .
  FILTER NOT EXISTS { ?row ldso:isHeader true }
  ?cell ldso:orderIndex ?colIdx ;
        ldso:text ?text .
}
ORDER BY ?rowIdx ?colIdx
```

---

## References

### CQ-C-20 — Which elements cite an external resource?

```sparql
SELECT ?element ?citation ?target WHERE {
  ?element ldso:cites ?target ;
           ldso:citation ?citation .
}
```

---

### CQ-C-21 — What is the surface text of all cross-references in the document?

```sparql
SELECT ?ref ?anchorText WHERE {
  <https://example.org/doc/temporary-admission/EN>
    ldso:contains+ ?ref .
  ?ref a ldso:Reference ;
       ldso:anchorText ?anchorText .
}
```

---

## Validation Support

### CQ-C-22 — Which elements have `ldso:citation` that does not start with their parent's citation?

*Answered by the `ldso:CitationChainShape` SPARQL constraint in `shapes.ttl`.*

```sparql
SELECT ?child ?childCitation ?parentCitation WHERE {
  ?child ldso:citation ?childCitation ;
         ldso:partOf ?parent .
  ?parent ldso:citation ?parentCitation .
  FILTER NOT EXISTS {
    FILTER(STRSTARTS(?childCitation, CONCAT(?parentCitation, ".")))
  }
}
```

---

### CQ-C-23 — Which elements use rdf:List ordering (prohibited)?

```sparql
SELECT ?element WHERE {
  ?element a ldso:LegalElement ;
           rdf:first ?anything .
}
```

*Expected result: no rows.*
