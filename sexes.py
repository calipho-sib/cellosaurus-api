from namespace import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Sex:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label):
        self.label = label
        self.IRI = get_sex_IRI(label)
        self.count = 0
    def __str__(self):
        return f"Sex(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Sexes:
# - - - - - - - - - - - - - - - - - - - - - - - - - - -         
    def __init__(self):
        self.sex_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("SX   "):
                label = line[5:]
                if label not in self.sex_dic: self.sex_dic[label] = Sex(label)
                rec = self.sex_dic[label]
                rec.count += 1
        f_in.close()


    def keys(self):
        return self.sex_dic.keys()
    
    def get(self, k):
        return self.sex_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_sex_IRI(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    prefix = ns.onto.prefix()
    name = label.title().replace(" ", "").replace("(", "").replace(")", "").replace("/","").replace("-","")
    return prefix + ":" + name



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    sexes = Sexes()
    for k in sexes.keys():
        print(sexes.get(k))