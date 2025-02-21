from lxml import html
from api_platform import ApiPlatform

# - - - - - - - - - - - - - - - - - - 
class HtmlBuilder:
# - - - - - - - - - - - - - - - - - - 


    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, platform: ApiPlatform):
    # - - - - - - - - - - - - - - - - - - 
        self.platform = platform
        self.nav_node = self.get_navigation_node()
        


    # - - - - - - - - - - - - - - - - - - 
    def get_navigation_node(self):
    # - - - - - - - - - - - - - - - - - - 
        input_file = "./html.templates/nav.template.html"
        content = self.get_file_content(input_file)
        content = content.replace("$sparql_service_url", self.platform.get_public_sparql_service_IRI())
        html_tree = html.fromstring(content)
        return html_tree.xpath('/html/body/nav')[0]


    # - - - - - - - - - - - - - - - - - - 
    def add_nav_node_to_body(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        body_node = some_tree.xpath('/html/body')[0]
        nav_node = self.get_navigation_node()
        body_node.insert(0, nav_node)


    # - - - - - - - - - - - - - - - - - - 
    def get_script_node(self):
    # - - - - - - - - - - - - - - - - - - 
        input_file = "./html.templates/nav.template.html"
        content = self.get_file_content(input_file)
        html_tree = html.fromstring(content)
        return html_tree.xpath('/html/head/script')[0]


    # - - - - - - - - - - - - - - - - - - 
    def add_script_node_to_head(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        head_node = some_tree.xpath('/html/head')[0]
        script_node = self.get_script_node()
        head_node.append(script_node)


    # - - - - - - - - - - - - - - - - - - 
    def add_nav_css_link_to_head(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        # <link type="text/css" rel="stylesheet" href="navstyles.css">
        head_node = some_tree.xpath("/html/head")[0]
        lnk = html.Element("link")
        lnk.set("type", "text/css")
        lnk.set("rel", "stylesheet")
        lnk.set("href", "/static/navstyles.css")
        head_node.insert(0, lnk)

    # - - - - - - - - - - - - - - - - - - 
    def fix_ontology_css_collisions(self, some_tree):
    # - - - - - - - - - - - - - - - - - - 
        body = some_tree.xpath("/html/body")[0]
        body.set("style", "padding: 0px;")
        cont = body.xpath("./div[@class='container']")[0]
        cont.set("style", "padding-left: 80px;")
        stat = cont.xpath("./div[@class='status']")[0]
        stat.set("style", "top: 80px;")
        

    # - - - - - - - - - - - - - - - - - - 
    def get_file_content(self, filename):
    # - - - - - - - - - - - - - - - - - - 
        f_in = open(filename, 'r', encoding='utf-8')
        file_content = f_in.read()
        f_in.close()
        return file_content

    # - - - - - - - - - - - - - - - - - - 
    def get_html_tree(self, filename):
    # - - - - - - - - - - - - - - - - - - 
        html_content = self.get_file_content(filename)
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
