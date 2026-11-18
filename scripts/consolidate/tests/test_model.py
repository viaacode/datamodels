"""Small end-to-end checks of migration fidelity and deliberate corruption."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from rdflib import BNode, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
from rdflib.compare import isomorphic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from merge_model import build, build_run, main as merge_main, readable_turtle
from model_common import ModelError, SH, SKOS, document_uri, external_reference, load_outputs, naming, parse_turtle, read_config, term_data, union
from verify_model import main as verify_main, verify_graphs, verify_run

EX = Namespace('https://example.test/')
HA = Namespace('https://data.hetarchief.be/ns/')
PREMIS = Namespace('http://www.loc.gov/premis/rdf/v3/')
ODRL = Namespace('http://www.w3.org/ns/odrl/2/')
VOCABULARY = '''@prefix ex: <https://example.test/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

ex:Person a rdfs:Class ;
    rdfs:label "Person"@en, "Persoon"@nl .

ex:Work a rdfs:Class .

ex:creates a rdf:Property ;
    rdfs:domain ex:Person ;
    rdfs:range ex:Work ;
    owl:inverseOf ex:isCreatedBy .

ex:isCreatedBy a rdf:Property ;
    owl:inverseOf ex:creates .
'''
SHAPES = '''@base <https://example.test/shapes> .
@prefix ex: <https://example.test/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<#PersonShape> a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        a sh:PropertyShape ;
        sh:path ex:creates ;
        sh:name "contextual work count"@en, "aantal werken"@nl ;
        sh:minCount 1 ;
        sh:maxCount 3 ;
        sh:or (
            [ sh:class ex:Work ]
            [ sh:datatype xsd:string ]
        )
    ] ;
    sh:property [
        a sh:PropertyShape ;
        sh:path ex:creates ;
        sh:maxCount 10
    ] .

<#WorkShape> a sh:NodeShape ;
    sh:targetClass ex:Work ;
    sh:property [
        a sh:PropertyShape ;
        sh:path ex:creates ;
        sh:name "contextual work count"@en, "aantal werken"@nl ;
        sh:minCount 1 ;
        sh:maxCount 3 ;
        sh:or (
            [ sh:class ex:Work ]
            [ sh:datatype xsd:string ]
        )
    ] ;
    sh:property [
        a sh:PropertyShape ;
        sh:path ex:creates ;
        sh:maxCount 10
    ] .
'''


class ModelMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'core').mkdir()
        (self.root / 'core/vocabulary.rdfs.ttl').write_text(VOCABULARY)
        (self.root / 'core/shapes.shacl.ttl').write_text(SHAPES)
        self.config = json.loads((Path(__file__).resolve().parents[1] / 'model-config.json').read_text())
        self.config.update(core=['core/vocabulary.rdfs.ttl', 'core/shapes.shacl.ttl'],
                           drafts=[], external=[], local_concepts=[], supplemental=[], missing_definitions={}, merges=[],
                           consolidate_collisions=False, prune_unused_superclasses=False)
        self.config['naming']['overrides'] = {}
        self.config['naming']['property_names'] = {str(EX.creates): 'creates', str(EX.isCreatedBy): 'isCreatedBy'}
        self.config['naming']['inverse_pairs'] = [{'direct': str(EX.creates), 'reverse': str(EX.isCreatedBy),
                                                  'direct_name': 'creates', 'reverse_name': 'isCreatedBy'}]
        self.manifest = build(self.config, self.root)
        self.outputs = self.read_outputs()

    def read_outputs(self, manifest=None):
        config = dict(self.config, outputs=(manifest or self.manifest)['outputs'])
        return load_outputs(config, self.root)

    def verify(self, manifest=None):
        return verify_graphs(self.config, self.root, manifest or self.manifest, self.outputs)

    def add_consolidation_fixture(self):
        self.config['consolidate_collisions'] = True
        vocabulary = self.root / 'core/vocabulary.rdfs.ttl'
        vocabulary.write_text(vocabulary.read_text() + f'''
@prefix ebu: <http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix premis: <{PREMIS}> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ebu:Agent a rdfs:Class ; rdfs:label "EBU agent"@en ;
    rdfs:comment "EBU definition"@en ; rdfs:seeAlso foaf:Agent .
foaf:Agent a rdfs:Class ; rdfs:label "FOAF agent"@en, "Agent"@nl ;
    rdfs:comment "FOAF definition"@en .
ebu:name a rdf:Property ; rdfs:domain ebu:Agent ; rdfs:range xsd:string .
foaf:name a rdf:Property ; rdfs:domain foaf:Agent ; rdfs:range xsd:string .
premis:Agent a rdfs:Class ; rdfs:label "PREMIS agent"@en .
premis:name a rdf:Property ; rdfs:label "PREMIS name"@en ; rdfs:domain premis:Agent .
''')
        shapes = self.root / 'core/shapes.shacl.ttl'
        shapes.write_text(shapes.read_text() + '''
@prefix ebu: <http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<#AgentShape> a sh:NodeShape ; sh:targetClass ebu:Agent, foaf:Agent ;
    sh:property [ sh:path ebu:name ; sh:minCount 1 ],
                [ sh:path foaf:name ; sh:maxCount 2 ] ;
    sh:sparql [ sh:message "check agent"@en ;
        sh:select "SELECT $this WHERE { $this a ebu:Agent ; foaf:name ?name . }" ] .
''')
        self.manifest = build(self.config, self.root)
        self.outputs = self.read_outputs()

    def test_colliding_classes_and_properties_consolidate_with_original_links(self):
        self.add_consolidation_fixture()
        ebu = Namespace('http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#')
        foaf = Namespace('http://xmlns.com/foaf/0.1/')
        graph = self.outputs['rdfs']
        for original, target in [(ebu.Agent, HA.Agent), (foaf.Agent, HA.Agent),
                                 (ebu.name, HA.hasName), (foaf.name, HA.hasName)]:
            self.assertEqual(self.manifest['terms'][str(original)]['target'], str(target))
            self.assertIn((target, RDFS.seeAlso, original), graph)
            self.assertFalse(any(graph.triples((original, None, None))))
        self.assertEqual(set(graph.objects(HA.Agent, RDFS.comment)),
                         {Literal('EBU definition', lang='en'), Literal('FOAF definition', lang='en')})
        self.assertIn((HA.Agent, RDFS.label, Literal('Agent', lang='nl')), graph)
        self.assertIn((HA.hasName, RDFS.domain, HA.Agent), graph)
        self.assertEqual(len(self.manifest['consolidations']), 2)
        shapes = self.outputs['shacl']
        self.assertEqual(set(shapes.objects(HA.AgentShape, SH.targetClass)), {HA.Agent})
        self.assertEqual(len(set(shapes.subjects(SH.path, HA.hasName))), 2)
        query = str(next(shapes.objects(None, SH.select)))
        self.assertIn(f'<{HA.Agent}>', query)
        self.assertIn(f'<{HA.hasName}>', query)
        self.verify()
        before = {p: (self.root / p).read_bytes() for p in self.config['outputs'].values()}
        build(self.config, self.root)
        self.assertEqual(before, {p: (self.root / p).read_bytes() for p in before})

    def test_consolidation_excludes_retained_namespaces(self):
        self.add_consolidation_fixture()
        for original in (PREMIS.Agent, PREMIS.name):
            self.assertEqual(self.manifest['terms'][str(original)]['target'], str(original))
            self.assertFalse(any(self.outputs['rdfs'].triples((None, RDFS.seeAlso, original))))
        self.assertIn((PREMIS.Agent, RDFS.label, Literal('PREMIS agent', lang='en')), self.outputs['rdfs'])
        self.assertTrue(all(str(PREMIS.Agent) not in group['uris'] for group in self.manifest['consolidations']))
        self.verify()

    def test_future_collision_consolidates_without_config_changes(self):
        self.add_consolidation_fixture()
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '\n<https://other.test/Agent> a rdfs:Class .\n')
        manifest = build(self.config, self.root)
        self.assertEqual(manifest['terms']['https://other.test/Agent']['target'], str(HA.Agent))
        group = next(g for g in manifest['consolidations'] if g['target'] == str(HA.Agent))
        self.assertEqual(len(group['uris']), 3)

    def test_consolidation_does_not_allow_shape_or_mixed_kind_collisions(self):
        self.config['consolidate_collisions'] = True
        self.config['naming']['overrides']['https://example.test/shapes#WorkShape'] = {'name': 'PersonShape'}
        with self.assertRaisesRegex(ModelError, 'Naming collision'):
            build(self.config, self.root)
        self.config['naming']['overrides'] = {str(EX.Work): {'name': 'creates'}}
        self.config['naming']['class_case'] = 'lowerCamelCase'
        with self.assertRaisesRegex(ModelError, 'Naming collision'):
            build(self.config, self.root)

    def test_consolidation_rejects_incompatible_labels_and_disjoint_classes(self):
        self.add_consolidation_fixture()
        self.config['naming']['overrides']['http://xmlns.com/foaf/0.1/Agent'] = {'label': 'different agent'}
        with self.assertRaisesRegex(ModelError, 'Incompatible English labels'):
            build(self.config, self.root)
        self.config['naming']['overrides'] = {}
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '\nebu:Agent owl:disjointWith foaf:Agent .\n')
        with self.assertRaisesRegex(ModelError, 'disjoint with itself'):
            build(self.config, self.root)

    def test_verifier_rejects_forged_consolidations_and_missing_original_links(self):
        self.add_consolidation_fixture()
        forged = deepcopy(self.manifest)
        forged['consolidations'] = []
        with self.assertRaisesRegex(ModelError, 'Map consolidations differ'):
            self.verify(forged)
        original = URIRef('http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#Agent')
        self.outputs['rdfs'].remove((HA.Agent, RDFS.seeAlso, original))
        with self.assertRaisesRegex(ModelError, 'lost/changed'):
            self.verify()
        forged = deepcopy(self.manifest)
        forged['changes'] = [c for c in forged['changes'] if not (
            c['reason'] == 'original term reference' and c['after'][2] == {'uri': str(original)})]
        with self.assertRaisesRegex(ModelError, 'Missing original term reference'):
            self.verify(forged)

    def add_retained_fixture(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'''
@prefix premis: <{PREMIS}> .
@prefix odrl: <{ODRL}> .
ex:Work rdfs:subClassOf premis:File ;
    odrl:hasPolicy odrl:Policy ;
    ex:stamp "01"^^premis:FileFormat ;
    ex:vocabulary premis: .
ex:stamp a rdf:Property .
ex:vocabulary a rdf:Property .
''')
        shapes = self.root / 'core/shapes.shacl.ttl'
        shapes.write_text(shapes.read_text() + f'''
@prefix premis: <{PREMIS}> .
@prefix odrl: <{ODRL}> .
<#PersonShape> sh:node odrl:PolicyShape ;
    sh:sparql [ sh:message "check policy"@en ;
        sh:select "SELECT $this WHERE {{ $this odrl:hasPolicy ?policy . ?policy a <{PREMIS}File> . $this ex:creates ?work . }}" ] .
''')
        (self.root / 'retained.rdfs.ttl').write_text(f'''
@prefix ex: <{EX}> .
@prefix premis: <{PREMIS}> .
@prefix odrl: <{ODRL}> .
@prefix rdf: <{RDF}> .
@prefix rdfs: <{RDFS}> .
@prefix owl: <{OWL}> .
@prefix sh: <{SH}> .
@prefix vann: <http://purl.org/vocab/vann/> .
vann:preferredNamespacePrefix a rdf:Property .
premis:File a rdfs:Class ;
    rdfs:label "PREMIS file"@en, "File"@en, "Bestand"@nl ;
    rdfs:isDefinedBy premis: ;
    rdfs:subClassOf ex:Parent ;
    premis:hasPart premis:File .
premis:hasPart a rdf:Property ; owl:inverseOf premis:isPartOf .
premis:isPartOf a rdf:Property ; owl:inverseOf premis:hasPart .
premis:FileFormat a rdfs:Datatype .
premis: a owl:Ontology ;
    rdfs:label "PREMIS vocabulary"@en ;
    vann:preferredNamespacePrefix "premis" ;
    owl:imports odrl: .
odrl:hasPolicy a rdf:Property ; rdfs:range odrl:Policy .
odrl:Policy a rdfs:Class ; rdfs:label "Policy"@en .
odrl:PolicyShape a sh:NodeShape ; sh:targetClass odrl:Policy ; sh:name "Source policy shape"@en .
odrl:Unused a rdfs:Class .
ex:Parent a rdfs:Class .
''')
        self.config['external'] = ['retained.rdfs.ttl']
        self.config['naming']['overrides'][str(PREMIS.File)] = {'name': 'RenamedFile', 'label': 'renamed file'}
        self.config['naming']['overrides'][str(PREMIS)] = {'name': 'premisVocabulary', 'label': 'premis vocabulary'}
        self.config['naming']['inverse_pairs'].append({
            'direct': str(PREMIS.hasPart), 'reverse': str(PREMIS.isPartOf),
            'direct_name': 'hasPart', 'reverse_name': 'isPartOf',
        })
        self.config['naming']['property_names'].update({str(PREMIS.hasPart): 'hasPart', str(PREMIS.isPartOf): 'isPartOf'})
        self.manifest = build(self.config, self.root)
        self.outputs = self.read_outputs()

    def test_retained_namespaces_keep_definitions_labels_and_dependencies(self):
        self.add_retained_fixture()
        combined = union(self.outputs)
        for original, entry in self.manifest['terms'].items():
            if original.startswith((str(PREMIS), str(ODRL))):
                self.assertEqual(entry['target'], original)
                self.assertEqual(entry['sources'], ['retained.rdfs.ttl'])
        self.assertIn((HA.Work, RDFS.subClassOf, PREMIS.File), combined)
        self.assertIn((HA.Work, ODRL.hasPolicy, ODRL.Policy), combined)
        self.assertIn((PREMIS.File, RDFS.subClassOf, HA.Parent), combined)
        self.assertIn((HA.Work, HA.hasStamp, Literal('01', datatype=PREMIS.FileFormat, normalize=False)), combined)
        self.assertIn((PREMIS.FileFormat, RDF.type, RDFS.Datatype), combined)
        self.assertIn((ODRL.hasPolicy, RDF.type, RDF.Property), combined)
        self.assertEqual(set(combined.objects(PREMIS.File, RDFS.label)), {
            Literal('File', lang='en'), Literal('PREMIS file', lang='en'), Literal('Bestand', lang='nl'),
        })
        self.assertIn((ODRL.PolicyShape, SH.name, Literal('Source policy shape', lang='en')), combined)
        self.assertFalse(list(combined.objects(ODRL.PolicyShape, RDFS.label)))
        self.assertFalse(list(combined.objects(PREMIS.FileFormat, RDFS.label)))
        self.assertIn((PREMIS.File, RDFS.isDefinedBy, URIRef(str(PREMIS))), combined)
        self.assertIn((URIRef(str(PREMIS)), OWL.imports, URIRef(str(ODRL))), combined)
        prefix_property = URIRef('http://purl.org/vocab/vann/preferredNamespacePrefix')
        self.assertIn((URIRef(str(PREMIS)), prefix_property, Literal('premis')), combined)
        self.assertNotIn(str(ODRL.Unused), self.manifest['terms'])
        self.assertEqual(self.manifest['terms'][str(PREMIS.File)]['english_label'], 'File')
        query = str(next(combined.objects(None, SH.select)))
        self.assertIn('odrl:hasPolicy', query)
        self.assertIn(f'<{PREMIS}File>', query)
        self.assertIn(f'<{HA}creates>', query)
        self.verify()

    def test_namespace_retention_can_be_disabled_individually(self):
        self.add_retained_fixture()
        for namespaces in ([str(PREMIS)], [], None):
            with self.subTest(retain_namespaces=namespaces):
                if namespaces is None:
                    self.config.pop('retain_namespaces')
                else:
                    self.config['retain_namespaces'] = namespaces
                manifest = build(self.config, self.root)
                for original, entry in manifest['terms'].items():
                    if original.startswith((str(PREMIS), str(ODRL))):
                        self.assertEqual(entry['target'] == original, any(original.startswith(ns) for ns in namespaces or []))
                if not namespaces:
                    self.assertEqual(manifest['terms'][str(PREMIS.File)]['target'], str(HA.RenamedFile))
                    graph = union(self.read_outputs(manifest))
                    self.assertIn((HA.RenamedFile, RDFS.label, Literal('renamed file', lang='en')), graph)

    def test_retained_inverse_pairs_need_no_configured_renaming(self):
        self.add_retained_fixture()
        self.config['naming']['inverse_pairs'].pop()
        build(self.config, self.root)

    def test_mixed_inverse_pair_retains_only_the_external_property(self):
        self.add_retained_fixture()
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '\nex:owns a rdf:Property ; owl:inverseOf premis:isOwnedBy .\n')
        external = self.root / 'retained.rdfs.ttl'
        external.write_text(external.read_text() + '\npremis:isOwnedBy a rdf:Property ; owl:inverseOf ex:owns .\n')
        self.config['naming']['property_names'][str(EX.owns)] = 'owns'
        self.config['naming']['inverse_pairs'].append({
            'direct': str(EX.owns), 'reverse': str(PREMIS.isOwnedBy),
            'direct_name': 'owns', 'reverse_name': 'isOwnedBy',
        })
        manifest = build(self.config, self.root)
        self.assertEqual(manifest['terms'][str(EX.owns)]['target'], str(HA.owns))
        self.assertEqual(manifest['terms'][str(PREMIS.isOwnedBy)]['target'], str(PREMIS.isOwnedBy))
        graph = union(self.read_outputs(manifest))
        self.assertIn((HA.owns, OWL.inverseOf, PREMIS.isOwnedBy), graph)
        self.assertIn((PREMIS.isOwnedBy, OWL.inverseOf, HA.owns), graph)

    def test_undefined_retained_term_stops_the_build(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'\nex:Work rdfs:subClassOf <{PREMIS}Unknown> .\n')
        with self.assertRaisesRegex(ModelError, str(PREMIS.Unknown)):
            build(self.config, self.root)

    def test_invalid_namespace_retention_config_is_rejected(self):
        for invalid in ('http://example.org/', [''], [1]):
            with self.subTest(retain_namespaces=invalid):
                self.config['retain_namespaces'] = invalid
                with self.assertRaisesRegex(ModelError, 'retain_namespaces must be a list'):
                    build(self.config, self.root)

    def test_verifier_rejects_changed_retained_uri_and_labels(self):
        self.add_retained_fixture()
        forged = deepcopy(self.manifest)
        forged['terms'][str(PREMIS.File)]['target'] = str(HA.File)
        with self.assertRaisesRegex(ModelError, 'Incorrect mapping'):
            self.verify(forged)
        self.outputs['external/premis.rdfs.ttl'].set((PREMIS.File, RDFS.label, Literal('renamed file', lang='en')))
        with self.assertRaisesRegex(ModelError, 'lost/changed'):
            self.verify()

    def test_retained_labels_cannot_be_changed_through_the_manifest(self):
        self.add_retained_fixture()
        forged = deepcopy(self.manifest)
        forged['changes'].append({
            'source': 'retained.rdfs.ttl',
            'before': list(map(term_data, (PREMIS.File, RDFS.label, Literal('File', lang='en')))),
            'after': list(map(term_data, (PREMIS.File, RDFS.label, Literal('renamed file', lang='en')))),
            'reason': 'configured English name',
        })
        with self.assertRaisesRegex(ModelError, 'Unapproved change'):
            self.verify(forged)
        forged = deepcopy(self.manifest)
        forged['changes'].append({
            'source': 'retained.rdfs.ttl', 'before': None,
            'after': list(map(term_data, (PREMIS.FileFormat, RDFS.label, Literal('FileFormat', lang='en')))),
            'reason': 'configured English label',
        })
        with self.assertRaisesRegex(ModelError, 'Unapproved annotation addition'):
            self.verify(forged)

    def test_external_files_keep_source_definitions_and_local_imports(self):
        self.add_retained_fixture()
        name = 'external/premis.rdfs.ttl'
        self.assertEqual(self.manifest['external_documents'], {
            str(PREMIS): name, str(ODRL): 'external/odrl.rdfs.ttl',
        })
        self.assertIn((PREMIS.File, RDF.type, RDFS.Class), self.outputs[name])
        self.assertIn((ODRL.PolicyShape, RDF.type, SH.NodeShape), self.outputs['external/odrl.rdfs.ttl'])
        self.assertFalse(list(self.outputs['rdfs'].triples((PREMIS.File, None, None))))
        self.assertFalse(list(self.outputs['shacl'].triples((ODRL.PolicyShape, None, None))))
        self.assertFalse(list(self.outputs[name].triples((HA.Work, None, None))))
        self.assertIn((document_uri(self.config, 'rdfs'), OWL.imports, document_uri(self.config, name)),
                      self.outputs['rdfs'])
        core_text = (self.root / self.manifest['outputs']['rdfs']).read_text()
        self.assertIn('<external/premis.rdfs.ttl>', core_text)
        self.assertFalse(any(str(s).startswith(str(HA)) for s in self.outputs[name].subjects()))
        self.assertNotIn(str(ODRL.Unused), self.manifest['terms'])
        self.verify()

    def test_ha_definitions_and_attached_expressions_stay_in_main_model(self):
        core = self.root / 'core/vocabulary.rdfs.ttl'
        core.write_text(core.read_text() + f'\nex:Work rdfs:subClassOf ex:Organization, <{PREMIS}File> .\n')
        shapes = self.root / 'core/shapes.shacl.ttl'
        shapes.write_text(shapes.read_text() + '\n<#PersonShape> sh:node ex:OrganizationShape .\n')
        (self.root / 'mixed.ttl').write_text(f"""
