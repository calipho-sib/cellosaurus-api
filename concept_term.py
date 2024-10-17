

# - - - - - - - - - - - - - - - - - - - - - - 
class ConceptTermData:
# - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
        f_in = open("data_in/concept_cello_terms_onto.txt")
        self.prefixes = dict()
        self.data = dict()
        line_no = 0
        section_key = None
        section_rec = None
        term_key = None
        term_rec = None
        while True:
            line = f_in.readline()
            if line == "":break
            line_no += 1
            line == line.strip()
            if line == "" or line.startswith("#"): continue

            if line.startswith("PX   "):
                pfx, baseurl = line[5:].split()
                self.prefixes[pfx] = baseurl

            elif line.startswith("SC   "):
                section_key = line[5:].split()[0]
                section_rec = dict()
                self.data[section_key] = section_rec
                
            elif line.startswith("LB   "):
                term_key = line[5:].split("[")[0].split("(")[0].strip() 
                term_rec = { "EQ": list(), "BR": list(), "<<": list(), "CL": list() }
                section_rec[term_key] = term_rec
                
            elif line.startswith("IR   "):
                term_key = line[5:].strip() 
                term_rec = { "EQ": list(), "BR": list(), "<<": list(), "CL": list() }
                section_rec[term_key] = term_rec

            elif line.startswith("EQ   ") or line.startswith("BR   ") or line.startswith("<<   ") or line.startswith("CL   "):
                key = line[0:2]
                words = line[5:].split("[")[0].split("(")[0].strip().split()
                iri = words[0]
                lbl = " ".join(words[1:])
                pfx, ac = iri.split(":")
                expanded_iri = self.prefixes[pfx] + ac
                related_term = {"IRI": expanded_iri, "LB": lbl}
                term_rec[key].append(related_term)
                                
        f_in.close()
    
    def getCelloTerms(self, section_key): return self.data[section_key].items()
    def getSuperClassTermList(self, term): return term["<<"]
    def getEquivalentTermList(self, term): return term["EQ"]
    def getBroaderTermList(self, term) : return term["BR"]
    def getCloseTermList(self, term) : return term["CL"]
    def getTermIRI(self, term):   return term["IRI"]
    def getTermLabel(self, term): return term["LB"]

    def getCelloTermKeys(self, section_key): return self.data[section_key]
    def getCelloTerm(self, section_key, term_key): return self.data[section_key][term_key]



# = = = = = = = = = = = = = = = = = = = = = = = = 
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = =

    obj = ConceptTermData()

    for k in obj.prefixes:
        print(k, obj.prefixes[k])

    print("---------------")

    sections = ["CellLine", "GenomeModificationMethod", "CellLineProperties", "SequenceVariation", "MiscClasses"]
    for sct in sections:
        print("section (super class):", sct)
        for key in obj.getCelloTermKeys(sct):
            data = obj.getCelloTerm(sct, key)
            print("cello term key:",key)
            for eqTerm in obj.getEquivalentTermList(data):
                iri = obj.getTermIRI(eqTerm)
                lbl = obj.getTermLabel(eqTerm)
                print(f"  EQ <{iri}> : '{lbl}'")
            for brTerm in obj.getBroaderTermList(data):
                iri = obj.getTermIRI(brTerm)
                lbl = obj.getTermLabel(brTerm)
                print(f"  BR <{iri}> : '{lbl}'")
            for brTerm in obj.getCloseTermList(data):
                iri = obj.getTermIRI(brTerm)
                lbl = obj.getTermLabel(brTerm)
                print(f"  CL <{iri}> : '{lbl}'")
            for brTerm in obj.getSuperClassTermList(data):
                iri = obj.getTermIRI(brTerm)
                lbl = obj.getTermLabel(brTerm)
                print(f"  << <{iri}> : '{lbl}'")

    print("---------------")

    for ct_key in obj.getCelloTermKeys("SequenceVariation"):
        print("cello_term_key", ct_key)
        for prop_key in obj.getCelloTerm("SequenceVariation", ct_key):
            print("prop_key", prop_key)
            prop_term = "???"
            if prop_key == "EQ": prop_term = "owl:"