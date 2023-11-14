from rdfizer import BaseNamespace, CloNamespace, getBlankNode, XsdNamespace, OwlNamespace

# usage: pytest test_rdfizer.py

def test_base_namespace_class():
    url = "http://test.org/rdf#"
    pfx = "ns0"
    ns = BaseNamespace(baseurl=url, prefix=pfx)
    assert ns.baseurl() == url
    assert ns.prefix() == pfx
    assert ns.getTtlPrefixDeclaration() == "@prefix " + pfx + ": <" + url + "> ."

def test_clo_namespace_class():
    url = "http://cellosaurus.org/rdf#"
    pfx = ""
    clo = CloNamespace()
    assert clo.baseurl() == url
    assert clo.prefix() == pfx
    assert clo.getTtlPrefixDeclaration() == "@prefix " + pfx + ": <" + url + "> ."
    assert clo.CellLine() == pfx + ":CellLine"
    assert clo.group() == pfx + ":group"

def test_blank_node_generation():
    n1 = getBlankNode()
    # Blank nodes always start with _:BN
    assert n1.startswith("_:BN")
    # Blank nodes are random strings is 36 chars long (including 4 first fixed chars)
    assert len(n1) == 36
    n2 = getBlankNode()
    # Blank nodes generated are always different
    assert n1 != n2

def test_xsd_namespace():
    xsd = XsdNamespace()
    # strings are delimited with triple <"> to allow multiline strings, etc.
    s = xsd.string("jack")
    assert s == "\"\"\"jack\"\"\"^^xsd:string"
    s = xsd.date("2022-08-27")
    # dates are delimited with single <">
    assert s == "\"2022-08-27\"^^xsd:date"
    # integers have no delimiters nor xsd data type (syntax shortcut allowed in ttl)
    s = xsd.integer(234)
    assert s == "234"

def test_x():
    owl = OwlNamespace()
    owl.Class()