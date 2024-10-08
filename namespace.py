import re
import hashlib
from ApiCommon import get_rdf_base_IRI, get_help_base_IRI

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def replace_non_alphanumeric(input_string):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Use a regular expression to replace non-alphanumeric characters with underscore
    return re.sub(r'[^a-zA-Z0-9]', '_', input_string)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def getTtlPrefixDeclaration(prefix, baseurl):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    return "".join(["@prefix ", prefix, ": <", baseurl, "> ."])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def getSparqlPrefixDeclaration(prefix, baseurl):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    return "".join(["PREFIX ", prefix, ": <", baseurl, "> "])



# namespace ancestor class 
# handles prefix and base URL
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BaseNamespace:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, prefix, baseurl):
        self.pfx = prefix
        self.url = baseurl
    def prefix(self): return self.pfx
    def baseurl(self): return self.url
    def getTtlPrefixDeclaration(self): 
        return getTtlPrefixDeclaration(self.prefix(), self.baseurl())
    def getSparqlPrefixDeclaration(self): 
        return getSparqlPrefixDeclaration(self.prefix(), self.baseurl())
    def getSQLforVirtuoso(self):
        return f"insert into DB.DBA.SYS_XML_PERSISTENT_NS_DECL values ('{self.pfx}', '{self.url}');"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class PubMedNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(PubMedNamespace, self).__init__("pubmed", "https://www.ncbi.nlm.nih.gov/pubmed/")


