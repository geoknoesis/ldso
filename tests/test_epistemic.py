"""Release guards for LDSO-Epistemic: artifacts parse, examples parse, every term documented."""
from decimal import Decimal
from pathlib import Path
import re
import unittest
from rdflib import Graph, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, RDFS, OWL, SKOS, SH, XSD
from rdflib.plugins.sparql import processor as sparql_processor
from rdflib.plugins.sparql.processor import prepareQuery
from pyshacl import validate

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'ldso-epistemic'
IMPORTS=['ldso-core','ldso-epistemic']
EPI=Namespace('https://w3id.org/ldso/epistemic#')

def _cache_sparql():
    """Parse and translate each SPARQL constraint once (see test_deontic.py)."""
    original=sparql_processor.SPARQLProcessor.query
    prepared={}
    def query(self,strOrQuery,initBindings=None,initNs=None,base=None,DEBUG=False):
        if isinstance(strOrQuery,str):
            key=(strOrQuery,base,tuple(sorted((k,str(v)) for k,v in (initNs or {}).items())))
            if key not in prepared:prepared[key]=prepareQuery(strOrQuery,initNs=initNs,base=base)
            strOrQuery=prepared[key]
        return original(self,strOrQuery,initBindings,initNs,base,DEBUG)
    sparql_processor.SPARQLProcessor.query=query
_cache_sparql()

PREFIXES="""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix epi: <https://w3id.org/ldso/epistemic#> .
@prefix ex: <https://example.org/kyc/> .
"""
# A small executable belief: two sources, claims of several shapes (denied identity claims among them),
# a correction, a retraction, a policy with a scoped chain, and a stored result.
BASE="""
ex:src_a a epi:Source ; epi:tier 3 .
ex:src_b a epi:Source ; epi:tier 1 ; epi:admissionFloor 0.7 .
ex:c1 a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;
  epi:claimedBy ex:src_a ; epi:confidence 1.0 ; epi:claimedAt "2026-03-04T00:00:00Z"^^xsd:dateTime .
ex:c2 a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:sanctioned ; rdf:object ex:Listed ;
  epi:negated true ; epi:claimedBy ex:src_b ; epi:confidence 0.91 .
ex:c3 a epi:Claim ; rdf:subject ex:acme ; rdf:predicate owl:sameAs ; rdf:object ex:acme_ltd ;
  epi:negated true ; epi:claimedBy ex:src_b .
ex:c4 a epi:Claim ; rdf:subject ex:acme ; rdf:predicate owl:differentFrom ; rdf:object ex:acme_inc ;
  epi:negated true ; epi:claimedBy ex:src_b .
ex:c5 a epi:Claim ; rdf:subject ex:acme ; rdf:predicate rdf:type ; rdf:object ex:Company ;
  epi:claimedBy ex:src_a ; epi:supersedes ex:c2 .
ex:ret a epi:Retraction ; epi:claimedBy ex:src_a ; epi:claimedAt "2026-05-01T00:00:00Z"^^xsd:dateTime ;
  epi:retracts ex:c4 .
ex:policy a epi:ResolutionPolicy ; epi:admissionFloor 0.5 ; epi:confidenceMargin 0.05 ;
  epi:criteria ( epi:ByTier epi:ByConfidence epi:ByRecency ) ; epi:hasScopedChain ex:chain .
ex:chain a epi:ScopedChain ; epi:appliesTo ex:registeredAddress ; epi:criteria ( epi:ByRecency epi:ByTier ) .
ex:conflict_0 a epi:Conflict ; epi:involves ex:c1 , ex:c2 .
ex:d_0 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:winner ex:c1 ; epi:loser ex:c2 ; epi:decidedBy epi:ByTier ;
  epi:comparedValues "tier 3 over tier 1" .
ex:a_1 a epi:Assessment ; epi:assesses ex:c2 ; epi:status epi:Rejected ; epi:reason "in conflict 0" .
"""

def tbox():
    g=Graph()
    for module in IMPORTS:g.parse(ROOT/module/'ontology.ttl')
    return g

