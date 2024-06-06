# ------------------------
class Term:
# ------------------------
    def __init__(self, id, prefLabel, altLabelList, parentIdList, scheme):
        self.id = id
        self.prefLabel = prefLabel
        self.altLabelList = altLabelList
        self.parentIdList = parentIdList
        self.scheme = scheme

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


    # - - - - - - - - - - - - - - - - - - - - 
    def get(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - 
        return self.onto_dict.get(abbrev)