#
# impossible because of weird chars and / in identifier
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class DOINamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def __init__(self): 
#         super(DOINamespace, self).__init__("doi", "https://doi.org/")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class XsdNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(XsdNamespace, self).__init__("xsd", "http://www.w3.org/2001/XMLSchema#")

    def escape_string(self, str):
        # escape backslashes with double backslashes (\ => \\)
        str=str.replace("\\","\\\\")
        # escape double-quotes (" => \")
        str = str.replace("\"", "\\\"")
        return str

    # string datatype with triple quotes allow escape chars like \n \t etc.
    def string(self, str):
        if '"' in str:
            return self.string3(str)
        else:
            return self.string1(str)

    def string1(self, str):
        return "".join(["\"", self.escape_string(str), "\"^^xsd:string"])

    def string3(self, str): 
        return "".join(["\"\"\"", self.escape_string(str), "\"\"\"^^xsd:string"])
    
    def date(self, str): return "".join(["\"", str, "\"^^xsd:date"])
    def integer(self, int_number): return str(int_number)
    def float(self, float_number): return "".join(["\"", str(float_number), "\"^^xsd:float"])
    def boolean(self, boolean_value): return str(boolean_value).lower() 
    def dateDataType(self) : return "xsd:date"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(RdfNamespace, self).__init__("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    def type(self): return "rdf:type"
    def Property(self): return "rdf:Property"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(RdfsNamespace, self).__init__("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    def Class(self): return "rdfs:Class"
    def subClassOf(self): return "rdfs:subClassOf"
    def subPropertyOf(self): return "rdfs:subPropertyOf"
    def comment(self): return "rdfs:comment"
    def label(self): return "rdfs:label"
    def domain(self): return "rdfs:domain"
    def range(self): return "rdfs:range"
    def seeAlso(self): return "rdfs:seeAlso"
    def isDefinedBy(self): return "rdfs:isDefinedBy"
    def Literal(self): return "rdfs:Literal"
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OwlNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OwlNamespace, self).__init__("owl", "http://www.w3.org/2002/07/owl#")
    def Class(self): return "owl:Class"
    def DatatypeProperty(self): return "owl:DatatypeProperty"
    def FunctionalProperty(self): return "owl:FunctionalProperty"
    def NamedIndividual(self): return "owl:NamedIndividual"
    def ObjectProperty(self): return "owl:ObjectProperty"
    def TransitiveProperty(self): return "owl:TransitiveProperty"
    def allValuesFrom(self): return "owl:allValuesFrom"
    def sameAs(self): return "owl:sameAs"
    def unionOf(self): return "owl:unionOf"
    def equivalentClass(self): return "owl:equivalentClass"
    def equivalentProperty(self): return "owl:equivalentProperty"
    def versionInfo(self): return "owl:versionInfo"
    def Ontology(self): return "owl:Ontology"
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SkosNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(SkosNamespace, self).__init__("skos", "http://www.w3.org/2004/02/skos/core#")
    def Concept(self): return "skos:Concept"
    def ConceptScheme(self): return "skos:ConceptScheme"
    def inScheme(self): return "skos:inScheme"
    def notation(self): return "skos:notation"
    def prefLabel(self): return "skos:prefLabel"
    def altLabel(self): return "skos:altLabel"
    def broader(self): return "skos:broader"
    def exactMatch(self): return "skos:exactMatch"
    def closeMatch(self): return "skos:closeMatch"
    def broadMatch(self): return "skos:broadMatch"
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WikidataWdNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(WikidataWdNamespace, self).__init__("wd", "http://www.wikidata.org/entity/")
    def IRI(self, ac): return "wd:" + ac
    def P3289_AC(self): return "wd:P3289" 
    def P3578_OI(self): return "wd:P3578"    
    def P9072_OX(self): return "wd:P9072"
    def P5166_DI(self): return "wd:P5166"
    def P3432_HI(self): return "wd:P3432"
    def P21_SX(self):   return "wd:P21" # could not figure out how sex is related to cell lines in wikidata


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WikidataWdtNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(WikidataWdtNamespace, self).__init__("wdt", "http://www.wikidata.org/prop/direct/")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OaNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OaNamespace, self).__init__("oa", "http://www.w3.org/ns/oa#")
    def Annotation(self): return "oa:Annotation"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class W3OrgNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(W3OrgNamespace, self).__init__("org", "http://www.w3.org/ns/org#")
    def site(self): return "org:site"
    def Organization(self): return "org:Organization"
    def memberOf(self): return "org:mermberOf"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FoafNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(FoafNamespace, self).__init__("foaf", "http://xmlns.com/foaf/0.1/")
    def Agent(self): return "foaf:Agent"
    def Person(self): return "foaf:Person"
    def name(self): return "foaf:name"
    def Organization(self): return "foaf:Organization"
    # def Organization(self): return "foaf:Organization" (defined in OurOntologyNamespace)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FabioNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(FabioNamespace, self).__init__("fabio", "http://purl.org/spar/fabio/")
    def hasPubMedCentralId(self): return "fabio:hasPubMedCentralId"
    def hasPubMedId(self): return "fabio:hasPubMedId"
    def Expression(self): return "fabio:Expression"
    def Thesis(self): return "fabio:Thesis"
    def BachelorsThesis(self): return "fabio:BachelorsThesis"
    def MastersThesis(self): return "fabio:MastersThesis"
    def DoctoralThesis(self): return "fabio:DoctoralThesis"
    def Patent(self): return "fabio:Patent"
    def JournalArticle(self): return "fabio:JournalArticle"
    def Book(self): return "fabio:Book"
    def BookChapter(self): return "fabio:BookChapter"
    def ConferencePaper(self): return "fabio:ConferencePaper"
    def TechnicalReport(self): return "fabio:TechnicalReport"
    def hasPubMedCentralId(self): return "fabio:hasPubMedCentralId"
    def hasPubMedId(self): return "fabio:hasPubMedId"
    def hasPubMedId(self): return "fabio:hasPubMedId"
    def hasPublicationYear(self): return "fabio:hasPublicationYear"
    
    
    
    
    



