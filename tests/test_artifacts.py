"""Syntax and serialization release guards for the six published foundations."""
from pathlib import Path
import unittest
from rdflib import Graph
from rdflib.namespace import SKOS
from rdflib.compare import isomorphic
from pyshacl import validate

ROOT=Path(__file__).resolve().parents[1]
MODULES=['ldso-core','ldso-entities','ldso-annotations','lifecycle','ldso-semantics','ldso-operations']

class ArtifactTests(unittest.TestCase):
    def test_all_distributions_and_examples_parse(self):
        for module in MODULES:
            for filename in ['ontology.ttl','shapes.ttl','examples/example.ttl','examples/example.jsonld']:
                with self.subTest(module=module,file=filename):Graph().parse(ROOT/module/filename)

    def test_all_shapes_pass_meta_shacl(self):
        for module in MODULES:
            # meta_shacl raises if shape syntax fails. Ordinary validation of
            # empty data may fail a fixed target and is not a syntax failure.
            with self.subTest(module=module):validate(Graph(),shacl_graph=Graph().parse(ROOT/module/'shapes.ttl'),meta_shacl=True)

    def test_semantics_embedded_turtle_examples_parse(self):
        g=Graph().parse(ROOT/'ldso-semantics/ontology.ttl')
        prefixes='\n'.join(f'@prefix {p}: <{iri}> .' for p,iri in g.namespaces())
        prefixes+='\n@prefix ex: <https://example.org/test/> .\n'
        for subject,example in g.subject_objects(SKOS.example):
            with self.subTest(term=str(subject)):Graph().parse(data=prefixes+str(example),format='turtle')

    def test_example_serializations_agree(self):
        for module in MODULES:
            with self.subTest(module=module):
                self.assertTrue(isomorphic(Graph().parse(ROOT/module/'examples/example.ttl'),
                                           Graph().parse(ROOT/module/'examples/example.jsonld')))

if __name__=='__main__':unittest.main()