TBOX=tbox()
SHAPES=Graph().parse(MOD/'shapes.ttl')
PROFILE=Graph().parse(MOD/'hydradl-profile-shapes.ttl')

def results(data,shapes):
    """(severity, message) of every result. The data is merged with its imports, not passed as
    ont_graph: pyshacl does not show ont_graph triples to shapes nested in sh:or."""
    _,report,_=validate(data+TBOX,shacl_graph=shapes,inference='rdfs',advanced=True,allow_warnings=True)
    return {(str(report.value(r,SH.resultSeverity)).split('#')[-1],str(report.value(r,SH.resultMessage)))
            for r in report.subjects(RDF.type,SH.ValidationResult)}

def belief(extra=''):
    return Graph().parse(data=PREFIXES+BASE+extra,format='turtle')

class EpistemicArtifactTests(unittest.TestCase):
    def test_artifacts_parse(self):
        for f in ['ontology.ttl','shapes.ttl','hydradl-profile-shapes.ttl','alignments.ttl']:
            with self.subTest(file=f):Graph().parse(MOD/f)
        self.assertTrue((MOD/'README.md').is_file())

    def test_embedded_turtle_examples_parse(self):
        g=Graph().parse(MOD/'ontology.ttl')
        prefixes='\n'.join(f'@prefix {p}: <{iri}> .' for p,iri in g.namespaces())
        prefixes+='\n@prefix ex: <https://example.org/test/> .\n'
        examples=list(g.subject_objects(SKOS.example))
        self.assertTrue(examples)
        for subject,example in examples:
            with self.subTest(term=str(subject)):Graph().parse(data=prefixes+str(example),format='turtle')

    def test_every_term_documented(self):
        g=Graph().parse(MOD/'ontology.ttl')
        classes={s for s in g.subjects(RDF.type,OWL.Class) if str(s).startswith(str(EPI))}
        properties={s for t in (OWL.ObjectProperty,OWL.DatatypeProperty,RDF.Property)
                    for s in g.subjects(RDF.type,t) if str(s).startswith(str(EPI))}
        self.assertTrue(classes and properties)
        for term in sorted(classes|properties):
            for p in (RDFS.label,SKOS.definition,SKOS.scopeNote,SKOS.example):
                with self.subTest(term=str(term),predicate=str(p)):
                    self.assertIsNotNone(g.value(term,p),f'{term} lacks {p}')
        for term in sorted(classes):
            with self.subTest(term=str(term),predicate='rdfs:subClassOf'):
                self.assertIsNotNone(g.value(term,RDFS.subClassOf),f'{term} has no superclass')

    def test_ontology_header(self):
        g=Graph().parse(MOD/'ontology.ttl')
        iri=Namespace('https://w3id.org/ldso/')
        self.assertIn((iri.epistemic,RDF.type,OWL.Ontology),g)
        self.assertEqual(str(g.value(iri.epistemic,OWL.versionInfo)),'0.1.0')
        imports={str(o) for o in g.objects(iri.epistemic,OWL.imports)}
        self.assertEqual(imports,{'https://w3id.org/ldso/core','http://www.w3.org/ns/prov-o#'})

    def test_shapes_pass_meta_shacl(self):
        for f in ['shapes.ttl','hydradl-profile-shapes.ttl']:
            with self.subTest(file=f):validate(Graph(),shacl_graph=Graph().parse(MOD/f),meta_shacl=True)

    def test_base_belief_is_well_formed_and_executable(self):
        self.assertEqual(results(belief(),SHAPES),set())
        self.assertEqual(results(belief(),PROFILE),set())

