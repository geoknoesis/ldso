"""Release guards for LDSO-Deontic: artifacts, examples, and that every shape fires."""
from pathlib import Path
import re
import unittest
from rdflib import Graph
from rdflib.namespace import RDF, SH, SKOS
from rdflib.compare import isomorphic
from rdflib.plugins.sparql import processor as sparql_processor
from rdflib.plugins.sparql.processor import prepareQuery
from pyshacl import validate

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'ldso-deontic'
IMPORTS=['ldso-core','ldso-entities','ldso-semantics','ldso-operations','ldso-deontic']
GAPS={'G2','G3','G4','G5','G7','G8','G9'}
PREFIXES='''@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ops: <https://w3id.org/ldso/operations#> .
@prefix deo: <https://w3id.org/ldso/deontic#> .
@prefix ex: <https://example.org/insurance/> .
'''

def tbox():
    g=Graph()
    for module in IMPORTS:g.parse(ROOT/module/'ontology.ttl')
    return g

def _cache_sparql():
    """pyshacl hands rdflib the text of each SPARQL constraint once per focus node, and rdflib
    parses it every time: parsing was 60-70% of the run, and the pyparsing parser's memory use
    grew until a run ended in a MemoryError. Parse and translate each query once instead; a
    prepared query is reusable with any initial bindings."""
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

TBOX=tbox()
SHAPES=Graph().parse(MOD/'shapes.ttl')
PROFILE=Graph().parse(MOD/'hydradl-profile-shapes.ttl')
INSURANCE=Graph().parse(MOD/'examples/example.ttl')

def results(data,shapes):
    """(severity, message) of every result. The data is merged with its imports, not passed
    as ont_graph: pyshacl does not show ont_graph triples to shapes nested in sh:or."""
    _,report,_=validate(data+TBOX,shacl_graph=shapes,inference='rdfs',advanced=True,allow_warnings=True)
    return {(str(report.value(r,SH.resultSeverity)).split('#')[-1],str(report.value(r,SH.resultMessage)))
            for r in report.subjects(RDF.type,SH.ValidationResult)}

def insurance(extra=''):
    g=Graph()+INSURANCE
    if extra:g.parse(data=PREFIXES+extra,format='turtle')
    return g

class DeonticArtifactTests(unittest.TestCase):
    def test_artifacts_parse(self):
        for f in ['ontology.ttl','shapes.ttl','hydradl-profile-shapes.ttl','alignments.ttl',
                  'examples/example.ttl','examples/example.jsonld','examples/licence.ttl','examples/licence.jsonld']:
            with self.subTest(file=f):Graph().parse(MOD/f)

    def test_shapes_pass_meta_shacl(self):
        for f in ['shapes.ttl','hydradl-profile-shapes.ttl']:
            with self.subTest(file=f):validate(Graph(),shacl_graph=Graph().parse(MOD/f),meta_shacl=True)

    def test_embedded_turtle_examples_parse(self):
        g=Graph().parse(MOD/'ontology.ttl')
        prefixes='\n'.join(f'@prefix {p}: <{iri}> .' for p,iri in g.namespaces())
        prefixes+='\n@prefix ex: <https://example.org/test/> .\n'
        for subject,example in g.subject_objects(SKOS.example):
            with self.subTest(term=str(subject)):Graph().parse(data=prefixes+str(example),format='turtle')

    def test_example_serializations_agree(self):
        for name in ['example','licence']:
            with self.subTest(example=name):
                self.assertTrue(isomorphic(Graph().parse(MOD/f'examples/{name}.ttl'),
                                           Graph().parse(MOD/f'examples/{name}.jsonld')))

    def test_insurance_example_is_executable(self):
        self.assertEqual(results(insurance(),SHAPES),set())
        self.assertEqual(results(insurance(),PROFILE),set())

    def test_licence_example_is_well_formed_and_hits_every_gap(self):
        data=Graph().parse(MOD/'examples/licence.ttl')
        self.assertEqual(results(data,SHAPES),set())
        violations=[m for s,m in results(data,PROFILE) if s=='Violation']
        gaps={re.match(r'G\d+',m).group() for m in violations if re.match(r'G\d+\b',m)}
        self.assertEqual(gaps,GAPS)
        # every violation is a gap: the duty precondition, the comparisons with stated values and
        # the chain ending in a permission are executable
        self.assertTrue(all(re.match(r'G\d+\b',m) for m in violations),violations)
        self.assertTrue(any(m.startswith('G4 (part-of and set operands):') for m in violations))

    def test_competency_questions_have_answers(self):
        text=(MOD/'competency-questions.md').read_text(encoding='utf-8')
        blocks=re.findall(r'```sparql\n(.*?)```',text,re.S)
        prefixes,queries=blocks[0],blocks[1:]
        against=re.findall(r'^Against: `(.*?)`',text,re.M)
        titles=re.findall(r'^### (CQ-D-\d+)',text,re.M)
        self.assertEqual(len(queries),len(titles))
        self.assertEqual(len(against),len(titles))
        for title,source,query in zip(titles,against,queries):
            with self.subTest(cq=title):
                rows=list(Graph().parse(MOD/source).query(prefixes+query))
                self.assertTrue(rows,f'{title} has no answer in {source}')

