from namespaces import BaseNamespace, get_rdf_base_IRI

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CelloOntologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CelloOntologyNamespace, self).__init__("cello", get_rdf_base_IRI() + "/ontology/")

        #
        # Classes
        #

        # Publication classes 
        self.Publication = self.registerClass("Publication")                                    # described
        self.MedicalDegreeThesis = self.registerClass("MedicalDegreeThesis")                    # described
        self.MedicalDegreeMasterThesis = self.registerClass("MedicalDegreeMasterThesis")        # described
        self.PrivaDocentThesis = self.registerClass("PrivaDocentThesis")                        # described
        self.VeterinaryMedicalDegreeThesis = self.registerClass("VeterinaryMedicalDegreeThesis")# described
        self.TechnicalDocument = self.registerClass("TechnicalDocument")                        # described
        self.MiscellaneousDocument = self.registerClass("MiscellaneousDocument")                # described

        # entites commented below are replaced with fabio classes (see FabioNamespace)
        #self.JournalArticle = self.registerClass("JournalArticle")              # described, defined if fabio namespace
        #self.Patent = self.registerClass("Patent")                              # described, defined if fabio namespace
        #self.Thesis = self.registerClass("Thesis")                              # described, defined if fabio namespace
        #self.BachelorThesis = self.registerClass("BachelorThesis")              # described, defined if fabio namespace
        #self.MasterThesis = self.registerClass("MasterThesis")                  # described, defined if fabio namespace
        #self.DoctoralThesis = self.registerClass("DoctoralThesis")              # described, defined if fabio namespace
        #self.Book = self.registerClass("Book")                                  # described, defined if fabio namespace
        #self.BookChapter = self.registerClass("BookChapter")                    # described, defined if fabio namespace
        #self.ConferencePublication = self.registerClass("ConferencePublication")    # described, defined if fabio namespace


        # cell line classes with label as found in cellosaurus.txt
        comment = "A population of cells that originates from a primary culture, adapted to grow and divide under laboratory conditions. Used in biotechnology to consistently produce biological substances"
        self.CellLine = self.registerClass("CellLine", comment=comment) # with human readable var name because used at several locations
        self.CancerCellLine = self.registerClass("CancerCellLine")
        self.ConditionallyImmortalizedCellLine = self.registerClass("ConditionallyImmortalizedCellLine")
        self.EmbryonicStemCell = self.registerClass("EmbryonicStemCell")
        self.FactorDependentCellLine = self.registerClass("FactorDependentCellLine")
        self.FiniteCellLine = self.registerClass("FiniteCellLine")
        self.HybridCellLine = self.registerClass("HybridCellLine")
        self.Hybridoma = self.registerClass("Hybridoma")
        self.InducedPluripotentStemCell = self.registerClass("InducedPluripotentStemCell")
        self.SomaticStemCell = self.registerClass("SomaticStemCell")
        self.SpontaneouslyImmortalizedCellLine = self.registerClass("SpontaneouslyImmortalizedCellLine")
        self.StromalCellLine = self.registerClass("StromalCellLine")
        self.TelomeraseImmortalizedCellLine = self.registerClass("TelomeraseImmortalizedCellLine")
        self.TransformedCellLine = self.registerClass("TransformedCellLine")


        # described as sub of OBI class with owl:oneOf local NIs defined below (see onto builder)
        self.GenomeModificationMethod = self.registerClass("GenomeModificationMethod", hidden=True)       
        # Genome modification method individuals
        # which are instances of external classes
        self.GenomeModificationMethodNOS = self.registerNamedIndividual("GenomeModificationMethodNOS", label="Genome modification method NOS")   
        self.CrispCas9 = self.registerNamedIndividual("CrispCas9", label="CRISPR/Cas9")   
        self.XRay = self.registerNamedIndividual("XRay", label="X-ray")                                  
        self.GammaRadiation = self.registerNamedIndividual("GammaRadiation", label="Gamma radiation")                         
        self.Transfection = self.registerNamedIndividual("Transfection", label="Transfection")   
        self.Mutagenesis = self.registerNamedIndividual("Mutagenesis", label="Mutagenesis")
        self.SiRNAKnockdown = self.registerNamedIndividual("SiRNAKnockdown", label="siRNA knockdown")
        self.TALEN = self.registerNamedIndividual("TALEN", label="TALEN")
        self.ZFN = self.registerNamedIndividual("ZFN", label="ZFN")
        self.GeneTrap = self.registerNamedIndividual("GeneTrap", label="Gene trap")
        self.Transduction = self.registerNamedIndividual("Transduction", label="Transduction")
        # which are instances of local classes
        self.BacHomologousRecombination = self.registerNamedIndividual("BacHomologousRecombination", label="BAC homologous recombination")                    # described
        self.CreLoxp = self.registerNamedIndividual("CreLoxp", label="Cre/loxP")                                                                              # described
        self.CrisprCas9N = self.registerNamedIndividual("CrisprCas9N", label="CRISPR/Cas9n")                                                                  # described
        self.EbvBasedVectorSirnaKnockdown = self.registerNamedIndividual("EbvBasedVectorSirnaKnockdown", label="EBV-based vector siRNA knockdown")            # described
        self.FloxingCreRecombination = self.registerNamedIndividual("FloxingCreRecombination", label="Floxing/Cre recombination")                             # described
        self.GeneTargetedKoMouse = self.registerNamedIndividual("GeneTargetedKoMouse", label="Gene-targeted KO mouse")                                        # described
        self.HelperDependentAdenoviralVector = self.registerNamedIndividual("HelperDependentAdenoviralVector", label="Helper-dependent adenoviral vector")    # described
        self.HomologousRecombination = self.registerNamedIndividual("HomologousRecombination", label="Homologous recombination")                              # described
        self.KnockoutFirstConditional = self.registerNamedIndividual("KnockoutFirstConditional", label="Knockout-first conditional")                          # described
        self.KoMouse = self.registerNamedIndividual("KoMouse", label="KO mouse")                                                              # described
        self.KoPig = self.registerNamedIndividual("KoPig", label="KO pig")                                                                    # described
        self.MirnaKnockdown = self.registerNamedIndividual("MirnaKnockdown", label="miRNA knockdown")                                         # described
        self.NullMutation = self.registerNamedIndividual("NullMutation", label="Null mutation")                                               # described
        self.PElement = self.registerNamedIndividual("PElement", label="P-element")                                                           # described
        self.PiggybacTransposition = self.registerNamedIndividual("PiggybacTransposition", label="PiggyBac transposition")                    # described
        self.PrimeEditing = self.registerNamedIndividual("PrimeEditing", label="Prime editing")                                               # described
        self.PromoterlessGeneTargeting = self.registerNamedIndividual("PromoterlessGeneTargeting", label="Promoterless gene targeting")       # described
        self.RecombinantAdenoAssociatedVirus = self.registerNamedIndividual("RecombinantAdenoAssociatedVirus", label="Recombinant Adeno-Associated Virus")    # described
        self.ShrnaKnockdown = self.registerNamedIndividual("ShrnaKnockdown", label="shRNA knockdown")                                                         # described
        self.SleepingBeautyTransposition = self.registerNamedIndividual("SleepingBeautyTransposition", label="Sleeping Beauty transposition")                 # described
        self.SpontaneousMutation = self.registerNamedIndividual("SpontaneousMutation", label="Spontaneous mutation")                          # described
        self.TargetedIntegration = self.registerNamedIndividual("TargetedIntegration", label="Targeted integration")                          # described
        self.TransductionTransfection = self.registerNamedIndividual("TransductionTransfection", label="Transduction/transfection")           # described
        self.TransfectionTransduction = self.registerNamedIndividual("TransfectionTransduction", label="Transfection/transduction")           # described
        self.TransgenicFish = self.registerNamedIndividual("TransgenicFish", label="Transgenic fish")                                         # described
        self.TransgenicMouse = self.registerNamedIndividual("TransgenicMouse", label="Transgenic mouse")                                      # described
        self.TransgenicRat = self.registerNamedIndividual("TransgenicRat", label="Transgenic rat")                                            # described


        self.Database = self.registerClass("Database")                          # described

        comment="Class of cellosaurus terminologies containing some concepts used for annotating cell lines."
        self.CelloConceptScheme = self.registerClass("CelloConceptScheme", label="Cellosaurus Concept Scheme", comment=comment)      # described
        
        # self.Organization = self.registerClass("Organization")                  # described, defined in schema namespace

        self.Xref = self.registerClass("Xref", "Cross-Reference")                                  # described as NCIT:C43621 subclass
        self.GenomeAncestry = self.registerClass("GenomeAncestry")              # described as OBI:0001225 subclass
        self.PopulationPercentage = self.registerClass("PopulationPercentage")  # LATER: define as restriction


        self.HLATyping = self.registerClass("HLATyping", label="HLA Typing")    # described as OBI:0001404 subclass
        self.Gene = self.registerClass("Gene")                                  # described as equivalent as NCIt:C16612
        self.HLAGene = self.registerClass("HLAGene", label="HLA Gene")          # described as cello:Gene subclass
        self.HLA_Allele = self.registerClass("HLAAllele", label="HLA Allele")   # described as GENO:0000512 subclass, used in HLA, str and later in genetic integration

        #self.Locus = self.registerClass("Locus")                                        # unused: descrided as equivalent of NCIt.C45822, used in STR profile    
        self.STR_Allele = self.registerClass("STRAllele", label="STR Allele")           # described as GENO:0000512 subclass
        comment = "Area of repetitive DNA within the genome consisting of multiple, end-to-end copies of a short DNA sequence usually comprised of di-, tri-, or tetranucleotide repeat units."
        self.Marker = self.registerClass("Marker", label="Marker", comment=comment)  # described as owl:equal NCIT:C13441(Short Tandem Repeat)
        self.ShortTandemRepeatProfile = self.registerClass("ShortTandemRepeatProfile")  # described as subClass of OBI:0001404
        self.hasTarget = self.registerObjectProperty("hasTarget")                       # described as subProp of schema:obserationAbout
        
        comment = "A chemical entity is a physical entity of interest in chemistry including molecular entities, parts thereof, and chemical substances."
        self.ChemicalEntity = self.registerClass("ChemicalEntity", comment=comment)     # defined as equiv of CHEBI:24431: instances are drugbank, ncit, chebi xrefs (+free text)

        comment = "A biological macromolecule minimally consisting of one polypeptide chain synthesized at the ribosome."
        self.Protein = self.registerClass("Protein", comment=comment)                   # defined as CHEBI:36080, a child of CHEBI:24431

        comment="A protein complex that consists of two heavy chains (gamma, alpha, delta, epsilon or mu). The larger of the two immunoglobulin chain types determines the immunoglobulin class (G, A, D, E or M, respectively). The heavy chain molecules exhibit the same structure and composition, which consists of constant, variable, and hypervariable regions."
        self.ImmunoglobulinHeavyChain = self.registerClass("ImmunoglobulinHeavyChain", comment=comment)

        comment="A protein complex that consists of two light chains (kappa and lambda). The light chain molecules are of the same structure and composition, consisting of constant, variable, and hypervariable regions."
        self.ImmunoglobulinLightChain = self.registerClass("ImmunoglobulinLightChain", comment=comment)

        #self.TransformantAgent = self.registerClass("TransformantAgent")       # synonym of CHEBI:24431, instances are ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)

        self.GeneKnockout = self.registerClass("GeneKnockout")                          # described as child of OBI:0001364 : characteristics of genetic alteration
        self.GeneticIntegration = self.registerClass("GeneticIntegration")              # described as child of OBI:0001364 : characteristics of genetic alteration
        self.SequenceVariationComment = self.registerClass("SequenceVariationComment")  # described as child of OBI:0001364 : characteristics of genetic alteration
        # - - - gene variation classes - - -
        comment = "A variation in or modification of the molecular sequence of a gene or gene product." 
        self.SequenceVariation = self.registerClass("SequenceVariation", comment=comment)          # generic class, described as owl:Equiv NCIt:C36391
        comment="An increase in the copy number of a particular gene. This type of abnormality can be either inherited or somatic"
        self.GeneAmplification = self.registerClass("GeneAmplification", comment=comment)          # described as owl:Equiv NCIt:C45581
        comment="A deletion that results in the loss of a DNA segment encompassing an entire gene sequence"
        self.GeneDeletion = self.registerClass("GeneDeletion", comment=comment)                    # described as owl:Equiv NCIt:C...
        comment="Any hybrid gene formed from two previously separate genes. Such fusions occur as a result of translocation, intersititial deletion or chromosomal inversion, and often result in gene products with functions different from the two fusion partners. Gene fusions are associated frequently with hematological cancers, sarcomas and prostate cancer"
        self.GeneFusion = self.registerClass("GeneFusion", comment=comment)                        # described as owl:Equiv NCIt:C...
        comment="The result of any gain, loss or alteration of the sequences comprising a gene, including all sequences transcribed into RN"
        self.GeneMutation = self.registerClass("GeneMutation", comment=comment)                    # described as owl:Equiv NCIt:C...
        #
        self.GeneDuplication = self.registerClass("GeneDuplication")            # described as child of gene amplification
        self.GeneTriplication = self.registerClass("GeneTriplication")          # described as child of gene amplification
        self.GeneQuadruplication = self.registerClass("GeneQuadruplication")    # described as child of gene amplification
        self.GeneExtensiveAmplification = self.registerClass("GeneExtensiveAmplification")  # described as child of gene amplification
        self.RepeatExpansion = self.registerClass("RepeatExpansion")            # described as child of gene mutation
        #self.SimpleMutation = self.registerClass("SimpleMutation")              # unused 
        #self.UnexplicitMutation = self.registerClass("UnexplicitMutation")      # unused
        # - - - 
        comment = "A part of a cellular organism that is either an immaterial entity or a material entity with granularity above the level of a protein complex. Or, a substance produced by a cellular organism with granularity above the level of a protein complex."
        self.AnatomicalEntity = self.registerClass("AnatomicalEntity", comment=comment)        # defined as equiv CARO:0000000
        comment="A material entity of anatomical origin (part of or deriving from an organism) that has as its parts a maximally connected cell compartment surrounded by a plasma membrane. The definition of cell is intended to represent all cells, and thus a cell is defined as a material entity and not an anatomical structure, which implies that it is part of an organism (or the entirety of one)."
        self.CellType = self.registerClass("CellType", comment=comment)                          # defined as equiv to CL:0000000

        self.Disease = self.registerClass("Disease")                            # described as superclass of ORDO clinical entity and NCIt disorder
        self.Species = self.registerClass("Species")                            # described as subClassOf NCIt taxon
        comment="A group of animals homogeneous in appearance and other characteristics that distinguish it from other animals of the same species."
        self.Breed = self.registerClass("Breed", comment=comment)               # described as equivalent of NCIt corresponding class

        self.Population = self.registerClass("Population")                          # described as child of OBI_0000181

        self.KaryotypicInfoComment = self.registerClass("KaryotypicInfoComment")    # described as subclass of OBI:Genetic info & equiv as OBI:Karyotype info
        self.MicrosatelliteInstability = self.registerClass("MicrosatelliteInstability")    # described as subclass of OBI:Genetic info

        self.GeneralTopic = self.registerClass("GeneralTopic")
        self.BiotechnologyComment = self.registerClass("BiotechnologyComment")          # described as a Data iterm cello:GeneralTopic
        self.SenescenceComment = self.registerClass("SenescenceComment")                # described as an IAO:Topic
        self.DoublingTimeComment = self.registerClass("DoublingTimeComment")            # described as an IAO:Topic
        self.VirologyComment = self.registerClass("VirologyComment")                    # described as an IAO:Topic
        self.OmicsComment = self.registerClass("OmicsComment")                          # described as an IAO:Topic
        self.CharacteristicsComment = self.registerClass("CharacteristicsComment")      # described as an IAO:Topic
        self.MiscellaneousInfoComment = self.registerClass("MiscellaneousInfoComment")  # described as an IAO:Topic
        self.CautionComment = self.registerClass("CautionComment")                      # described as an IAO:Topic
        self.AnecdotalComment = self.registerClass("AnecdotalComment")                  # described as an IAO:Topic
        self.MisspellingRecord = self.registerClass("MisspellingRecord")                # described as an IAO:Topic
        self.DonorInfoComment = self.registerClass("DonorInfoComment")                  # described as an IAO:Topic
        self.DiscontinuationRecord = self.registerClass("DiscontinuationRecord")        # described as an IAO:Topic
        self.RegistrationRecord = self.registerClass("RegistrationRecord")              # described as an IAO:Topic


        #self.MabTarget = self.registerClass("MabTarget")
        self.MabIsotype = self.registerClass("MabIsotype", label="Monoclonal antibody isotype") # TODO:0

        # next 3 lines as some kind of experiment result
        self.detectedTarget = self.registerDatatypeProperty("detectedTarget")           # TODO later
        self.detectedAllele = self.registerObjectProperty("detectedAllele")             # TODO: later
        self.repeatNumber = self.registerDatatypeProperty("repeatNumber")               # TODO: later, question: separate number dand variant id ?

        self.conflicting = self.registerDatatypeProperty("conflicting")                 # TODO: later

        self.Sex = self.registerClass("Sex")                                            # TODO: later, has some special cases like mixed sex

        comment = "An entity which is used as a source of information, mostly originating from a cross-reference, a publication or an organization."
        self.Source = self.registerClass("Source", comment=comment)                     # TODO: later, a wrapper of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)


        #
        # Properties
        #

        # publication properties
        # see also https://sparontologies.github.io/fabio/current/fabio.html
        # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html


        self.internalId = self.registerDatatypeProperty("internalId", label="internal identifier")        # described as sub dcterms:identifier

        self.pmcId = self.registerDatatypeProperty("pmcId", label="pmcId")      # described as sub prop of fabio:haspmcid which is a subprop of dcterms:identifier
        self.pmid = self.registerDatatypeProperty("pmid", label="pmid")                          # described as sub prop of fabio:haspmid which is a subprop of dcterms:identifier
        self.publicationYear = self.registerDatatypeProperty("publicationYear", label="publication year")             # described as sub prop of fabio:hasPublicationYear

        self.issn13 = self.registerDatatypeProperty("issn13", label="ISSN13")                                   # described as sub dcterms:identifier

        comment="An identifier for a particular volume of a resource, such as a journal or a multi-volume book."
        self.volume = self.registerDatatypeProperty("volume", comment=comment)             # described as sub of prism:volume which is sub of dcterms:identifier  
        self.doi = self.registerDatatypeProperty("doi", label="DOI")                # described as sub of prism:volume which is sub of dcterms:identifier
        self.publicationDate = self.registerDatatypeProperty("publicationDate", label="publication date")   # described as sub of prism term
        self.startingPage = self.registerDatatypeProperty("startingPage" )                                      # described as sub of prism term
        self.endingPage = self.registerDatatypeProperty("endingPage")                                           # described as sub of prism term

        # journal abbreviation, see also:
        # https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt
        # https://en.wikipedia.org/wiki/ISO_4

        # described as sub dcterms:identifier: # Amos uses abbreviation also used by UniProt based on ISO4
        self.iso4JournalTitleAbbreviation = self.registerDatatypeProperty(                                       # described, see line above
            "iso4JournalTitleAbbreviation", label="ISO4 Journal Title Abbreviation") 
        
        self.title = self.registerDatatypeProperty("title")                             # defined as sub prop of dcterms
        self.creator = self.registerObjectProperty("creator")                            # defined as sub prop of dcterms equivalent
        self.publisher = self.registerObjectProperty("publisher")                        # sdefined as sub prop of dcterms equivalent
        
        self.editor = self.registerObjectProperty("editor")                                                         # described as sub of dcterms:contributor

        self.hasAnnotation = self.registerObjectProperty("hasAnnotation")                                           # described as inverse of IAO:is_about

        comment = "Unique identifier for an entity in a database."
        self.accession = self.registerDatatypeProperty("accession", comment=comment)                                # described as subProp of dcterms:identifier
        comment = "Unique identifier of the cell line. It is normally stable across Cellosaurus versions"
        self.primaryAccession = self.registerDatatypeProperty("primaryAccession", comment=comment)                  # described as subProp of dcterms:identifier
        comment = "Former primary accession kept here to ensure the access to a cell line via old identifiers."
        self.secondaryAccession = self.registerDatatypeProperty("secondaryAccession", comment=comment)              # described as subProp of dcterms:identifier
        

        comment = "A human-readable version of a resource's name."
        self.name = self.registerAnnotationProperty("name", comment=comment)                                          # described, as sub prop of rdfs:label
        #comment = "A name which serves as a concise or abbreviated version of a longer name."
        #self.shortname = self.registerAnnotationProperty("shortname")                                                 # described as sub prop of cello:name

        comment="Most frequently the name of the cell line as provided in the original publication"
        self.recommendedName = self.registerAnnotationProperty("recommendedName", comment=comment)                    # described as sub of skos:prefLabel sub of cello:name      

        comment="Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"
        self.alternativeName = self.registerAnnotationProperty("alternativeName", comment=comment)                    # described as sub of skos:altLabel sub of cello:name

        comment="A name as it appears in some register or official list."        
        self.registeredName = self.registerAnnotationProperty("registeredName", comment=comment)                      # described as sub of cello:name
        comment="A misspelling as it appears in some publication or external resource"
        self.misspellingName = self.registerAnnotationProperty("misspellingName", comment=comment)                    # described as sub of skos:hiddenLabel sub of cello:name


        comment="A related resource from which the described resource is derived or originates."
        self.hasSource = self.registerObjectProperty("hasSource", comment=comment)                                  # defined as subproperty of dcterms:source

        comment="A related resource in which the described resource appears."
        self.appearsIn = self.registerObjectProperty("appearsIn", comment=comment)                                  # defined as sub prop of dcterms:source

        comment="A publication that is referenced, cited, or otherwise pointed to by the described resource."
        self.references = self.registerAnnotationProperty("references", comment=comment)                            # defined as subproperty of dcterms:references

        comment="A database cross-reference that is referenced, cited, or otherwise pointed to with the purpose to provide further information about the described resource"
        self.seeAlsoXref = self.registerAnnotationProperty("seeAlsoXref", label="see also xref", comment=comment)         # defined as sub prop of rdfs:seeAlso

        comment="A database cross-reference that is referenced, cited, or otherwise pointed to with the purpose to unequivocally identify the described resource."
        self.isIdentifiedByXref = self.registerAnnotationProperty("isIdentifiedByXref", label="is identified by xref", comment=comment)         # defined as sub prop of rdfs:seeAlso

        comment="An IRI that is referenced, cited, or otherwise pointed to with the purpose to unequivocally identify the described resource."
        self.isIdentifiedByIRI = self.registerAnnotationProperty("isIdentifiedByIRI", label="is identified by IRI", comment=comment)         # defined as sub prop of rdfs:seeAlso


        self.hasGenomeAncestry = self.registerObjectProperty("hasGenomeAncestry")                                   # described as sub cello:hasAnnotation

        self.hasComponent = self.registerObjectProperty("hasComponent")                                             # described as sub prop of BFO:has_part 
        self.hasPopulation = self.registerObjectProperty("hasPopulation")                                           # TODO: later # as link between PopulationPercentage and Population
        self.percentage = self.registerDatatypeProperty("percentage")                                               # TODO: later # as link between PopulationPercentage and percentage

        self.hasHLAtyping = self.registerObjectProperty("hasHLAtyping", label="has HLA Typing")                     # described as sub cello:hasAnnotation
        #self.hasAllele = self.registerObjectProperty("hasAllele")                                                  # unused, described as ns.GENO:0000413 subprop
        #self.isAlleleOf = self.registerObjectProperty("isAlleleOf")                                                # unused, described as ns.GENO:0000408 subprop
        self.alleleIdentifier = self.registerDatatypeProperty("alleleIdentifier")                                   # described as dcterms:identifier subprop
        self.includesObservation = self.registerObjectProperty("includesObservation")                               # described as sub prop of BFO:has_part, link between some genetic information and a gene allele

        self.markerId = self.registerDatatypeProperty("markerId")                                                   # described as sub dcterms:identifier  

        self.ofGene = self.registerObjectProperty("ofGene")                                                         # TODO: later

        comment="The belonging to a specific panel or collection of cell lines"
        self.inCollection = self.registerDatatypeProperty("inCollection", comment=comment)                                # described as sub prop of schema:category

        comment="Laboratory, research institute, university having established the cell line."
        self.establishedBy = self.registerObjectProperty("establishedBy", comment=comment)                          # described as sub prop of dcterms:source # cannot use function name "from" (is python reserved word)
        
        #self.commentedSequenceVariation = self.registerObjectProperty("commentedSequenceVariation")                 # unused: we use cello:hasTarget instead
        
        self.zygosity = self.registerDatatypeProperty("zygosity")                                                   # described as sub prop of GENO:_0000608_has_zygozity

        comment="Notation acoording to the HGVS Nomenclature. HGVS is an internationally-recognized standard for the description of DNA, RNA, and protein sequence variants."
        self.hgvs = self.registerDatatypeProperty("hgvs", comment=comment)                                          # described as sub of skos:notation ?
        self.noneReported = self.registerDatatypeProperty("noneReported")                                           # TODO: later
        self.variationStatus = self.registerDatatypeProperty("variationStatus")                                     # TODO: later

        self.comesFomIndividualBelongingToBreed = self.registerObjectProperty("comesFromIndividualBelongingToBreed") # described as cello:hasAnnotation
        self.hasSequenceVariationComment = self.registerObjectProperty("hasSequenceVariationComment")                # described as cello:hasAnnotation

        self.hasAnecdotalComment = self.registerObjectProperty("hasAnecdotalComment")                               # described as cello:hasAnnotation
        self.hasCharacteristicsComment = self.registerObjectProperty("hasCharacteristicsComment")                   # described as cello:hasAnnotation
        self.hasBiotechnologyComment = self.registerObjectProperty("hasBiotechnologyComment")                       # described as cello:hasAnnotation
        self.hasCautionComment = self.registerObjectProperty("hasCautionComment")                                   # described as cello:hasAnnotation

        self.siteType = self.registerDatatypeProperty("siteType")                                                   # TODO:later

        self.isDerivedFromSite = self.registerObjectProperty("isDerivedFromSite")                                   # described as cello:hasAnnotation
        self.isDerivedFromCellType = self.registerObjectProperty("isDerivedFromCellType" )                          # described as cello:hasAnnotation

        self.hasDonorInfoComment = self.registerObjectProperty("hasDonorInfoComment")                               # described as cello:hasAnnotation
        self.hasDoublingTimeComment = self.registerObjectProperty("hasDoublingTimeComment")                         # described as cello:hasAnnotation
        self.hasKaryotypicInfoComment = self.registerObjectProperty("hasKaryotypicInfoComment")                     # described as cello:hasAnnotation
        self.hasMiscellaneousInfoComment = self.registerObjectProperty("hasMiscellaneousInfoComment")               # described as cello:hasAnnotation
        self.hasMisspellingRecord = self.registerObjectProperty("hasMisspellingRecord")                             # described as cello:hasAnnotation
        self.hasSenescenceComment = self.registerObjectProperty("hasSenescenceComment")                             # described as cello:hasAnnotation
        self.hasVirologyComment = self.registerObjectProperty("hasVirologyComment")                                 # described as cello:hasAnnotation
        self.hasOmicsComment = self.registerObjectProperty("hasOmicsComment")                                       # described as cello:hasAnnotation
        self.comesFromIndividualBelongingToPopulation = self.registerObjectProperty("comesFromIndividualBelongingToPopulation")       # described as cello:hasAnnotation

        comment="Population doubling-time of the cell line. Expressed in hours, days, weeks, months or qualitatively."
        self.duration = self.registerDatatypeProperty("duration", comment=comment)                                  # TODO: later
        self.inGroup = self.registerDatatypeProperty("inGroup")                                                     # described as sub prop of schema:category

        self.hasRegistationRecord = self.registerObjectProperty("hasRegistationRecord")                                   # described as cello:hasAnnotation
        self.inRegister = self.registerObjectProperty("inRegister")                                                 # described as sub prop of BFO:part_of
        
        self.hasGeneKnockout = self.registerObjectProperty("hasGeneKnockout")                                       # described as cello:hasAnnotation
        self.hasGeneticIntegration = self.registerObjectProperty("hasGeneticIntegration")                           # described as cello:hasAnnotation
        self.hasGenomeModificationMethod = self.registerObjectProperty("hasGenomeModificationMethod")               # TODO: later

        comment="Discontinuation status of the item represented by the described resource (a cross-reference)."
        self.discontinued = self.registerDatatypeProperty("discontinued", comment=comment)                          # TODO: later

        comment="Discontinuation record of the cell line in a cell line catalog."
        self.hasDiscontinuationRecord = self.registerObjectProperty("hasDiscontinuationRecord", comment=comment)    # TODO: LATER
        
        self.hasProvider = self.registerObjectProperty("hasProvider")                                               # described as sub of schema:provider
        self.productId = self.registerDatatypeProperty("productId", label="product Identifier")                     # described as sub of dcterms:identifier

        self.msiValue = self.registerDatatypeProperty("msiValue", label="microsatellite instability value")     # TODO: later

        self.hasMicrosatelliteInstability = self.registerObjectProperty("hasMicrosatelliteInstability")             # described as cello:hasAnnotation        
        self.hasMabIsotype = self.registerObjectProperty("hasMabIsotype", label="has monoclonal antibody isotype")  # described as cello:hasAnnotation
        self.hasMabTarget = self.registerObjectProperty("hasMabTarget", label="has monoclonal antibody target")     # described as cello:hasAnnotation
        
        self.hasAntibodyHeavyChain = self.registerObjectProperty("hasAntibodyHeavyChain")                           # described as sub prop of BFO:part_of
        self.hasAntibodyLightChain = self.registerObjectProperty("hasAntibodyLightChain")                           # described as sub prop of BFO:part_of

        self.hasResistance = self.registerObjectProperty("hasResistance")                                           # described as cello:hasAnnotation
        self.transformedBy = self.registerObjectProperty("transformedBy")                                           # described as cello:hasAnnotation
        self.hasShortTandemRepeatProfile = self.registerObjectProperty("hasShortTandemRepeatProfile")               # described as cello:hasAnnotation


        self.comesFromIndividualWithDisease = self.registerObjectProperty("comesFromIndividualWithDisease")         # described as cello:hasAnnot, = wd:P5166_DI
        self.comesFromIndividualBelongingToSpecies = self.registerObjectProperty("comesFromIndividualBelongingToSpecies")     # described as cello:hasAnnot, = wd:
        self.comesFromIndividualWithSex = self.registerObjectProperty("comesFromIndividualWithSex")                 # described as cello:hasAnnot, close to wd:
        self.comesFromIndividualAtAge = self.registerDatatypeProperty("comesFromIndividualAtAge")                   # described as cello:hasAnnot

        self.comesFromSameIndividualAs = self.registerObjectProperty("comesFromSameIndividualAs")                   # described as cello:hasAnnot, = wd:P3578
        self.hasParentCellLine = self.registerObjectProperty("hasParentCellLine")                                   # described as cello:hasAnnot, = wd:P3432_HI , inverse of parentCellLine
        self.hasChildCellLine = self.registerObjectProperty("hasChildCellLine")                                     # described as cello:hasAnnot, inverse of parentCellLine
        

        self.version = self.registerDatatypeProperty("version")                                                    # described as sub of dcterms term
        self.created = self.registerDatatypeProperty("created")                                                     # described as sub of dcterms term
        self.modified = self.registerDatatypeProperty("modified")                                                   # described as sub of dcterms term

        self.originatesFrom = self.registerObjectProperty("originatesFrom")                                         # TODO later
        self.database = self.registerObjectProperty("database")                                                     # TODO: later
        self.isMemberOf = self.registerObjectProperty("isMemberOf")                                                 # described, defined in schema namespace
        self.city = self.registerDatatypeProperty("city")                                                           # described as sub of schema:location
        self.country = self.registerDatatypeProperty("country")                                                     # described as sub of schema:location

        self.bookTitle = self.registerDatatypeProperty("bookTitle")                                                 # described as sub dcterms:title
        self.conferenceTitle = self.registerDatatypeProperty("conferenceTitle")                                     # described as sub dcterms:title
        self.documentTitle = self.registerDatatypeProperty("documentTitle")                                         # described as sub dcterms:title
        self.documentSerieTitle = self.registerDatatypeProperty("documentSerieTitle")                               # described as sub dcterms:title
        
        comment="Links two concepts where he subject concept is more specific than the object concept. The semantics is similar to skos:broader."
        self.more_specific_than = self.registerObjectProperty("more_specific_than", comment=comment)                # described as equivalent of skos:broader
        