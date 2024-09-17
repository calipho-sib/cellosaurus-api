from namespace import NamespaceRegistry as ns
from ApiCommon import log_it, split_string
from sparql_client import EndpointClient
import sys
from datetime import datetime
from tree_functions import Tree
from databases import Database, Databases, get_db_category_IRI
from cl_categories import CellLineCategory, CellLineCategories, get_cl_category_IRI
from sexes import Sex, Sexes, get_sex_IRI


#-------------------------------------------------
class OntologyBuilder:
#-------------------------------------------------


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # Note
        # we must declare in pur ontology file the external entities that are used 
        # as object of owl:equivalentProperty 
        # otherwise they are not displayed by widoco
        # we also declare claases used as object of owl:equivalentClass to be consistent

        self.imported_terms = {
            ns.wd.P3289_AC(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.DatatypeProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P3289")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.wd.P9072_OX(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.ObjectProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P9072")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.wd.P3578_OI(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.ObjectProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P3578")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.wd.P5166_DI(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.ObjectProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P5166" )} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.wd.P3432_HI(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.ObjectProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P3432")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.wd.P21_SX(): { ns.rdf.type(): { ns.rdf.Property(), ns.owl.ObjectProperty()} ,
                                ns.rdfs.label() : { ns.xsd.string("wd:P21")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.wd.prefix()}:" }} ,
            ns.org.Organization(): { ns.rdf.type(): { ns.owl.Class()} ,
                                ns.rdfs.label() : { ns.xsd.string("org:Organization")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.org.prefix()}:" }} ,
            ns.foaf.Organization(): { ns.rdf.type(): { ns.owl.Class()} ,
                                ns.rdfs.label() : { ns.xsd.string("foaf:Organization")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.foaf.prefix()}:" }} ,
            ns.up.Protein(): { ns.rdf.type(): { ns.owl.Class()} ,
                                ns.rdfs.label() : { ns.xsd.string("up:Protein")} ,
                                ns.rdfs.isDefinedBy() : { f"{ns.up.prefix()}:" }} ,
        }

        self.ontodata = {

                ns.onto.Database(): { ns.skos.closeMatch(): { ns.up.Database()}},
                ns.onto.CelloTerminology() : { ns.rdfs.subClassOf() : { ns.skos.ConceptScheme() }},

                

                ns.onto.CellLine(): { ns.skos.closeMatch(): { "<http://purl.obolibrary.org/obo/CLO_0000031>", 
                                                             "<http://id.nlm.nih.gov/mesh/D002460>",
                                                             "<https://www.wikidata.org/wiki/Q21014462>"},
                                      ns.rdfs.seeAlso(): { "<https://www.cellosaurus.org/>"}},

                ns.onto.Organization(): { ns.rdfs.subClassOf(): {ns.foaf.Agent()}, 
                                        ns.owl.equivalentClass(): { ns.foaf.Organization() , ns.org.Organization() }},

                ns.onto.city() : { ns.rdfs.subPropertyOf() : {ns.org.site() }},
                ns.onto.country() : { ns.rdfs.subPropertyOf() : {ns.org.site() }},

                ns.onto.Annotation(): { ns.rdfs.subClassOf(): {ns.oa.Annotation()}, 
                                        ns.skos.closeMatch(): { ns.up.Annotation()}},

                ns.onto.AnecdotalComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.AnatomicalElement() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.BiotechnologyComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.Breed() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.CautionComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.CellType() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.CharacteristicsComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.DiscontinuationRecord() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.Disease() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.DonorInfoComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.DoublingTimeComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.GeneticIntegration() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.GenomeAncestry() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.HLATyping() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.KaryotypicInfoComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.KnockoutComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.MabIsotype() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.MicrosatelliteInstability() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.MiscellaneousInfoComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.MisspellingComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.OmicsComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.PopulationComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
               
                #ns.onto.MabTarget() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.Protein() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }, 
                                        ns.owl.equivalentClass() : { ns.up.Protein() }},
                ns.onto.ChemicalAgent() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.Antigen() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
               
                ns.onto.SenescenceComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.SequenceVariationComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.ShortTandemRepeatProfile() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.Species() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.TransformantAgent() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},
                ns.onto.VirologyComment() : { ns.rdfs.subClassOf() : { ns.onto.Annotation() }},                

                ns.onto.Publication(): { ns.rdfs.subClassOf() : { ns.fabio.Expression() },
                                        ns.skos.closeMatch() : { ns.up.Published_Citation()} },
                ns.onto.Thesis(): { ns.rdfs.subClassOf() : { ns.onto.Publication(), ns.fabio.Thesis() },
                                    ns.skos.closeMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.BachelorThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.BachelorsThesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.MasterThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.MastersThesis()  },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.DoctoralThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.DoctoralThesis()  },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.MedicalDegreeMasterThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.MastersThesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }}, 
                ns.onto.MedicalDegreeThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis()   },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.PrivaDocentThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis()   },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.VeterinaryMedicalDegreeThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }}, 
                ns.onto.Patent(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.Patent() }},
                ns.onto.JournalArticle(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.JournalArticle() },
                                            ns.skos.closeMatch() : { ns.up.Journal_Citation() }}, 
                ns.onto.Book(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.Book()  },
                                            ns.skos.broadMatch() : { ns.up.Published_Citation() }},
                ns.onto.BookChapter(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.BookChapter() },
                                            ns.skos.closeMatch() : { ns.up.Book_Citation() }},
                ns.onto.TechnicalDocument(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.TechnicalReport() },
                                            ns.skos.broadMatch() : { ns.up.Citation() }},
                ns.onto.MiscellaneousDocument(): { ns.rdfs.subClassOf() : {ns.onto.Publication()  },
                                            ns.skos.broadMatch() : { ns.up.Citation() }},
                ns.onto.ConferencePublication(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.ConferencePaper() },
                                            ns.skos.broadMatch() : { ns.up.Published_Citation() }},

                ns.onto.GeneMutation() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation() }},
                ns.onto.RepeatExpansion() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.SimpleMutation() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.UnexplicitMutation() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.GeneFusion() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation()  }},
                ns.onto.GeneAmplification() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation() }}, 
                ns.onto.GeneDuplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneTriplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneQuarduplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneExtensiveAmplification() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification() }}, 
                ns.onto.GeneDeletion() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation()  }},


                ns.onto.datatypeAnnotation() : { ns.rdf.type(): {ns.owl.DatatypeProperty() }},
                ns.onto.objectAnnotation() : { ns.rdf.type(): {ns.owl.ObjectProperty()}},

                ns.onto.anecdotalComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.biotechnologyComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.cautionComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.cellType() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.characteristicsComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.derivedFromSite() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.discontinuationRecord() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.donorInfoComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.doublingTimeComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.fromIndividualAtAge() : { ns.rdfs.subPropertyOf() : { ns.onto.datatypeAnnotation() }},
                ns.onto.fromIndividualBelongingToBreed() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.fromIndividualBelongingToSpecies() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() },
                                                               ns.owl.equivalentProperty() : { ns.wd.P9072_OX() }},
                ns.onto.fromIndividualWithDisease() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() },
                                                        ns.owl.equivalentProperty() :{ ns.wd.P5166_DI()} },
                ns.onto.fromIndividualWithSex() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.fromSameIndividualAs() : { ns.owl.equivalentProperty(): { ns.wd.P3578_OI()}},
                
                ns.onto.geneticIntegration() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.genomeAncestry() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.hlaTyping() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.karyotypicInfoComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.knockout() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.mabIsotype() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.mabTarget() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.microsatelliteInstability() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.miscellaneousInfoComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.misspellingComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.omicsComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.parentCellLine() : { ns.owl.equivalentProperty() : { ns.wd.P3432_HI()}},
                ns.onto.populationComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.registration() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.resistance() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.senescenceComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.sequenceVariationComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.shortTandemRepeatProfile() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.transformant() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},
                ns.onto.virologyComment() : { ns.rdfs.subPropertyOf() : { ns.onto.objectAnnotation() }},

                ns.onto.publisher() : { ns.rdfs.subPropertyOf() : { ns.dcterms.publisher() }},
                ns.onto.editor() : { ns.rdfs.subPropertyOf() : { ns.dcterms.contributor() }},
                
                ns.onto.accession(): { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), 
                                                                   ns.skos.notation() }},
                ns.onto.primaryAccession(): { ns.rdfs.subPropertyOf() : { ns.onto.accession() },
                                              ns.owl.equivalentProperty(): {ns.wd.P3289_AC() }},
                ns.onto.secondaryAccession(): { ns.rdfs.subPropertyOf() : { ns.onto.accession() }},

                ns.onto.name() : { ns.rdfs.subPropertyOf() : { ns.foaf.name() }},
                ns.onto.registeredName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.misspellingName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.populationName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.shortname() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.recommendedName() : { ns.rdfs.subPropertyOf() : { ns.skos.prefLabel(), ns.onto.name() }},
                ns.onto.alternativeName() : { ns.rdfs.subPropertyOf() : { ns.skos.altLabel(), ns.onto.name() }},

                ns.onto.creator() : { ns.rdfs.subPropertyOf() : { ns.dcterms.creator() }},

                ns.onto.title() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }, 
                                    ns.skos.closeMatch(): { ns.up.title() }},
                ns.onto.bookTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.documentTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.conferenceTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.documentSerieTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                
                ns.onto.memberOf() : { ns.rdfs.subPropertyOf() : { ns.org.memberOf() }},
                ns.onto.more_specific_than() : { ns.rdfs.subPropertyOf() : { ns.skos.broader() }},

                ns.onto.hasPublicationYear() : { ns.rdfs.subPropertyOf(): { ns.fabio.hasPublicationYear() }},
                ns.onto.productId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.issn13() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.hasDOI() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.bibo.doi() }},
                ns.onto.hasInternalId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.hasPMCId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.fabio.hasPubMedCentralId() }},
                ns.onto.hasPubMedId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.fabio.hasPubMedId() }},
                ns.onto.hgvs() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.volume() : { ns.rdfs.subPropertyOf() : { ns.up.volume() }},

                ns.onto.hasVersion() : { ns.rdfs.subPropertyOf(): { ns.dcterms.hasVersion() } , ns.skos.closeMatch(): { ns.up.version() }},
                ns.onto.modified() : { ns.rdfs.subPropertyOf(): { ns.dcterms.modified() } , ns.skos.closeMatch(): { ns.up.modified() }},
                ns.onto.created() : { ns.rdfs.subPropertyOf(): { ns.dcterms.created() } , ns.skos.closeMatch(): { ns.up.created() }},
                
            }
        
        # we add programmaticaly here to self.ontodata the subClassOf relationships between Database and its children
        # so that we can take advantage of close_parent_set() method during computation of domain / ranges of related properties
        databases = Databases()
        for k in databases.categories():
            cat = databases.categories()[k]
            cat_IRI = get_db_category_IRI(cat["label"])
            self.ontodata[cat_IRI] = { ns.rdfs.subClassOf(): {ns.onto.Database()} }

        # we also add programmaticaly here to self.ontodata the subClassOf relationships between CellLine and its children
        cl_cats = CellLineCategories()
        for k in cl_cats.keys():
            cat : CellLineCategory = cl_cats.get(k)
            self.ontodata[cat.IRI] = { ns.rdfs.subClassOf(): {ns.onto.CellLine()} }

        # we also add programmaticaly here to self.ontodata the subClassOf relationships between Sex and its children
        # NOTE: currently represented as NamedIndividual
        # sexes = Sexes()
        # for k in sexes.keys():
        #     sex : Sex = sexes.get(k)
        #     self.ontodata[sex.IRI] = { ns.rdfs.subClassOf(): {ns.onto.Sex()} }


        # NOW build tree with local child - parent relationships based on rdfs:subClassOf()
        edges = dict()
        for child in self.ontodata:
            child_rec = self.ontodata.get(child) or {}
            parents = child_rec.get(ns.rdfs.subClassOf()) or {}
            for parent in parents:
                if self.term_is_local(parent): 
                    edges[child]=parent
        self.tree = Tree(edges)                    

        lines = list()
        for this_ns in ns.namespaces: lines.append(this_ns.getSparqlPrefixDeclaration())
        prefixes = "\n".join(lines)

        self.client = EndpointClient("http://localhost:8890/sparql")

        self.domain_query_template = prefixes + """
            select ?prop ?value (count(distinct ?s) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                ?s rdf:type ?value .
            }
            group by ?prop ?value
            """
        
        self.range_query_template = prefixes + """
            select  ?prop ?value (count(*) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                optional { ?o rdf:type ?cl . }
                BIND(
                IF (bound(?cl) , ?cl,  IF ( isIRI(?o), 'rdfs:Resource', datatype(?o))
                ) as ?value)
            }
            group by ?prop ?value
            """

        

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # domain / ranges to remove
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_domain_to_remove = dict()
        self.rdfs_domain_to_remove[ns.onto.accession()] = { ns.skos.Concept() }
        #self.rdfs_domain_to_remove[ns.onto.category()] = { ns.skos.Concept(), ns.owl.NamedIndividual()  }
        self.rdfs_domain_to_remove[ns.onto.database()] = { ns.skos.Concept()  }
        self.rdfs_domain_to_remove[ns.onto.hasVersion()] = { ns.owl.NamedIndividual() }
        self.rdfs_domain_to_remove[ns.onto.shortname()] = { ns.owl.NamedIndividual() }
        self.rdfs_domain_to_remove[ns.onto.more_specific_than()] = { ns.onto.Xref()  }

        self.rdfs_range_to_remove = dict()
        self.rdfs_range_to_remove[ns.onto.xref()] = { ns.skos.Concept() }
        self.rdfs_range_to_remove[ns.onto.more_specific_than()] = { ns.onto.Xref() } 
        self.rdfs_range_to_remove[ns.onto.database()] = { ns.owl.NamedIndividual(), ns.onto.CelloTerminology() } 
        self.rdfs_range_to_remove[ns.onto.genomeEditingMethod()] = { ns.owl.NamedIndividual() } 
        self.rdfs_range_to_remove[ns.onto.fromIndividualWithSex()] = { ns.owl.NamedIndividual() }



        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # non default labels for classes and properties
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_label = dict()
        self.rdfs_label[ns.onto.HLATyping()] = "HLA typing"
        self.rdfs_label[ns.onto.hlaTyping()] = "has HLA typing"
        self.rdfs_label[ns.onto.MabIsotype()] = "Monoclonal antibody isotype"
        #self.rdfs_label[ns.onto.MabTarget()] = "Monoclonal antibody target"
        self.rdfs_label[ns.onto.mabIsotype()] = "has monoclonal antibody isotype"
        self.rdfs_label[ns.onto.mabTarget()] = "has monoclonal antibody target"
        self.rdfs_label[ns.onto.hasPMCId()] = "has PMC identifier"
        self.rdfs_label[ns.onto.hasPubMedId()] = "has PubMed identifier"
        self.rdfs_label[ns.onto.hasDOI()] = "has DOI identifier"
        self.rdfs_label[ns.onto.msiValue()] = "has microsatellite instability value"
        self.rdfs_label[ns.onto.productId()] = "product identifier"
        self.rdfs_label[ns.onto.xref()] = "has cross-reference"
        self.rdfs_label[ns.onto.Xref()] = "Cross-reference"
        self.rdfs_label[ns.onto.CelloTerminology()] = "Cellosaurus terminology"


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # comments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.rdfs_comment = dict()
        # comments for classes
        self.rdfs_comment[ns.onto.CellLine()] = "Cell line as defined in the Cellosaurus"
        # comments for props
        self.rdfs_comment[ns.onto.recommendedName()] = "Most frequently the name of the cell line as provided in the original publication"
        self.rdfs_comment[ns.onto.alternativeName()] = "Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"
        self.rdfs_comment[ns.onto.more_specific_than()] = "Links two concepts. The subject concept is more specific than the object concept. The semantics is the similar to the skos:broader property but its label less ambiguous."
        self.rdfs_comment[ns.onto.CelloTerminology()] = "Class of cellosaurus terminologies containing some concepts used for annotating cell lines."


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_label(self, str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if str in self.rdfs_label:
            return self.rdfs_label[str]
        else:
            return self.build_default_label(str)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_default_label(self, prefixed_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if ":" in prefixed_name:
            str = prefixed_name.split(":")[1]
        else:
            str = prefixed_name

        # 1) insert space instead of "_" and on case change  
        chars = list()
        wasupper = False
        for ch in str:
            if ch.isupper() and not wasupper and len(chars)>0:
                chars.append(" ")
                chars.append(ch)
            elif ch == "_":
                chars.append(" ")
            else:
                chars.append(ch)
            wasupper = ch.isupper()
        sentence = "".join(chars).replace("  ", " ")
        words = sentence.split(" ")

        # 2) lower all words except first and those having all chars uppercase
        first = True
        new_words = list()
        for w in words:
            if first:
                first = False
                new_words.append(w)
            else:
                allUpper = True
                for ch in w:
                    if ch.islower(): allUpper = False
                if allUpper:
                    new_words.append(w)
                else:
                    new_words.append(w.lower())

        return " ".join(new_words)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_url(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        onto_url = ns.onto.baseurl()
        if onto_url.endswith("#"): onto_url = onto_url[:-1]
        return onto_url


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_imported_terms(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        lines.append("#")
        lines.append("# External terms used as equivalent class or property in this ontology")
        lines.append("#")
        lines.append("")
        for s in self.imported_terms:
            lines.append(s)
            s_data = self.imported_terms[s]
            for p in s_data:
                p_data = s_data[p]
                for o in p_data:
                    lines.append(f"    {p} {o} ;")
            lines.append("    .")
            lines.append("")
        return lines

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_header(self, version="alpha"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()

        # append prefixes fefined in our namespace
        for this_ns in ns.namespaces: lines.append(this_ns.getTtlPrefixDeclaration())
        lines.append("")

        # set last modification date for ontology
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        
        # set ontology URL
        onto_url = "<" + self.get_onto_url() + ">"
        
        # set ontology description
        onto_descr = """The Cellosaurus ontology describes the concepts used to build the Cellosaurus knowledge resource on cell lines. 
        The Cellosaurus attempts to describe all cell lines used in biomedical research."""
        
        # set ontology abstract
        onto_abstract = onto_descr

        # set preferred prefix for ontology
        onto_prefix = "cls" 

        # set ontology introduction
        onto_intro = onto_descr

        # Note: all the prefixes are declared in namespace.py but not necessarily all the properties because used only once...
        lines.append(onto_url)
        lines.append("    a " + ns.owl.Ontology() + " ;")
        lines.append("    " + ns.rdfs.label() + " " + ns.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    " + ns.dcterms.created() + " " + ns.xsd.date("2024-07-30") + " ;")
        lines.append("    " + ns.dcterms.modified() + " " + ns.xsd.date(date_string) + " ;")
        lines.append("    " + ns.dcterms.description() + " " + ns.xsd.string3(onto_descr) + " ;")
        lines.append("    " + ns.dcterms.license() + " <http://creativecommons.org/licenses/by/4.0> ;")
        lines.append("    " + ns.dcterms.title() + " " + ns.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    " + ns.dcterms.hasVersion() + " " + ns.xsd.string(version) + " ;")
        lines.append("    " + ns.owl.versionInfo() + " " + ns.xsd.string(version) + " ;")
        lines.append("    " + ns.dcterms.abstract() + " " + ns.xsd.string3(onto_abstract) + " ;")
        lines.append("    " + ns.vann.preferredNamespacePrefix() + " " + ns.xsd.string(onto_prefix) + " ;")
        lines.append("    " + ns.bibo.status() + " <http://purl.org/ontology/bibo/status/published> ;")
        lines.append("    " + ns.widoco.introduction() + " " + ns.xsd.string3(onto_intro) + " ;")
        lines.append("    " + ns.rdfs.seeAlso() + " " + ns.help.IRI("index-en.html") + " ;")      
        lines.append("    " + ns.widoco.rdfxmlSerialization() + " " + ns.help.IRI("ontology.owl") + " ;")      
        lines.append("    " + ns.widoco.ntSerialization() + " " + ns.help.IRI("ontology.nt") + " ;")      
        lines.append("    " + ns.widoco.turtleSerialization() + " " + ns.help.IRI("ontology.ttl") + " ;")      
        lines.append("    " + ns.widoco.jsonldSerialization() + " " + ns.help.IRI("ontology.jsonld") + " ;")      
        lines.append("    .")
        lines.append("")
        return lines


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_classes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology Classes", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        for method_name in dir(ns.onto):
            if callable(getattr(ns.onto, method_name)):
                if method_name[0].isupper():
                    #print("method name", method_name)
                    method = getattr(ns.onto, method_name)
                    class_name = method()
                    #print("class_name", class_name)
                    lines.append(class_name)
                    lines.append(f"    rdf:type owl:Class ;")
                    class_label =  ns.xsd.string(self.build_label(class_name))
                    lines.append(f"    rdfs:label {class_label} ;")

                    for p in self.ontodata.get(class_name) or {}:
                        for o in self.ontodata[class_name][p]:
                            lines.append(f"    {p} {o} ;")

                    class_comment = self.rdfs_comment.get(class_name)
                    if class_comment is not None:
                        class_comment =  ns.xsd.string(class_comment)
                        lines.append(f"    rdfs:comment {class_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")
                    lines.append("    .")
                    lines.append("")
        return lines
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term_is_local(self, term):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return term.startswith(":")


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_props(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology properties", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        prop_count = 0
        for method_name in dir(ns.onto):
            if callable(getattr(ns.onto, method_name)):
                if method_name[0].islower():
                    # skip those below, they are not ontology terms but helper functions of the super class
                    if method_name in ["prefix", "baseurl", "getTtlPrefixDeclaration", "getSparqlPrefixDeclaration", "getSQLforVirtuoso"]: continue 
                    method = getattr(ns.onto, method_name)
                    prop_name = method()
                    prop_label =  ns.xsd.string(self.build_label(prop_name))
                    prop_comment = self.rdfs_comment.get(prop_name)

                    #if prop_count > 10: break
                    prop_count += 1

                    log_it("DEBUG", "querying prop_name", prop_name, "domains")
                    domain_dic = dict()
                    domain_query = self.domain_query_template.replace("$prop", prop_name)
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

                    log_it("DEBUG", "querying prop_name", prop_name, "ranges")
                    range_dic = dict()
                    range_query = self.range_query_template.replace("$prop", prop_name)
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

                    # prop type
                    prop_types = set() # we should have a single item in this set (otherwise OWL reasoners dislike it)
                    for r in range_dic:
                        if r.startswith("xsd:") or r == ns.rdfs.Literal(): 
                            prop_types.add("owl:DatatypeProperty") 
                        else:
                            prop_types.add("owl:ObjectProperty") 
                    lines.append(prop_name)
                    lines.append("    a rdf:Property ;")
                    for typ in prop_types: lines.append("    a " + typ + " ;")

                    #prop label, comment, definition
                    lines.append(f"    rdfs:label {prop_label} ;")
                    if prop_comment is not None:
                        prop_comment =  ns.xsd.string(prop_comment)
                        lines.append(f"    rdfs:comment {prop_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")

                    # add props declared in onto data
                    for p in self.ontodata.get(prop_name) or {}:
                        for o in self.ontodata[prop_name][p]:
                            lines.append(f"    {p} {o} ;")

                    # ttl comment about domain classes found in data
                    tmp = ["domain classes found in data are"]
                    for k in domain_dic: tmp.append(f"{k}({domain_dic[k]})")
                    for line in split_string(" ".join(tmp), 120):
                        lines.append("#   " + line)

                    # prop domain definition
                    domain_set = set(domain_dic.keys())
                    if len(domain_set)>3: 
                        domain_set = self.tree.get_close_parent_set(domain_set)
            
                    for domain_to_remove in self.rdfs_domain_to_remove.get(prop_name) or {}:
                        domain_set = domain_set - { domain_to_remove }

                    if len(domain_set)==1:
                        name = domain_set.pop()
                        line = "    rdfs:domain " + name + " ;"
                        lines.append(line)
                    elif len(domain_set)>1:
                        lines.append("    rdfs:domain [ a owl:Class ; owl:unionOf (")
                        for name in domain_set:
                            line = "        " + name
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    # ttl comment about prop range
                    tmp = ["range classes found in data are"]
                    for k in range_dic: tmp.append(f"{k}({range_dic[k]})")
                    for line in split_string(" ".join(tmp), 120):
                        lines.append("#   " + line)

                    # prop range definition
                    range_set = set(range_dic.keys())
                    if len(range_set)>3:
                        range_set = self.tree.get_close_parent_set(range_set)

                    # hack to replace xsd:date with rdfs:Literal to be OWL2 frienly                    
                    if ns.xsd.dateDataType() in range_set:
                        range_set = range_set - { ns.xsd.dateDataType() }
                        range_set.add(ns.rdfs.Literal())
                        
                    for range_to_remove in self.rdfs_range_to_remove.get(prop_name) or {}:
                        range_set = range_set - { range_to_remove } 

                    if len(range_set)==1:
                        name = range_set.pop()
                        line = "    rdfs:range " + name + " ;"
                        lines.append(line)
                    elif len(range_set)>1:
                        lines.append("    rdfs:range [ a owl:Class ; owl:unionOf (")
                        for name in range_set:
                            line = "        " + name
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    lines.append("    .")
                    lines.append("")

        return lines


# --------------------------------------------
if __name__ == '__main__':
# --------------------------------------------

    # print(ontodata)
    # builder = OntologyBuilder()
    # node_set = {
    #     #":GeneMutation",
    #     #":Patent",
    #     #":MedicalDegreeThesis", 
    #     #":MedicalDegreeMasterThesis",
    #     #":DoctoralThesis",
    #     #":MasterThesis",
    #     #":TechnicalDocument", 
    #     #":BachelorThesis", 
    #     #":VeterinaryMedicalDegreeThesis",
    #     #":ConferencePublication",
    #     #":BookChapter",
    #     #":PrivaDocentThesis",
    #     #":Book",
    #     #":MiscellaneousDocument",
    #     #":JournalArticle"
    # }
    # result = builder.tree.get_close_parent_set(node_set)
    # print(result)
    # # c1 = ns.onto.BachelorThesis()
    # # c2 = ns.onto.Publication()
    # # c3 = ns.onto.AnatomicalElement()
    # # print(builder.tree.get_close_parent_set({c1,c2,c3}))    
    # #print("remote root if thesis", builder.get_root_ancestors(ns.onto.Thesis(), locality=False))
    # sys.exit()

    builder = OntologyBuilder()
    # tests
    if 1==2:
        print(builder.build_label("this_is_DNA"))
        print(builder.build_label(ns.onto.mabIsotype()))
        print(builder.build_label(ns.onto.hasDOI()))
        print(builder.build_label(ns.onto.cvclEntryCreated()))
        print(builder.build_label(ns.onto.hlaTyping()))
        print(builder.build_label(ns.onto.HLATyping()))
        print(builder.build_label(ns.onto.AnecdotalComment()))
        print(builder.build_label(ns.onto.anecdotalComment()))

        print(builder.get_root_ancestor(ns.onto.Publication()))
        print(builder.get_root_ancestor(ns.onto.MedicalDegreeMasterThesis()))
        print(builder.get_root_ancestor(ns.onto.AnecdotalComment()))

    # real ontology generation
    else:  
        lines = list()
        lines.extend(builder.get_onto_header(version="1.0"))
        lines.extend(builder.get_imported_terms())
        lines.extend(builder.get_classes())
        lines.extend(builder.get_props())
        for line in lines: print(line)