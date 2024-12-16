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
        self.CelloConceptScheme = self.registerClass("CelloConceptScheme")      # described
        
        # self.Organization = self.registerClass("Organization")                  # described, defined in schema namespace

        self.Xref = self.registerClass("Xref")                                  # described as NCIT:C43621 subclass
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
        self.detectedTarget = self.registerDatatypeProperty("detectedTarget")           # TODO later
        self.detectedAllele = self.registerObjectProperty("detectedAllele")             # TODO: later
        self.hasTarget = self.registerObjectProperty("hasTarget")                       # described as subProp of schema:obserationAbout
        self.conflicting = self.registerDatatypeProperty("conflicting")                 # TODO: later
        self.containsObservation = self.registerObjectProperty("containsObservation")   # TODO: later
        self.repeatNumber = self.registerDatatypeProperty("repeatNumber")               # TODO: later, question: separate number dand variant id ?
        

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
        self.Breed = self.registerClass("Breed", comment=comment)                   # described as equivalent of NCIt corresponding class

        comment = "An entity which is used as a source of information (mostly a cross-reference, a publication or an organization)"
        self.Source = self.registerClass("Source", comment=comment)                 # a wrapper of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)
        self.Population = self.registerClass("Population")                          # described as child of OBI_0000181

        self.Sex = self.registerClass("Sex")                                        # TODO: later, has some special cases like mixed sex

        self.KaryotypicInfoComment = self.registerClass("KaryotypicInfoComment")    # described as subclass of OBI:Genetic info & equiv as OBI:Karyotype info
        self.MicrosatelliteInstability = self.registerClass("MicrosatelliteInstability")    # described as subclass of OBI:Genetic info

        self.BiotechnologyComment = self.registerClass("BiotechnologyComment")          # described
        self.SenescenceComment = self.registerClass("SenescenceComment")                # described
        self.DoublingTimeComment = self.registerClass("DoublingTimeComment")            # described
        self.VirologyComment = self.registerClass("VirologyComment")                    # described
        self.OmicsComment = self.registerClass("OmicsComment")                          # described
        self.CharacteristicsComment = self.registerClass("CharacteristicsComment")      # described     
        self.MiscellaneousInfoComment = self.registerClass("MiscellaneousInfoComment")  # described
        self.CautionComment = self.registerClass("CautionComment")                      # described
        self.AnecdotalComment = self.registerClass("AnecdotalComment")                  # described
        self.MisspellingComment = self.registerClass("MisspellingComment")              # described
        self.DonorInfoComment = self.registerClass("DonorInfoComment")                  # described

        self.MabIsotype = self.registerClass("MabIsotype")                          # TODO:
        self.DiscontinuationRecord = self.registerClass("DiscontinuationRecord")    # TODO:
        self.Registration = self.registerClass("Registration")                      # TODO:


        #self.MabTarget = self.registerClass("MabTarget")


        #
        # Properties
        #

        # publication properties
        # see also https://sparontologies.github.io/fabio/current/fabio.html
        # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html

        #self.hasIdentifier = self.registerDatatypeProperty("hasIdentifier") # generic prop, parent of hasDOI, hasPubMedId # we use the  as an ancestor
        self.hasInternalId = self.registerDatatypeProperty("hasInternalId")             # TODO:
        self.hasDOI = self.registerDatatypeProperty("hasDOI")                           # TODO: see bibo
        self.hasPubMedId = self.registerDatatypeProperty("hasPubMedId")                 # TODO:
        self.hasPMCId = self.registerDatatypeProperty("hasPMCId")                       # TODO:
        self.publicationDate = self.registerDatatypeProperty("publicationDate")         # TODO:
        self.hasPublicationYear = self.registerDatatypeProperty("hasPublicationYear")   # TODO:
        self.startingPage = self.registerDatatypeProperty("startingPage" )              # TODO:
        self.endingPage = self.registerDatatypeProperty("endingPage")                   # TODO:
        # journal abbreviation, see also:
        # https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt
        # https://en.wikipedia.org/wiki/ISO_4
        #self.hasNLMJournalTitleAbbreviation = self.registerObjectProperty("hasNLMJournalTitleAbbreviation") # unused
        self.hasISO4JournalTitleAbbreviation = self.registerDatatypeProperty("hasISO4JournalTitleAbbreviation") # TODO: # Amos uses abbreviation also used by UniProt based on ISO4
        self.title = self.registerDatatypeProperty("title")                             # TODO:
        self.volume = self.registerDatatypeProperty("volume")                           # TODO: see bibo
        self.creator = self.registerObjectProperty("creator")                           # TODO: # with range = foaf:Person (authors)
        self.editor = self.registerObjectProperty("editor")                             # TODO:# with range = foaf:Person (editors)

        self.accession = self.registerDatatypeProperty("accession")                     # TODO: # should be defined as subProp of skos:notation / dcterms:identifier
        self.primaryAccession = self.registerDatatypeProperty("primaryAccession")       # TODO: # should be defined as subProp of skos:notation / dcterms:identifier
        self.secondaryAccession = self.registerDatatypeProperty("secondaryAccession")   # TODO: # should be defined as subProp of skos:notation / dcterms:identifier
        
        self.name = self.registerDatatypeProperty("name")                               # TODO: # described, as subProp of dcterms:title
        self.shortname = self.registerDatatypeProperty("shortname")                     # TODO:
        self.recommendedName = self.registerDatatypeProperty("recommendedName")         # TODO:
        self.alternativeName = self.registerDatatypeProperty("alternativeName")         # TODO:
        self.registeredName = self.registerDatatypeProperty("registeredName")           # TODO:
        self.misspellingName = self.registerDatatypeProperty("misspellingName")         # TODO: # should be defined as subProp of skos:hiddenName

        self.appearsIn = self.registerObjectProperty("appearsIn")                       # TODO:
        self.source = self.registerObjectProperty("source")                             # defined as subproperty of dcterms:source, TODO: rename has_source
        self.xref = self.registerObjectProperty("xref")                                 # TODO:
        self.reference = self.registerObjectProperty("reference")                       # defined as subproperty of dcterms:references, TODO: rename has_reference or references

        self.genomeAncestry = self.registerObjectProperty("genomeAncestry")             # TODO:
        self.component = self.registerObjectProperty("component")                       # TODO: # component object = population percentage of genome ancestry

        self.population = self.registerObjectProperty("population")                     # TODO: # as link between PopulationPercentage and Population
        self.percentage = self.registerDatatypeProperty("percentage")                   # TODO: # as link between PopulationPercentage and percentage
        self.populationName = self.registerDatatypeProperty("populationName")           # TODO: # as sub property of rdfs:label as name, recommendedName,...

        self.hlaTyping = self.registerObjectProperty("hlaTyping")                       # TODO:
        #self.hasAllele = self.registerObjectProperty("hasAllele")                      # unused, described as ns.GENO:0000413 subprop
        #self.isAlleleOf = self.registerObjectProperty("isAlleleOf")                    # unused, described as ns.GENO:0000408 subprop
        self.alleleIdentifier = self.registerDatatypeProperty("alleleIdentifier")       # described as dcterms:identifier subprop
        self.includesObservationOf = self.registerObjectProperty("includesObservationOf")   # TODO link between some gneetic information and a gene allele

        self.markerId = self.registerDatatypeProperty("markerId")                       # TODO:

        self.gene = self.registerObjectProperty("gene")                                 # TODO:

        self.partOf = self.registerDatatypeProperty("partOf")                           # TODO:

        self._from = self.registerObjectProperty("from")                                # TODO: # cannot use function name "from" (is python reserved word)
        
        self.sequenceVariation = self.registerObjectProperty("sequenceVariation")       # TODO:
        
        self.zygosity = self.registerDatatypeProperty("zygosity")                       # TODO:
        self.hgvs = self.registerDatatypeProperty("hgvs")                               # TODO:
        self.noneReported = self.registerDatatypeProperty("noneReported")               # TODO:
        self.variationStatus = self.registerDatatypeProperty("variationStatus")         # TODO:

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
        self.misspellingComment = self.registerObjectProperty("misspellingComment")     # TODO:
        self.senescenceComment = self.registerObjectProperty("senescenceComment")       # TODO:
        self.virologyComment = self.registerObjectProperty("virologyComment")           # TODO:
        self.omicsComment = self.registerObjectProperty("omicsComment")                 # TODO:
        self.fromIndividualBelongingToPopulation = self.registerObjectProperty("fromIndividualBelongingToPopulation")       # TODO:

        self.duration = self.registerDatatypeProperty("duration")                       # TODO:
        self.group = self.registerDatatypeProperty("group")                             # TODO:

        self.registration = self.registerObjectProperty("registration")                 # TODO:
        
        self.geneKnockout = self.registerObjectProperty("geneKnockout")                 # TODO:
        self.geneticIntegration = self.registerObjectProperty("geneticIntegration")     # TODO:
        self.genomeModificationMethod = self.registerObjectProperty("genomeModificationMethod")   # TODO:

        self.discontinued = self.registerDatatypeProperty("discontinued")               # TODO:

        self.discontinuationRecord = self.registerObjectProperty("discontinuationRecord")   # TODO:
        
        self.provider = self.registerDatatypeProperty("provider")                       # TODO:
        self.productId = self.registerDatatypeProperty("productId")                     # TODO:

        self.microsatelliteInstability = self.registerObjectProperty("microsatelliteInstability")   # TODO:
        
        self.msiValue = self.registerDatatypeProperty("msiValue")                       # TODO:

        self.mabIsotype = self.registerObjectProperty("mabIsotype")                     # TODO:
        self.mabTarget = self.registerObjectProperty("mabTarget")                       # TODO:
        
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
        
        self.publisher = self.registerObjectProperty("publisher")                       # TODO: # to be defined as sub propf of dcterms:publisher

        self.hasVersion = self.registerDatatypeProperty("hasVersion")                 # described as sub of dcterms term
        self.created = self.registerDatatypeProperty("created")                       # described as sub of dcterms term
        self.modified = self.registerDatatypeProperty("modified")                     # described as sub of dcterms term

        self.organization = self.registerObjectProperty("organization")                 # TODO:
        self.database = self.registerObjectProperty("database")                         # TODO:
        self.memberOf = self.registerObjectProperty("memberOf")                         # described, defined in schema namespace
        self.city = self.registerDatatypeProperty("city")                               # described as sub of schema:location
        self.country = self.registerDatatypeProperty("country")                         # described as sub of schema:location

        self.issn13 = self.registerDatatypeProperty("issn13")                           # TODO
        self.bookTitle = self.registerDatatypeProperty("bookTitle")                     # TODO
        self.conferenceTitle = self.registerDatatypeProperty("conferenceTitle")         # TODO
        self.documentTitle = self.registerDatatypeProperty("documentTitle")             # TODO
        self.documentSerieTitle = self.registerDatatypeProperty("documentSerieTitle")   # TODO
        
        self.more_specific_than = self.registerObjectProperty("more_specific_than")     # TODO as equivalent of skos:broader
        