@prefix ex: <{EX}> . @prefix premis: <{PREMIS}> .
@prefix rdfs: <{RDFS}> . @prefix owl: <{OWL}> . @prefix sh: <{SH}> .
ex:Organization a rdfs:Class ; rdfs:isDefinedBy ex:vocabulary ; rdfs:subClassOf _:shared .
premis:File a rdfs:Class ; rdfs:subClassOf _:shared .
_:shared a owl:Class ; owl:unionOf (ex:Person ex:Work) .
ex:OrganizationShape a sh:NodeShape ; sh:targetClass ex:Organization ;
    sh:property [ sh:path ex:creates ; sh:or ([ sh:class ex:Person ] [ sh:class ex:Work ]) ] .
""")
        self.config['external'] = ['mixed.ttl']
        manifest = build(self.config, self.root)
        outputs = self.read_outputs(manifest)
        external = outputs['external/premis.rdfs.ttl']
        self.assertIn((HA.Organization, RDF.type, RDFS.Class), outputs['rdfs'])
        self.assertIn((HA.Organization, RDFS.isDefinedBy, document_uri(self.config, 'rdfs')), outputs['rdfs'])
        self.assertIn((HA.OrganizationShape, RDF.type, SH.NodeShape), outputs['shacl'])
        self.assertIn((PREMIS.File, RDF.type, RDFS.Class), external)
        self.assertFalse(any(str(s).startswith(str(HA)) for s in external.subjects()))
        for graph, subject in ((outputs['rdfs'], HA.Organization), (external, PREMIS.File)):
            expression = next(graph.objects(subject, RDFS.subClassOf))
            head = graph.value(expression, OWL.unionOf)
            self.assertEqual(list(graph.items(head)), [HA.Person, HA.Work])
        verify_graphs(self.config, self.root, manifest, outputs)

    def test_removed_link_does_not_move_shared_external_metadata_to_main(self):
        core = self.root / 'core/vocabulary.rdfs.ttl'
        core.write_text(core.read_text() + f'\nex:Work rdfs:subClassOf ex:Organization, <{PREMIS}File> .\n')
        (self.root / 'mixed.ttl').write_text(f"""