class ShapeFiresTests(unittest.TestCase):
    """Each case adds one defect to the base belief; the named shape must report it."""
    STRUCTURAL=[
        ('ex:c_nopred a epi:Claim ; rdf:subject ex:acme ; rdf:object ex:Ireland ; epi:claimedBy ex:src_a .','exactly one rdf:predicate'),
        ('ex:c1 rdf:object ex:France .','exactly one rdf:object'),
        ('ex:c1 rdf:subject ex:other .','exactly one rdf:subject'),
        ('ex:c_conf a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;'
         ' epi:claimedBy ex:src_a ; epi:confidence 1.2 .','epi:confidence MUST be'),
        ('ex:c_nosrc a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland .','exactly one epi:claimedBy'),
        ('ex:c_lit a epi:Claim ; rdf:subject ex:acme ; rdf:predicate rdf:type ; rdf:object "Company" ; epi:claimedBy ex:src_a .','IRI object'),
        ('ex:ret_empty a epi:Retraction ; epi:claimedBy ex:src_a .','retract at least one'),
        ('ex:ret_nosrc a epi:Retraction ; epi:retracts ex:c1 .','exactly one epi:claimedBy'),
        ('ex:policy2 a epi:ResolutionPolicy ; epi:criteria ( epi:ByTier ex:ByLuck ) .','epi:Criterion'),
        ('ex:chain epi:criteria ( epi:ByTier ex:ByLuck ) .','epi:Criterion'),
        ('ex:src_neg a epi:Source ; epi:tier -1 .','non-negative integer'),
        ('ex:src_b epi:admissionFloor 1.5 .','epi:admissionFloor MUST be'),
        ('ex:policy epi:confidenceMargin 2.0 .','epi:confidenceMargin MUST be'),
        ('ex:chain2 a epi:ScopedChain ; epi:criteria ( epi:ByTier ) .','exactly one epi:appliesTo'),
        ('ex:chain3 a epi:ScopedChain ; epi:appliesTo ex:registeredAddress ; epi:criteria ( epi:ByTier ) .\n'
         'ex:policy epi:hasScopedChain ex:chain3 .','at most one scoped chain'),
        ('ex:a_1 epi:status ex:Maybe .','one of the five'),
        ('ex:a_2 a epi:Assessment ; epi:status epi:Accepted .','exactly one epi:assesses'),
        ('ex:conflict_1 a epi:Conflict .','involve at least one'),
        # a decision compares two claims; winner, loser and criterion are all present or all absent
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 ; epi:comparedValues "undecided after tier" .','compare exactly two'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 , ex:c5 ; epi:comparedValues "undecided after tier" .',
         'compare exactly two'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:winner ex:c1 ;'
         ' epi:comparedValues "undecided after tier, confidence, recency" .','each exactly once'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:winner ex:c1 ; epi:loser ex:c2 ;'
         ' epi:comparedValues "tier 3 over tier 1" .','each exactly once'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:decidedBy epi:ByTier ;'
         ' epi:comparedValues "tier 3 over tier 1" .','each exactly once'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:winner ex:c5 ; epi:loser ex:c2 ;'
         ' epi:decidedBy epi:ByTier .','among the two claims'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c2 ; epi:winner ex:c1 ; epi:loser ex:c1 ;'
         ' epi:decidedBy epi:ByTier .','other than the epi:loser'),
    ]
    PROFILE_CASES=[
        ('ex:c_nested a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;'
         ' epi:claimedBy ex:c1 .','E1 '),
        ('ex:c2 epi:corroborates ex:c1 .','E2 '),
        ('ex:c1 epi:validFrom "2010-01-01T00:00:00Z"^^xsd:dateTime .','E3 '),
        ('ex:c1 epi:validUntil "2012-01-01T00:00:00Z"^^xsd:dateTime .','E3 '),
        ('ex:c_ax a epi:Claim ; rdf:subject ex:Company ; rdf:predicate rdfs:subClassOf ; rdf:object ex:Legal ;'
         ' epi:claimedBy ex:src_a .','E4 '),
        ('ex:c_ax2 a epi:Claim ; rdf:subject ex:Company ; rdf:predicate rdf:type ; rdf:object owl:Class ;'
         ' epi:claimedBy ex:src_a .','E4 '),
        ('ex:src_a epi:trustedFor ex:Ireland .','E5 '),
        ('ex:src_a epi:trustLevel ex:HighTrust .','E6 '),
        ('ex:src_c a epi:Source ; epi:tier "high" .','E6 '),
        ('ex:c1 epi:supersedes ex:c5 .\nex:c5 epi:supersedes ex:c1 .','validate: epi:supersedes MUST NOT be cyclic'),
        ('ex:c5 epi:supersedes ex:c5 .','validate: epi:supersedes MUST NOT be cyclic'),
        ('ex:c3 epi:supersedes ex:c4 .\nex:c4 epi:supersedes ex:c6 .\nex:c6 a epi:Claim ; epi:supersedes ex:c3 .',
         'validate: epi:supersedes MUST NOT be cyclic'),
        ('ex:ret2 a epi:Retraction ; epi:claimedBy ex:src_a ; epi:retracts ex:ret .','validate: a retraction counts as no claim'),
        ('ex:c3 epi:supersedes ex:ret .','validate: a retraction counts as no claim'),
        ('ex:c_nosource a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;'
         ' epi:claimedBy ex:nobody .','validate: claimedBy'),
        ('ex:ret3 a epi:Retraction ; epi:claimedBy ex:nobody ; epi:retracts ex:c1 .','validate: claimedBy'),
        ('ex:c_blank a epi:Claim ; rdf:subject [] ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;'
         ' epi:claimedBy ex:src_a .','validate: the engine cannot hold'),
        ('ex:c_digits a epi:Claim ; rdf:subject ex:acme ; rdf:predicate ex:registeredIn ; rdf:object ex:Ireland ;'
         ' epi:claimedBy ex:src_a ; epi:confidence 0.1234567 .','validate: more than six decimals'),
        ('ex:policy epi:confidenceMargin 0.0500001 .','validate: more than six decimals'),
        # stored decisions as the engine writes them
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c5 .','result: the engine writes exactly one'),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c5 ; epi:comparedValues "tier 3 over tier 1" .',
         'result: '),
        ('ex:d_1 a epi:Decision ; epi:compares ex:c1 , ex:c5 ; epi:winner ex:c1 ; epi:loser ex:c5 ;'
         ' epi:decidedBy epi:ByTier ; epi:comparedValues "undecided after tier" .','result: '),
    ]
    # An undecided pair: two compared claims, no winner, loser or criterion.
    UNDECIDED=('ex:d_u a epi:Decision ; epi:compares ex:c1 , ex:c5 ;'
               ' epi:comparedValues "undecided after tier, confidence, recency" .')
    # A denied identity claim is the opposite identity claim, and a negated claim of any other kind is
    # a negative assertion: all are executable.
    EXECUTABLE=[
        'ex:c_nsa a epi:Claim ; rdf:subject ex:a ; rdf:predicate owl:sameAs ; rdf:object ex:b ; epi:negated true ; epi:claimedBy ex:src_a .',
        'ex:c_nda a epi:Claim ; rdf:subject ex:a ; rdf:predicate owl:differentFrom ; rdf:object ex:b ; epi:negated true ; epi:claimedBy ex:src_a .',
        'ex:c_nt a epi:Claim ; rdf:subject ex:a ; rdf:predicate rdf:type ; rdf:object ex:B ; epi:negated true ; epi:claimedBy ex:src_a .',
        'ex:c_data a epi:Claim ; rdf:subject ex:a ; rdf:predicate ex:age ; rdf:object 42 ; epi:claimedBy ex:src_a ; epi:confidence 1 .',
        'ex:policy_2 a epi:ResolutionPolicy ; epi:criteria () .',
        'ex:src_free a epi:Source .',
        'ex:src_typed a epi:Source ; epi:tier "3"^^xsd:nonNegativeInteger ; epi:admissionFloor "1"^^xsd:nonNegativeInteger .',
        UNDECIDED,
    ]

    def check(self,cases,shapes):
        for extra,expected in cases:
            with self.subTest(defect=extra.splitlines()[0]):
                found=results(belief(extra),shapes)
                self.assertTrue(any(expected in m for _,m in found),f'{expected!r} not in {found}')

    def test_structural_shapes_fire(self):self.check(self.STRUCTURAL,SHAPES)
    def test_profile_shapes_fire(self):self.check(self.PROFILE_CASES,PROFILE)

    def test_profile_messages_start_with_their_code(self):
        for extra,_ in self.PROFILE_CASES:
            with self.subTest(defect=extra.splitlines()[0]):
                for severity,message in results(belief(extra),PROFILE):
                    if severity=='Violation':
                        self.assertTrue(re.match(r'(E[1-6]|validate:|result:) ',message),message)

    def test_undecided_decision_validates(self):
        found=results(belief(self.UNDECIDED),SHAPES)|results(belief(self.UNDECIDED),PROFILE)
        self.assertEqual(found,set())

    def test_undecided_decision_with_a_winner_fails(self):
        extra=self.UNDECIDED.replace(' ; epi:comparedValues',' ; epi:winner ex:c1 ; epi:comparedValues')
        found={m for _,m in results(belief(extra),SHAPES)}
        self.assertTrue(any('each exactly once' in m for m in found),found)

    def test_decided_decision_without_decided_by_fails(self):
        extra=('ex:d_x a epi:Decision ; epi:compares ex:c1 , ex:c5 ; epi:winner ex:c1 ; epi:loser ex:c5 ;'
               ' epi:comparedValues "tier 3 over no tier" .')
        found={m for _,m in results(belief(extra),SHAPES)}
        self.assertTrue(any('each exactly once' in m for m in found),found)

    def test_executable_constructs_pass_both_shape_sets(self):
        for extra in self.EXECUTABLE:
            with self.subTest(addition=extra.splitlines()[0]):
                self.assertEqual(results(belief(extra),SHAPES),set())
                self.assertEqual(results(belief(extra),PROFILE),set())

