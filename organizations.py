

# ---------------------------------------------
class Organization:
# ---------------------------------------------

# - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, name, shortname=None, city=None, country=None, contact=None, isInstitute=False, isOnlineResource=False):
# - - - - - - - - - - - - - - - - - - - - - - 
        self.name = name
        self.shortname = shortname
        self.city = city
        self.country = country
        self.contact = contact
        self.isInstitute = isInstitute
        self.isOnlineResource = isOnlineResource

# - - - - - - - - - - - - - - - - - - - - - - 
    def __str__(self):
# - - - - - - - - - - - - - - - - - - - - - - 
        return f"Organization({self.name}, {self.shortname}, {self.city}, {self.country}, {self.contact}, {self.isInstitute}, {self.isOnlineResource})"


# ---------------------------------------------
class KnownOrganizations:
# ---------------------------------------------

# - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
# - - - - - - - - - - - - - - - - - - - - - - 
        self.korg_dict = dict()

# - - - - - - - - - - - - - - - - - - - - - - 
    def loadInstitutions(self, file):
# - - - - - - - - - - - - - - - - - - - - - - 
        f_in = open(file) # we expect institution_list file here
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.strip()
            pos = line.find("; Short=")
            if pos == -1:
                name = line
                shortname = None
            else: 
                name = line[0:pos]
                shortname = line[pos + 8:]
            korg = Organization(name = name, shortname = shortname, isInstitute=True)
            other_korg = None
            if name in self.korg_dict: other_korg = self.korg_dict[name]
            if shortname in self.korg_dict: other_korg = self.korg_dict[shortname]
            if other_korg is None:
                if name is not None and len(name)>0: self.korg_dict[name] = korg
                if shortname is not None and len(shortname)>0: self.korg_dict[shortname] = korg
            else:
                print(f"WARNING: will ne insert\n{korg}\nwhile\n{other_korg} already exists")
                
        f_in.close()

# - - - - - - - - - - - - - - - - - - - - - - 
    def loadOnlineResources(self, file):
# - - - - - - - - - - - - - - - - - - - - - - 
        f_in = open(file) # we expect cellosaurus_xrefs.txt file here
        shortname = None
        name = None
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.strip()

            if line.startswith  ("Abbrev: "): 
                shortname = line[8:].strip()
            elif line.startswith("Name  : "): 
                name = line[8:].strip()
            elif line.startswith("//"):
                korg = Organization(name = name, shortname = shortname, isOnlineResource=True)
                if name in self.korg_dict and shortname in self.korg_dict:
                    #print("case 1 - update")
                    self.korg_dict[name].isOnlineResource = True
                else:
                    other_korg = None
                    if name in self.korg_dict: 
                        other_korg = self.korg_dict[name]
                    elif shortname in self.korg_dict:
                        other_korg = self.korg_dict[shortname]
                    if other_korg is None:
                        #print("case 2 - insert")
                        if name is not None and len(name)>0: self.korg_dict[name] = korg
                        if shortname is not None and len(shortname)>0: self.korg_dict[shortname] = korg
                    else:
                        #print("case 3 - ignore")
                        print(f"WARNING: will ignore\n{korg}\nsince\n{other_korg}\nalready exists")
                shortname = None
                name = None                
        f_in.close()

# - - - - - - - - - - - - - - - - - - - - - - 
    def get(self, key):
# - - - - - - - - - - - - - - - - - - - - - - 
        return self.korg_dict.get(key)      

# - - - - - - - - - - - - - - - - - - - - - - 
    def print(self):
# - - - - - - - - - - - - - - - - - - - - - - 
        for k in self.korg_dict:
            print(k, "-->", self.korg_dict[k])        
        


# ===========================================================================================
if __name__ == "__main__":
# ===========================================================================================

    known_orgs = KnownOrganizations()
    known_orgs.loadInstitutions("data_in/institution_list")
    known_orgs.loadOnlineResources("data_in/cellosaurus_xrefs.txt")
    known_orgs.print()
