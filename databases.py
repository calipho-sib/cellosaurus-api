from namespace_registry import NamespaceRegistry
from api_platform import ApiPlatform

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Database:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev, name, url, cat, in_up, ns):
        self.abbrev = abbrev
        self.rdf_id = ns.xref.cleanDb(abbrev)
        self.name = name
        self.url = url
        self.cat = cat
        self.in_up = in_up
    def __str__(self):
        return(f"Database({self.abbrev}, {self.name}, {self.url}, {self.cat}, rdf_id={self.rdf_id}, in_up={self.in_up})")
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Databases:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, ns, src_file="data_in/cellosaurus_xrefs.txt"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        f_in = open("uniprot-db-abbr.txt")
        self.uniprot_set = set()
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.strip()
            if line.startswith("#"): continue
            if line == "": continue
            self.uniprot_set.add(line)
        f_in.close()

        self.db_dict = dict()
        f_in = open(src_file)
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.strip()
            if line.startswith(  "Abbrev: "):
                abbrev = line[8:]; name = ""; url = ""; cat = ""
            elif line.startswith("Name  : "):
                name = line[8:]
            elif line.startswith("Server: "):
                url = line[8:]
            elif line.startswith("Cat   : "):
                cat = line[8:]
            elif line.startswith("//"):
                in_up = abbrev in self.uniprot_set
                self.db_dict[abbrev] = Database(abbrev, name, url, cat, in_up, ns)
        f_in.close()

        self.cats = dict()
        for db_key in self.db_dict:
            db = self.db_dict[db_key]
            cat = db.cat
            if cat not in self.cats: 
                self.cats[cat] = { "label": cat, "count": 0, "IRI": get_db_category_IRI(cat, ns)}
            rec = self.cats[cat]
            rec["count"] += 1


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def categories(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.cats 


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def keys(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.db_dict.keys()
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.db_dict.get(abbrev)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_db_category_IRI(label, ns):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    prefix = ns.cello.pfx
    name = label.title().replace(" ", "").replace("(", "").replace(")", "").replace("/","").replace("-","")
    return prefix + ":" + name
    
    
# = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = =
    ns = NamespaceRegistry(ApiPlatform("local"))
    dbs = Databases(ns)
    for abbrev in dbs.keys():
        db = dbs.get(abbrev) 
        print(abbrev, "==>", db )
    print("----- cats -----")
    for cat in dbs.categories():
        print(dbs.categories()[cat])