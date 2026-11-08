"""Regenerate JSON-LD examples from their canonical Turtle examples."""
from pathlib import Path
from rdflib import Graph
from rdflib.compare import isomorphic

ROOT=Path(__file__).resolve().parents[1]
for path in sorted(ROOT.glob('*/examples/example.ttl')):
    graph=Graph().parse(path)
    context={p:str(iri) for p,iri in graph.namespaces()}
    output=path.with_suffix('.jsonld')
    graph.serialize(output,format='json-ld',context=context,auto_compact=True,indent=2,encoding='utf-8')
    if not isomorphic(graph,Graph().parse(output)):
        raise RuntimeError('JSON-LD round-trip mismatch: '+str(path))
    print(path.parent.parent.name,len(graph),'triples')