@prefix ex: <{EX}> . @prefix premis: <{PREMIS}> . @prefix rdf: <{RDF}> . @prefix rdfs: <{RDFS}> .
ex:Organization a rdfs:Class ; rdfs:seeAlso _:shared .
premis:File a rdfs:Class ; ex:note _:shared .
ex:note a rdf:Property .
_:shared rdfs:comment "external metadata" .
""")
        self.config['external'] = ['mixed.ttl']
        manifest = build(self.config, self.root)
        outputs = self.read_outputs(manifest)
        self.assertFalse(list(outputs['rdfs'].triples((None, RDFS.comment, Literal('external metadata')))))
        self.assertTrue(list(outputs['external/premis.rdfs.ttl'].triples((None, RDFS.comment, Literal('external metadata')))))
        verify_graphs(self.config, self.root, manifest, outputs)

    def test_remapped_ontology_does_not_create_an_external_file(self):
        core = self.root / 'core/vocabulary.rdfs.ttl'
        core.write_text(core.read_text() + '\nex:Work rdfs:subClassOf ex:Organization .\n')
        (self.root / 'organization.ttl').write_text(f'@prefix ex: <{EX}> . ex:Organization a <{RDFS}Class> .')
        self.config['external'] = ['organization.ttl']
        manifest = build(self.config, self.root)
        outputs = self.read_outputs(manifest)
        self.assertEqual(manifest['external_documents'], {})
        self.assertEqual(set(outputs), {'rdfs', 'shacl'})
        self.assertIn((HA.Organization, RDF.type, RDFS.Class), outputs['rdfs'])
        self.assertFalse((self.root / 'model/external').exists())
        verify_graphs(self.config, self.root, manifest, outputs)

    def test_verifier_rejects_ha_definitions_in_external_files(self):
        self.add_retained_fixture()
        triple = (HA.Parent, RDF.type, RDFS.Class)
        self.assertIn(triple, self.outputs['rdfs'])
        self.outputs['rdfs'].remove(triple)
        self.outputs['external/premis.rdfs.ttl'].add(triple)
        with self.assertRaisesRegex(ModelError, 'consolidated namespace definition in external output'):
            self.verify()

    def test_odrl_curated_and_fallback_definitions_share_one_namespace_file(self):
        self.add_retained_fixture()
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'\nex:Work rdfs:subClassOf <{ODRL}Asset> .\n')
        folder = self.root / 'external_ontologies_complete'
        folder.mkdir()
        fallback = 'external_ontologies_complete/odrl.ttl'
        (self.root / fallback).write_text(f"""
