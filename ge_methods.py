from namespace_registry import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class GeMethod:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label):
        self.label = label
        self.IRI = get_method_class_IRI(label)
        self.count = 0
    def __str__(self):
        return f"GenomeModificationMethod(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class GenomeModificationMethods:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
        self.method_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("CC   Genetic integration") or line.startswith("CC   Knockout cell"):
                pos = line.find("Method=")
                if pos == -1:
                    print(f"ERROR, no method found at line: {line}")
                    continue
                label = line[pos +7:]
                pos = label.find(";")
                if pos == -1:
                    print(f"ERROR, no ';' found after method at line: {line}")
                    continue
                label = label[0:pos]
                if label not in self.method_dic: self.method_dic[label] = GeMethod(label)
                rec = self.method_dic[label]
                rec.count += 1
        f_in.close()

    def keys(self):
        return self.method_dic.keys()
    
    def get(self, k):
        return self.method_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_method_class_IRI(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    if label == "Not specified": return ns.OBI.GenomeModificationMethod # return most generic class name
    prefix = ns.cello.pfx
    name = label.title().replace(" ", "").replace("(", "").replace(")", "").replace("/","").replace("-","")
    return prefix + ":" + name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_method_clean_label(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    if label == "Not specified": return "Genome modification method" # return label of generic class name
    return label



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    methods = GenomeModificationMethods()
    for k in methods.keys():
        print(methods.get(k))