# Cellosaurus ontology namespace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOntologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OurOntologyNamespace, self).__init__("", get_rdf_base_IRI() + "/ontology/")

    # --------
    # CLASSES
    # --------

    def Database(self): return ":Database"

    def CellLine(self): return ":CellLine"
 
    # Organization could be a sublass of foaf:Organization or org:Organization
    # see https://www.w3.org/ns/org#%5B4
    def Organization(self): return ":Organization"
    
    # publication-related classes
    # see also https://sparontologies.github.io/fabio/current/fabio.html
    # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html

    def Publication(self): return ":Publication"
    def Thesis(self): return ":Thesis"
    def BachelorThesis(self): return ":BachelorThesis"
    def MasterThesis(self): return ":MasterThesis"
    def DoctoralThesis(self): return ":DoctoralThesis"
    def MedicalDegreeThesis(self): return ":MedicalDegreeThesis"
    def MedicalDegreeMasterThesis(self): return ":MedicalDegreeMasterThesis"
    def PrivaDocentThesis(self): return ":PrivaDocentThesis"
    def VeterinaryMedicalDegreeThesis(self): return ":VeterinaryMedicalDegreeThesis"

    def GenomeEditingMethod(self): return ":GenomeEditingMethod"

    def Patent(self): return ":Patent"
    def JournalArticle(self): return ":JournalArticle"
    def BookChapter(self): return ":BookChapter"
    def Book(self): return ":Book"
    def TechnicalDocument(self): return ":TechnicalDocument"
    def MiscellaneousDocument(self): return ":MiscellaneousDocument"
    def ConferencePublication(self): return ":ConferencePublication"
    

    def Xref(self): return ":Xref"
    def GenomeAncestry(self): return ":GenomeAncestry"
    def PopulationPercentage(self): return ":PopulationPercentage"
    def HLATyping(self): return ":HLATyping"
    def Gene(self): return ":Gene"
    def Protein(self): return ":Protein"
    def GeneAlleles(self): return ":GeneAlleles"  # used in HLA
    def MarkerAlleles(self): return ":MarkerAlleles"    # used in short tandem repeat

    def SequenceVariation(self): return ":SequenceVariation" # most generic class
    def GeneAmplification(self): return ":GeneAmplification"
    def GeneDuplication(self): return ":GeneDuplication"
    def GeneTriplication(self): return ":GeneTriplication"
    def GeneQuarduplication(self): return ":GeneQuadruplication"
    def GeneExtensiveAmplification(self): return ":GeneExtensiveAmplification"
    def GeneDeletion(self): return ":GeneDeletion"
    def GeneFusion(self): return ":GeneFusion"
    def GeneMutation(self): return ":GeneMutation"
    def RepeatExpansion(self): return ":RepeatExpansion"
    def SimpleMutation(self): return ":SimpleMutation"
    def UnexplicitMutation(self): return ":UnexplicitMutation"

    def AnatomicalElement(self): return ":AnatomicalElement"
    def CellType(self): return ":CellType"
    def Disease(self): return ":Disease"

    def SequenceVariationComment(self): return ":SequenceVariationComment"
    def DoublingTimeComment(self): return ":DoublingTimeComment"
    def DiscontinuationRecord(self): return ":DiscontinuationRecord"
    def KnockoutComment(self): return ":KnockoutComment"

    def Annotation(self): return ":Annotation" 
    def AnecdotalComment(self): return ":AnecdotalComment"
    def CharacteristicsComment(self): return ":CharacteristicsComment"
    def BiotechnologyComment(self): return ":BiotechnologyComment"
    def DonorInfoComment(self): return ":DonorInfoComment"
    def CautionComment(self): return ":CautionComment"
    def KaryotypicInfoComment(self): return ":KaryotypicInfoComment"
    def MiscellaneousInfoComment(self): return ":MiscellaneousInfoComment"
    def MisspellingComment(self): return ":MisspellingComment"
    def Registration(self): return ":Registration"
    def SenescenceComment(self): return ":SenescenceComment"
    def GeneticIntegration(self): return ":GeneticIntegration"
    def VirologyComment(self): return ":VirologyComment"
    def OmicsComment(self) : return ":OmicsComment"
    def PopulationComment(self) : return ":PopulationComment"
    def MicrosatelliteInstability(self): return ":MicrosatelliteInstability"
    def MabIsotype(self): return ":MabIsotype"
    #def MabTarget(self): return ":MabTarget"

    def Antigen(self): return ":Antigen" 
    def ChemicalAgent(self): return ":ChemicalAgent" # drugbank, ncit, chebi (+free text)
    def TransformantAgent(self): return ":TransformantAgent" # ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)
    def ShortTandemRepeatProfile(self): return ":ShortTandemRepeatProfile"
    def Species(self): return ":Species"

    def Source(self): return ":Source" # a superclass of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)

    def Breed(self): return ":Breed"
    def Sex(self): return ":Sex"

    def CelloTerminology(self): return ":CelloTerminology"
    


    # -----------
    # Properties
    # -----------

    # publication properties
    # see also https://sparontologies.github.io/fabio/current/fabio.html
    # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html

    #def hasIdentifier(self): return ":hasIdentifier" # generic prop, parent of hasDOI, hasPubMedId # we use the  as an ancestor
    def hasInternalId(self): return ":hasInternalId"
    def hasDOI(self): return ":hasDOI"
    def hasPubMedId(self): return ":hasPubMedId"
    def hasPMCId(self): return ":hasPMCId"
    def publicationDate(self): return ":publicationDate"
    def hasPublicationYear(self): return ":hasPublicationYear"
    def startingPage(self): return ":startingPage" 
    def endingPage(self): return ":endingPage"
    # journal abbreviation, see also:
    # https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt
    # https://en.wikipedia.org/wiki/ISO_4
    #def hasNLMJournalTitleAbbreviation(self): return ":hasNLMJournalTitleAbbreviation" # unused
    def hasISO4JournalTitleAbbreviation(self): return ":hasISO4JournalTitleAbbreviation" # Amos uses abbreviation also used by UniProt based on ISO4
    def title(self): return ":title"
    def volume(self): return ":volume"
    def creator(self): return ":creator" # with range = foaf:Person (authors)
    def editor(self): return ":editor" # with range = foaf:Person (editors)

    def accession(self): return ":accession"
    def primaryAccession(self): return ":primaryAccession"
    def secondaryAccession(self): return ":secondaryAccession"
    
    def name(self): return ":name"
    def shortname(self): return ":shortname"
    def recommendedName(self): return ":recommendedName"
    def alternativeName(self): return ":alternativeName"
    def registeredName(self): return ":registeredName"
    def misspellingName(self): return ":misspellingName"

    def appearsIn(self): return ":appearsIn"
    def source(self): return ":source"
    def xref(self): return ":xref"
    def reference(self): return ":reference"

    def genomeAncestry(self): return ":genomeAncestry"
    def component(self): return ":component" # component object = population percentage of genome ancestry
    def percentage(self): return ":percentage"
    def populationName(self): return ":populationName" # as sub property of rdfs:label

    def hlaTyping(self): return ":hlaTyping"
    def geneAlleles(self): return ":geneAlleles"
    def markerAlleles(self): return ":markerAlleles"
    def alleles(self): return ":alleles"
    def markerId(self): return ":markerId"
    def gene(self): return ":gene"
    def partOf(self): return ":partOf"

    def _from(self): return ":from" # cannot use function name "from" (is python reserved word)
    
    def sequenceVariation(self): return ":sequenceVariation"
    def zygosity(self): return ":zygosity"
    def hgvs(self): return ":hgvs"
    def noneReported(self): return ":noneReported"
    def variationStatus(self): return ":variationStatus"
    def fromIndividualBelongingToBreed(self): return ":fromIndividualBelongingToBreed"
    def sequenceVariationComment(self): return ":sequenceVariationComment"
    def annotation(self): return ":annotation"
    def datatypeAnnotation(self): return ":datatypeAnnotation"
    def objectAnnotation(self): return ":objectAnnotation"
    def anecdotalComment(self): return ":anecdotalComment"
    def characteristicsComment(self): return ":characteristicsComment"
    def biotechnologyComment(self): return ":biotechnologyComment"
    def cautionComment(self): return ":cautionComment"
    def siteType(self): return ":siteType"
    def derivedFromSite(self): return ":derivedFromSite" 
    def cellType(self): return ":cellType" 
    def donorInfoComment(self): return ":donorInfoComment"
    def doublingTimeComment(self): return ":doublingTimeComment"
    def duration(self): return ":duration"
    def group(self): return ":group"
    def karyotypicInfoComment(self): return ":karyotypicInfoComment"
    def miscellaneousInfoComment(self): return ":miscellaneousInfoComment"
    def misspellingComment(self): return ":misspellingComment"
    def registration(self): return ":registration"
    def senescenceComment(self): return ":senescenceComment"
    def geneticIntegration(self): return ":geneticIntegration"
    def virologyComment(self): return ":virologyComment"
    def omicsComment(self) : return ":omicsComment"
    def populationComment(self) : return ":populationComment"

    def knockout(self): return ":knockout"
    def genomeEditingMethod(self): return ":genomeEditingMethod"

    def discontinued(self): return ":discontinued"
    def discontinuationRecord(self): return ":discontinuationRecord"
    def provider(self): return ":provider"
    def productId(self): return ":productId"
    def microsatelliteInstability(self): return ":microsatelliteInstability"
    def msiValue(self): return ":msiValue"
    def mabIsotype(self): return ":mabIsotype"
    def mabTarget(self): return ":mabTarget"
    def antibodyHeavyChain(self): return ":antibodyHeavyChain"
    def antibodyLightChain(self): return ":antibodyLightChain"
    def resistance(self): return ":resistance"
    def transformant(self): return ":transformant"
    def shortTandemRepeatProfile(self): return ":shortTandemRepeatProfile"
    def conflict(self): return ":conflict"
    def fromIndividualWithDisease(self): return ":fromIndividualWithDisease" # renamed: OK
    def fromIndividualBelongingToSpecies(self): return ":fromIndividualBelongingToSpecies" # renamed: OK
    def fromIndividualWithSex(self): return ":fromIndividualWithSex"         # renamed OK
    def fromIndividualAtAge(self): return ":fromIndividualAtAge"
    def fromSameIndividualAs(self): return ":fromSameIndividualAs" # OI field
    def parentCellLine(self): return ":parentCellLine" # HI field
    def childCellLine(self): return ":childCellLine" # CH field
    #def category(self): return ":category" # CA field
    def publisher(self): return ":publisher" # links thesis -> universtities (orga)

    def hasVersion(self): return ":hasVersion"
    def created(self): return ":created"
    def modified(self): return ":modified"

    def organization(self): return ":organization"
    def database(self): return ":database"
    def memberOf(self): return ":memberOf" # defined in https://www.w3.org/ns/org#%5B4
    def city(self): return ":city"
    def country(self): return ":country"

    def issn13(self): return ":issn13"
    def bookTitle(self): return ":bookTitle"
    def conferenceTitle(self): return ":conferenceTitle"
    def documentTitle(self): return ":documentTitle"
    def documentSerieTitle(self): return ":documentSerieTitle"
    
    def more_specific_than(self): return ":more_specific_than"
    


