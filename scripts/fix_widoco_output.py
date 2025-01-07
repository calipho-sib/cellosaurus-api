from lxml import html
import sys

input_file = sys.argv[1]
f_in = open(input_file, 'r', encoding='utf-8')
html_content = f_in.read()
f_in.close()
tree = html.fromstring(html_content)

dd_list = tree.xpath('//dd')
for elems in dd_list:
    if len(elems) == 4:
        if elems[0].tag == "a" and "exactMatch" in elems[0].get("href"):
            # remove spaces in hallucinated labels of skos:exactMatch objects in 3rd element
            elems[2].text = elems[2].text.replace(" ", "")
            # remove wrong "annotation property tag" added to skos:exactMatch in 2nd element <sup class="type-ap ...>"
            elems[1].getparent().remove(elems[1])
            # remove wrong "external property tag" added to object in last elem <sup class="type-ep" ... >
            elems[2].getparent().remove(elems[2])
            #print(elems[2].text)
            #print(elems[0].get("href"))

nodes_to_be_deleted = list()
dd_list = tree.xpath('//dd')
for elems in dd_list:
    if len(elems)>0 and elems[0].tag == "a" and "_:genid" in elems[0].get("href"):
        nodes_to_be_deleted.append(elems)
        print("to be deleted:", elems.tag)
        nodes_to_be_deleted.append(elems.getprevious())
        print("to be deleted:", elems.getprevious().tag)
for node in nodes_to_be_deleted:
    node.getparent().remove(node)

output_file = input_file + ".fixed"
f_out = open(output_file, 'wb')
f_out.write(html.tostring(tree, pretty_print=True, method="html", encoding="utf-8"))
f_out.close()

