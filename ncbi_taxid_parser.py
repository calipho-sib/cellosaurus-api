from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
import os

class NcbiTaxid_Parser:

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev):
    # - - - - - - - - - - - - - - - - - - 
        self.abbrev = abbrev
        self.term_dir = "terminologies/" + self.abbrev + "/"
        self.name_dict = dict()
        self.parent_dict = dict()
        self.load_names()
        self.load_nodes()

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_termi_version(self):
    # - - - - - - - - - - - - - - - - - - 
        file_path = self.term_dir + "names.dmp"
        creation_time = os.path.getctime(file_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
        return creation_date

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_with_parent_list(self, some_id):
    # - - - - - - - - - - - - - - - - - - 
        path = [some_id]
        child_id = some_id
        while True:
            parent_id = self.parent_dict.get(child_id)
            if parent_id is None:
                print("WARNING", "found no way to root", path)
                return path
            path.append(parent_id)
            if parent_id == "1": break
            child_id = parent_id
        return path
    
    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_term(self, id):
    # - - - - - - - - - - - - - - - - - - 
        pref = self.get_scientific_name(id)
        if pref is None: return None
        alt = self.get_alternate_names(id)
        parent_id = self.parent_dict.get(id)
        parent_ids = list()
        if parent_id is not None: parent_ids.append(parent_id)
        return Term(id, pref, alt, parent_ids, self.abbrev)



    # - - - - - - - - - - - - - - - - - - 
    def load_names(self):
    # - - - - - - - - - - - - - - - - - - 
        t0 = datetime.now()
        filename = self.term_dir + "names.dmp"
        log_it("INFO:", "Loading", filename)
        max_lines = -1000
        f_in = open(filename)
        line_no = 0
        while True:
            line = f_in.readline()
            if line == "": break
            line_no += 1
            if max_lines > 0 and line_no > max_lines: break
            fields = line.split("|")
            id = fields[0].strip()
            name = fields[1].strip()
            type = fields[3].strip().replace(' ', '_')
            #print(id,name, type)
            if id not in self.name_dict: self.name_dict[id] = ""
            self.name_dict[id] += "|".join([type, name, ""])
        f_in.close()
        log_it("INFO:", "Loaded", filename, duration_since=t0)

    # - - - - - - - - - - - - - - - - - - 
    def load_nodes(self):
    # - - - - - - - - - - - - - - - - - - 
        t0 = datetime.now()
        filename = self.term_dir + "nodes.dmp"
        log_it("INFO:", "Loading", filename)
        max_lines = -1000
        f_in = open(filename)
        line_no = 0
        while True:
            line = f_in.readline()
            if line == "": break
            line_no += 1
            if max_lines > 0 and line_no > max_lines: break
            fields = line.split("|")
            id = fields[0].strip()
            parent_id = fields[1].strip()
            if id in self.parent_dict: 
                print(f"Oopps, {id} seems to have 2 parents, second parent at line {line_no}")
            if id != "1": self.parent_dict[id] = parent_id
        f_in.close()
        log_it("INFO:", "Loaded", filename, duration_since=t0)


    



    # - - - - - - - - - - - - - - - - - - 
    def get_scientific_name(self, id):
    # - - - - - - - - - - - - - - - - - - 
        names = self.name_dict.get(id)
        if names is None:
            print("WARNING: found no names for", id) 
            return None
        elems =  names.split("|")
        for idx in range(len(elems)):
            if elems[idx]=="scientific_name":
                return elems[idx+1]
        print("WARNING: found no names for", id) 
        return None

    # - - - - - - - - - - - - - - - - - - 
    def get_alternate_names(self, id):
    # - - - - - - - - - - - - - - - - - - 
        name_list = list()
        names = self.name_dict.get(id)
        if names is None:
            print("WARNING: found no names for", id) 
            return []
        elems =  names.split("|")
        for idx in range(len(elems)):
            if idx % 2 == 1: continue 
            name_type = elems[idx]
            if name_type=="": break # odd number of elems due to final '|' in name string
            if name_type=="scientific_name": continue
            name_list.append(elems[idx+1])
        return name_list



# =======================================================
if __name__ == '__main__':
# =======================================================

    parser = NcbiTaxid_Parser("NCBI_TaxID")
    path = parser.get_with_parent_list("9606")
    for id in path:
        print(id, parser.get_scientific_name(id))
    print("------")
    for nl in parser.get_alternate_names("9606"):
        print(id, "alternate-name", nl)
    print(parser.get_termi_version())
    
