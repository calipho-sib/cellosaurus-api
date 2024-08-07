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
class Ontology:
# ------------------------
    def __init__(self, abbrev, name, url, parser_name):
        self.abbrev = abbrev 
        self.name = name
        self.url = url
        self.parser_name = parser_name
        self.version = "" # set later by parser

# ------------------------
class Ontologies:
# ------------------------
    def __init__(self):

        self.onto_dict = dict()

        self.onto_dict["NCBI_TaxID"] = Ontology(
            "NCBI_TaxID", "NCBI taxonomy database", 
            "https://www.ncbi.nlm.nih.gov/taxonomy", "NcbiTaxid_Parser")

        self.onto_dict["ChEBI"] = Ontology(
            "ChEBI", "Chemical Entities of Biological Interest", 
            "https://www.ebi.ac.uk/chebi/", "Chebi_Parser")

        self.onto_dict["CL"] = Ontology(
            "CL", "Cell Ontology", 
            "https://obophenotype.github.io/cell-ontology/", "Cl_Parser")

        self.onto_dict["UBERON"] = Ontology(
            "UBERON", "Uber-anatomy ontology", 
            "https://uberon.github.io/", "Uberon_Parser")

        self.onto_dict["NCIt"] = Ontology(
            "NCIt", "NCI thesaurus", 
            "https://ncit.nci.nih.gov/ncitbrowser", "Ncit_Parser")

        self.onto_dict["ORDO"] = Ontology(
            "ORDO", "Orphanet Rare Disease Ontology", 
            "https://www.ebi.ac.uk/ols4/ontologies/ordo", "Ordo_Parser")
        
        self.onto_dict["VBO"] = Ontology(
            "VBO", "Vertebrate Breed Ontology", 
            "https://monarch-initiative.github.io/vertebrate-breed-ontology/", "Vbo_Parser")
        
        self.onto_dict["RS"] = Ontology(
            "RS", "Rat Strain Ontology", 
            "https://github.com/rat-genome-database/RS-Rat-Strain-Ontology", "Rs_Parser")
        
        

    # - - - - - - - - - - - - - - - - - - - - 
    def get(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - 
        return self.onto_dict.get(abbrev)

