from api_platform import ApiPlatform
from namespace_registry import NamespaceRegistry


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Sex:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label, ns: NamespaceRegistry):
        self.label = label
        self.IRI = get_sex_IRI(label, ns)
        self.count = 0
    def __str__(self):
        return f"Sex(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Sexes:
# - - - - - - - - - - - - - - - - - - - - - - - - - - -         
    def __init__(self, ns: NamespaceRegistry):
        self.sex_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("SX   "):
                label = line[5:]
                if label not in self.sex_dic: self.sex_dic[label] = Sex(label, ns)
                rec = self.sex_dic[label]
                rec.count += 1
        f_in.close()


    def keys(self):
        return self.sex_dic.keys()
    
    def get(self, k):
        return self.sex_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_sex_IRI(label, ns):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    prefix = ns.cello.pfx
    name = label.title().replace(" ", "").replace("(", "").replace(")", "").replace("/","").replace("-","")
    return prefix + ":" + name



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    sexes = Sexes(NamespaceRegistry(ApiPlatform("local")))
    for k in sexes.keys():
        print(sexes.get(k))