# ------------------------
class Term:
# ------------------------
    def __init__(self, id, prefLabel, altLabelList, parentIdList, scheme):
        self.id = id
        self.prefLabel = prefLabel
        self.altLabelList = altLabelList
        self.parentIdList = parentIdList
        self.scheme = scheme

    def __str__(self):
        return(f"Term({self.id}, {self.prefLabel}, parents: {self.parentIdList} )")

# ------------------------
class Terminology:
# ------------------------
    def __init__(self, abbrev, name, url, parser_name):
        self.abbrev = abbrev 
        self.name = name
        self.url = url
        self.parser_name = parser_name
        self.version = "" # set later by parser

# ------------------------
class Terminologies:
# ------------------------
    def __init__(self):

        self.termi_dict = dict()

        self.termi_dict["NCBI_TaxID"] = Terminology(
            "NCBI_TaxID", "NCBI taxonomy database", 
            "https://www.ncbi.nlm.nih.gov/taxonomy", "NcbiTaxid_Parser")

        self.termi_dict["ChEBI"] = Terminology(
            "ChEBI", "Chemical Entities of Biological Interest", 
            "https://www.ebi.ac.uk/chebi/", "Chebi_Parser")

        self.termi_dict["CL"] = Terminology(
            "CL", "Cell Ontology", 
            "https://obophenotype.github.io/cell-ontology/", "Cl_Parser")

        self.termi_dict["UBERON"] = Terminology(
            "UBERON", "Uber-anatomy ontology", 
            "https://uberon.github.io/", "Uberon_Parser")

        self.termi_dict["NCIt"] = Terminology(
            "NCIt", "NCI thesaurus", 
            "https://ncit.nci.nih.gov/ncitbrowser", "Ncit_Parser")

        self.termi_dict["ORDO"] = Terminology(
            "ORDO", "Orphanet Rare Disease Ontology", 
            "https://www.ebi.ac.uk/ols4/ontologies/ordo", "Ordo_Parser")
        
        self.termi_dict["VBO"] = Terminology(
            "VBO", "Vertebrate Breed Ontology", 
            "https://monarch-initiative.github.io/vertebrate-breed-ontology/", "Vbo_Parser")
        
        self.termi_dict["RS"] = Terminology(
            "RS", "Rat Strain Ontology", 
            "https://github.com/rat-genome-database/RS-Rat-Strain-Ontology", "Rs_Parser")
        
        

    # - - - - - - - - - - - - - - - - - - - - 
    def get(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - 
        return self.termi_dict.get(abbrev)

