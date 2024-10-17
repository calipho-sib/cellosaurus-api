from namespace_registry import NamespaceRegistry as ns

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class HLAGene:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label):
        self.label = label
        self.IRI = get_gene_class_IRI(label)
        self.count = 0
    def __str__(self):
        return f"HLAGene(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class HLAGenes:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
        self.gene_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("CC   HLA typing: "):
                for el in line.split():
                    if "*" in el:
                        gene = "HLA-" + el.split("*")[0]
                        if gene not in self.gene_dic: 
                            self.gene_dic[gene] = HLAGene(gene)
                        gene_rec = self.gene_dic[gene]
                        gene_rec.count += 1
        f_in.close()

    def keys(self):
        return self.gene_dic.keys()
    
    def get(self, k):
        return self.gene_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_gene_class_IRI(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    prefix = ns.cello.pfx
    name = "-".join([label, "Gene"])
    return prefix + ":" + name



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    genes = HLAGenes()
    for k in genes.keys():
        print(genes.get(k))