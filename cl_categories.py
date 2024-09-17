from namespace import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class CellLineCategory:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label):
        self.label = label
        self.IRI = get_cl_category_IRI(label)
        self.count = 0
    def __str__(self):
        return f"CellLineCategory(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class CellLineCategories:
# - - - - - - - - - - - - - - - - - - - - - - - - - - -         
    def __init__(self):
        self.cat_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("CA   "):
                label = line[5:]
                if label not in self.cat_dic: self.cat_dic[label] = CellLineCategory(label)
                rec = self.cat_dic[label]
                rec.count += 1
        f_in.close()


    def keys(self):
        return self.cat_dic.keys()
    
    def get(self, k):
        return self.cat_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_cl_category_IRI(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    prefix = ns.onto.prefix()
    name = label.title().replace(" ", "").replace("(", "").replace(")", "").replace("/","").replace("-","")
    return prefix + ":" + name



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    cats = CellLineCategories()
    for k in cats.keys():
        print(cats.get(k))