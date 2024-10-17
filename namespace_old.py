#import re
import hashlib
from ApiCommon import get_rdf_base_IRI, get_help_base_IRI

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def replace_non_alphanumeric(input_string):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     # Use a regular expression to replace non-alphanumeric characters with underscore
#     return re.sub(r'[^a-zA-Z0-9]', '_', input_string)


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
        return getTtlPrefixDeclaration(self.pfx, self.url)
    def getSparqlPrefixDeclaration(self): 
        return getSparqlPrefixDeclaration(self.pfx, self.url)
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
class ShaclNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(ShaclNamespace, self).__init__("sh", "http://www.w3.org/ns/shacl#")
    def declare(self): return "sh:declare"
    def _prefix(self): return "sh:prefix"
    def namespace(self): return "sh:namespace"

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
    def hasPublicationYear(self): return "fabio:hasPublicationYear"
    
    
    
    
    



# Cellosaurus ontology namespace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOntologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OurOntologyNamespace, self).__init__("cello", get_rdf_base_IRI() + "/ontology/")
        #super(OurOntologyNamespace, self).__init__("", get_rdf_base_IRI() + "/ontology/")

    # --------
    # CLASSES
    # --------

    def Database(self): return "cello:Database"

    def CellLine(self): return "cello:CellLine"
 
    # Organization could be a sublass of foaf:Organization or org:Organization
    # see https://www.w3.org/ns/org#%5B4
    def Organization(self): return "cello:Organization"
    
    # publication-related classes
    # see also https://sparontologies.github.io/fabio/current/fabio.html
    # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html

    def Publication(self): return "cello:Publication"
    def Thesis(self): return "cello:Thesis"
    def BachelorThesis(self): return "cello:BachelorThesis"
    def MasterThesis(self): return "cello:MasterThesis"
    def DoctoralThesis(self): return "cello:DoctoralThesis"
    def MedicalDegreeThesis(self): return "cello:MedicalDegreeThesis"
    def MedicalDegreeMasterThesis(self): return "cello:MedicalDegreeMasterThesis"
    def PrivaDocentThesis(self): return "cello:PrivaDocentThesis"
    def VeterinaryMedicalDegreeThesis(self): return "cello:VeterinaryMedicalDegreeThesis"


    def Patent(self): return "cello:Patent"
    def JournalArticle(self): return "cello:JournalArticle"
    def BookChapter(self): return "cello:BookChapter"
    def Book(self): return "cello:Book"
    def TechnicalDocument(self): return "cello:TechnicalDocument"
    def MiscellaneousDocument(self): return "cello:MiscellaneousDocument"
    def ConferencePublication(self): return "cello:ConferencePublication"
    

    def GenomeModificationMethod(self): return "cello:GenomeModificationMethod"

    def Xref(self): return "cello:Xref"
    def GenomeAncestry(self): return "cello:GenomeAncestry"
    def PopulationPercentage(self): return "cello:PopulationPercentage"
    def HLATyping(self): return "cello:HLATyping"
    def Gene(self): return "cello:Gene"
    def Protein(self): return "cello:Protein"
    def GeneAlleles(self): return "cello:GeneAlleles"  # used in HLA
    def MarkerAlleles(self): return "cello:MarkerAlleles"    # used in short tandem repeat

    def SequenceVariation(self): return "cello:SequenceVariation" # most generic class
    def GeneAmplification(self): return "cello:GeneAmplification"
    def GeneDuplication(self): return "cello:GeneDuplication"
    def GeneTriplication(self): return "cello:GeneTriplication"
    def GeneQuadruplication(self): return "cello:GeneQuadruplication"
    def GeneExtensiveAmplification(self): return "cello:GeneExtensiveAmplification"
    def GeneDeletion(self): return "cello:GeneDeletion"
    def GeneFusion(self): return "cello:GeneFusion"
    def GeneMutation(self): return "cello:GeneMutation"
    def RepeatExpansion(self): return "cello:RepeatExpansion"
    def SimpleMutation(self): return "cello:SimpleMutation"
    def UnexplicitMutation(self): return "cello:UnexplicitMutation"

    def AnatomicalElement(self): return "cello:AnatomicalElement"
    def CellType(self): return "cello:CellType"
    def Disease(self): return "cello:Disease"

    def SequenceVariationComment(self): return "cello:SequenceVariationComment"
    def DoublingTimeComment(self): return "cello:DoublingTimeComment"
    def DiscontinuationRecord(self): return "cello:DiscontinuationRecord"
    def KnockoutComment(self): return "cello:KnockoutComment"

    def Annotation(self): return "cello:Annotation" 
    def AnecdotalComment(self): return "cello:AnecdotalComment"
    def CharacteristicsComment(self): return "cello:CharacteristicsComment"
    def BiotechnologyComment(self): return "cello:BiotechnologyComment"
    def DonorInfoComment(self): return "cello:DonorInfoComment"
    def CautionComment(self): return "cello:CautionComment"
    def KaryotypicInfoComment(self): return "cello:KaryotypicInfoComment"
    def MiscellaneousInfoComment(self): return "cello:MiscellaneousInfoComment"
    def MisspellingComment(self): return "cello:MisspellingComment"
    def Registration(self): return "cello:Registration"
    def SenescenceComment(self): return "cello:SenescenceComment"
    def GeneticIntegration(self): return "cello:GeneticIntegration"
    def VirologyComment(self): return "cello:VirologyComment"
    def OmicsComment(self) : return "cello:OmicsComment"
    def Population(self) : return "cello:Population"
    def MicrosatelliteInstability(self): return "cello:MicrosatelliteInstability"
    def MabIsotype(self): return "cello:MabIsotype"
    #def MabTarget(self): return "cello:MabTarget"

    def Antigen(self): return "cello:Antigen" 
    def ChemicalAgent(self): return "cello:ChemicalAgent" # drugbank, ncit, chebi (+free text)
    def TransformantAgent(self): return "cello:TransformantAgent" # ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)
    def ShortTandemRepeatProfile(self): return "cello:ShortTandemRepeatProfile"
    def Species(self): return "cello:Species"

    def Source(self): return "cello:Source" # a superclass of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)

    def Breed(self): return "cello:Breed"
    def Sex(self): return "cello:Sex"

    def CelloTerminology(self): return "cello:CelloTerminology"
    


    # -----------
    # Properties
    # -----------

    # publication properties
    # see also https://sparontologies.github.io/fabio/current/fabio.html
    # see also https://sibils.text-analytics.ch/doc/api/sparql/sibils-ontology.html

    #def hasIdentifier(self): return "cello:hasIdentifier" # generic prop, parent of hasDOI, hasPubMedId # we use the  as an ancestor
    def hasInternalId(self): return "cello:hasInternalId"
    def hasDOI(self): return "cello:hasDOI"
    def hasPubMedId(self): return "cello:hasPubMedId"
    def hasPMCId(self): return "cello:hasPMCId"
    def publicationDate(self): return "cello:publicationDate"
    def hasPublicationYear(self): return "cello:hasPublicationYear"
    def startingPage(self): return "cello:startingPage" 
    def endingPage(self): return "cello:endingPage"
    # journal abbreviation, see also:
    # https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt
    # https://en.wikipedia.org/wiki/ISO_4
    #def hasNLMJournalTitleAbbreviation(self): return "cello:hasNLMJournalTitleAbbreviation" # unused
    def hasISO4JournalTitleAbbreviation(self): return "cello:hasISO4JournalTitleAbbreviation" # Amos uses abbreviation also used by UniProt based on ISO4
    def title(self): return "cello:title"
    def volume(self): return "cello:volume"
    def creator(self): return "cello:creator" # with range = foaf:Person (authors)
    def editor(self): return "cello:editor" # with range = foaf:Person (editors)

    def accession(self): return "cello:accession"
    def primaryAccession(self): return "cello:primaryAccession"
    def secondaryAccession(self): return "cello:secondaryAccession"
    
    def name(self): return "cello:name"
    def shortname(self): return "cello:shortname"
    def recommendedName(self): return "cello:recommendedName"
    def alternativeName(self): return "cello:alternativeName"
    def registeredName(self): return "cello:registeredName"
    def misspellingName(self): return "cello:misspellingName"

    def appearsIn(self): return "cello:appearsIn"
    def source(self): return "cello:source"
    def xref(self): return "cello:xref"
    def reference(self): return "cello:reference"

    def genomeAncestry(self): return "cello:genomeAncestry"
    def component(self): return "cello:component" # component object = population percentage of genome ancestry
    def percentage(self): return "cello:percentage"
    def populationName(self): return "cello:populationName" # as sub property of rdfs:label

    def hlaTyping(self): return "cello:hlaTyping"
    def geneAlleles(self): return "cello:geneAlleles"
    def markerAlleles(self): return "cello:markerAlleles"
    def alleles(self): return "cello:alleles"
    def markerId(self): return "cello:markerId"
    def gene(self): return "cello:gene"
    def partOf(self): return "cello:partOf"

    def _from(self): return "cello:from" # cannot use function name "from" (is python reserved word)
    
    def sequenceVariation(self): return "cello:sequenceVariation"
    def zygosity(self): return "cello:zygosity"
    def hgvs(self): return "cello:hgvs"
    def noneReported(self): return "cello:noneReported"
    def variationStatus(self): return "cello:variationStatus"
    def fromIndividualBelongingToBreed(self): return "cello:fromIndividualBelongingToBreed"
    def sequenceVariationComment(self): return "cello:sequenceVariationComment"
    def annotation(self): return "cello:annotation"
    def datatypeAnnotation(self): return "cello:datatypeAnnotation"
    def objectAnnotation(self): return "cello:objectAnnotation"
    def anecdotalComment(self): return "cello:anecdotalComment"
    def characteristicsComment(self): return "cello:characteristicsComment"
    def biotechnologyComment(self): return "cello:biotechnologyComment"
    def cautionComment(self): return "cello:cautionComment"
    def siteType(self): return "cello:siteType"
    def derivedFromSite(self): return "cello:derivedFromSite" 
    def cellType(self): return "cello:cellType" 
    def donorInfoComment(self): return "cello:donorInfoComment"
    def doublingTimeComment(self): return "cello:doublingTimeComment"
    def duration(self): return "cello:duration"
    def group(self): return "cello:group"
    def karyotypicInfoComment(self): return "cello:karyotypicInfoComment"
    def miscellaneousInfoComment(self): return "cello:miscellaneousInfoComment"
    def misspellingComment(self): return "cello:misspellingComment"
    def registration(self): return "cello:registration"
    def senescenceComment(self): return "cello:senescenceComment"
    def geneticIntegration(self): return "cello:geneticIntegration"
    def virologyComment(self): return "cello:virologyComment"
    def omicsComment(self) : return "cello:omicsComment"
    def fromIndividualBelongingToPopulation(self) : return "cello:fromIndividualBelongingToPopulation"

    def knockout(self): return "cello:knockout"
    def genomeModificationMethod(self): return "cello:genomeModificationMethod"

    def discontinued(self): return "cello:discontinued"
    def discontinuationRecord(self): return "cello:discontinuationRecord"
    def provider(self): return "cello:provider"
    def productId(self): return "cello:productId"
    def microsatelliteInstability(self): return "cello:microsatelliteInstability"
    def msiValue(self): return "cello:msiValue"
    def mabIsotype(self): return "cello:mabIsotype"
    def mabTarget(self): return "cello:mabTarget"
    def antibodyHeavyChain(self): return "cello:antibodyHeavyChain"
    def antibodyLightChain(self): return "cello:antibodyLightChain"
    def resistance(self): return "cello:resistance"
    def transformant(self): return "cello:transformant"
    def shortTandemRepeatProfile(self): return "cello:shortTandemRepeatProfile"
    def conflict(self): return "cello:conflict"
    def fromIndividualWithDisease(self): return "cello:fromIndividualWithDisease" # renamed: OK
    def fromIndividualBelongingToSpecies(self): return "cello:fromIndividualBelongingToSpecies" # renamed: OK
    def fromIndividualWithSex(self): return "cello:fromIndividualWithSex"         # renamed OK
    def fromIndividualAtAge(self): return "cello:fromIndividualAtAge"
    def fromSameIndividualAs(self): return "cello:fromSameIndividualAs" # OI field
    def parentCellLine(self): return "cello:parentCellLine" # HI field
    def childCellLine(self): return "cello:childCellLine" # CH field
    #def category(self): return "cello:category" # CA field
    def publisher(self): return "cello:publisher" # links thesis -> universtities (orga)

    def hasVersion(self): return "cello:hasVersion"
    def created(self): return "cello:created"
    def modified(self): return "cello:modified"

    def organization(self): return "cello:organization"
    def database(self): return "cello:database"
    def memberOf(self): return "cello:memberOf" # defined in https://www.w3.org/ns/org#%5B4
    def city(self): return "cello:city"
    def country(self): return "cello:country"

    def issn13(self): return "cello:issn13"
    def bookTitle(self): return "cello:bookTitle"
    def conferenceTitle(self): return "cello:conferenceTitle"
    def documentTitle(self): return "cello:documentTitle"
    def documentSerieTitle(self): return "cello:documentSerieTitle"
    
    def more_specific_than(self): return "cello:more_specific_than"
    


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
    def Thesis_Citation(self): return "up:THesis_Citation"
    def Book_Citation(self): return "up:Book_Citation"
    def Journal_Citation(self): return "up:JOurnal_Citation"
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


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class CelloWebsiteNamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def __init__(self): 
#         super(CelloWebsiteNamespace, self).__init__("cello", "https://www.cellosaurus.org/")
#     def IRI(self, primaryAccession): return "cello:" + primaryAccession

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
    sh = ShaclNamespace()
    #cello = CelloWebsiteNamespace()
    help = HelpNamespace()

    namespaces = [onto, cvcl, xref, pub, orga, db, xsd, rdf, rdfs, skos, owl, foaf, dcterms, fabio, up, bibo, widoco, vann, oa, org, wdt, wd, sh, help, pubmed]


if __name__ == '__main__':
    myonto = NamespaceRegistry.orga
    print(myonto.getSparqlPrefixDeclaration())
    print(myonto.pfx)
    print(myonto.url)
    print(myonto.pfx)
    print(myonto.url)
    print(myonto.getSQLforVirtuoso())