# Cellosaurus cell-line instances namespace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurCellLineNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OurCellLineNamespace, self).__init__("cvcl", get_rdf_base_IRI() + "/cvcl/")
    def IRI(self, primaryAccession): return "cvcl:" + primaryAccession


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class DctermsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(DctermsNamespace, self).__init__("dcterms", "http://purl.org/dc/terms/")
    def abstract(self): return "dcterms:abstract"
    def created(self): return "dcterms:created"
    def modified(self): return "dcterms:modified"
    def description(self): return "dcterms:description"
    def license(self): return "dcterms:license"
    def title(self): return "dcterms:title"
    def hasVersion(self): return "dcterms:hasVersion"
    def creator(self): return "dcterms:creator"
    def publisher(self): return "dcterms:publisher"
    def contributor(self): return "dcterms:contributor"
    def identifier(self): return "dcterms:identifier"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class VannNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(VannNamespace, self).__init__("vann", "http://purl.org/vocab/vann/")
    def preferredNamespacePrefix(self): return "vann:preferredNamespacePrefix"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BiboNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(BiboNamespace, self).__init__("bibo", "http://purl.org/ontology/bibo/")
    def status(self): return "bibo:status"
    def doi(self): return "bibo:doi"
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WidocoNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(WidocoNamespace, self).__init__("widoco", "https://w3id.org/widoco/vocab#")
    def introduction(self): return "widoco:introduction"
    def rdfxmlSerialization(self): return "widoco:rdfxmlSerialization"
    def turtleSerialization(self): return "widoco:turtleSerialization"
    def ntSerialization(self): return "widoco:ntSerialization"
    def jsonldSerialization(self): return "widoco:jsonldSerialization"




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class UniProtCoreNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(UniProtCoreNamespace, self).__init__("up", "http://purl.uniprot.org/core/")
    def volume(self): return "up:volume"
    def Citation(self): return "up:Citation"
    def Published_Citation(self): return "up:Published_Citation"
    def Thesis_Citation(self): return "up:Published_Citation"
    def Book_Citation(self): return "up:Published_Citation"
    def Journal_Citation(self): return "up:Published_Citation"
    def Annotation(self): return "up:Annotation"
    def annotation(self): return "up:annotation"
    def title(self): return "up:title"
    def version(self): return "up:version"
    def modified(self): return "up:modified"
    def created(self): return "up:created"
    def Database(self): return "up:Database"
    def Protein(self): return "up:Protein"
    



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurXrefNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_dict = dict()
    def __init__(self): super(OurXrefNamespace, self).__init__("xref", get_rdf_base_IRI() + "/xref/")
    def cleanDb(self, db):
        return db.replace("/", "-") # necessary for db="IPD-IMGT/HLA" otherwise IRI contains SLASH which is forbidden
    def IRI(self, db, ac, props, store=True):
        our_dict = OurXrefNamespace.dbac_dict
        # we expect to get props as a string like: cat={cat}|lbl={lbl}|dis={dis}|url={url}
        xref_key = "".join([db,"=", ac])
        if store == True:
            # store requested db ac pairs and optional props for which an IRI was requested 
            # so that we can describe Xref afterwards
            # we use a string to store props rather a dict for memory spare
            if xref_key not in our_dict: our_dict[xref_key] = set()
            # we want to store all distinct props for merging and debug purpose
            our_dict[xref_key].add(props)
        # build a md5 based IRI from db and ac only 
        xref_md5 = hashlib.md5(xref_key.encode('utf-8')).hexdigest()
        return "".join(["xref:", self.cleanDb(db), "_", xref_md5])
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOrganizationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # we store name, shortname, country, city, contact
    nccc_dict = dict()
    def __init__(self): super(OurOrganizationNamespace, self).__init__("orga", get_rdf_base_IRI() + "/orga/")
    def IRI(self, name, shortname, city, country, contact, store=True):
        our_dict = OurOrganizationNamespace.nccc_dict
        # store name, shortname, city, country, contact tuples for which an IRI was requested 
        # so that we can describe Organization afterwards
        org_key = "".join([name, "|", shortname or '', "|", city or '', "|", country or '', "|", contact or ''])
        if store == True:
            if org_key not in our_dict: our_dict[org_key] = 0
            our_dict[org_key] += 1        
        org_md5 = hashlib.md5(org_key.encode('utf-8')).hexdigest()
        org_iri = "".join(["orga:", org_md5])
        return org_iri


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CelloWebsiteNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CelloWebsiteNamespace, self).__init__("cello", "https://www.cellosaurus.org/")
    def IRI(self, primaryAccession): return "cello:" + primaryAccession

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class HelpNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(HelpNamespace, self).__init__("help", get_help_base_IRI() + "/")
    def IRI(self, page): return "help:" + page


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurDatabaseAndTerminologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OurDatabaseAndTerminologyNamespace, self).__init__("db", get_rdf_base_IRI() + "/db/")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurPublicationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_set = set()
    def __init__(self): super(OurPublicationNamespace, self).__init__("pub", get_rdf_base_IRI() + "/pub/")
    def IRI(self, db, ac):
        pub_key = "".join([db, "|", ac])
        # store requested db ac pairs for which an IRI was requested so that we can describe Xref afterwards
        OurPublicationNamespace.dbac_set.add(pub_key)
        pub_md5 = hashlib.md5(pub_key.encode('utf-8')).hexdigest()
        return "".join(["pub:", db, "_", pub_md5])



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NamespaceRegistry:    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # instanciate namespaces
    onto = OurOntologyNamespace()
    cvcl = OurCellLineNamespace()
    xref = OurXrefNamespace()
    pub = OurPublicationNamespace()
    orga = OurOrganizationNamespace()
    db = OurDatabaseAndTerminologyNamespace()
    xsd  = XsdNamespace()
    rdf = RdfNamespace()
    rdfs = RdfsNamespace()
    skos = SkosNamespace()
    owl = OwlNamespace()
    foaf = FoafNamespace()
    dcterms = DctermsNamespace()
    fabio = FabioNamespace()
    up = UniProtCoreNamespace()
    bibo = BiboNamespace()
    widoco = WidocoNamespace()
    vann = VannNamespace()
    #doi = DOINamespace()
    pubmed = PubMedNamespace()
    oa = OaNamespace()
    org = W3OrgNamespace()
    wdt = WikidataWdtNamespace()
    wd = WikidataWdNamespace()
    cello = CelloWebsiteNamespace()
    help = HelpNamespace()

    namespaces = [onto, cvcl, xref, pub, orga, db, xsd, rdf, rdfs, skos, owl, foaf, dcterms, fabio, up, bibo, widoco, vann, oa, org, wdt, wd, cello, help, pubmed]


if __name__ == '__main__':
    myonto = NamespaceRegistry.orga
    print(myonto.getSparqlPrefixDeclaration())
    print(myonto.prefix())
    print(myonto.baseurl())
    print(myonto.pfx)
    print(myonto.url)
    print(myonto.getSQLforVirtuoso())