EX='https://example.org/kyc/'
EX_NS=Namespace(EX)
KYC=MOD/'examples/kyc.ttl'
GAPS=MOD/'examples/gaps.ttl'

# Task 8's table (crates/hydradl-epistemic/tests/kyc.rs), hard-coded:
# id, source, (subject, predicate, object), confidence, claimedAt (epoch seconds), supersedes, expected status
KYC_CLAIMS=[
    ('regDoi','registry',('acme','dateOfIncorporation','2011-03-04T00:00:00Z'),None,None,[],'Accepted'),
    ('nerDoi','newsA',('acme','dateOfIncorporation','2012-03-04T00:00:00Z'),Decimal('0.8'),None,[],'Rejected'),
    ('newsUk','newsA',('acme','incorporatedIn','UK'),Decimal('0.91'),None,[],'Contested'),
    ('newsCy','newsB',('acme','incorporatedIn','CY'),Decimal('0.88'),None,[],'Contested'),
    ('formAddrOld','onboardingForm',('acme','registeredAddress','1 Old St'),None,1714521600,[],'NotAdmitted'),
    ('formAddrNew','onboardingForm',('acme','registeredAddress','2 New St'),None,1738368000,['formAddrOld'],'Accepted'),
    ('regAddr','registry',('acme','registeredAddress','9 Registry Rd'),None,1685577600,[],'Rejected'),
    ('regActive','registry',('acme','type','ActiveCompany'),None,None,[],'Accepted'),
    ('newsDissolved','newsB',('acme','type','DissolvedCompany'),Decimal('0.7'),None,[],'NotAdmitted'),
    ('nerShell','newsA',('acme','type','ShellCompany'),Decimal('0.4'),None,[],'NotAdmitted'),
    ('sancIvan','sanctionsList',('ivan','type','SanctionedPerson'),None,None,[],'Accepted'),
    ('formCleared','onboardingForm',('acme','type','ClearedEntity'),None,None,[],'Accepted'),
    ('newsControl','newsA',('acme','controlledBy','ivan'),Decimal('0.9'),None,[],'Rejected'),
]
KYC_TIERS={'registry':3,'sanctionsList':3,'onboardingForm':2,'newsA':1,'newsB':1}

