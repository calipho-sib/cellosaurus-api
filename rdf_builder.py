import uuid
from namespace import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_prefixes():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    lines = list()
    for item in ns.namespaces:
        lines.append(item.getTtlPrefixDeclaration())
    return "\n".join(lines) + "\n"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_blank_node():
# -- - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return "_:BN" + uuid.uuid4().hex


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cl(ac, cl_obj):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    print(cl_obj)
    lines = list()
    cl_iri = ns.inst.IRI(ac)
    line = " ".join([ cl_iri, ns.rdf.type(), ns.onto.CellLine(), ".\n" ])
    lines.append(line)
    cl_data = cl_obj["cell-line"]
    for ac_obj in cl_data["accession-list"]:
        some_ac = ns.xsd.string(ac_obj["value"])
        line = " ".join([ cl_iri, ns.onto.accession(), some_ac, ".\n" ])
        lines.append(line)
        pred = ns.onto.primaryAccession() if ac_obj["type"] == "primary" else ns.onto.secondaryAccession()
        line = " ".join([ cl_iri, pred, some_ac, ".\n" ])
        lines.append(line)

    return("".join(lines))

