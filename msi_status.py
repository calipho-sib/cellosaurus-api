from api_platform import ApiPlatform
from namespace_registry import NamespaceRegistry


# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class MsiStatus:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, label, ns: NamespaceRegistry):
        self.label = label
        self.IRI = get_Msi_Status_IRI(label, ns)
        self.count = 0
    def __str__(self):
        return f"MsiStatus(label:{self.label}, IRI:{self.IRI}, count:{self.count})"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class MsiStatusList:
# - - - - - - - - - - - - - - - - - - - - - - - - - - -       
    #     97 Instable (MSI)
    #     93 Instable (MSI-high)
    #     62 Instable (MSI-low)
    #   1230 Stable (MSS)
  
    def __init__(self, ns: NamespaceRegistry):
        self.status_dic = dict()
        f_in = open("data_in/cellosaurus.txt")
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.rstrip()
            if line.startswith("CC   Microsatellite instability"):
                parts = line.split(": ")[1].split(" ")
                label = " ".join([parts[0], parts[1]])
                if label not in self.status_dic: self.status_dic[label] = MsiStatus(label, ns)
                rec = self.status_dic[label]
                rec.count += 1
        f_in.close()


    def keys(self):
        return self.status_dic.keys()
    
    def get(self, k):
        return self.status_dic.get(k)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_Msi_Status_IRI(label, ns):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    label2IRI = {
        "Stable (MSS)": "MicrosatelliteInstabilityStatusStable",
        "Instable (MSI)": "MicrosatelliteInstabilityStatusInstable",
        "Instable (MSI-low)": "MicrosatelliteInstabilityStatusInstableLow",
        "Instable (MSI-high)": "MicrosatelliteInstabilityStatusInstableHigh"
    }
    prefix = ns.cello.pfx
    name = label2IRI[label]
    return prefix + ":" + name



# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    statusList = MsiStatusList(NamespaceRegistry(ApiPlatform("local")))
    for k in statusList.keys():
        print(statusList.get(k))