def local(term):
    return str(term).removeprefix(EX).removeprefix(str(RDF))

class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kyc=Graph().parse(KYC)
        cls.gaps=Graph().parse(GAPS)

    def test_example_serializations_agree(self):
        for name in ['kyc','gaps']:
            with self.subTest(example=name):
                self.assertTrue(isomorphic(Graph().parse(MOD/f'examples/{name}.ttl'),
                                           Graph().parse(MOD/f'examples/{name}.jsonld')))

    def test_kyc_example_is_executable(self):
        self.assertEqual(results(self.kyc,SHAPES),set())
        self.assertEqual(results(self.kyc,PROFILE),set())

    def test_gaps_example_hits_every_gap(self):
        self.assertEqual(results(self.gaps,SHAPES),set())
        violations=[m for s,m in results(self.gaps,PROFILE) if s=='Violation']
        codes=[re.match(r'E[1-6]\b',m).group() for m in violations if re.match(r'E[1-6]\b',m)]
        self.assertEqual(set(codes),{'E1','E2','E3','E4','E5','E6'})
        self.assertEqual(len(codes),6,'each gap is hit exactly once')
        # the only other violation: a claim attributed to a claim has no source (the same defect as E1)
        others=[m for m in violations if not re.match(r'E[1-6]\b',m)]
        self.assertEqual(len(others),1,others)
        self.assertTrue(others[0].startswith('validate: claimedBy'),others)

    def test_kyc_matches_rust_scenario(self):
        g=self.kyc
        rows=g.query("""PREFIX epi: <https://w3id.org/ldso/epistemic#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?c ?src ?tier ?s ?p ?o ?conf ?at WHERE {
              ?c a epi:Claim ; rdf:subject ?s ; rdf:predicate ?p ; rdf:object ?o ; epi:claimedBy ?src .
              ?src epi:tier ?tier .
              OPTIONAL { ?c epi:confidence ?conf } OPTIONAL { ?c epi:claimedAt ?at } }""")
        found={}
        for r in rows:
            at=int(r.at.toPython().timestamp()) if r.at is not None else None
            conf=Decimal(str(r.conf)) if r.conf is not None else None
            # rdflib normalises a dateTime's lexical form (+00:00 for Z): compare the instant
            obj=r.o.toPython().strftime('%Y-%m-%dT%H:%M:%SZ') if getattr(r.o,'datatype',None)==XSD.dateTime else local(r.o)
            found[local(r.c)]=(local(r.src),int(r.tier),(local(r.s),local(r.p),obj),conf,at)
        self.assertEqual(len(found),13)
        self.assertEqual(set(found),{c[0] for c in KYC_CLAIMS})
        for cid,src,triple,conf,at,_,_ in KYC_CLAIMS:
            with self.subTest(claim=cid):
                self.assertEqual(found[cid],(src,KYC_TIERS[src],triple,conf,at))
        # no claim is denied
        self.assertEqual(list(g.subjects(EPI.negated,None)),[])
        # sources: exactly the five, tiers as in the table, no floor of their own
        self.assertEqual({local(s):int(g.value(s,EPI.tier)) for s in g.subjects(RDF.type,EPI.Source)},KYC_TIERS)
        floors=list(g.subject_objects(EPI.admissionFloor))
        self.assertEqual([local(s) for s,_ in floors],['policy'])
        # the supersede pair
        self.assertEqual({(local(a),local(b)) for a,b in g.subject_objects(EPI.supersedes)},{('formAddrNew','formAddrOld')})
        # the retraction
        retractions=list(g.subjects(RDF.type,EPI.Retraction))
        self.assertEqual([local(r) for r in retractions],['newsBRetract'])
        ret=retractions[0]
        self.assertEqual(local(g.value(ret,EPI.claimedBy)),'newsB')
        self.assertEqual([local(t) for t in g.objects(ret,EPI.retracts)],['newsDissolved'])
        self.assertIsNone(g.value(ret,EPI.claimedAt))
        # the policy: floor 0.5, margin 0.05, default chain, one scoped chain on registeredAddress
        policies=list(g.subjects(RDF.type,EPI.ResolutionPolicy))
        self.assertEqual(len(policies),1)
        pol=policies[0]
        self.assertEqual(Decimal(str(g.value(pol,EPI.admissionFloor))),Decimal('0.5'))
        self.assertEqual(Decimal(str(g.value(pol,EPI.confidenceMargin))),Decimal('0.05'))
        self.assertEqual(list(Collection(g,g.value(pol,EPI.criteria))),[EPI.ByTier,EPI.ByConfidence,EPI.ByRecency])
        chains=list(g.objects(pol,EPI.hasScopedChain))
        self.assertEqual(len(chains),1)
        self.assertEqual(local(g.value(chains[0],EPI.appliesTo)),'registeredAddress')
        self.assertEqual(list(Collection(g,g.value(chains[0],EPI.criteria))),[EPI.ByRecency,EPI.ByTier])

    def test_kyc_stored_assessment(self):
        g=self.kyc
        stored={local(g.value(a,EPI.assesses)):local(g.value(a,EPI.status)).removeprefix(str(EPI)) for a in g.subjects(RDF.type,EPI.Assessment)}
        self.assertEqual(stored,{c[0]:c[6] for c in KYC_CLAIMS})
        conflicts=sorted(sorted(local(c) for c in g.objects(k,EPI.involves)) for k in g.subjects(RDF.type,EPI.Conflict))
        self.assertEqual(conflicts,[['formAddrNew','regAddr'],['formCleared','newsControl','sancIvan'],
                                    ['nerDoi','regDoi'],['newsCy','newsUk']])
        # decision: (compared claims, winner, loser, criterion); conflict 3 is undecided
        decisions={local(d):(sorted(local(c) for c in g.objects(d,EPI.compares)),
                             *(local(g.value(d,p) or '').removeprefix(str(EPI)) or None
                               for p in (EPI.winner,EPI.loser,EPI.decidedBy)))
                   for d in g.subjects(RDF.type,EPI.Decision)}
        self.assertEqual(decisions,{
            'd_address':(['formAddrNew','regAddr'],'formAddrNew','regAddr','ByRecency'),
            'd_cleared_over_control':(['formCleared','newsControl'],'formCleared','newsControl','ByTier'),
            'd_sanctioned_over_cleared':(['formCleared','sancIvan'],'sancIvan','formCleared','ByTier'),
            'd_sanctioned_over_control':(['newsControl','sancIvan'],'sancIvan','newsControl','ByTier'),
            'd_country':(['newsCy','newsUk'],None,None,None),
        })
        self.assertEqual(str(g.value(EX_NS.d_country,EPI.comparedValues)),'undecided after tier, confidence, recency')

    def test_competency_questions_have_answers(self):
        text=(MOD/'competency-questions.md').read_text(encoding='utf-8')
        blocks=re.findall(r'```sparql\n(.*?)```',text,re.S)
        prefixes,queries=blocks[0],blocks[1:]
        against=re.findall(r'^Against: `(.*?)`',text,re.M)
        titles=re.findall(r'^### (CQ-E-\d+)',text,re.M)
        self.assertEqual(titles,[f'CQ-E-{i}' for i in range(1,8)])
        self.assertEqual(len(queries),len(titles))
        self.assertEqual(len(against),len(titles))
        for title,source,query in zip(titles,against,queries):
            with self.subTest(cq=title):
                rows=list(Graph().parse(MOD/source).query(prefixes+query))
                self.assertTrue(rows,f'{title} has no answer in {source}')

class TestSpecPage(unittest.TestCase):
    def test_spec_is_current(self):
        import subprocess,sys,tempfile
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'index.html'
            subprocess.run([sys.executable,str(ROOT/'tools'/'build_epistemic_spec.py'),str(out)],check=True,capture_output=True)
            self.assertEqual(out.read_bytes(),(MOD/'index.html').read_bytes())
        disclaimer=(ROOT/'CLAUDE.md').read_text(encoding='utf-8')
        sentence=re.search(r'^> (This document is not an official W3C Standard.*)$',disclaimer,re.M).group(1)
        self.assertIn(sentence,(MOD/'index.html').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
