from namespace import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Database:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev, name, url, cat):
        self.abbrev = abbrev
        self.rdf_id = ns.xref.cleanDb(abbrev)
        self.name = name
        self.url = url
        self.cat = cat
    def __str__(self):
        return(f"Database({self.abbrev}, {self.name}, {self.url}, {self.cat}, rdf_id={self.rdf_id})")
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Databases:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, src_file="data_in/cellosaurus_xrefs.txt"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
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
                self.db_dict[abbrev] = Database(abbrev, name, url, cat)
        f_in.close()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def keys(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.db_dict.keys()
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return self.db_dict.get(abbrev)

    
    
    
# = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = =
    dbs = Databases()
    for abbrev in dbs.keys():
        db = dbs.get(abbrev) 
        if db.rdf_id != abbrev:
            print(abbrev, "==>", db )