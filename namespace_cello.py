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

        #self.CellLine = self.registerClass("CellLine")                                                                         # described, defined in wd namespace
        #self.GenomeModificationMethod = self.registerClass("GenomeModificationMethod", "Genome Modification Method NOS")       # described, defined in OBI namespace

        # Genome modification methods sublasses not found in NCIt, OBI, FBcv
        # WARNING: labels must match what's found in cellosaurus.txt !!!
        self.BacHomologousRecombination = self.registerClass("BacHomologousRecombination", label="BAC homologous recombination")                    # described
        self.CreLoxp = self.registerClass("CreLoxp", label="Cre/loxP")                                                                              # described
        self.CrisprCas9N = self.registerClass("CrisprCas9N", label="CRISPR/Cas9n")                                                                  # described
        self.EbvBasedVectorSirnaKnockdown = self.registerClass("EbvBasedVectorSirnaKnockdown", label="EBV-based vector siRNA knockdown")            # described
        self.FloxingCreRecombination = self.registerClass("FloxingCreRecombination", label="Floxing/Cre recombination")                             # described
        self.GeneTargetedKoMouse = self.registerClass("GeneTargetedKoMouse", label="Gene-targeted KO mouse")                                        # described
        self.HelperDependentAdenoviralVector = self.registerClass("HelperDependentAdenoviralVector", label="Helper-dependent adenoviral vector")    # described
        self.HomologousRecombination = self.registerClass("HomologousRecombination", label="Homologous recombination")                              # described
        self.KnockoutFirstConditional = self.registerClass("KnockoutFirstConditional", label="Knockout-first conditional")                          # described
        self.KoMouse = self.registerClass("KoMouse", label="KO mouse")                                                              # described
        self.KoPig = self.registerClass("KoPig", label="KO pig")                                                                    # described
        self.MirnaKnockdown = self.registerClass("MirnaKnockdown", label="miRNA knockdown")                                         # described
        self.NullMutation = self.registerClass("NullMutation", label="Null mutation")                                               # described
        self.PElement = self.registerClass("PElement", label="P-element")                                                           # described
        self.PiggybacTransposition = self.registerClass("PiggybacTransposition", label="PiggyBac transposition")                    # described
        self.PrimeEditing = self.registerClass("PrimeEditing", label="Prime editing")                                               # described
        self.PromoterlessGeneTargeting = self.registerClass("PromoterlessGeneTargeting", label="Promoterless gene targeting")       # described
        self.RecombinantAdenoAssociatedVirus = self.registerClass("RecombinantAdenoAssociatedVirus", label="Recombinant Adeno-Associated Virus")    # described
        self.ShrnaKnockdown = self.registerClass("ShrnaKnockdown", label="shRNA knockdown")                                                         # described
        self.SleepingBeautyTransposition = self.registerClass("SleepingBeautyTransposition", label="Sleeping Beauty transposition")                 # described
        self.SpontaneousMutation = self.registerClass("SpontaneousMutation", label="Spontaneous mutation")                          # described
        self.TargetedIntegration = self.registerClass("TargetedIntegration", label="Targeted integration")                          # described
        self.TransductionTransfection = self.registerClass("TransductionTransfection", label="Transduction/transfection")           # described
        self.TransfectionTransduction = self.registerClass("TransfectionTransduction", label="Transfection/transduction")           # described
        self.TransgenicFish = self.registerClass("TransgenicFish", label="Transgenic fish")                                         # described
        self.TransgenicMouse = self.registerClass("TransgenicMouse", label="Transgenic mouse")                                      # described
        self.TransgenicRat = self.registerClass("TransgenicRat", label="Transgenic rat")                                            # described

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

        self.Locus = self.registerClass("Locus")                                        # descrided as equivalent of NCIt.C45822, used in STR profile    
        self.STR_Allele = self.registerClass("STRAllele", label="STR Allele")           # described as GENO:0000512 subclass
        self.Marker = self.registerClass("Marker", label="Marker")                      # described as NCIT:C45822(Locus) subclass AND as  NCIT:C13441(Short Tandem Repeat) subclass
        #self.MarkerAlleles = self.registerClass("MarkerAlleles")                       # obsolete, was used in short tandem repeat
        self.ShortTandemRepeatProfile = self.registerClass("ShortTandemRepeatProfile")  # described as subClass of OBI:0001404
        self.hasTarget = self.registerObjectProperty("hasTarget")                       # described as subProp of schema:obserationAbout
        
        #self.ChemicalAgent = self.registerClass("ChemicalAgent")               # unused, defined as CHEBI:24431: instances are drugbank, ncit, chebi xrefs (+free text)
        #self.Protein = self.registerClass("Protein")                           # unused, defined as CHEBI:36080, a child of CHEBI:24431
        #self.TransformantAgent = self.registerClass("TransformantAgent")       # synonym of CHEBI:24431, instances are ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)

        self.GeneKnockout = self.registerClass("GeneKnockout")                          # described as child of OBI:0001364 : characteristics of genetic alteration
        self.GeneticIntegration = self.registerClass("GeneticIntegration")              # described as child of OBI:0001364 : characteristics of genetic alteration
        self.SequenceVariationComment = self.registerClass("SequenceVariationComment")  # described as child of OBI:0001364 : characteristics of genetic alteration
        # ...
        #self.SequenceVariation = self.registerClass("SequenceVariation")        # # defined as NCIt:C36391 - Molecular genetic varation
        #self.GeneAmplification = self.registerClass("GeneAmplification")       # defined as NCIt:C45581
        self.GeneDuplication = self.registerClass("GeneDuplication")            # described as child of NCIt:C45581 - gene amplification
        self.GeneTriplication = self.registerClass("GeneTriplication")          # described as child of NCIt:C45581 - gene amplification
        self.GeneQuadruplication = self.registerClass("GeneQuadruplication")    # described as child of NCIt:C45581 - gene amplification
        self.GeneExtensiveAmplification = self.registerClass("GeneExtensiveAmplification")  # described as child of NCIt:C45581 - gene amplification
        #self.GeneDeletion = self.registerClass("GeneDeletion")                  # defined in NCIt namespace
        #self.GeneFusion = self.registerClass("GeneFusion")                      # defined in NCIt namespace
        #self.GeneMutation = self.registerClass("GeneMutation")                  # defined in NCIt namespace
        self.RepeatExpansion = self.registerClass("RepeatExpansion")            # described as child of NCIt:C18093 (gene mutation)
        #self.SimpleMutation = self.registerClass("SimpleMutation")              # unused 
        #self.UnexplicitMutation = self.registerClass("UnexplicitMutation")      # unused

        #self.AnatomicalElement = self.registerClass("AnatomicalElement")        # replaced with CARO:0000000
        #self.CellType = self.registerClass("CellType")                          # replaced with CL:0000000

        self.Disease = self.registerClass("Disease")                            # described as superclass of ORDO clinical entity and NCIt disorder
        self.Species = self.registerClass("Species")                            # described as subClassOf NCIt taxon
        comment="A group of animals homogeneous in appearance and other characteristics that distinguish it from other animals of the same species."
        self.Breed = self.registerClass("Breed", comment=comment)               # described as equivalent of NCIt corresponding class

        self.Population = self.registerClass("Population")                          # described as child of OBI_0000181

        self.KaryotypicInfoComment = self.registerClass("KaryotypicInfoComment")    # described as subclass of OBI:Genetic info & equiv as OBI:Karyotype info
        self.MicrosatelliteInstability = self.registerClass("MicrosatelliteInstability")    # described as subclass of OBI:Genetic info

        self.BiotechnologyComment = self.registerClass("BiotechnologyComment")          # described as a Data iterm cello:GeneralTopic
        self.SenescenceComment = self.registerClass("SenescenceComment")                # described as an IAO:Topic
        self.DoublingTimeComment = self.registerClass("DoublingTimeComment")            # described as an IAO:Topic
        self.VirologyComment = self.registerClass("VirologyComment")                    # described as an IAO:Topic
        self.OmicsComment = self.registerClass("OmicsComment")                          # described as an IAO:Topic
        self.CharacteristicsComment = self.registerClass("CharacteristicsComment")      # described as an IAO:Topic
        self.MiscellaneousInfoComment = self.registerClass("MiscellaneousInfoComment")  # described as an IAO:Topic
        self.CautionComment = self.registerClass("CautionComment")                      # described as an IAO:Topic
        self.AnecdotalComment = self.registerClass("AnecdotalComment")                  # described as an IAO:Topic
        self.MisspellingRecord = self.registerClass("MisspellingRecord")              # described as an IAO:Topic
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

        comment = "An entity which is used as a source of information (mostly a cross-reference, a publication or an organization)"
        self.Source = self.registerClass("Source", comment=comment)                     # TODO: later, a wrapper of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)


        #
        # Properties
        #

        # publication properties
        # see also https://sparontologies.github.io/fabio/current/fabio.html
        # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html


        #self.hasIdentifier = self.registerDatatypeProperty("hasIdentifier") # generic prop, parent of hasDOI, hasPubMedId # we use the  as an ancestor
        self.hasInternalId = self.registerDatatypeProperty("hasInternalId", label="has Internal Identifier")     # described as sub dcterms:identifier
        #self.hasDOI = self.registerDatatypeProperty("hasDOI"label=)                     # described as sub dcterms:identifier: see prism
        #self.hasPubMedId = self.registerDatatypeProperty("hasPubMedId")                 # described as sub dcterms:identifier: see fabio
        #self.hasPMCId = self.registerDatatypeProperty("hasPMCId")                       # described as sub dcterms:identifier, see fabio
        self.issn13 = self.registerDatatypeProperty("issn13", label="has ISSN13")        # described as sub dcterms:identifier

        #self.publicationDate = self.registerDatatypeProperty("publicationDate")         # described in prism
        #self.hasPublicationYear = self.registerDatatypeProperty("hasPublicationYear")   # described in dcterms
        # self.startingPage = self.registerDatatypeProperty("startingPage" )              # described in prism
        # self.endingPage = self.registerDatatypeProperty("endingPage")                   # described in prism

        # journal abbreviation, see also:
        # https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt
        # https://en.wikipedia.org/wiki/ISO_4

        # described as sub dcterms:identifier: # Amos uses abbreviation also used by UniProt based on ISO4
        self.hasISO4JournalTitleAbbreviation = self.registerDatatypeProperty(            # described, see line above
            "hasISO4JournalTitleAbbreviation",
            label="has ISO4 Journal Title Abbreviation") 
        
        #self.title = self.registerDatatypeProperty("title")                             # defined in dcterms
        #self.volume = self.registerDatatypeProperty("volume")                           # defined as sub dcterms:identifier: see prism
        #self.creator = self.registerObjectProperty("creator")                           # see dcterms
        #self.publisher = self.registerObjectProperty("publisher")                       # see dcterms
        
        self.editor = self.registerObjectProperty("editor")                              # TODO later : with range = foaf:Person (editors)

        self.hasAnnotation = self.registerObjectProperty("hasAnnotation")               # described as inverse of IAO:is_about

        comment = "Unique identifier for an entity in a database."
        self.accession = self.registerDatatypeProperty("accession", comment=comment)    # described as subProp of dcterms:identifier
        comment = "Unique identifier of the cell line. It is normally stable across Cellosaurus versions"
        self.primaryAccession = self.registerDatatypeProperty("primaryAccession", comment=comment)       # described as subProp of dcterms:identifier
        comment = "Former primary accession kept here to ensure the access to a cell line via old identifiers."
        self.secondaryAccession = self.registerDatatypeProperty("secondaryAccession", comment=comment)   # described as subProp of dcterms:identifier
        

        comment = "A human-readable version of a resource's name. It is an owl:equivalentProperty of rdfs:label"
        self.name = self.registerDatatypeProperty("name", comment=comment)              # described, as equivalent of rdfs:label
        comment = "A name which serves as a concise or abbreviated version of a longer name."
        self.shortname = self.registerDatatypeProperty("shortname")                     # described as sub prop of cello:name

        comment="Most frequently the name of the cell line as provided in the original publication"
        self.recommendedName = self.registerDatatypeProperty("recommendedName", comment=comment)   # described as sub of skos:prefLabel sub of cello:name      

        comment="Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"
        self.alternativeName = self.registerDatatypeProperty("alternativeName", comment=comment)   # described as sub of skos:altLabel sub of cello:name

        comment="A name as it appears in some register or official list."        
        self.registeredName = self.registerDatatypeProperty("registeredName", comment=comment)           # described as sub of cello:name
        comment="A misspelling as it appears in some publication or external resource"
        self.misspellingName = self.registerDatatypeProperty("misspellingName", comment=comment)         # described as sub of skos:hiddenLabel sub of cello:name


        comment="A related resource from which the described resource is derived or originates."
        self.hasSource = self.registerObjectProperty("hasSource", comment=comment)                       # defined as subproperty of dcterms:source

        comment="A related resource in which the described resource appears."
        self.appearsIn = self.registerObjectProperty("appearsIn", comment=comment)                       # defined as sub prop of dcterms:source

        comment="A publication that is referenced, cited, or otherwise pointed to by the described resource."
        self.references = self.registerObjectProperty("references", comment=comment)    # defined as subproperty of dcterms:references

        comment="A cross-reference that is referenced, cited, or otherwise pointed to by the described resource."
        self.hasXref = self.registerObjectProperty("hasXref", label="has cross-reference", comment=comment)    # defined as sub prop of dcterms:references
        
        self.hasGenomeAncestry = self.registerObjectProperty("hasGenomeAncestry")       # described as sub cello:hasAnnotation

        self.hasComponent = self.registerObjectProperty("hasComponent")                 # described as sub prop of BFO:has_part 
        self.hasPopulation = self.registerObjectProperty("hasPopulation")               # TODO: later # as link between PopulationPercentage and Population
        self.percentage = self.registerDatatypeProperty("percentage")                   # TODO: later # as link between PopulationPercentage and percentage

        self.hasHLAtyping = self.registerObjectProperty("hasHLAtyping", label="has HLA Typing")     # described as sub cello:hasAnnotation
        #self.hasAllele = self.registerObjectProperty("hasAllele")                                  # unused, described as ns.GENO:0000413 subprop
        #self.isAlleleOf = self.registerObjectProperty("isAlleleOf")                                # unused, described as ns.GENO:0000408 subprop
        self.alleleIdentifier = self.registerDatatypeProperty("alleleIdentifier")                   # described as dcterms:identifier subprop
        self.includesObservation = self.registerObjectProperty("includesObservation")   # described as sub prop of BFO:has_part, link between some genetic information and a gene allele

        self.markerId = self.registerDatatypeProperty("markerId")                       # described as sub cello:hasAnnotation  

        self.ofGene = self.registerObjectProperty("ofGene")                             # TODO: later

        comment="The belonging to a specific panel or collection of cell lines"
        self.belongsTo = self.registerDatatypeProperty("belongsTo", comment=comment)    # described as sub prop of schema:category

        comment="Laboratory, research institute, university having established the cell line."
        self.establishedBy = self.registerObjectProperty("establishedBy", comment=comment)   # described as sub prop of dcterms:source # cannot use function name "from" (is python reserved word)
        
        self.commentedSequenceVariation = self.registerObjectProperty("commentedSequenceVariation")  # TODO: later
        
        self.zygosity = self.registerDatatypeProperty("zygosity")                       # described as sub prop of GENO:_0000608_has_zygozity

        comment="Notation acoording to the HGVS Nomenclature. HGVS is an internationally-recognized standard for the description of DNA, RNA, and protein sequence variants."
        self.hgvs = self.registerDatatypeProperty("hgvs", comment=comment)              # described as sub of skos:notation ?
        self.noneReported = self.registerDatatypeProperty("noneReported")               # TODO: later
        self.variationStatus = self.registerDatatypeProperty("variationStatus")         # TODO: later

        self.fromIndividualBelongingToBreed = self.registerObjectProperty("fromIndividualBelongingToBreed") # TODO:
        self.sequenceVariationComment = self.registerObjectProperty("sequenceVariationComment")             # TODO:

        self.anecdotalComment = self.registerObjectProperty("anecdotalComment")         # TODO:
        self.characteristicsComment = self.registerObjectProperty("characteristicsComment") # TODO:
        self.biotechnologyComment = self.registerObjectProperty("biotechnologyComment") # TODO:
        self.cautionComment = self.registerObjectProperty("cautionComment")             # TODO:

        self.siteType = self.registerDatatypeProperty("siteType")                       # TODO:

        self.derivedFromSite = self.registerObjectProperty("derivedFromSite")           # TODO: rename it ?
        self.cellType = self.registerObjectProperty("cellType" )                        # TODO: rename it ? derivedFromCellType

        self.donorInfoComment = self.registerObjectProperty("donorInfoComment")         # TODO:
        self.doublingTimeComment = self.registerObjectProperty("doublingTimeComment")   # TODO:
        self.karyotypicInfoComment = self.registerObjectProperty("karyotypicInfoComment")           # TODO:
        self.miscellaneousInfoComment = self.registerObjectProperty("miscellaneousInfoComment")     # TODO:
        self.hasMisspellingRecord = self.registerObjectProperty("hasMisspellingRecord")     # TODO:
        self.senescenceComment = self.registerObjectProperty("senescenceComment")       # TODO:
        self.virologyComment = self.registerObjectProperty("virologyComment")           # TODO:
        self.omicsComment = self.registerObjectProperty("omicsComment")                 # TODO:
        self.fromIndividualBelongingToPopulation = self.registerObjectProperty("fromIndividualBelongingToPopulation")       # TODO:

        self.duration = self.registerDatatypeProperty("duration")                       # TODO:
        self.inGroup = self.registerDatatypeProperty("inGroup")                             # described as sub prop of schema:category

        self.isRegistered = self.registerObjectProperty("isRegistered")                # TODO:
        self.inRegister = self.registerObjectProperty("inRegister")                    # TODO
        
        self.geneKnockout = self.registerObjectProperty("geneKnockout")                 # TODO:
        self.geneticIntegration = self.registerObjectProperty("geneticIntegration")     # TODO:
        self.genomeModificationMethod = self.registerObjectProperty("genomeModificationMethod")   # TODO:

        self.discontinued = self.registerDatatypeProperty("discontinued")               # TODO:

        self.discontinuationRecord = self.registerObjectProperty("discontinuationRecord")   # TODO:
        
        self.provider = self.registerDatatypeProperty("provider")                       # TODO:
        self.productId = self.registerDatatypeProperty("productId", label="product Identifier")                     # TODO:

        self.microsatelliteInstability = self.registerObjectProperty("microsatelliteInstability")   # TODO:
        
        self.msiValue = self.registerDatatypeProperty("msiValue", label="has microsatellite instability value")                       # TODO:

        self.mabIsotype = self.registerObjectProperty("mabIsotype", label="has monoclonal antibody isotype")          # TODO:
        self.mabTarget = self.registerObjectProperty("mabTarget", label="has monoclonal antibody target")             # TODO:
        
        self.antibodyHeavyChain = self.registerDatatypeProperty("antibodyHeavyChain")   # TODO:
        self.antibodyLightChain = self.registerDatatypeProperty("antibodyLightChain")   # TODO:

        self.resistance = self.registerObjectProperty("resistance")                     # TODO:
        self.transformant = self.registerObjectProperty("transformant")                 # TODO:
        self.shortTandemRepeatProfile = self.registerObjectProperty("shortTandemRepeatProfile") # TODO:


        self.fromIndividualWithDisease = self.registerObjectProperty("fromIndividualWithDisease")               # described: # renamed: OK
        self.fromIndividualBelongingToSpecies = self.registerObjectProperty("fromIndividualBelongingToSpecies") # described: # renamed: OK
        self.fromIndividualWithSex = self.registerObjectProperty("fromIndividualWithSex")                       # described

        self.fromIndividualAtAge = self.registerDatatypeProperty("fromIndividualAtAge") # TODO:

        self.fromSameIndividualAs = self.registerObjectProperty("fromSameIndividualAs") # described: # OI field
        self.parentCellLine = self.registerObjectProperty("parentCellLine")             # described: # HI field
        self.childCellLine = self.registerObjectProperty("childCellLine")               # TODO: # as inverse of parentCellLine, CH field
        

        self.hasVersion = self.registerDatatypeProperty("hasVersion")                 # described as sub of dcterms term
        self.created = self.registerDatatypeProperty("created")                       # described as sub of dcterms term
        self.modified = self.registerDatatypeProperty("modified")                     # described as sub of dcterms term

        self.organization = self.registerObjectProperty("organization")                 # TODO:
        self.database = self.registerObjectProperty("database")                         # TODO:
        self.memberOf = self.registerObjectProperty("memberOf")                         # described, defined in schema namespace
        self.city = self.registerDatatypeProperty("city")                               # described as sub of schema:location
        self.country = self.registerDatatypeProperty("country")                         # described as sub of schema:location

        self.bookTitle = self.registerDatatypeProperty("bookTitle")                     # TODO
        self.conferenceTitle = self.registerDatatypeProperty("conferenceTitle")         # TODO
        self.documentTitle = self.registerDatatypeProperty("documentTitle")             # TODO
        self.documentSerieTitle = self.registerDatatypeProperty("documentSerieTitle")   # TODO
        
        comment="Links two concepts. The subject concept is more specific than the object concept. The semantics is the similar to the skos:broader property but its label less ambiguous."
        self.more_specific_than = self.registerObjectProperty("more_specific_than", comment=comment)     # TODO as equivalent of skos:broader
        