def buidNamespaceClassFile(nsName, nsPrefix, nsBaseurl, ontologyFile, prefixInOntologyFile=""):
    lines = list()
    INDENT = "    "
    QUOTE = "\""
    lines.append("from rdfizer import BaseNamespace\n"])
    lines.append("".join(["class", " ", nsName, "(BaseNamespace):\n"]))
    lines.append("".join([INDENT, "def __init__(self):\n"]))
    lines.append("".join([INDENT, INDENT, "super(", nsName, ", self).__init__(", QUOTE, nsPrefix, QUOTE,  ",", QUOTE, nsBaseurl, QUOTE, ")\n"]))
    # declare terms of namespace
    f_in = open(ontologyFile)
    termDefPrefix= prefixInOntologyFile +":"
    while(True):
        line = f_in.readline()
        if line == "": break
        if line.startswith(termDefPrefix):
            term = line.strip().split(" ")[0][len(termDefPrefix):]
            #       def subClassOf(self): return "rdfs:subClassOf"
            elems = [INDENT, "def ", term, "(self): return ", QUOTE, nsPrefix, ":", term, QUOTE, "\n"]
            lines.append("".join(elems))
    f_in.close()

    output_file = nsName + ".py"
    f_out = open(output_file, "w")
    for l in lines:
        f_out.write(l)
    f_out.close()


if __name__ == '__main__':
    buidNamespaceClassFile("SibiloNamespace", "", "http://sibils.org/rdf#", "../rdf4sibils/ontology/sibils-ontology.ttl")