@prefix odrl: <{ODRL}> . @prefix rdfs: <{RDFS}> .
odrl:Asset a rdfs:Class ; rdfs:label "Asset"@en .
odrl:UnusedFallback a rdfs:Class .
""")
        self.config['missing_definitions'][str(ODRL.Asset)] = [fallback]
        manifest = build(self.config, self.root)
        outputs = self.read_outputs(manifest)
        self.assertEqual(manifest['external_documents'][str(ODRL)], 'external/odrl.rdfs.ttl')
        self.assertEqual(set(outputs), {'rdfs', 'shacl', 'external/odrl.rdfs.ttl', 'external/premis.rdfs.ttl'})
        odrl = outputs['external/odrl.rdfs.ttl']
        self.assertIn((ODRL.Asset, RDF.type, RDFS.Class), odrl)
        self.assertIn((ODRL.Policy, RDF.type, RDFS.Class), odrl)
        self.assertFalse(list(odrl.triples((PREMIS.File, None, None))))
        self.assertEqual(manifest['terms'][str(ODRL.Asset)]['sources'], [fallback])
        self.assertEqual(manifest['terms'][str(ODRL.Policy)]['sources'], ['retained.rdfs.ttl'])
        self.assertNotIn(str(ODRL.UnusedFallback), manifest['terms'])
        verify_graphs(self.config, self.root, manifest, outputs)
        triple = (ODRL.Asset, RDF.type, RDFS.Class)
        odrl.remove(triple)
        outputs['external/premis.rdfs.ttl'].add(triple)
        with self.assertRaisesRegex(ModelError, 'lost/changed|unexplained definitions'):
            verify_graphs(self.config, self.root, manifest, outputs)

    def test_external_namespace_names_require_unambiguous_configured_prefixes(self):
        self.add_retained_fixture()
        prefixes = deepcopy(self.config['prefixes'])
        for collision in (False, True):
            with self.subTest(collision=collision):
                self.config['prefixes'] = dict(prefixes)
                self.config['prefixes'].pop('odrl')
                if collision:
                    self.config['prefixes']['PREMIS'] = str(ODRL)
                message = 'filenames collide' if collision else 'Configure a namespace prefix'
                with self.assertRaisesRegex(ModelError, message):
                    build(self.config, self.root)

    def test_namespace_file_combines_sources_and_exact_fallbacks_with_scoped_blank_nodes(self):
        self.config['retain_namespaces'].append(str(EX))
        self.config['prefixes']['ex'] = str(EX)
        core = self.root / 'core/vocabulary.rdfs.ttl'
        core.write_text(core.read_text() + '\nex:Work rdfs:subClassOf ex:First, ex:Second, ex:Fallback .\n')
        prefixes = f'@prefix ex: <{EX}> . @prefix rdfs: <{RDFS}> . @prefix owl: <{OWL}> .\n'
        for directory, term in (('one', 'First'), ('two', 'Second'), ('fallback', 'Fallback')):
            folder = self.root / directory
            folder.mkdir()
            (folder / 'vocabulary.ttl').write_text(prefixes + f"""
