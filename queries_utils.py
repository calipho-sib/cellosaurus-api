from namespace_registry import NamespaceRegistry

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Query:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.id = None
        self.label = None
        self.keywords = list()
        self.prefixes = list()
        self.sparql = list()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __str__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        lines.append(f"Query({self.id},")
        lines.append(f"  {self.label},")
        lines.append(f"  {self.keywords},")
        for line in self.sparql:
            lines.append("  " + line)
        lines.append(")")
        return "\n".join(lines)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def set_necessary_sparql_prefixes(self, ns_reg: NamespaceRegistry):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.prefixed = list()
        for ns in ns_reg.namespaces:
            pattern = f"{ns.pfx}:"
            for sparql_line in self.sparql:
                if pattern in sparql_line:
                    self.prefixes.append(f"PREFIX {ns.pfx}: <{ns.url}>")
                    break



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_sparql_endpoint(self, ns_reg: NamespaceRegistry):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        #
        # Output example:
        # cello:Query_002 a sh:SPARQLExecutable ;
        # rdfs:comment "Count of publication citations" ; 
        # sh:select "select (count(*) as ?cnt) where { ?cl rdf:type / rdfs:subClassOf cello:Publication . }" ; 
        # .
        #
        lines = list()
        lines.append(f"cello:Query_{self.id} a sh:SPARQLExecutable ;")
        lines.append(f"    rdfs:comment \"{self.label}\"^^xsd:string ; ")
        lines.append(f"    sh:select \"\"\"")
        self.set_necessary_sparql_prefixes(ns_reg)
        for line in self.prefixes: lines.append(f"{line}")
        for line in self.sparql: lines.append(f"{line}")
        lines.append(f"    \"\"\"")
        lines.append(f"    .")
        return "\n".join(lines)




    def get_ttl_for_github():
        pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class QueryFileReader:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
        f_in = open("./queries/query-list.txt", "r")
        isFirstId = True
        query: Query = Query()
        self.query_list = list[Query]()
        while True:
            line = f_in.readline()
            if line == '': break
            line = line.rstrip()
            if line == '': continue
            if line.startswith("##"): continue
            if line.startswith("ID: "):
                if not isFirstId: self.query_list.append(query)
                query = Query()
                query.id = line[4:].lstrip()
                isFirstId = False
            elif line.startswith("LB: "):
                query.label = line[4:].lstrip()
            elif line.startswith("KW: "):
                for k in line[4:].lstrip().split(","):
                    query.keywords.append(k.strip())
            else:
                query.sparql.append(line)
        self.query_list.append(query)
        f_in.close()


if __name__ == '__main__':



    reader = QueryFileReader()
    for q in reader.query_list:
        print(q)
        print("-----")        
        print(q.get_ttl_for_sparql_endpoint())
        print("---------------------------------------")        