class ShapeFiresTests(unittest.TestCase):
    """Each case adds one defect to the executable example; the named shape must report it."""
    STRUCTURAL=[
        ('ex:r_pay deo:strength deo:StrictStrength .','exactly one deo:strength'),
        ('ex:r_notify deo:activatedBy ex:c_approved .','own positive conditions'),
        ('ex:chain_pay deo:hasChainElement [ a deo:ChainElement ; deo:position 4 ; deo:statement ex:obl_notify ] .','without gaps'),
        ('ex:perm_x a deo:Permission ; deo:bearer ex:var_insurer ; deo:action ex:act_pay .\n'
         'ex:chain_pay deo:hasChainElement [ a deo:ChainElement ; deo:position 3 ; deo:statement ex:obl_notify ] .\n'
         'ex:chain_pay deo:hasChainElement [ a deo:ChainElement ; deo:position 2 ; deo:statement ex:perm_x ] .','last element'),
        ('ex:ov_back a deo:Override ; deo:overriding ex:r_flood_exclusion ; deo:overridden ex:r_flood_endorsement ; deo:overrideBasis deo:LexPosterior .','cycle'),
        ('ex:ov_self a deo:Override ; deo:overriding ex:r_pay ; deo:overridden ex:r_pay ; deo:overrideBasis deo:LexPosterior .','two different rules'),
        ('ex:ov_nobasis a deo:Override ; deo:overriding ex:r_notify ; deo:overridden ex:r_access .','legal basis'),
        ('ex:ov_clause a deo:Override ; deo:overriding ex:r_notify ; deo:overridden ex:r_access ; deo:overrideBasis deo:ExplicitClause .','SHOULD cite that clause'),
        ('ex:policy_2026 deo:inheritsFrom ex:policy_2026 .','MUST NOT be cyclic'),
        ('ex:act_pay deo:hasArgument [ a deo:Argument ; deo:argumentIndex 2 ; deo:argumentValue ex:var_claim ] .','run 0..n-1'),
        ('ex:alt a deo:Alternatives ; deo:alternative ex:r_pay , ex:r_notify ; deo:adopted ex:r_access .','one of the set'),
        ('ex:rep_x a deo:Reparation ; deo:repairs ex:obl_notify ; deo:imposes ex:obl_compensate ; deo:reparationKind deo:Remedy .','A Remedy answers'),
        ('ex:rep_y a deo:Reparation ; deo:repairs ex:right_access ; deo:imposes ex:obl_compensate .','repair exactly one Obligation or Prohibition'),
        ('ex:c_bad a deo:NormCondition ; deo:aboutStatement ex:right_access ; deo:normState deo:Violated .','cannot be violated'),
        ('ex:c_loop a deo:LogicalCondition ; deo:logicalOperator deo:Or ; deo:operand ex:c_loop , ex:c_flood .','contain itself'),
        ('ex:c_seq a deo:LogicalCondition ; deo:logicalOperator deo:AndSequence ; deo:operand ex:c_flood , ex:c_covered .','SequencedOperand'),
        ('ex:c_cmp a deo:ComparisonCondition ; deo:leftOperand ex:amount ; deo:operator ops:LessThan .','exactly one of deo:rightOperand'),
        ('ex:c_cmp2 a deo:ComparisonCondition ; deo:leftOperand ex:amount ; deo:operator ex:near ; deo:rightOperand 3 .','ops:Comparator or a deo:SetOperator'),
        ('ex:obl_pay deo:bearer "the insurer" .','MUST be an ent:NamedEntity'),
        ('ex:r_c a deo:ConstitutiveRule ; deo:strength deo:StrictStrength ; deo:hasConsequent ex:obl_pay ; deo:concludes ex:c_approved .','no deontic formula'),
        ('ex:r_untyped a deo:Rule ; deo:strength deo:StrictStrength .','PrescriptiveRule or deo:ConstitutiveRule'),
        ('ex:obl_notify deo:deonticContent ex:right_access .','not both'),
        # values: signatures
        ('ex:policy_2026 deo:declaresSignature [ a deo:PredicateSignature ; deo:signaturePredicate ex:bad ;'
         ' deo:keyLength 3 ; deo:isQuantity false ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ] .','MUST NOT exceed its number of argument slots'),
        ('ex:policy_2026 deo:declaresSignature [ a deo:PredicateSignature ; deo:signaturePredicate ex:bad ;'
         ' deo:keyLength 1 ; deo:isQuantity true ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
         ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Number ] ,'
         ' [ a deo:ArgumentSlot ; deo:argumentIndex 2 ; deo:valueType deo:Number ] ] .','exactly one argument slot after its key'),
        ('ex:sig_claim_amount deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 3 ; deo:valueType deo:Number ] .','slot indexes MUST be unique'),
        ('ex:policy_2026 deo:declaresSignature [ a deo:PredicateSignature ; deo:signaturePredicate ex:bad ; deo:keyLength 1 ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType ex:Money ] ] .','deo:valueType'),
        ('ex:policy_2026 deo:declaresSignature [ a deo:PredicateSignature ; deo:signaturePredicate ex:bad ; deo:keyLength 0 ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Number ] ] .','whether it is a quantity'),
        ('ex:policy_2026 deo:declaresSignature [ a deo:PredicateSignature ; deo:signaturePredicate ex:claimAmount ;'
         ' deo:keyLength 1 ; deo:isQuantity false ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
         ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Number ] ] .','at most one signature'),
        # the range types ex:obl_pay a deo:PredicateSignature, whose own shape reports it
        ('ex:policy_2026 deo:declaresSignature ex:obl_pay .','exactly one deo:signaturePredicate'),
        ('ex:policy_2026 deo:utcOffset "UTC-5" .','deo:utcOffset'),
        ('ex:policy_2026 deo:utcOffset 90000 .','deo:utcOffset'),
        # values: expressions
        ('ex:expr_fee_raw deo:hasOperand [ a deo:ExpressionOperand ; deo:position 4 ; deo:operandValue 1 ] .','operand positions MUST be unique and run 1..n'),
        ('ex:expr_x a deo:Expression ; deo:operation deo:Add ;'
         ' deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue 1 ] .','as many operands as its operation'),
        ('ex:expr_x a deo:Expression ; deo:operation deo:Now ;'
         ' deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue 1 ] .','as many operands as its operation'),
        ('ex:expr_x a deo:Expression ; deo:operation ex:power ;'
         ' deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue 2 ] .','exactly one deo:operation'),
        ('ex:expr_x a deo:Expression ; deo:operation deo:Round ; deo:places 2 ;'
         ' deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue 1.5 ] .','both be given on a deo:Round'),
        ('ex:expr_fee_raw deo:places 2 ; deo:roundingMode deo:HalfUp .','and only there'),
        ('ex:expr_fee deo:roundingMode ex:Bankers .','deo:RoundingModeScheme'),
        ('ex:expr_fee deo:places -1 .','deo:places MUST be'),
        ('ex:expr_loop a deo:Expression ; deo:operation deo:Neg ;'
         ' deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ; deo:operandValue ex:expr_loop ] .','expression MUST NOT contain itself'),
        ('ex:expr_x a deo:Expression ; deo:operation deo:Abs ; deo:hasOperand [ a deo:ExpressionOperand ; deo:position 1 ] .','exactly one deo:operandValue'),
        ('ex:expr_x a deo:Expression ; deo:operation deo:Abs ; deo:hasOperand [ a deo:ExpressionOperand ; deo:operandValue 1 ] .','exactly one deo:position'),
        # the range types ex:var_amount a deo:ExpressionOperand, whose own shape reports it
        ('ex:expr_x a deo:Expression ; deo:operation deo:Abs ; deo:hasOperand ex:var_amount .','ExpressionOperand MUST have exactly one deo:position'),
        # values: assignments and aggregates
        ('ex:c_let a deo:AssignmentCondition ; deo:assigns ex:var_fee .','exactly one deo:expression'),
        ('ex:c_let a deo:AssignmentCondition ; deo:assigns ex:regulator ; deo:expression 0 .','assign exactly one deo:Variable'),
        ('ex:c_fee deo:negated true .','cannot be negated'),
        ('ex:c_sum a deo:AggregateCondition ; deo:aggregateOperator deo:Sum ; deo:assigns ex:var_fee ; deo:expression ex:var_amount .','at least one deo:pattern'),
        ('ex:c_sum a deo:AggregateCondition ; deo:aggregateOperator deo:Sum ; deo:assigns ex:var_fee ; deo:expression ex:var_amount ;'
         ' deo:pattern ex:c_pay_violated .','each a fact, class or property condition'),
        ('ex:c_sum a deo:AggregateCondition ; deo:aggregateOperator deo:Average ; deo:assigns ex:var_fee ; deo:expression ex:var_amount ;'
         ' deo:pattern ex:c_claim_amount .','Sum, Count, Min or Max'),
        ('ex:c_sum a deo:AggregateCondition ; deo:aggregateOperator deo:Count ; deo:assigns ex:var_fee ; deo:pattern ex:c_claim_amount .','the value of each solution'),
        # values: fulfilment comparator and comparisons
        ('ex:obl_late_fee deo:fulfilmentComparator deo:IsPartOf .','deo:fulfilmentComparator MUST be'),
        ('ex:c_any a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator deo:IsAnyOf .','exactly one of deo:rightOperand'),
        ('ex:c_two a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:LessThan ; deo:rightOperand 1 , 2 .','Only deo:IsAnyOf and deo:IsNoneOf compare with a set'),
        ('ex:c_any a deo:ComparisonCondition ; deo:leftOperand ex:claimKind ; deo:operator deo:IsNoneOf ; deo:rightOperand ex:flood .','MUST be a literal value'),
        ('ex:c_isa a deo:ComparisonCondition ; deo:leftOperand ex:claimKind ; deo:operator deo:IsA ; deo:rightOperand "flood" .','a class IRI with deo:IsA'),
    ]
    PROFILE_CASES=[
        ('ex:r_flood_exclusion deo:hasConsequent ex:chain_pay .','DefeaterChain'),
        ('ex:var_other a deo:Variable .\nex:obl_notify deo:auxiliaryParty ex:var_other .\n'
         'ex:r_notify deo:hasCondition [ a deo:FactCondition ; deo:negated true ; deo:predicate ex:blocked ;'
         ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_holder ] ] .','Unsafe'),
        ('ex:policy_2026 deo:declaresComplete ex:latePayment .','ClosedHead'),
        ('ex:ov_out a deo:Override ; deo:overriding ex:r_elsewhere ; deo:overridden ex:r_pay ; deo:overrideBasis deo:LexSuperior .\n'
         'ex:r_elsewhere a deo:PrescriptiveRule ; deo:strength deo:StrictStrength ; deo:hasConsequent ex:obl_notify .\n'
         'ex:policy_2026 deo:hasOverride ex:ov_out .','UnknownRule'),
        ('ex:dl_30_days ops:deadlineDate "2027-01-01"^^xsd:date .','not both'),
        ('ex:dl_x a ops:Deadline ; ops:deadlineDuration "-P3D"^^xsd:duration .\nex:obl_notify deo:deadline ex:dl_x .','G8'),
        ('ex:proh_y a deo:Prohibition ; deo:bearer ex:var_insurer ; deo:action [ a deo:Action ; deo:predicate ex:paid ; deo:negated true ;'
         ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ] .','state a deo:Obligation instead'),
        ('ex:rep_mid a deo:Reparation ; deo:repairs ex:obl_pay ; deo:imposes ex:obl_compensate .','last element'),
        ('ex:obl_never a deo:Obligation ; deo:bearer ex:var_insurer ; deo:action ex:act_notify .\n'
         'ex:rep_never a deo:Reparation ; deo:repairs ex:obl_never ; deo:imposes ex:obl_compensate .','never applies'),
        ('ex:c_never a deo:NormCondition ; deo:aboutStatement ex:obl_never ; deo:normState deo:InForce .\n'
         'ex:obl_never a deo:Obligation ; deo:bearer ex:var_insurer ; deo:action ex:act_notify .','never established'),
        ('ex:lit_x a deo:Literal ; deo:predicate ex:paid .','different numbers of arguments'),
        ('ex:policy_2026 deo:policyType deo:Offer .','An Offer'),
        ('ex:obl_pay deo:bearer ex:var_holder .','exactly one bearer'),
        ('ex:obl_grant a deo:Obligation ; deo:bearer ex:var_insurer ; deo:deonticContent ex:right_access .\n'
         'ex:r_notify deo:hasConsequent ex:obl_grant .','G9'),
        ('ex:policy_2026 deo:policyType deo:Request .','Offer or Request'),
        # values
        ('ex:r_notify deo:hasCondition [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ;'
         ' deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',"cannot place the comparison's key"),
        ('ex:r_pay deo:hasCondition [ a deo:ComparisonCondition ; deo:leftOperand ex:claimedValue ;'
         ' deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .','has no signature with one key argument'),
        ('ex:c_part a deo:ComparisonCondition ; deo:leftOperand ex:location ; deo:operator deo:IsPartOf ; deo:rightOperand ex:eu .',
         'G4 (part-of and set operands)'),
        ('ex:c_ref a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:LessThan ;'
         ' deo:rightOperandReference ex:current_cap .','G4 (part-of and set operands)'),
        ('ex:r_notify deo:hasCondition [ a deo:FactCondition ; deo:predicate ex:claimAmount ;'
         ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ] .','NormError::Arity'),
        ('ex:r_notify deo:hasCondition [ a deo:FactCondition ; deo:negated true ; deo:predicate ex:claimAmount ;'
         ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ,'
         ' [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:var_amount ] ] .','NormError::NegatedQuantity'),
        ('ex:r_notify deo:hasCondition [ a deo:FactCondition ; deo:predicate ex:claimAmount ;'
         ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ,'
         ' [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:regulator ] ] .','an individual where the predicate'),
        ('ex:obl_pay deo:fulfilmentComparator ops:GreaterThan .','exactly one value argument'),
        ('ex:sig_ind a deo:PredicateSignature ; deo:signaturePredicate ex:notified ; deo:keyLength 1 ; deo:isQuantity false ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
         ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Individual ] .\n'
         'ex:policy_2026 deo:declaresSignature ex:sig_ind .\n'
         'ex:act_notify deo:hasArgument [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:var_insurer ] .\n'
         'ex:obl_notify deo:fulfilmentComparator ops:GreaterThanOrEqual .','(not an individual)'),
        ('ex:c_status a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:LessThan ;'
         ' deo:rightOperand 3 ; deo:status 2 .','G4 (part-of and set operands): HydraDL does not compare an ODRL status'),
        ('ex:r_pay deo:hasCondition [ a deo:ClassCondition ; deo:classExpression ex:Insurer ; deo:subject ex:var_insurer ] ,'
         ' [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',
         'the key is ambiguous'),
        ('ex:sig_text a deo:PredicateSignature ; deo:signaturePredicate ex:notified ; deo:keyLength 1 ; deo:isQuantity false ;'
         ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
         ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Text ] .\n'
         'ex:policy_2026 deo:declaresSignature ex:sig_text .\n'
         'ex:act_notify deo:hasArgument [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:var_fee ] .\n'
         'ex:r_notify deo:hasCondition ex:c_late_fee_amount .\n'
         'ex:obl_notify deo:fulfilmentComparator ops:GreaterThanOrEqual .','that value is a text'),
        ('ex:r_late_fee_amount deo:hasCondition [ a deo:ClassCondition ; deo:classExpression ex:CoveredClaim ; deo:subject ex:var_fee ] .',
         'must be fresh'),
        ('ex:var_y a deo:Variable .\nex:var_z a deo:Variable .\n'
         'ex:r_late_fee_amount deo:hasCondition [ a deo:AssignmentCondition ; deo:assigns ex:var_y ; deo:expression ex:var_z ] .','NormError::Unsafe'),
        ('ex:var_y a deo:Variable .\nex:var_z a deo:Variable .\n'
         'ex:r_late_fee_amount deo:hasCondition [ a deo:AggregateCondition ; deo:aggregateOperator deo:Sum ; deo:assigns ex:var_y ;'
         ' deo:expression ex:var_z ; deo:pattern ex:c_claim_amount ] .','of an aggregate is bound neither'),
        ('ex:perm_x a deo:Permission ; deo:bearer ex:var_insurer ; deo:action ex:act_access .\n'
         'ex:rep_p a deo:Reparation ; deo:repairs ex:obl_notify ; deo:imposes ex:perm_x .','the only reparation'),
        ('ex:chain_pay deo:hasChainElement [ a deo:ChainElement ; deo:position 3 ; deo:statement ex:right_access ] .',
         'which a reparation chain cannot hold'),
        ('ex:rep_r a deo:Reparation ; deo:repairs ex:obl_late_fee ; deo:imposes ex:right_access .','which a reparation (a chain element) cannot impose'),
    ]
    # Constructs outside the profile until the engine gained Fulfilled conditions, chains ending in a
    # permission and comparisons with values (G1, G6, G4): each must now pass both shape sets.
    EXECUTABLE=[
        # a permission requiring a duty, a Fulfilled condition, a reparation ending a chain in a permission
        'ex:perm_close a deo:Permission ; deo:bearer ex:var_insurer ; deo:action ex:act_compensate ; deo:requiresDuty ex:obl_notify .\n'
        'ex:rep_close a deo:Reparation ; deo:repairs ex:obl_late_fee ; deo:imposes ex:perm_close .\n'
        'ex:c_notified a deo:NormCondition ; deo:aboutStatement ex:obl_notify ; deo:normState deo:Fulfilled .\n'
        'ex:r_after_notice a deo:PrescriptiveRule ; deo:strength deo:DefeasibleStrength ;'
        ' deo:hasCondition ex:c_filed , ex:c_insurer_of , ex:c_notified ; deo:hasConsequent ex:perm_close ;'
        ' deo:formalizes ex:Oblig_Clause11 .\n'
        'ex:policy_2026 deo:hasRule ex:r_after_notice .',
        # a comparison keyed by the subject of the rule's only positive class condition (a negated one does not count)
        'ex:r_pay deo:hasCondition [ a deo:ClassCondition ; deo:negated true ; deo:classExpression ex:Insurer ; deo:subject ex:var_insurer ] ,'
        ' [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',
        # a comparison with a stated value, keyed by the subject of the rule's class condition
        'ex:r_pay deo:hasCondition [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ;'
        ' deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',
        # membership in a stated set (In), and a class test (IsA)
        'ex:sig_kind a deo:PredicateSignature ; deo:signaturePredicate ex:claimKind ; deo:keyLength 1 ; deo:isQuantity true ;'
        ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
        ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Text ] .\n'
        'ex:policy_2026 deo:declaresSignature ex:sig_kind .\n'
        'ex:r_pay deo:hasCondition [ a deo:ComparisonCondition ; deo:leftOperand ex:claimKind ;'
        ' deo:operator deo:IsNoneOf ; deo:rightOperand "fraud" , "test" ] ,'
        ' [ a deo:ComparisonCondition ; deo:leftOperand ex:insuredItem ; deo:operator deo:IsA ; deo:rightOperand ex:CoveredClaim ] .',
        # an aggregate over a pattern: the total of the late-fee payments of each covered claim. ?claim
        # is bound by the rule's class condition, so it is the group key; ?m is local to the pattern.
        'ex:var_n a deo:Variable .\nex:var_m a deo:Variable .\n'
        'ex:sig_total a deo:PredicateSignature ; deo:signaturePredicate ex:feePaidTotal ; deo:keyLength 1 ; deo:isQuantity true ;'
        ' deo:hasArgumentSlot [ a deo:ArgumentSlot ; deo:argumentIndex 0 ; deo:valueType deo:Individual ] ,'
        ' [ a deo:ArgumentSlot ; deo:argumentIndex 1 ; deo:valueType deo:Number ] .\n'
        'ex:policy_2026 deo:declaresSignature ex:sig_total ; deo:hasRule ex:r_total .\n'
        'ex:r_total a deo:ConstitutiveRule ; deo:strength deo:StrictStrength ; deo:formalizes ex:Oblig_Clause8 ;'
        ' deo:hasCondition ex:c_covered , [ a deo:AggregateCondition ; deo:aggregateOperator deo:Sum ; deo:assigns ex:var_n ;'
        ' deo:expression ex:var_m ; deo:pattern [ a deo:FactCondition ; deo:predicate ex:paidLateFee ;'
        ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ,'
        ' [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:var_m ] ] ] ;'
        ' deo:concludes [ a deo:Literal ; deo:predicate ex:feePaidTotal ;'
        ' deo:hasArgument [ a deo:Argument ; deo:argumentIndex 0 ; deo:argumentValue ex:var_claim ] ,'
        ' [ a deo:Argument ; deo:argumentIndex 1 ; deo:argumentValue ex:var_n ] ] .',
    ]

    def check(self,cases,shapes):
        for extra,expected in cases:
            with self.subTest(defect=extra.splitlines()[0]):
                found=results(insurance(extra),shapes)
                self.assertTrue(any(expected in m for _,m in found),f'{expected!r} not in {found}')

    def test_structural_shapes_fire(self):self.check(self.STRUCTURAL,SHAPES)
    def test_profile_shapes_fire(self):self.check(self.PROFILE_CASES,PROFILE)

    def test_unplaceable_comparison_key_is_a_violation(self):
        # no key (no target, no positive class condition), and an ambiguous key (two class subjects)
        for extra in ['ex:r_notify deo:hasCondition [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ;'
                      ' deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',
                      'ex:r_notify deo:hasCondition [ a deo:ClassCondition ; deo:negated true ; deo:classExpression ex:Insurer ;'
                      ' deo:subject ex:var_insurer ] , [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ;'
                      ' deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .',
                      'ex:r_pay deo:hasCondition [ a deo:ClassCondition ; deo:classExpression ex:Insurer ; deo:subject ex:var_insurer ] ,'
                      ' [ a deo:ComparisonCondition ; deo:leftOperand ex:claimAmount ; deo:operator ops:GreaterThan ; deo:rightOperand 0 ] .']:
            with self.subTest(addition=extra):
                found=results(insurance(extra),PROFILE)
                self.assertTrue(any(s=='Violation' and "cannot place the comparison's key" in m for s,m in found),found)

    def test_former_gaps_are_executable(self):
        for extra in self.EXECUTABLE:
            with self.subTest(addition=extra.splitlines()[0]):
                self.assertEqual(results(insurance(extra),SHAPES),set())
                self.assertEqual(results(insurance(extra),PROFILE),set())

if __name__=='__main__':unittest.main()