ex:{term} a rdfs:Class ; rdfs:isDefinedBy ex:vocabulary ; rdfs:subClassOf _:shared .
_:shared a owl:Class ; owl:unionOf (ex:Person ex:Work) .
ex:Unused a rdfs:Class .
""")
        self.config['external'] = ['one/*.ttl', 'two/*.ttl']
        self.config['missing_definitions'] = {str(EX.Fallback): ['fallback/vocabulary.ttl']}
        manifest = build(self.config, self.root)
        outputs = self.read_outputs(manifest)
        self.assertEqual(manifest['external_documents'], {str(EX): 'external/ex.rdfs.ttl'})
        blank_nodes = []
        for directory, term in (('one', 'First'), ('two', 'Second'), ('fallback', 'Fallback')):
            partition = 'external/ex.rdfs.ttl'
            self.assertEqual(manifest['terms'][str(EX[term])]['sources'], [f'{directory}/vocabulary.ttl'])
            target = URIRef(manifest['terms'][str(EX[term])]['target'])
            self.assertIn((target, RDFS.isDefinedBy, EX.vocabulary), outputs[partition])
            self.assertFalse(list(outputs['rdfs'].triples((target, RDF.type, None))))
            blank_nodes.append(next(outputs[partition].objects(target, RDFS.subClassOf)))
        self.assertEqual(len(set(blank_nodes)), 3)
        self.assertNotIn(str(EX.Unused), manifest['terms'])
        verify_graphs(self.config, self.root, manifest, outputs)

    def test_verifier_rejects_misplaced_external_triples_and_forged_file_provenance(self):
        self.add_retained_fixture()
        forged = deepcopy(self.manifest)
        forged['external_documents'] = {}
        with self.assertRaisesRegex(ModelError, 'External document provenance'):
            self.verify(forged)
        triple = (PREMIS.File, RDF.type, RDFS.Class)
        self.outputs['external/premis.rdfs.ttl'].remove(triple)
        self.outputs['rdfs'].add(triple)
        with self.assertRaisesRegex(ModelError, 'lost/changed|unexplained definitions'):
            self.verify()

    def test_verifier_requires_external_files_and_local_imports(self):
        self.add_retained_fixture()
        run_dir, manifest = build_run(self.config, self.root, self.root / 'runs/external')
        saved, root = read_config(run_dir / 'model-config.json')
        self.assertEqual(saved['outputs'], manifest['outputs'])
        self.assertEqual(verify_run(saved, root)['constructs'], len(manifest['terms']))
        self.outputs['rdfs'].remove((document_uri(self.config, 'rdfs'), OWL.imports,
                                     document_uri(self.config, 'external/premis.rdfs.ttl')))
        with self.assertRaisesRegex(ModelError, 'lost/changed'):
            self.verify()
        (run_dir / 'external/premis.rdfs.ttl').unlink()
        with self.assertRaises(FileNotFoundError):
            verify_run(saved, root)

    def test_conflicting_constraints_across_external_files_stop_the_build(self):
        source = self.root / 'core/shapes.shacl.ttl'
        source.write_text(source.read_text() + '\n<#PersonShape> sh:property ex:CommonShape .\n')
        for count in (1, 2):
            (self.root / f'constraints-{count}.ttl').write_text(f"""
@prefix ex: <{EX}> . @prefix sh: <{SH}> .
ex:CommonShape a sh:PropertyShape ; sh:path ex:creates ; sh:minCount {count} .
""")
        self.config['external'] = ['constraints-*.ttl']
        with self.assertRaisesRegex(ModelError, 'Incompatible .*minCount'):
            build(self.config, self.root)

    def test_round_trip_and_identical_repeat(self):
        report = self.verify()
        self.assertEqual(report['core_files'], 2)
        before = {p: (self.root / p).read_bytes() for p in self.config['outputs'].values()}
        build(self.config, self.root)
        self.assertEqual(before, {p: (self.root / p).read_bytes() for p in before})
        self.assertIn((HA.Person, Namespace('http://www.w3.org/2000/01/rdf-schema#').label, Literal('Persoon', lang='nl')), self.outputs['rdfs'])

    def test_run_folders_are_isolated_reproducible_and_verifiable(self):
        original_config = deepcopy(self.config)
        before = {p: (self.root / p).read_bytes() for p in self.config['outputs'].values()}
        first, manifest = build_run(self.config, self.root, self.root / 'runs/first')
        second, repeated = build_run(self.config, self.root, self.root / 'runs/second')
        self.assertEqual(self.config, original_config)
        self.assertEqual(before, {p: (self.root / p).read_bytes() for p in before})
        self.assertEqual({p.name for p in first.iterdir()}, {
            'model-config.json', 'model-map.json', 'model.rdfs.ttl', 'model.shacl.ttl', 'model-map.html',
        })
        for name in ('model.rdfs.ttl', 'model.shacl.ttl', 'model-map.html'):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
        self.assertNotEqual(manifest['outputs'], repeated['outputs'])
        self.assertEqual({k: v for k, v in manifest.items() if k != 'outputs'},
                         {k: v for k, v in repeated.items() if k != 'outputs'})
        saved, root = read_config(first / 'model-config.json')
        self.assertEqual(root, self.root.resolve())
        self.assertEqual(saved['outputs'], manifest['outputs'])
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(verify_main(['--config', str(first / 'model-config.json')]), 0)
        self.assertIn('100% coverage', output.getvalue())

    def test_cli_defaults_to_timestamped_run(self):
        config_path = self.root / 'config.json'
        config_path.write_text(json.dumps(dict(self.config, root=str(self.root))))
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(merge_main(['--config', str(config_path)]), 0)
        runs = list((self.root / 'model/runs').iterdir())
        self.assertEqual(len(runs), 1)
        self.assertRegex(runs[0].name, r'^\d{8}T\d{6}\.\d{6}Z$')
        self.assertTrue((runs[0] / 'model-map.html').is_file())
        self.assertIn(str(runs[0]), output.getvalue())

    def test_existing_run_folder_is_rejected(self):
        run_dir = self.root / 'existing'
        run_dir.mkdir()
        with self.assertRaises(FileExistsError):
            build_run(self.config, self.root, run_dir)
        self.assertEqual(list(run_dir.iterdir()), [])
        marker = run_dir / 'keep.txt'
        marker.write_text('previous run')
        with self.assertRaises(FileExistsError):
            build_run(self.config, self.root, run_dir)
        self.assertEqual(marker.read_text(), 'previous run')

    def test_failed_run_publishes_no_artifacts(self):
        self.config['naming']['overrides'][str(EX.Work)] = {'name': 'Person'}
        before = (self.root / self.config['outputs']['map']).read_bytes()
        run_dir = self.root / 'runs/failed'
        with self.assertRaisesRegex(ModelError, 'Naming collision'):
            build_run(self.config, self.root, run_dir)
        self.assertEqual(list(run_dir.parent.iterdir()), [])
        self.assertEqual(before, (self.root / self.config['outputs']['map']).read_bytes())

    def test_source_hashes_detect_changes_without_graph_changes(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '\n# changed after the build\n')
        with self.assertRaisesRegex(ModelError, 'Source file hashes differ'):
            self.verify()

    def test_report_failure_publishes_no_artifacts(self):
        run_dir = self.root / 'runs/failed-report'
        with patch('merge_model.render', side_effect=ValueError('report failed')):
            with self.assertRaisesRegex(ModelError, 'HTML report failed: report failed'):
                build_run(self.config, self.root, run_dir)
        self.assertEqual(list(run_dir.parent.iterdir()), [])

    def test_removed_constraint_fails(self):
        self.outputs['shacl'].remove((None, SH.minCount, None))
        with self.assertRaisesRegex(ModelError, 'lost/changed.*core/shapes.shacl.ttl'):
            self.verify()

    def test_nested_constraint_and_list_order_are_checked(self):
        shape = next(self.outputs['shacl'].subjects(SH['class'], HA.Work))
        self.outputs['shacl'].remove((shape, SH['class'], HA.Work))
        with self.assertRaisesRegex(ModelError, 'lost/changed'):
            self.verify()

    def test_uri_collision_fails_without_overwriting_outputs(self):
        self.config['naming']['overrides'][str(EX.Work)] = {'name': 'Person'}
        before = (self.root / self.config['outputs']['map']).read_bytes()
        with self.assertRaisesRegex(ModelError, 'Naming collision'):
            build(self.config, self.root)
        self.assertEqual(before, (self.root / self.config['outputs']['map']).read_bytes())

    def test_incorrect_inverse_mapping_fails(self):
        manifest = deepcopy(self.manifest)
        manifest['terms'][str(EX.creates)]['target'] = str(HA.isCreatedBy)
        manifest['terms'][str(EX.isCreatedBy)]['target'] = str(HA.creates)
        with self.assertRaisesRegex(ModelError, 'Incorrect mapping'):
            self.verify(manifest)

    def test_constraint_deletion_cannot_be_approved_by_map(self):
        manifest = deepcopy(self.manifest)
        from model_common import parse_source
        triple = next(parse_source(self.root, 'core/shapes.shacl.ttl').triples((None, SH.minCount, None)))
        manifest['changes'].append({'source': 'core/shapes.shacl.ttl', 'before': list(map(term_data, triple)),
                                    'after': None, 'reason': 'configured English name'})
        with self.assertRaisesRegex(ModelError, 'Unapproved change'):
            self.verify(manifest)

    def test_distinct_contexts_and_identical_anonymous_shapes(self):
        graph = self.outputs['shacl']
        self.assertEqual(len(set(graph.subjects(SH.maxCount, Literal(10)))), 1)
        self.assertEqual(len(set(graph.subjects(SH.maxCount, Literal(3)))), 1)
        self.assertTrue(any(graph.subjects(SH.name, Literal('contextual work count', lang='en'))))
        self.verify()

    def test_missing_mapping_fails(self):
        manifest = deepcopy(self.manifest)
        del manifest['terms'][str(EX.Work)]
        with self.assertRaisesRegex(ModelError, 'Missing/unexplained mappings'):
            self.verify(manifest)

    def test_unresolved_definition_stops_build(self):
        p = self.root / 'core/vocabulary.rdfs.ttl'
        p.write_text(p.read_text() + '\nex:creates rdfs:range ex:Missing .\n')
        with self.assertRaisesRegex(ModelError, 'Unresolved definitions.*|Unresolved definitions'):
            build(self.config, self.root)

    def test_executable_references_are_mapped_without_changing_strings(self):
        p = self.root / 'core/shapes.shacl.ttl'
        p.write_text(p.read_text() + '''
<#PersonShape> sh:sparql [
    sh:message "check works"@en ;
    sh:select """PREFIX ex: <https://example.test/>
