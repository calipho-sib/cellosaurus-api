from namespaces import BaseNamespace, get_rdf_base_IRI

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CelloOntologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CelloOntologyNamespace, self).__init__("cello", get_rdf_base_IRI() + "/ontology/")

        #
        # Classes
        #

        # Note: described
        # Publication classes 
        self.Publication = self.registerClass("Publication")                    # described
        self.JournalArticle = self.registerClass("JournalArticle")              # described
        self.Patent = self.registerClass("Patent")                              # described
        self.Thesis = self.registerClass("Thesis")                              # described
        self.BachelorThesis = self.registerClass("BachelorThesis")              # described
        self.MasterThesis = self.registerClass("MasterThesis")                  # described
        self.DoctoralThesis = self.registerClass("DoctoralThesis")              # described
        self.MedicalDegreeThesis = self.registerClass("MedicalDegreeThesis")    # described
        self.MedicalDegreeMasterThesis = self.registerClass("MedicalDegreeMasterThesis")    # described
        self.PrivaDocentThesis = self.registerClass("PrivaDocentThesis")        # described
        self.VeterinaryMedicalDegreeThesis = self.registerClass("VeterinaryMedicalDegreeThesis")    # described
        self.Book = self.registerClass("Book")                                  # described
        self.BookChapter = self.registerClass("BookChapter")                    # described
        self.TechnicalDocument = self.registerClass("TechnicalDocument")        # described
        self.MiscellaneousDocument = self.registerClass("MiscellaneousDocument")    # described
        self.ConferencePublication = self.registerClass("ConferencePublication")    # described

        self.CellLine = self.registerClass("CellLine")                          # described
        
        self.GenomeModificationMethod = self.registerClass("GenomeModificationMethod")    # described

        self.Database = self.registerClass("Database")                          # described
        self.CelloConceptScheme = self.registerClass("CelloConceptScheme")      # described

        self.Organization = self.registerClass("Organization")                  # described

        self.Xref = self.registerClass("Xref")                                  # TODO:
        self.GenomeAncestry = self.registerClass("GenomeAncestry")              # described
        self.PopulationPercentage = self.registerClass("PopulationPercentage")  # TODO:

        self.HLATyping = self.registerClass("HLATyping")                        # described as OBI:0001404
        self.HLAGene = self.registerClass("HLAGene")                            # TODO: ongoing
        self.Gene = self.registerClass("Gene")                                  # TODO: ongoing
        self.Locus = self.registerClass("Locus")                                  # TODO: ongoing, used in STR profile    
        self.Allele = self.registerClass("Allele")                                  # TODO: ongoing, used in HLA, str and later in genetic integration
        #self.GeneAlleles = self.registerClass("GeneAlleles")                    # TODO: ongoing , used in HLA typing
        #self.MarkerAlleles = self.registerClass("MarkerAlleles")                # TODO: , used in short tandem repeat

        self.Protein = self.registerClass("Protein")                            # TODO: ongoing

        self.SequenceVariation = self.registerClass("SequenceVariation")        # described incl. related terms
        self.GeneAmplification = self.registerClass("GeneAmplification")        # described incl. related terms
        self.GeneDuplication = self.registerClass("GeneDuplication")            # described incl. related terms
        self.GeneTriplication = self.registerClass("GeneTriplication")          # described incl. related terms
        self.GeneQuadruplication = self.registerClass("GeneQuadruplication")    # described incl. related terms
        self.GeneExtensiveAmplification = self.registerClass("GeneExtensiveAmplification")  # described incl. related terms
        self.GeneDeletion = self.registerClass("GeneDeletion")                  # described incl. related terms
        self.GeneFusion = self.registerClass("GeneFusion")                      # described incl. related terms
        self.GeneMutation = self.registerClass("GeneMutation")                  # described incl. related terms
        self.RepeatExpansion = self.registerClass("RepeatExpansion")            # described incl. related terms
        self.SimpleMutation = self.registerClass("SimpleMutation")              # described incl. related terms
        self.UnexplicitMutation = self.registerClass("UnexplicitMutation")      # described incl. related terms

        self.AnatomicalElement = self.registerClass("AnatomicalElement")        # TODO:
        self.CellType = self.registerClass("CellType")                          # TODO:
        self.Disease = self.registerClass("Disease")                            # TODO:

        self.SequenceVariationComment = self.registerClass("SequenceVariationComment")  # TODO:
        self.DoublingTimeComment = self.registerClass("DoublingTimeComment")            # TODO:
        self.DiscontinuationRecord = self.registerClass("DiscontinuationRecord")        # TODO:

        self.Annotation = self.registerClass("Annotation" )                         # TODO:  keep this one ?
        self.AnecdotalComment = self.registerClass("AnecdotalComment")              # TODO:
        self.CharacteristicsComment = self.registerClass("CharacteristicsComment")  # TODO:
        self.BiotechnologyComment = self.registerClass("BiotechnologyComment")      # TODO:
        self.DonorInfoComment = self.registerClass("DonorInfoComment")              # TODO:
        self.CautionComment = self.registerClass("CautionComment")                  # TODO:
        self.KaryotypicInfoComment = self.registerClass("KaryotypicInfoComment")    # TODO:
        self.MiscellaneousInfoComment = self.registerClass("MiscellaneousInfoComment")  # TODO:
        self.MisspellingComment = self.registerClass("MisspellingComment")          # TODO:
        self.Registration = self.registerClass("Registration")                      # TODO:
        self.SenescenceComment = self.registerClass("SenescenceComment")            # TODO:
        self.GeneKnockout = self.registerClass("GeneKnockout")                      # described as child of OBI:0001364
        self.GeneticIntegration = self.registerClass("GeneticIntegration")          # described as child of OBI:0001364
        self.VirologyComment = self.registerClass("VirologyComment")                # TODO
        self.OmicsComment = self.registerClass("OmicsComment")                      # TODO:
        self.Population = self.registerClass("Population")                          # described
        self.MicrosatelliteInstability = self.registerClass("MicrosatelliteInstability")    # TODO:
        self.MabIsotype = self.registerClass("MabIsotype")                          # TODO:
        #self.MabTarget = self.registerClass("MabTarget")

        self.Antigen = self.registerClass("Antigen")                                # TODO:
        self.ChemicalAgent = self.registerClass("ChemicalAgent")                    # TODO: # drugbank, ncit, chebi (+free text)
        self.TransformantAgent = self.registerClass("TransformantAgent")            # TODO: # ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)
        self.ShortTandemRepeatProfile = self.registerClass("ShortTandemRepeatProfile")  # TODO:
        self.Species = self.registerClass("Species")                                    # TODO:

        self.Source = self.registerClass("Source")                                  # TODO: # define as a superclass of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)

        self.Breed = self.registerClass("Breed")                                    # TODO:
        self.Sex = self.registerClass("Sex")                                        # TODO:

        #
        # Properties
        #

        self.annotation = self.registerObjectProperty("annotation")                     # TODO: keep this one ???        
        self.datatypeAnnotation = self.registerDatatypeProperty("datatypeAnnotation")   # TODO: keep this one ??? 
        self.objectAnnotation = self.registerObjectProperty("objectAnnotation")         # TODO: keep this one ??? 

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
        
        self.name = self.registerDatatypeProperty("name")                               # TODO:
        self.shortname = self.registerDatatypeProperty("shortname")                     # TODO:
        self.recommendedName = self.registerDatatypeProperty("recommendedName")         # TODO:
        self.alternativeName = self.registerDatatypeProperty("alternativeName")         # TODO:
        self.registeredName = self.registerDatatypeProperty("registeredName")           # TODO:
        self.misspellingName = self.registerDatatypeProperty("misspellingName")         # TODO: # should be defined as subProp of skos:hiddenName

        self.appearsIn = self.registerObjectProperty("appearsIn")                       # TODO:
        self.source = self.registerObjectProperty("source")                             # TODO:
        self.xref = self.registerObjectProperty("xref")                                 # TODO:
        self.reference = self.registerObjectProperty("reference")                       # TODO:

        self.genomeAncestry = self.registerObjectProperty("genomeAncestry")             # TODO:
        self.component = self.registerObjectProperty("component")                       # TODO: # component object = population percentage of genome ancestry

        self.population = self.registerObjectProperty("population")                     # TODO: # as link between PopulationPercentage and Population
        self.percentage = self.registerDatatypeProperty("percentage")                   # TODO: # as link between PopulationPercentage and percentage
        self.populationName = self.registerDatatypeProperty("populationName")           # TODO: # as sub property of rdfs:label or cello/foaf/schema:name

        self.hlaTyping = self.registerObjectProperty("hlaTyping")                       # TODO:
        self.geneAlleles = self.registerObjectProperty("geneAlleles")                   # TODO:
        self.markerAlleles = self.registerObjectProperty("markerAlleles")               # TODO:

        self.alleles = self.registerDatatypeProperty("alleles")                         # TODO:
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

        self.derivedFromSite = self.registerObjectProperty("derivedFromSite")           # TODO:
        self.cellType = self.registerObjectProperty("cellType" )                        # TODO:

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

        self.conflict = self.registerDatatypeProperty("conflict")                       # TODO:

        self.fromIndividualWithDisease = self.registerObjectProperty("fromIndividualWithDisease")               # described: # renamed: OK
        self.fromIndividualBelongingToSpecies = self.registerObjectProperty("fromIndividualBelongingToSpecies") # described: # renamed: OK
        self.fromIndividualWithSex = self.registerObjectProperty("fromIndividualWithSex")                       # described

        self.fromIndividualAtAge = self.registerDatatypeProperty("fromIndividualAtAge") # TODO:

        self.fromSameIndividualAs = self.registerObjectProperty("fromSameIndividualAs") # described: # OI field
        self.parentCellLine = self.registerObjectProperty("parentCellLine")             # described: # HI field
        self.childCellLine = self.registerObjectProperty("childCellLine")               # TODO: # as inverse of parentCellLine, CH field
        
        self.publisher = self.registerObjectProperty("publisher")                       # TODO: # links thesis -> universities (orga)

        self.hasVersion = self.registerAnnotationProperty("hasVersion")                 # described as sub of dcterms term
        self.created = self.registerAnnotationProperty("created")                       # described as sub of dcterms term
        self.modified = self.registerAnnotationProperty("modified")                     # described as sub of dcterms term

        self.organization = self.registerObjectProperty("organization")                 # TODO:
        self.database = self.registerObjectProperty("database")                         # TODO:
        self.memberOf = self.registerObjectProperty("memberOf")                         # described as sub of schema:location
        self.city = self.registerDatatypeProperty("city")                               # described as sub of schema:location
        self.country = self.registerDatatypeProperty("country")                         # described as sub of schema:location

        self.issn13 = self.registerDatatypeProperty("issn13")                           # TODO
        self.bookTitle = self.registerDatatypeProperty("bookTitle")                     # TODO
        self.conferenceTitle = self.registerDatatypeProperty("conferenceTitle")         # TODO
        self.documentTitle = self.registerDatatypeProperty("documentTitle")             # TODO
        self.documentSerieTitle = self.registerDatatypeProperty("documentSerieTitle")   # TODO
        
        self.more_specific_than = self.registerObjectProperty("more_specific_than")     # TODO as equivalent of skos:broader
        