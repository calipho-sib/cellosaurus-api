from lxml import html


# - - - - - - - - - - - - - - - - - - 
class HtmlBuilder:
# - - - - - - - - - - - - - - - - - - 


    # - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - 
        self.nav_node = self.get_navigation_node()


    # - - - - - - - - - - - - - - - - - - 
    def get_navigation_node(self):
    # - - - - - - - - - - - - - - - - - - 
        input_file = "./html.templates/nav.template.html"
        tree = self.get_html_tree(input_file)
        return tree.xpath('//nav')[0]

    # - - - - - - - - - - - - - - - - - - 
    def add_nav_node_to_body(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        body_node = some_tree.xpath('//body')[0]
        nav_node = self.get_navigation_node()
        body_node.insert(0, nav_node)


    # - - - - - - - - - - - - - - - - - - 
    def add_nav_css_link_to_head(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        # <link type="text/css" rel="stylesheet" href="navstyles.css">
        head_node = some_tree.xpath("//head")[0]
        lnk = html.Element("link")
        lnk.set("type", "text/css")
        lnk.set("rel", "stylesheet")
        lnk.set("href", "static/navstyles.css")
        head_node.insert(0, lnk)


    # - - - - - - - - - - - - - - - - - - 
    def get_html_tree(self, filename):
    # - - - - - - - - - - - - - - - - - - 
        f_in = open(filename, 'r', encoding='utf-8')
        html_content = f_in.read()
        f_in.close()
        return html.fromstring(html_content)



# =======================================================
if __name__ == '__main__':
# =======================================================
    builder = HtmlBuilder()
    #nav_node =  builder.nav_node
    #print("nav  node:",nav_node)
    some_tree = builder.get_html_tree("./html.templates/api-basic-help.template.html")
    # body_node = some_tree.xpath('//body')[0]
    # print("body node:", body_node)
    # body_node.insert(0, nav_node)
    builder.add_nav_node_to_body(some_tree)
    builder.add_nav_css_link_to_head(some_tree)
    f_out = open("./static/test.html", 'wb')
    f_out.write(html.tostring(some_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8"))
    f_out.close()