SELECT $this WHERE { $this ex:creates ?work . FILTER(?work = "ex:Work") }
"""
] .
''')
        build(self.config, self.root)
        graph = Graph().parse(self.root / self.config['outputs']['shacl'])
        query = str(next(graph.objects(None, SH.select)))
        self.assertIn('<' + str(HA.creates) + '>', query)
        self.assertIn('"ex:Work"', query)

    def test_literal_lexical_form_is_preserved(self):
        from rdflib import RDFS, XSD
        p = self.root / 'core/vocabulary.rdfs.ttl'
        p.write_text(p.read_text() + '\nex:Work rdfs:comment "01"^^<http://www.w3.org/2001/XMLSchema#integer> .\n')
        build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['rdfs'], str(HA) + 'model.rdfs.ttl')
        self.assertIn((HA.Work, RDFS.comment, Literal('01', datatype=XSD.integer, normalize=False)), graph)

    def test_complete_list_order_is_checked(self):
        graph = self.outputs['shacl']
        head = next(graph.objects(None, SH['or']))
        tail = graph.value(head, RDF.rest)
        first, second = graph.value(head, RDF.first), graph.value(tail, RDF.first)
        graph.set((head, RDF.first, second))
        graph.set((tail, RDF.first, first))
        with self.assertRaisesRegex(ModelError, 'lost/changed'):
            self.verify()

    def test_turtle_serialization_preserves_shared_list_tails_and_their_constraints(self):
        graph = Graph().parse(data='''
@prefix ex: <https://example.test/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:shape sh:or _:head ; ex:sharedTail _:tail .
_:head rdf:first [ sh:datatype xsd:string ] ; rdf:rest _:tail .
_:tail rdf:first [ sh:datatype xsd:integer ] ; rdf:rest rdf:nil .
''', format='turtle')
        serialized = readable_turtle(graph, self.config)
        reparsed = Graph().parse(data=serialized, format='turtle')
        self.assertTrue(isomorphic(graph, reparsed))
        self.assertEqual(serialized, readable_turtle(graph, self.config))

    def test_anonymous_rdfs_class_expressions_remain_inline_after_mapping(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text().replace(
            'rdfs:domain ex:Person ;',
            'rdfs:domain [ a rdfs:Class, owl:Class ; owl:unionOf (ex:Person ex:Work) ] ;'
        ).replace(
            'rdfs:range ex:Work ;',
            '''rdfs:range [ a rdfs:Class ; owl:intersectionOf (
                ex:Work [ a rdfs:Class, owl:Restriction ;
                    owl:onProperty ex:creates ; owl:someValuesFrom ex:Person ]
            ) ] ;'''
        ))
        build(self.config, self.root)
        text = (self.root / self.config['outputs']['rdfs']).read_text()
        self.assertRegex(text, r'rdfs:domain\s+\[')
        self.assertRegex(text, r'rdfs:range\s+\[')
        self.assertRegex(text, r'owl:intersectionOf\s+\(')
        self.assertNotRegex(text, r'(?m)^_:')
        graph = parse_turtle(None, str(HA) + 'model.rdfs.ttl', data=text)
        self.assertEqual(set(graph.objects(None, OWL.someValuesFrom)), {HA.Person})
        self.assertEqual(set(graph.objects(None, OWL.onProperty)), {HA.creates})

    def test_shared_anonymous_rdfs_classes_keep_their_identity(self):
        graph = Graph().parse(data='''
@prefix ex: <https://example.test/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
ex:first rdfs:domain _:shared .
ex:second rdfs:domain _:shared .
_:shared a rdfs:Class ; owl:unionOf (ex:Person ex:Work) .
''', format='turtle')
        serialized = readable_turtle(graph, self.config)
        reparsed = Graph().parse(data=serialized, format='turtle')
        self.assertTrue(isomorphic(graph, reparsed))
        self.assertEqual(reparsed.value(EX.first, RDFS.domain), reparsed.value(EX.second, RDFS.domain))

    def test_blank_node_labels_are_scoped_per_source(self):
        from rdflib import RDFS
        first = self.root / 'core/vocabulary.rdfs.ttl'
        first.write_text(first.read_text() + '\nex:note a rdf:Property .\nex:Person ex:note _:same .\n_:same rdfs:comment "first" .\n')
        second = self.root / 'core/annotations.rdfs.ttl'
        second.write_text(VOCABULARY + '\nex:note a rdf:Property .\nex:Person ex:note _:same .\n_:same rdfs:comment "second" .\n')
        self.config['core'].append('core/annotations.rdfs.ttl')
        build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['rdfs'], str(HA) + 'model.rdfs.ttl')
        self.assertEqual(len([o for o in graph.objects(HA.Person, HA.hasNote) if isinstance(o, BNode)]), 2)

    def test_ontology_description_vocabulary_is_not_remapped(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'''
@prefix skos: <{SKOS}> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix schema: <https://schema.org/> .
@prefix vs: <http://www.w3.org/2003/06/sw-vocab-status/ns#> .
ex:Person skos:definition "An agent"@en, "Een agent"@nl ;
    skos:note "Original note"@en ; dct:issued "2026-11-17" ; vs:term_status "stable" .
ex:creates schema:domainIncludes ex:Person ; schema:inverseOf ex:isCreatedBy .
''')
        manifest = build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['rdfs'], str(HA) + 'model.rdfs.ttl')
        self.assertIn((HA.Person, SKOS.definition, Literal('An agent', lang='en')), graph)
        self.assertIn((HA.Person, SKOS.definition, Literal('Een agent', lang='nl')), graph)
        self.assertIn((HA.Person, SKOS.note, Literal('Original note', lang='en')), graph)
        self.assertIn((HA.Person, URIRef('http://purl.org/dc/terms/issued'), Literal('2026-11-17')), graph)
        self.assertIn((HA.creates, URIRef('https://schema.org/domainIncludes'), HA.Person), graph)
        self.assertIn((HA.creates, URIRef('https://schema.org/inverseOf'), HA.isCreatedBy), graph)
        self.assertNotIn(str(SKOS.definition), manifest['terms'])
        self.assertFalse(any(graph.triples((None, HA.hasSkosDefinition, None))))
        self.assertFalse(any(graph.triples((None, HA.hasTermStatus, None))))

    def test_ontology_headers_keep_metadata_vocabulary_and_nested_authors(self):
        vocabulary = self.root / 'core/vocabulary.rdfs.ttl'
        vocabulary.write_text(vocabulary.read_text() + '\n<https://schema.org/name> a rdf:Property .\n')
        shapes = self.root / 'core/shapes.shacl.ttl'
        shapes.write_text(shapes.read_text() + '''
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix schema: <https://schema.org/> .
@prefix vann: <http://purl.org/vocab/vann/> .
@prefix pav: <http://purl.org/pav/> .
<#Ontology> a owl:Ontology ; dct:title "Original title"@en ;
    dct:creator [ schema:name "Original author" ; schema:email "author@example.test" ] ;
    vann:preferredNamespacePrefix "ex" ; pav:version "1.0" .
<#PersonShape> sh:property [ sh:path schema:name ] .
''')
        manifest = build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['shacl'], str(HA) + 'model.shacl.ttl')
        dct = Namespace('http://purl.org/dc/terms/')
        schema = Namespace('https://schema.org/')
        self.assertIn((HA.ontology, dct.title, Literal('Original title', lang='en')), graph)
        author = graph.value(HA.ontology, dct.creator)
        self.assertIsInstance(author, BNode)
        self.assertIn((author, schema.name, Literal('Original author')), graph)
        self.assertIn((author, schema.email, Literal('author@example.test')), graph)
        self.assertIn((HA.ontology, URIRef('http://purl.org/vocab/vann/preferredNamespacePrefix'), Literal('ha')), graph)
        self.assertTrue(any(graph.triples((None, SH.path, HA.hasName))))
        self.assertEqual(manifest['terms'][str(schema.name)]['target'], str(HA.hasName))
        self.assertNotIn(str(dct.creator), manifest['terms'])

    def test_see_also_only_links_to_a_different_uri_hostname(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'''
ex:Person rdfs:seeAlso <{HA}legacy/Person>,
    <http://data.hetarchief.be/old/Person>, <https://data.hetarchief.be:8443/Person>,
    <urn:example:Person>, "not a URI", [ rdfs:comment "discarded reference details" ],
    <https://external.test/ExternalThing> .
<{HA}legacy/Widget> a rdfs:Class .
<https://external.test/ExternalThing> a rdfs:Class .
''')
        self.manifest = build(self.config, self.root)
        self.outputs = self.read_outputs()
        graph = self.outputs['rdfs'] + self.outputs['shacl']
        self.assertIn((HA.Person, RDFS.seeAlso, URIRef('https://external.test/ExternalThing')), graph)
        self.assertFalse(any(graph.triples((HA.Widget, RDFS.seeAlso, None))))
        self.assertFalse(any(graph.triples((None, RDFS.comment, Literal('discarded reference details')))))
        for subject, obj in graph.subject_objects(RDFS.seeAlso):
            self.assertTrue(external_reference(subject, obj))
        omitted = [c for c in self.manifest['changes'] if c['reason'].startswith('omit non-external reference')]
        self.assertEqual(len(omitted), 7)
        self.verify()
        forged = deepcopy(self.manifest)
        forged['changes'].append({'source': 'core/vocabulary.rdfs.ttl', 'before': None,
                                 'after': list(map(term_data, (HA.Widget, RDFS.seeAlso, URIRef(str(HA) + 'legacy/Widget')))),
                                 'reason': 'original term reference'})
        with self.assertRaisesRegex(ModelError, 'Unapproved annotation addition'):
            self.verify(forged)
        forged = deepcopy(self.manifest)
        forged['changes'].append({'source': 'core/vocabulary.rdfs.ttl',
                                 'before': list(map(term_data, (EX.Person, RDFS.seeAlso, URIRef('https://external.test/ExternalThing')))),
                                 'after': None, 'reason': 'omit non-external reference'})
        with self.assertRaisesRegex(ModelError, 'Duplicate change record|Unapproved change'):
            self.verify(forged)

    def test_discarded_see_also_does_not_remove_shared_blank_nodes(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '''
ex:note a rdf:Property .
ex:Person rdfs:seeAlso _:shared ; ex:note _:shared .
_:shared rdfs:comment "still needed" .
''')
        build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['rdfs'], str(HA) + 'model.rdfs.ttl')
        node = graph.value(HA.Person, HA.hasNote)
        self.assertIsInstance(node, BNode)
        self.assertIn((node, RDFS.comment, Literal('still needed')), graph)
        self.assertNotIn((HA.Person, RDFS.seeAlso, node), graph)

    def test_selected_dependencies_and_local_scheme_members(self):
        from model_common import SKOS
        self.config['preserve_namespaces'].append(str(SKOS))
        p = self.root / 'core/vocabulary.rdfs.ttl'
        p.write_text(p.read_text() + '''
ex:Work rdfs:subClassOf ex:Parent ;
    ex:category ex:Scheme .

ex:category a rdf:Property .
''')
        (self.root / 'fallback.ttl').write_text('''@prefix ex: <https://example.test/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Parent a rdfs:Class .

ex:Unused a rdfs:Class .
''')
        (self.root / 'choices.skos.ttl').write_text('''@prefix ex: <https://example.test/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

ex:Scheme a skos:ConceptScheme .

ex:One a skos:Concept ;
    skos:inScheme ex:Scheme .

ex:Unrelated a skos:Concept .
''')
        self.config['local_concepts'] = ['choices.skos.ttl']
        self.config['missing_definitions'] = {str(EX.Parent): ['fallback.ttl']}
        manifest = build(self.config, self.root)
        self.assertIn(str(EX.Parent), manifest['terms'])
        self.assertIn(str(EX.One), manifest['terms'])
        self.assertNotIn(str(EX.Unused), manifest['terms'])
        self.assertNotIn(str(EX.Unrelated), manifest['terms'])

    def add_hierarchy_fixture(self):
        self.config['prune_unused_superclasses'] = True
        core = self.root / 'core/vocabulary.rdfs.ttl'
        core.write_text(core.read_text() + '''
ex:Work rdfs:subClassOf ex:Parent, ex:Person .
ex:media a rdf:Property ; rdfs:range ex:MediaResource ; rdfs:domain ex:Parent .
''')
        (self.root / 'hierarchy.ttl').write_text('''
@prefix ex: <https://example.test/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
ex:Parent a rdfs:Class ; rdfs:subClassOf ex:Grandparent .
ex:Grandparent a rdfs:Class .
ex:MediaResource a rdfs:Class ; rdfs:subClassOf ex:Parent ;
    owl:disjointWith ex:Grandparent .
''')
        self.config['external'] = ['hierarchy.ttl']

    def test_unused_superclasses_are_pruned_without_losing_direct_range_dependencies(self):
        self.add_hierarchy_fixture()
        self.manifest = build(self.config, self.root)
        self.outputs = self.read_outputs()
        for uri in (EX.Parent, EX.Grandparent):
            self.assertNotIn(str(uri), self.manifest['terms'])
            self.assertFalse(any(self.outputs['rdfs'].triples((None, None, uri))))
        self.assertIn(str(EX.MediaResource), self.manifest['terms'])
        self.assertIn((HA.hasMedia, RDFS.range, HA.MediaResource), self.outputs['rdfs'])
        self.assertIn((HA.Work, RDFS.subClassOf, HA.Person), self.outputs['rdfs'])
        omitted = [c for c in self.manifest['changes'] if c['reason'] == 'omit unused superclass axiom']
        self.assertEqual(len(omitted), 4)
        self.verify()
        forged = deepcopy(self.manifest)
        forged['changes'].remove(omitted[0])
        with self.assertRaisesRegex(ModelError, 'lost/changed|Missing superclass omission record'):
            self.verify(forged)
        forged = deepcopy(self.manifest)
        forged['changes'].append({'source': 'core/vocabulary.rdfs.ttl',
                                 'before': list(map(term_data, (EX.Work, RDFS.subClassOf, EX.Person))),
                                 'after': None, 'reason': 'omit unused superclass axiom'})
        with self.assertRaisesRegex(ModelError, 'Unapproved change'):
            self.verify(forged)

    def test_linked_shapes_and_executable_class_uses_preserve_needed_superclasses(self):
        self.add_hierarchy_fixture()
        shapes = self.root / 'core/shapes.shacl.ttl'
        shapes.write_text(shapes.read_text() + '\n<#WorkShape> sh:node ex:ExtraShape .\n')
        external = self.root / 'hierarchy.ttl'
        external.write_text(external.read_text() + '''
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:ExtraShape a sh:NodeShape ; sh:or ( [ sh:class ex:Parent ] [ sh:class ex:Person ] ) ;
    sh:sparql [ sh:message "parent check"@en ;
        sh:select "SELECT $this WHERE { $this a ex:MediaResource, ex:QueryParent . }" ] .
ex:Work rdfs:subClassOf ex:QueryParent .
ex:QueryParent a rdfs:Class ; rdfs:subClassOf ex:Grandparent .
''')
        manifest = build(self.config, self.root)
        graph = union(self.read_outputs(manifest))
        self.assertIn(str(EX.Parent), manifest['terms'])
        self.assertIn(str(EX.QueryParent), manifest['terms'])
        self.assertNotIn(str(EX.Grandparent), manifest['terms'])
        self.assertIn((HA.MediaResource, RDFS.subClassOf, HA.Parent), graph)
        self.assertIn((HA.Work, RDFS.subClassOf, HA.QueryParent), graph)

    def test_unused_undefined_superclasses_do_not_require_fallback_definitions(self):
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + '\nex:Work rdfs:subClassOf ex:UndefinedParent .\n')
        self.config['prune_unused_superclasses'] = True
        manifest = build(self.config, self.root)
        self.assertNotIn(str(EX.UndefinedParent), manifest['terms'])
        self.config['prune_unused_superclasses'] = False
        with self.assertRaisesRegex(ModelError, 'Unresolved definitions'):
            build(self.config, self.root)

    def test_superclass_pruning_can_be_disabled(self):
        self.add_hierarchy_fixture()
        self.config['prune_unused_superclasses'] = False
        manifest = build(self.config, self.root)
        self.assertIn(str(EX.Parent), manifest['terms'])
        self.assertIn(str(EX.Grandparent), manifest['terms'])
        self.assertFalse(any(c['reason'] == 'omit unused superclass axiom' for c in manifest['changes']))

    def test_classes_and_shapes_use_uppercase_iri_names(self):
        self.config['preserve_namespaces'].append(str(SKOS))
        source = self.root / 'core/vocabulary.rdfs.ttl'
        source.write_text(source.read_text() + f'''
@prefix skos: <{SKOS}> .
ex:Choices a skos:ConceptScheme .
ex:Choice a skos:Concept ; skos:inScheme ex:Choices .
ex:Individual a ex:Person .
ex:Vocabulary a owl:Ontology .
''')
        manifest = build(self.config, self.root)
        expected = {EX.Person: HA.Person, EX.Choices: HA.choices, EX.Choice: HA.choice,
                    EX.Individual: HA.individual, EX.Vocabulary: HA.vocabulary,
                    URIRef('https://example.test/shapes#PersonShape'): HA.PersonShape}
        for uri, target in expected.items():
            self.assertEqual(manifest['terms'][str(uri)]['target'], str(target))
        for original, entry in manifest['terms'].items():
            if entry['target'] != original:
                name = entry['target'].removeprefix(str(HA))
                self.assertEqual(name[0].isupper(), entry['kind'] in ('class', 'shape'))
        defaults = deepcopy(self.config)
        for construct in ('scheme', 'concept', 'ontology'):
            defaults['naming'].pop(construct + '_case', None)
            self.assertTrue(naming(EX.Sample, construct, defaults)[0][0].islower())
        defaults['naming'].pop('shape_case', None)
        self.assertEqual(naming(EX.Sample, 'shape', defaults)[0], 'SampleShape')
        self.config['naming']['overrides'][str(EX.Choice)] = {'name': 'UppercaseChoice'}
        with self.assertRaisesRegex(ModelError, 'Invalid concept name'):
            build(self.config, self.root)

    def test_implicit_shape_preserves_its_blank_node_constraints(self):
        p = self.root / 'core/shapes.shacl.ttl'
        p.write_text(p.read_text().replace('<#PersonShape> a sh:NodeShape ;', '<#PersonShape>'))
        manifest = build(self.config, self.root)
        self.assertEqual(manifest['terms']['https://example.test/shapes#PersonShape']['kind'], 'shape')

    def test_unexplained_orphan_constraint_fails(self):
        self.outputs['shacl'].add((BNode(), SH.minCount, Literal(99)))
        with self.assertRaisesRegex(ModelError, 'unexplained anonymous'):
            self.verify()

    def test_shacl_prefix_declarations_are_used_in_executable_references(self):
        p = self.root / 'core/shapes.shacl.ttl'
        p.write_text(p.read_text() + '''
<#PersonShape> sh:declare [
    sh:prefix "vocab" ;
    sh:namespace "https://example.test/"^^xsd:anyURI
] ;
    sh:sparql [
        sh:prefixes <#PersonShape> ;
        sh:message "check works"@en ;
        sh:select "SELECT $this WHERE { $this vocab:creates ?work . }"
    ] .
''')
        build(self.config, self.root)
        graph = parse_turtle(self.root / self.config['outputs']['shacl'], str(HA) + 'model.shacl.ttl')
        self.assertIn('<' + str(HA.creates) + '>', str(next(graph.objects(None, SH.select))))


if __name__ == '__main__':
    unittest.main()
