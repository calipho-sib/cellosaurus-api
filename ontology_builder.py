import sys
from datetime import datetime
from namespace_term import Term
from namespace_registry import NamespaceRegistry
from ApiCommon import log_it, split_string
from api_platform import ApiPlatform
from sparql_client import EndpointClient
from tree_functions import Tree
from databases import Database, Databases, get_db_category_IRI


#-------------------------------------------------
class OntologyBuilder:
#-------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, platform: ApiPlatform, describe_ranges_and_domains=True):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
        # - - - - - - - - - - - - - - - - - - - - - - - - - - -         
        # load info from data_in used later by describe...() functions
        # - - - - - - - - - - - - - - - - - - - - - - - - - - -         
        self.platform = platform
        self.ns = NamespaceRegistry(platform)
        self.prefixes = list()
        for space in self.ns.namespaces: self.prefixes.append(space.getTtlPrefixDeclaration())
        lines = list()
        for space in self.ns.namespaces: lines.append(space.getSparqlPrefixDeclaration())
        rqPrefixes = "\n".join(lines)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # store queries used to retrieve ranges and domains of properties from sparql endpoint
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.client = EndpointClient(platform.get_builder_sparql_service_IRI(), self.ns)
        self.domain_query_template = rqPrefixes + """
            select ?prop ?value (count(distinct ?s) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                ?s rdf:type ?value .
            } group by ?prop ?value"""        
        self.range_query_template = rqPrefixes + """
            select  ?prop ?value (count(*) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                optional { ?o rdf:type ?cl . }
                BIND(
                IF (bound(?cl) , ?cl,  IF ( isIRI(?o), 'rdfs:Resource', datatype(?o))
                ) as ?value)
            } group by ?prop ?value"""


        self.setup_domains_ranges_to_remove()
        self.describe_cell_line_and_subclasses()
        self.describe_genetic_characteristics_and_subclasses()
        self.describe_genome_editing_method_and_subclasses()
        self.describe_sequence_variation_and_subclasses()
        self.describe_publication_hierarchy_based_on_fabio_no_redundancy()
        self.describe_terminology_database_and_subclasses()
        self.describe_organization_related_terms()
        self.describe_misc_terms()
        if describe_ranges_and_domains: self.describe_ranges_and_domains()
        self.describe_annotation_properties()
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def setup_domains_ranges_to_remove(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        self.rdfs_domain_to_remove = dict()
        self.rdfs_domain_to_remove[ns.cello.accession] = { ns.skos.Concept }
        #self.rdfs_domain_to_remove[ns.cello.category] = { ns.skos.Concept, ns.owl.NamedIndividual  }
        self.rdfs_domain_to_remove[ns.cello.database] = { ns.skos.Concept  }
        self.rdfs_domain_to_remove[ns.cello.version] = { ns.owl.NamedIndividual, ns.cello.Database }
        self.rdfs_domain_to_remove[ns.cello.alternativeName] = { ns.owl.NamedIndividual }
        self.rdfs_domain_to_remove[ns.cello.recommendedName] = { ns.owl.NamedIndividual }
        self.rdfs_domain_to_remove[ns.cello.name] = { ns.owl.NamedIndividual }
        self.rdfs_domain_to_remove[ns.cello.more_specific_than] = { ns.cello.Xref  }
        self.rdfs_range_to_remove = dict()
        self.rdfs_range_to_remove[ns.cello.seeAlsoXref] = { ns.skos.Concept }
        self.rdfs_range_to_remove[ns.cello.isIdentifiedByXref] = { ns.skos.Concept }
        self.rdfs_range_to_remove[ns.cello.more_specific_than] = { ns.cello.Xref } 
        self.rdfs_range_to_remove[ns.cello.database] = { ns.owl.NamedIndividual, ns.cello.CelloConceptScheme } 
        self.rdfs_range_to_remove[ns.cello.hasGenomeModificationMethod] = { ns.owl.NamedIndividual } 
        self.rdfs_range_to_remove[ns.cello.derivedFromIndividualWithSex] = { ns.owl.NamedIndividual }


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_class_tree(self, local_only=False):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # NOW build tree with (local) child - parent relationships based on rdfs:subClassOf()
        edges = dict()
        relevant_namespaces = ns.namespaces
        if local_only: relevant_namespaces = [ ns.cello ]
        for space in relevant_namespaces:
            for term_id in space.terms:
                term: Term = space.terms[term_id]
                if not term.isA(ns.owl.Class): continue
                for parent_iri in term.props.get(ns.rdfs.subClassOf) or set():
                    if parent_iri.startswith(ns.cello.pfx) or not local_only:
                        #print("DEBUG tree", term.iri, "has parent", parent_iri)
                        if term.iri in edges:
                            log_it(f"WARNING, multiple parents for {term.iri}:  parent {edges[term.iri]} replaced with {parent_iri}")
                        edges[term.iri] = parent_iri
        self.tree = Tree(edges)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_annotation_properties(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        ns.describe(ns.cello.version, ns.rdfs.subPropertyOf, ns.dcterms.hasVersion)
        ns.describe(ns.cello.modified, ns.rdfs.subPropertyOf, ns.dcterms.modified)
        ns.describe(ns.cello.created, ns.rdfs.subPropertyOf, ns.dcterms.created)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_organization_related_terms(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # describing our own terms as subClass/Prop of terms defined elsewhere 
        # instead of simply using these external terms allow to give them a domain / range
        # and additional semantic relationships to other terms
        ns.describe(ns.cello.isMemberOf, ns.rdfs.subPropertyOf, ns.schema.memberOf)
        ns.describe(ns.cello.city, ns.rdfs.subPropertyOf, ns.schema.location)
        ns.describe(ns.cello.country, ns.rdfs.subPropertyOf, ns.schema.location)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_genetic_characteristics_and_subclasses(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # For info
        # OBI:0001404 - genetic characteristics information
        # OBI:0001364 - genetic alteration information = superclass for seq var + gen.int + gen.ko)
        # OBI:0001225 - genetic population background information
        ns.describe(ns.OBI._0001225, ns.rdfs.subClassOf, ns.OBI._0001404)     
        ns.describe(ns.OBI._0001364, ns.rdfs.subClassOf, ns.OBI._0001404)     
        ns.describe(ns.cello.GeneticIntegration, ns.rdfs.subClassOf, ns.OBI._0001364)
        ns.describe(ns.cello.SequenceVariationInfo, ns.rdfs.subClassOf, ns.OBI._0001364)
        ns.describe(ns.cello.GeneKnockout, ns.rdfs.subClassOf, ns.OBI._0001364)
        ns.describe(ns.cello.GenomeAncestry, ns.rdfs.subClassOf, ns.OBI._0001225)
        ns.describe(ns.cello.HLAtyping, ns.rdfs.subClassOf, ns.OBI._0001404)
        ns.describe(ns.cello.ShortTandemRepeatProfile, ns.rdfs.subClassOf, ns.OBI._0001404)
        ns.describe(ns.cello.MicrosatelliteInstability, ns.rdfs.subClassOf, ns.OBI._0001404)
        ns.describe(ns.cello.KaryotypicInfoComment, ns.rdfs.subClassOf, ns.OBI._0001404)     
        ns.describe(ns.cello.KaryotypicInfoComment, ns.owl.equivalentClass, ns.OBI._0002769)             


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_genome_editing_method_and_subclasses(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns

        # NOTE: the description of cello:GenomeModificationMethod is done
        # in RdfBuilder.get_ttl_for_local_gem_class() because it 
        # requires a member variable of RdfBuilder

        # external classes for genome modification methods
        ns.describe(ns.FBcv._0003008, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.NCIt.C17262, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.NCIt.C44386, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0001152, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0001154, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0002626, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0003134, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0003135, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0003137, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)
        ns.describe(ns.OBI._0600059, ns.rdfs.subClassOf, ns.cello.GenomeModificationMethod)

        # local named individuals of external classes for genome modification methods
        ns.describe(ns.cello.CrisprCas9, ns.rdf.type, ns.FBcv._0003008)
        ns.describe(ns.cello.XRay, ns.rdf.type, ns.NCIt.C17262)
        ns.describe(ns.cello.GammaRadiation, ns.rdf.type, ns.NCIt.C44386)
        ns.describe(ns.cello.Transfection, ns.rdf.type, ns.OBI._0001152)
        ns.describe(ns.cello.Mutagenesis, ns.rdf.type, ns.OBI._0001154)
        ns.describe(ns.cello.SiRNAKnockdown, ns.rdf.type, ns.OBI._0002626)
        ns.describe(ns.cello.TALEN, ns.rdf.type, ns.OBI._0003134)
        ns.describe(ns.cello.ZFN, ns.rdf.type, ns.OBI._0003135)
        ns.describe(ns.cello.GeneTrap, ns.rdf.type, ns.OBI._0003137)
        ns.describe(ns.cello.Transduction, ns.rdf.type, ns.OBI._0600059)

        # local named individuals of generic local class genome modification method
        ns.describe(ns.cello.GenomeModificationMethodNOS, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.BacHomologousRecombination, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.CreLoxp, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.CrisprCas9N, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.EbvBasedVectorSirnaKnockdown, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.FloxingCreRecombination, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.GeneTargetedKoMouse, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.HelperDependentAdenoviralVector, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.HomologousRecombination, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.KnockoutFirstConditional, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.KoMouse, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.KoPig, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.MirnaKnockdown, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.NullMutation, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.PElement, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.PiggybacTransposition, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.PrimeEditing, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.PromoterlessGeneTargeting, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.RecombinantAdenoAssociatedVirus, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.RMCE, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.ShrnaKnockdown, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.SleepingBeautyTransposition, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.SpontaneousMutation, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TargetedIntegration, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TransductionTransfection, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TransfectionTransduction, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TransgenicFish, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TransgenicMouse, ns.rdf.type, ns.cello.GenomeModificationMethod)
        ns.describe(ns.cello.TransgenicRat, ns.rdf.type, ns.cello.GenomeModificationMethod)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_ranges_and_domains(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.build_class_tree()
        ns = self.ns
        for term_id in ns.cello.terms:
            term: Term = ns.cello.terms[term_id]
            if not term.isA(ns.rdf.Property): continue
            # gather domain classes
            log_it("DEBUG", "querying prop_name", term.iri, "domains")
            domain_dic = dict()
            domain_query = self.domain_query_template.replace("$prop", term.iri)
            response = self.client.run_query(domain_query)
            if not response.get("success"):
                log_it("ERROR", response.get("error_type"))
                log_it(response.get("error_msg"))
                sys.exit(2)
            rows = response.get("results").get("bindings")
            for row in rows:
                value = self.client.apply_prefixes(row.get("value").get("value"))
                count = int(row.get("count").get("value"))
                domain_dic[value]=count

            # simplify domain
            domain_set1 = set(domain_dic.keys())
            if len(domain_set1)>3: 
                domain_set = self.tree.get_close_parent_set(domain_set1)
            else:
                domain_set = set(domain_set1)
            for domain_to_remove in self.rdfs_domain_to_remove.get(term.iri) or {}:
                domain_set = domain_set - { domain_to_remove }
            # DEBUG CODE
            # if domain_set1 != domain_set:
            #     print("domain simplified for", term_id)
            #     print("simplified :", domain_set)
            #     print("original   :", domain_set1)

            # gather range datatypes / classes
            log_it("DEBUG", "querying prop_name", term.iri, "ranges")
            range_dic = dict()
            range_query = self.range_query_template.replace("$prop", term.iri)
            response = self.client.run_query(range_query)
            if not response.get("success"):
                log_it("ERROR", response.get("error_type"))
                log_it(response.get("error_msg"))
                sys.exit(2)
            rows = response.get("results").get("bindings")
            for row in rows:
                value = self.client.apply_prefixes(row.get("value").get("value"))
                count = int(row.get("count").get("value"))
                range_dic[value]=count
            # ttl comment about domain classes found in data
            domain_comments = list()
            tmp = list()
            for k in domain_dic: tmp.append(f"{k}({domain_dic[k]})")
            for line in split_string(" ".join(tmp), 90):
                domain_comments.append("#   domain classes found in data: " + line)

            # simplify ranges
            range_set = set(range_dic.keys())
            if len(range_set)>3:
                range_set = self.tree.get_close_parent_set(range_set)
            # hack to replace xsd:date with rdfs:Literal to be OWL2 frienly                    
            if ns.xsd.dateDataType in range_set:
                range_set = range_set - { ns.xsd.dateDataType }
                range_set.add(ns.rdfs.Literal)
            for range_to_remove in self.rdfs_range_to_remove.get(term.iri) or {}:
                range_set = range_set - { range_to_remove } 
            # ttl comment about prop range
            range_comments = list()
            tmp = list()
            for k in range_dic: tmp.append(f"{k}({range_dic[k]})")
            for line in split_string(" ".join(tmp), 90):
                range_comments.append("#   range entities found in data: " + line)
            # check prop type
            prop_types = set() # we should have a single item in this set (otherwise OWL reasoners dislike it)
            for r in range_dic:
                if r.startswith("xsd:") or r == ns.rdfs.Literal: prop_types.add("owl:DatatypeProperty") 
                else: prop_types.add("owl:ObjectProperty") 
            if len(prop_types) != 1: 
                log_it("ERROR", term.iri, "has not one and only one type", prop_types)
            else:
                declared_types = term.props.get(ns.rdf.type) # also includes rdf:Property
                found_type = prop_types.pop()
                if found_type not in declared_types and ns.owl.AnnotationProperty not in declared_types: 
                    log_it("ERROR", term.iri, f"range declaration {declared_types} does not match data {found_type}")
                        
            for domain in domain_set: ns.describe(term.iri, ns.rdfs.domain, domain)
            for comment in domain_comments: ns.describe(term.iri, "domain_comments", comment)
            for range in range_set: ns.describe(term.iri, ns.rdfs.range, range)
            for comment in range_comments: ns.describe(term.iri, "range_comments", comment)



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_publication_hierarchy_based_on_fabio_no_redundancy(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # Publication hierarchy based on fabio Expression
        ns.describe( ns.cello.Publication,              ns.rdfs.subClassOf, ns.fabio.Expression)
        ns.describe( ns.fabio.Book,                     ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.BookChapter,              ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.JournalArticle,           ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.PatentDocument,           ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.ReportDocument,           ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.cello.TechnicalDocument,        ns.rdfs.subClassOf, ns.fabio.ReportDocument)
        ns.describe( ns.cello.MiscellaneousDocument,    ns.rdfs.subClassOf, ns.fabio.ReportDocument)
        ns.describe( ns.fabio.ConferencePaper,          ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.Thesis,                   ns.rdfs.subClassOf, ns.cello.Publication)
        ns.describe( ns.fabio.BachelorsThesis,               ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.fabio.MastersThesis,                 ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.fabio.DoctoralThesis,                ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.cello.MedicalDegreeThesis,           ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.cello.MedicalDegreeMasterThesis,     ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.cello.PrivaDocentThesis,             ns.rdfs.subClassOf, ns.fabio.Thesis)
        ns.describe( ns.cello.VeterinaryMedicalDegreeThesis, ns.rdfs.subClassOf, ns.fabio.Thesis)

        # Relationships with UniProt
        ns.describe( ns.cello.Publication,              ns.skos.closeMatch, ns.up.Published_Citation)
        ns.describe( ns.fabio.BookChapter,              ns.skos.closeMatch, ns.up.Book_Citation)  # book citation is for book chapter !
        ns.describe( ns.fabio.JournalArticle,            ns.skos.closeMatch, ns.up.Journal_Citation )
        ns.describe( ns.fabio.PatentDocument,                   ns.skos.closeMatch, ns.up.Patent_Citation)
        ns.describe( ns.fabio.Thesis,                   ns.skos.closeMatch, ns.up.Thesis_Citation)
        ns.describe( ns.fabio.BachelorsThesis,               ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.fabio.MastersThesis,                 ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.fabio.DoctoralThesis,               ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.cello.MedicalDegreeThesis,          ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.cello.MedicalDegreeMasterThesis,    ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.cello.PrivaDocentThesis,            ns.skos.broadMatch, ns.up.Thesis_Citation)
        ns.describe( ns.cello.VeterinaryMedicalDegreeThesis, ns.skos.broadMatch, ns.up.Thesis_Citation)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_misc_terms(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # - - - - - - - - 
        # misc classes
        # - - - - - - - - 

        # local classes defined as equivalent of external classes for practical reasons
        ns.describe(ns.cello.AnatomicalEntity, ns.owl.equivalentClass, ns.CARO.AnatomicalEntity)
        ns.describe(ns.cello.CellType, ns.owl.equivalentClass, ns.CL.CellType)
        ns.describe(ns.cello.ChemicalEntity, ns.owl.equivalentClass, ns.CHEBI.ChemicalEntity)
        ns.describe(ns.cello.Protein, ns.owl.equivalentClass, ns.CHEBI.Protein)
        ns.describe(ns.cello.ImmunoglobulinLightChain, ns.owl.equivalentClass, ns.NCIt.C16720_IGL)
        ns.describe(ns.cello.ImmunoglobulinHeavyChain, ns.owl.equivalentClass, ns.NCIt.C16717_IGH)

        ns.describe(ns.cello.SequenceVariation, ns.owl.equivalentClass, ns.NCIt.SequenceVariation)
        ns.describe(ns.cello.GeneMutation, ns.owl.equivalentClass, ns.NCIt.GeneMutation)
        ns.describe(ns.cello.GeneFusion, ns.owl.equivalentClass, ns.NCIt.GeneFusion)
        ns.describe(ns.cello.GeneAmplification, ns.owl.equivalentClass, ns.NCIt.GeneAmplification)
        ns.describe(ns.cello.GeneDeletion, ns.owl.equivalentClass, ns.NCIt.GeneDeletion)

        # some local props defined as sub props of external props for practical reasons
        ns.describe(ns.cello.publisher, ns.rdfs.subPropertyOf, ns.dcterms.publisher)
        ns.describe(ns.cello.creator, ns.rdfs.subPropertyOf, ns.dcterms.creator)
        ns.describe(ns.fabio.hasPubMedCentralId, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.pmcId, ns.rdfs.subPropertyOf, ns.fabio.hasPubMedCentralId)
        ns.describe(ns.fabio.hasPubMedId, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.pmid, ns.rdfs.subPropertyOf, ns.fabio.hasPubMedId)
        ns.describe(ns.cello.publicationYear, ns.rdfs.subPropertyOf, ns.fabio.hasPublicationYear)
        ns.describe(ns.prism.hasDOI, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.doi, ns.rdfs.subPropertyOf, ns.prism.hasDOI)
        ns.describe(ns.prism.volume, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.volume, ns.rdfs.subPropertyOf, ns.prism.volume)
        ns.describe(ns.cello.startingPage, ns.rdfs.subPropertyOf, ns.prism.startingPage)
        ns.describe(ns.cello.endingPage, ns.rdfs.subPropertyOf, ns.prism.endingPage)
        ns.describe(ns.cello.publicationDate, ns.rdfs.subPropertyOf, ns.prism.publicationDate)


        # describe our disease class as a superclass of ncit disorder and ordo clinical entities
        ns.describe(ns.NCIt.C2991_Disease, ns.rdfs.subClassOf, ns.cello.Disease)
        ns.describe(ns.ORDO.C001_Clinical_Entity, ns.rdfs.subClassOf, ns.cello.Disease)
        
        ns.describe(ns.cello.Breed, ns.owl.equivalentClass, ns.NCIt.C53692_Breed)
        ns.describe(ns.cello.Species, ns.rdfs.subClassOf, ns.NCIt.C40098_Taxon)
    
        ns.describe(ns.cello.Population, ns.rdfs.subClassOf, ns.OBI._0000181)
        ns.describe(ns.cello.Gene, ns.owl.equivalentClass, ns.NCIt.C16612)
        ns.describe(ns.cello.HLAGene, ns.rdfs.subClassOf, ns.cello.Gene)
        ns.describe(ns.cello.HLA_Allele, ns.rdfs.subClassOf, ns.GENO._0000512_Allele)

        #ns.describe(ns.cello.Locus, ns.owl.equivalentClass, ns.NCIt.C45822) # locus unused
        ns.describe(ns.cello.STR_Allele, ns.rdfs.subClassOf, ns.GENO._0000512_Allele)
        ns.describe(ns.cello.Marker, ns.owl.equivalentClass, ns.NCIt.C13441_ShortTandemRepeat)
        #ns.describe(ns.cello.Marker, ns.rdfs.subClassOf, ns.cello.Locus) # locus unused

        ns.describe(ns.cello.Protein, ns.rdfs.subClassOf, ns.cello.ChemicalEntity)
        ns.describe(ns.cello.Protein, ns.skos.closeMatch, ns.up.Protein)
        ns.describe(ns.cello.ImmunoglobulinLightChain, ns.rdfs.subClassOf, ns.cello.Protein)
        ns.describe(ns.cello.ImmunoglobulinHeavyChain, ns.rdfs.subClassOf, ns.cello.Protein)

        # - - - - - - - - 
        # misc properties
        # - - - - - - - - 

        # ns.describe(ns.cello.hasAllele, ns.rdfs.subPropertyOf, ns.GENO._0000413_has_allele) # unused
        # ns.describe(ns.cello.isAlleleOf, ns.rdfs.subPropertyOf, ns.GENO._0000408_is_allele_of) # unused
        ns.describe(ns.cello.hasTarget, ns.rdfs.subPropertyOf, ns.schema.observationAbout)
        
        ns.describe(ns.cello.hasSource, ns.rdfs.subPropertyOf, ns.dcterms.source)
        ns.describe(ns.cello.appearsIn, ns.rdfs.subPropertyOf, ns.dcterms.source)
        ns.describe(ns.cello.references, ns.rdfs.subPropertyOf, ns.dcterms.references)
        ns.describe(ns.cello.seeAlsoXref, ns.rdfs.subPropertyOf, ns.rdfs.seeAlso)
        ns.describe(ns.cello.isIdentifiedByXref, ns.rdfs.subPropertyOf, ns.rdfs.seeAlso)
        ns.describe(ns.cello.isIdentifiedByIRI, ns.rdfs.subPropertyOf, ns.rdfs.seeAlso)

        ns.describe(ns.cello.title, ns.rdfs.subPropertyOf, ns.dcterms.title)
        ns.describe(ns.cello.conferenceTitle, ns.rdfs.subPropertyOf, ns.cello.title)
        ns.describe(ns.cello.bookTitle, ns.rdfs.subPropertyOf, ns.cello.title)
        ns.describe(ns.cello.documentTitle, ns.rdfs.subPropertyOf, ns.cello.title)
        ns.describe(ns.cello.documentSerieTitle, ns.rdfs.subPropertyOf, ns.cello.title)

        ns.describe(ns.cello.hasAnnotation, ns.owl.inverseOf, ns.IAO.is_about_0000136)

        ns.describe(ns.cello.editor, ns.rdfs.subPropertyOf, ns.dcterms.contributor)
        
        ns.describe(ns.cello.internalId, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.issn13, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.iso4JournalTitleAbbreviation, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.productId, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        
        ns.describe(ns.cello.markerId, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.alleleIdentifier, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.accession, ns.rdfs.subPropertyOf, ns.dcterms.identifier)
        ns.describe(ns.cello.primaryAccession, ns.rdfs.subPropertyOf, ns.cello.accession)
        ns.describe(ns.cello.primaryAccession, ns.owl.equivalentProperty, ns.wd.P3289_AC)
        ns.describe(ns.cello.secondaryAccession, ns.rdfs.subPropertyOf, ns.cello.accession)
        
        ns.describe(ns.cello.name, ns.rdfs.subPropertyOf, ns.rdfs.label)
        ns.describe(ns.skos.prefLabel, ns.rdfs.subPropertyOf, ns.rdfs.label)
        ns.describe(ns.skos.altLabel, ns.rdfs.subPropertyOf, ns.rdfs.label)
        ns.describe(ns.skos.hiddenLabel, ns.rdfs.subPropertyOf, ns.rdfs.label)
        #ns.describe(ns.cello.shortname, ns.rdfs.subPropertyOf, ns.cello.name)
        ns.describe(ns.cello.registeredName, ns.rdfs.subPropertyOf, ns.cello.name)
        ns.describe(ns.cello.recommendedName, ns.rdfs.subPropertyOf, ns.skos.prefLabel)
        ns.describe(ns.cello.alternativeName, ns.rdfs.subPropertyOf, ns.skos.altLabel)
        ns.describe(ns.cello.misspellingName, ns.rdfs.subPropertyOf, ns.skos.hiddenLabel)
        ns.describe(ns.cello.hgvs, ns.rdfs.subPropertyOf, ns.skos.notation)
        
        ns.describe(ns.cello.includesObservation, ns.rdfs.subPropertyOf, ns.BFO._0000051_has_part)
        ns.describe(ns.cello.hasComponent, ns.rdfs.subPropertyOf, ns.BFO._0000051_has_part)
        ns.describe(ns.cello.inRegister, ns.rdfs.subPropertyOf, ns.BFO._0000051_has_part)
        ns.describe(ns.cello.hasAntibodyHeavyChain, ns.rdfs.subPropertyOf, ns.BFO._0000051_has_part)
        ns.describe(ns.cello.hasAntibodyLightChain, ns.rdfs.subPropertyOf, ns.BFO._0000051_has_part)
        
        ns.describe(ns.cello.zygosity, ns.rdfs.subPropertyOf, ns.GENO._0000608_has_zygozity)

        ns.describe(ns.cello.inGroup, ns.rdfs.subPropertyOf, ns.schema.category)
        ns.describe(ns.cello.inCollection, ns.rdfs.subPropertyOf, ns.schema.category)
        ns.describe(ns.cello.hasProvider, ns.rdfs.subPropertyOf, ns.schema.provider)

        ns.describe(ns.cello.establishedBy, ns.rdfs.subPropertyOf, ns.dcterms.source)

        ns.describe(ns.cello.derivedFromCellType, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromSite, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)

        ns.describe(ns.cello.hasGenomeAncestry, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasHLAtyping, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.comesFomIndividualBelongingToBreed, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasSequenceVariationInfo, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        
        ns.describe(ns.cello.hasAnecdotalComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasCautionComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasCharacteristicsComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasBiotechnologyComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        

        ns.describe(ns.cello.hasDonorInfoComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasDoublingTime, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasKaryotypicInfoComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasMiscellaneousInfoComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasProblematicCellLineComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasMisspellingRecord, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasSenescenceComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasVirologyComment, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasOmicsInfo, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromIndividualBelongingToPopulation, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasGeneKnockout, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasGeneticIntegration, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasRegistationRecord, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasDiscontinuationRecord, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasMoAbIsotype, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasMoAbTarget, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasMicrosatelliteInstability, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasResistance, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasShortTandemRepeatProfile, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.transformedBy, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)

        ns.describe(ns.cello.derivedFromIndividualWithDisease, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromIndividualWithDisease, ns.owl.equivalentProperty, ns.wd.P5166_DI)

        ns.describe(ns.cello.derivedFromIndividualBelongingToSpecies, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromIndividualBelongingToSpecies, ns.owl.equivalentProperty, ns.wd.P9072_OX)

        ns.describe(ns.cello.derivedFromIndividualWithSex, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromIndividualWithSex, ns.skos.closeMatch, ns.wd.P21_SX)

        # ns.describe(ns.cello.derivedFromIndividualAtAge, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation) # no, cos is a datatype prop so far

        ns.describe(ns.cello.derivedFromSameIndividualAs, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.derivedFromSameIndividualAs, ns.owl.equivalentProperty, ns.wd.P3578_OI)

        ns.describe(ns.cello.hasParentCellLine, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasParentCellLine, ns.owl.equivalentProperty, ns.wd.P3432_HI)
        ns.describe(ns.cello.hasParentCellLine, ns.owl.inverseOf, ns.cello.hasChildCellLine)

        ns.describe(ns.cello.hasChildCellLine, ns.rdfs.subPropertyOf, ns.cello.hasAnnotation)
        ns.describe(ns.cello.hasChildCellLine, ns.owl.inverseOf, ns.cello.hasParentCellLine)

        ns.describe(ns.cello.more_specific_than, ns.rdfs.subPropertyOf, ns.skos.broader)

        


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_terminology_database_and_subclasses(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # Describe root cellosaurus terminology class
        ns.describe(ns.cello.CelloConceptScheme, ns.rdfs.subClassOf, ns.skos.ConceptScheme)

        # Describe parent class of our Database class and equivalence to uniprot Database
        ns.describe(ns.cello.Database, ns.rdfs.subClassOf, ns.NCIt.C15426_Database)
        ns.describe(ns.cello.Database, ns.owl.equivalentClass, ns.up.Database)
        ns.describe(ns.cello.Xref, ns.rdfs.subClassOf, ns.NCIt.C43621_Xref)
        
        # we add programmaticaly the subClassOf relationships between Database and its children
        # so that we can take advantage of close_parent_set() method during computation of domain / ranges of related properties
        databases = Databases(ns)
        for k in databases.categories():
            cat = databases.categories()[k]
            cat_label = cat["label"]
            cat_IRI = get_db_category_IRI(cat_label, ns)
            cat_id = cat_IRI.split(":")[1]
            ns.cello.registerClass(cat_id)
            ns.describe(cat_IRI, ns.rdfs.subClassOf, ns.cello.Database)
            ns.describe(cat_IRI, ns.rdfs.label, ns.xsd.string(cat_label))            


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_sequence_variation_and_subclasses(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # describe children of SequenceVariation class
        ns.describe( ns.cello.GeneMutation, ns.rdfs.subClassOf, ns.cello.SequenceVariation )
        ns.describe( ns.cello.GeneFusion, ns.rdfs.subClassOf, ns.cello.SequenceVariation  )
        ns.describe( ns.cello.GeneAmplification, ns.rdfs.subClassOf, ns.cello.SequenceVariation ) 
        ns.describe( ns.cello.GeneDeletion, ns.rdfs.subClassOf, ns.cello.SequenceVariation  )
        ns.describe( ns.cello.RepeatExpansion, ns.rdfs.subClassOf, ns.cello.GeneMutation  )
        #ns.describe( ns.cello.SimpleMutation, ns.rdfs.subClassOf, ns.cello.GeneMutation  )          # SimpleMutation is not used
        #ns.describe( ns.cello.UnexplicitMutation, ns.rdfs.subClassOf, ns.cello.GeneMutation  )     # SimpleMutation is not used
        ns.describe( ns.cello.GeneDuplication, ns.rdfs.subClassOf, ns.cello.GeneAmplification  )
        ns.describe( ns.cello.GeneTriplication, ns.rdfs.subClassOf, ns.cello.GeneAmplification  )
        ns.describe( ns.cello.GeneQuadruplication, ns.rdfs.subClassOf, ns.cello.GeneAmplification  )
        ns.describe( ns.cello.GeneExtensiveAmplification, ns.rdfs.subClassOf, ns.cello.GeneAmplification ) 


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe_cell_line_and_subclasses(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # describe cell line class hierarchy
        ns.describe(ns.cello.CancerCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.ConditionallyImmortalizedCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.EmbryonicStemCell, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.FactorDependentCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.FiniteCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.HybridCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.Hybridoma, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.InducedPluripotentStemCell, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.SomaticStemCell, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.SpontaneouslyImmortalizedCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.StromalCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.TelomeraseImmortalizedCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.TransformedCellLine, ns.rdfs.subClassOf, ns.cello.CellLine)
        ns.describe(ns.cello.UndefinedCellLineType, ns.rdfs.subClassOf, ns.cello.CellLine)
        

        # describe equivalent classes in wikidata
        # Use query below to get subclasses of cell line at SPARQL endpoint https://query.wikidata.org/
        # SELECT ?subclass ?subclassLabel WHERE {
        # ?subclass wdt:P279* wd:Q21014462.
        # SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        # }        
        ns.describe(ns.cello.CancerCellLine, ns.owl.equivalentClass, ns.wd.Q23058136)
        ns.describe(ns.cello.ConditionallyImmortalizedCellLine, ns.owl.equivalentClass, ns.wd.Q27653145)
        ns.describe(ns.cello.EmbryonicStemCell, ns.owl.equivalentClass, ns.wd.Q107102664)
        ns.describe(ns.cello.FactorDependentCellLine, ns.owl.equivalentClass, ns.wd.Q27627225)
        ns.describe(ns.cello.FiniteCellLine, ns.owl.equivalentClass, ns.wd.Q27671617)
        ns.describe(ns.cello.HybridCellLine, ns.owl.equivalentClass, ns.wd.Q27555050)
        ns.describe(ns.cello.Hybridoma, ns.owl.equivalentClass, ns.wd.Q27554370)
        ns.describe(ns.cello.InducedPluripotentStemCell, ns.owl.equivalentClass, ns.wd.Q107103143)
        ns.describe(ns.cello.SomaticStemCell, ns.owl.equivalentClass, ns.wd.Q107103129)
        ns.describe(ns.cello.SpontaneouslyImmortalizedCellLine, ns.owl.equivalentClass, ns.wd.Q27555319)
        ns.describe(ns.cello.StromalCellLine, ns.owl.equivalentClass, ns.wd.Q27671698)
        ns.describe(ns.cello.TelomeraseImmortalizedCellLine, ns.owl.equivalentClass, ns.wd.Q27653701)
        ns.describe(ns.cello.TransformedCellLine, ns.owl.equivalentClass, ns.wd.Q27555384)
        #ns.describe(ns.cello.UndefinedCellLineType, ns.owl.equivalentClass, ns.wd.???) # found NO equivalent in wd
        ns.describe(ns.cello.CellLine, ns.owl.equivalentClass, ns.wd.Q21014462)

        # describe how CellLine classes relate in the universe 
        ns.describe(ns.cello.CellLine, ns.skos.closeMatch, "<http://purl.obolibrary.org/obo/CLO_0000031>")
        ns.describe(ns.cello.CellLine, ns.skos.closeMatch, "<http://id.nlm.nih.gov/mesh/D002460>")
        ns.describe(ns.cello.CellLine, ns.rdfs.seeAlso, "<https://www.cellosaurus.org/>")
        ns.describe(ns.cello.CancerCellLine, ns.skos.closeMatch, f"<{ns.OBI.url}0001906>" )
        ns.describe(ns.cello.EmbryonicStemCell, ns.skos.closeMatch, f"<{ns.BTO.url}0001581>" )
        ns.describe(ns.cello.EmbryonicStemCell, ns.skos.closeMatch, f"<{ns.CLO.url}0037279>" )
        ns.describe(ns.cello.FiniteCellLine, ns.skos.closeMatch, f"<{ns.CLO.url}0009829>" )
        ns.describe(ns.cello.Hybridoma, ns.skos.closeMatch, f"<{ns.BTO.url}0001926>" )
        ns.describe(ns.cello.Hybridoma, ns.skos.closeMatch, f"<{ns.CLO.url}0036932>" )
        ns.describe(ns.cello.InducedPluripotentStemCell, ns.skos.closeMatch, f"<{ns.CLO.url}0037307>" )
        ns.describe(ns.cello.StromalCellLine, ns.skos.closeMatch, f"<{ns.BTO.url}0005996>" )
        ns.describe(ns.cello.TransformedCellLine, ns.skos.closeMatch, f"<{ns.OMIT.url}0003790>" )


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_header(self, version="alpha"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns

        lines = list()

        # set last modification date for ontology
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        
        # set ontology URL
        onto_url = "<" + self.get_onto_url() + ">"
        
        # set ontology abstract
        # appears in abstract onto page
        onto_abstract = open('html.templates/onto_abstract.md', 'r').read()
        onto_abstract = onto_abstract.replace("$public_sparql_URL", self.platform.get_public_sparql_service_IRI())

        # set ontology introduction
        # appears in onto page, section 1
        # TODO: pam approach
        onto_intro = open('html.templates/onto_intro.md', 'r').read()
        onto_intro = onto_intro.replace("$cello_url", ns.cello.url)
        onto_intro = onto_intro.replace("$cvcl_url", ns.cvcl.url)
        onto_intro = onto_intro.replace("$orga_url", ns.orga.url)
        onto_intro = onto_intro.replace("$db_url", ns.db.url)
        onto_intro = onto_intro.replace("$xref_url", ns.xref.url)

        # set ontology description
        # appears in onto page, section 3 under webowl
        # TODO: pam approach
        onto_descr = open('html.templates/onto_descr.md', 'r').read()
        
        # Note: all the prefixes are declared in namespace.py but not necessarily all the properties because used only once...
        lines.append(onto_url)
        lines.append("    a " + ns.owl.Ontology + " ;")
        lines.append("    " + ns.rdfs.label + " " + ns.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    " + ns.dcterms.created + " " + ns.xsd.date("2024-07-30") + " ;")
        lines.append("    " + ns.dcterms.modified + " " + ns.xsd.date(date_string) + " ;")
        lines.append("    " + ns.dcterms.description + " " + ns.xsd.string3(onto_descr) + " ;")
        lines.append("    " + ns.dcterms.license + " <http://creativecommons.org/licenses/by/4.0> ;")
        lines.append("    " + ns.dcterms.title + " " + ns.xsd.string("Cellosaurus ontology") + " ;")

        version = " - ".join([version, str(datetime.now()), self.platform.platform_key])

        lines.append("    " + ns.dcterms.hasVersion + " " + ns.xsd.string(version) + " ;")
        lines.append("    " + ns.owl.versionInfo + " " + ns.xsd.string(version) + " ;")
        lines.append("    " + ns.dcterms.abstract + " " + ns.xsd.string3(onto_abstract) + " ;")
        lines.append("    " + ns.vann.preferredNamespacePrefix + " " + ns.xsd.string(self.platform.get_onto_preferred_prefix()) + " ;")
        #lines.append("    " + ns.bibo.status + " <http://purl.org/ontology/bibo/status/published> ;")
        lines.append("    " + ns.bibo.status + " <http://purl.org/ontology/bibo/status/draft> ;")
        lines.append("    " + ns.widoco.introduction + " " + ns.xsd.string3(onto_intro) + " ;")
        lines.append("    " + ns.rdfs.seeAlso + " " + ns.help.IRI("rdf-ontology") + " ;")   
        lines.append("    " + ns.widoco.rdfxmlSerialization + " " + ns.help.IRI("ontology.owl") + " ;")      
        lines.append("    " + ns.widoco.ntSerialization + " " + ns.help.IRI("ontology.nt") + " ;")      
        lines.append("    " + ns.widoco.turtleSerialization + " " + ns.help.IRI("ontology.ttl") + " ;")      
        lines.append("    " + ns.widoco.jsonldSerialization + " " + ns.help.IRI("ontology.jsonld") + " ;")
        lines.append("    " + ns.dcterms.contributor + " " + "<https://orcid.org/0000-0003-2826-6444>" + " ;")
        lines.append("    " + ns.dcterms.contributor + " " + "<https://orcid.org/0000-0002-0819-0473>" + " ;")
        lines.append("    " + ns.dcterms.contributor + " " + "<https://orcid.org/0000-0002-7023-1045>" + " ;")
        lines.append("    " + ns.dcterms.creator + " " + "<https://orcid.org/0000-0002-7023-1045>" + " ;")
        lines.append("    " + ns.dcterms.publisher + " " + "<https://www.sib.swiss>" + " ;")
        lines.append("    " + ns.dcterms.bibliographicCitation + " " + ns.xsd.string("(to be defined)") + " ;")
        

        # shacl declaration of prefixes for void tools        
        for elem in ns.namespaces:
            lines.append("    " + ns.sh.declare + " [ ")
            pfx = elem.pfx
            if pfx == "": pfx = "cello"
            lines.append("        " + ns.sh._prefix  + " " + ns.xsd.string(pfx) + " ;")
            lines.append("        " + ns.sh.namespace  + " " + ns.xsd.string(elem.url) + " ;")
            lines.append("    ] ;")
        lines.append("    .")
        lines.append("")

        # lines.append("<https://orcid.org/0000-0003-2826-6444>")
        # lines.append("    " + "<http://www.w3.org/ns/org#memberOf>" + " " + "<https://www.sib.swiss>" + " ;")
        # lines.append("    " + "<http://xmlns.com/foaf/0.1/name>" + " " + ns.xsd.string("Amos Bairoch") + " ;")
        # lines.append("    .")

        # lines.append("")
        # lines.append("<https://orcid.org/0000-0002-0819-0473>")
        # lines.append("    " + "<http://www.w3.org/ns/org#memberOf>" + " " + "<https://www.sib.swiss>" + " ;")
        # lines.append("    " + "<http://xmlns.com/foaf/0.1/name>" + " " + ns.xsd.string("Paula Duek") + " ;")
        # lines.append("    .")

        # lines.append("")
        # lines.append("<https://orcid.org/0000-0002-7023-1045>")
        # lines.append("    " + "<http://www.w3.org/ns/org#memberOf>" + " " + "<https://www.sib.swiss>" + " ;")
        # lines.append("    " + "<http://xmlns.com/foaf/0.1/name>" + " " + ns.xsd.string("Pierre-André Michel") + " ;")
        # lines.append("    .")

        lines.append("")
        return lines




    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_topic_and_topic_annotations(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        text = """

# Topic individuals based on classes defined outside our ontology

cello:Biotechnology a owl:NamedIndividual, NCIt:C16351 ; 
    rdfs:label "Biotechnology"^^xsd:string ;
    cello:name "Biotechnology"^^xsd:string ;
    rdfs:comment "The field devoted to applying the techniques of biochemistry, cellular biology, biophysics, and molecular biology to addressing issues related to human beings and the environment."^^xsd:string ;
    .

cello:DoublingTimeNI a owl:NamedIndividual, NCIt:C94346 ;
    rdfs:label "Doubling time"^^xsd:string ;
    cello:name "Doubling time"^^xsd:string ;
    rdfs:comment "In biology, the amount of time it takes for one cell to divide or for a group of cells (such as a tumor) to double in size. The doubling time is different for different kinds of cancer cells or tumors."^^xsd:string ;
    .

cello:Omics a owl:NamedIndividual, NCIt:C205365 ;
    rdfs:label "Omics"^^xsd:string ;
    cello:name "Omics"^^xsd:string ;
    rdfs:comment "The fields of research that use large scale sets of bioinformatics data to identify, describe and quantify the entire set of molecules and molecular processes that contribute to the form and function of cells, tissues and organisms."^^xsd:string ;
    .

cello:Senescence a owl:NamedIndividual, NCIt:C17467 ;
    rdfs:label "Senescence"^^xsd:string ;
    cello:name "Senescence"^^xsd:string ;
    rdfs:comment "PDL stands for Population Doubling Level. The process of growing old and showing the effects of time."^^xsd:string ;
    .

cello:Virology a owl:NamedIndividual, NCIt:C17256 ;
    rdfs:label "Virology"^^xsd:string ;
    cello:name "Virology"^^xsd:string ;
    rdfs:comment "The science that deals with the study of viruses."^^xsd:string ;
    .


# Class for topic individuals defined in our ontology

cello:GeneralTopic a owl:Class ;
    rdfs:label "General topic" ;
    rdfs:subClassOf EDAM:topic_0003 ;
    .

# Topic individuals based on classes defined within our ontology

cello:Characteristics a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Characteristics"^^xsd:string ;
    cello:name "Characteristics"^^xsd:string ;
    rdfs:comment "Production process or specific biological properties of the cell line"^^xsd:string ;
    .

cello:Discontinuation a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Discontinuation"^^xsd:string ;
    cello:name "Discontinuation"^^xsd:string ;
    rdfs:comment "Discontinuation status of the cell line in a cell line catalog."^^xsd:string ;
 	.
     
cello:Miscellaneous a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Miscellaneous"^^xsd:string ;
    cello:name "Miscellaneous"^^xsd:string ;
    rdfs:comment "Miscellaneous remarks about the cell line."^^xsd:string ;
    .

cello:ProblematicCellLine a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Problematic cell line"^^xsd:string ;
    cello:name "Problematic cell line"^^xsd:string ;
    rdfs:comment "Remarks about a problematic aspect of the cell line."^^xsd:string ;
    .
    
cello:Caution a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Caution"^^xsd:string ;
    cello:name "Caution"^^xsd:string ;
    rdfs:comment "Errors, inconsistencies, ambiguities regarding the origin or other aspects of the cell line."^^xsd:string ;
    .

cello:Anecdotal a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Anecdotal"^^xsd:string ;
    cello:name "Anecdotal"^^xsd:string ;
    rdfs:comment "Anecdotal details regarding the cell line (its origin, its name or any other particularity)."^^xsd:string ;
    .

cello:Misspelling a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Misspelling"^^xsd:string ;
    cello:name "Misspelling"^^xsd:string ;
    rdfs:comment "Identified misspelling(s) of the cell line name with in some case the specific publication or external resource entry where it appears."^^xsd:string ;
    .

cello:DonorInfo a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "DonorInfo"^^xsd:string ;
    cello:name "DonorInfo"^^xsd:string ;
    rdfs:comment "Miscellaneous information relevant to the donor of the cell line."^^xsd:string ;
    .

cello:Registration a owl:NamedIndividual, cello:GeneralTopic ;
    rdfs:label "Registration"^^xsd:string ;
    cello:name "Registration"^^xsd:string ;
    rdfs:comment "Register or official list in which the cell line is registered."^^xsd:string ;
    .

    


# Define cell line annotation topic class as a list of members (owl:oneOf)

cello:CellLineAnnotationTopic a owl:Class ;
    rdfs:label "Cell line annotation topic"^^xsd:string ;
    rdfs:subClassOf EDAM:topic_0003 ;
    owl:equivalentClass [
        owl:intersectionOf (
            EDAM:topic_0003
            [
                rdf:type owl:Class ;
                owl:oneOf (cello:Biotechnology cello:Senescence cello:DoublingTimeNI cello:Virology cello:Omics cello:Characteristics 
                cello:Miscellaneous cello:ProblematicCellLine cello:Caution cello:Anecdotal cello:DonorInfo cello:Misspelling cello:Discontinuation cello:Registration) ;
            ]
        )
    ] 
    .    
        
# Define a topic data item

cello:VirologyComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Virology ;
            ]
        )
    ] .

cello:BiotechnologyComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Biotechnology ;
            ]
        )
    ] .

cello:SenescenceComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Senescence ;
            ]
        )
    ] .

cello:DoublingTime a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:DoublingTimeNI ;
            ]
        )
    ] .

cello:OmicsInfo a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Omics ;
            ]
        )
    ] .

cello:CharacteristicsComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Characteristics ;
            ]
        )
    ] .

cello:DiscontinuationRecord a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Discontinuation ;
            ]
        )
    ] .

cello:MiscellaneousInfoComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Miscellaneous ;
            ]
        )
    ] .

cello:ProblematicCellLineComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:ProblematicCellLine ;
            ]
        )
    ] .

cello:CautionComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Caution ;
            ]
        )
    ] .

cello:AnecdotalComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Anecdotal ;
            ]
        )
    ] .

cello:MisspellingRecord a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Misspelling ;
            ]
        )
    ] .

cello:DonorInfoComment a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:DonorInfo ;
            ]
        )
    ] .

cello:RegistrationRecord a owl:Class ;
    rdfs:subClassOf IAO:0000027 ;
    owl:equivalentClass [
        owl:intersectionOf (
            IAO:0000027
            [ rdf:type owl:Restriction ;
              owl:onProperty EDAM:has_topic ;
              owl:hasValue cello:Registration ;
            ]
        )
    ] .

    

"""
        return text.split("\n")



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_url(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        onto_url = self.ns.cello.url
        if onto_url.endswith("#"): onto_url = onto_url[:-1]
        return onto_url

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.prefixes


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_imported_terms(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        lines = list()
        
        allButCello = list(ns.namespaces)
        
        # remove basic ones
        allButCello.remove(ns.xsd)
        allButCello.remove(ns.rdf)
        allButCello.remove(ns.rdfs)
        allButCello.remove(ns.owl)
        allButCello.remove(ns.sh)
        allButCello.remove(ns.widoco)
        #allButCello.remove(ns.dcterms) # only some terms are hidden for the moment
        
        # remove namespaces for our data
        allButCello.remove(ns.cello)
        allButCello.remove(ns.cvcl)
        allButCello.remove(ns.db)
        allButCello.remove(ns.orga)
        allButCello.remove(ns.xref)
        
        # remove irrelevant ones
        allButCello.remove(ns.pubmed)

        for nspace in allButCello: lines.extend(self.get_terms(nspace))
        return lines
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_terms(self, nspace, owlType=None):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for id in nspace.terms:
            term: Term = nspace.terms[id]
            if owlType is None or term.isA(owlType):
                term_lines = self.ns.ttl_lines_for_ns_term(term)
                lines.extend(term_lines)
        return lines
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_terms(self, owlType=None):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.get_terms(self.ns.cello, owlType)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_pretty_ttl_lines(self, version):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        lines = list()    
        lines.extend(self.get_onto_prefixes())
        lines.append("\n#\n# Ontology properties\n#\n")
        lines.extend(self.get_onto_header(version))
        lines.append("#\n# External terms used in ontology\n#\n")
        lines.extend(self.get_imported_terms())
        lines.append("#\n# Classes defined in ontology\n#\n")
        lines.extend(self.get_onto_terms(ns.owl.Class))
        lines.append("#\n# Annotation Properties used in ontology\n#\n")
        lines.extend(self.get_onto_terms(ns.owl.AnnotationProperty))
        lines.append("#\n# Object Properties used in ontology\n#\n")
        lines.extend(self.get_onto_terms(ns.owl.ObjectProperty))
        lines.append("#\n# Datatype Properties used in ontology\n#\n")
        lines.extend(self.get_onto_terms(ns.owl.DatatypeProperty))
        lines.extend(self.get_topic_and_topic_annotations())
        return lines


# =============================================
if __name__ == '__main__':
# =============================================

    ob = OntologyBuilder(plaform=ApiPlatform("local"))
    lines = ob.get_onto_pretty_ttl_lines("dev version")
    for l in lines: print(l)
