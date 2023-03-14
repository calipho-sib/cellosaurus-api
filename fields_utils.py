import datetime
from ApiCommon import CELLAPI_VERSION

class FldDef:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, file_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if file_name is None: file_name = 'fields_def.txt'
        f_in = open(file_name)
        line_no=0
        fld_dic = dict()
        while True:
            line = f_in.readline()
            if line == "": break
            line_no +=1
            line = line.strip()
            if line == "": continue
            if line[0:1]=="#": continue
            if line.startswith("TG   "):
                key=line[5:].lower().strip()         # make sure key only uses low case
                prefixes = list()
                xpaths = list()
                help_blocks = list()
            elif line.startswith("PR   "):
                prefixes.append(line[5:])
            elif line.startswith("XP   "):
                xpaths.append(line[5:])
            elif line.startswith("DE   "):
                help_blocks.append(line[5:].strip())
            elif line.startswith("//"):
                fld_dic[key] = {"prefixes": prefixes, "xpaths": xpaths, "help": " ".join(help_blocks)}
        f_in.close()
        self.fld_dic = fld_dic


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.fld_dic.keys()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_prefixes(self, fld_tags):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fld_tags is None or fld_tags=="": return None

        tags = fld_tags if isinstance(fld_tags,list) else fld_tags.split(",")
        pr_set = set()
        for tag in tags:
            fld = self.fld_dic.get(tag.lower().strip())
            if fld is None: continue
            for pr in fld["prefixes"]:
                pr_set.add(pr)
        return pr_set


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_xpaths(self, fld_tags):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fld_tags is None or fld_tags=="": return None

        tags = fld_tags if isinstance(fld_tags,list) else fld_tags.split(",")
        xp_set = set()
        for tag in tags:
            fld = self.fld_dic.get(tag.lower())
            if fld is None: continue
            for xp in fld["xpaths"]:
                xp_set.add(xp)
        return xp_set

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_description(self, tag):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if tag is None: tag==""
        rec = self.fld_dic.get(tag.lower().strip())
        descr = rec.get("help") if rec is not None else None
        return descr if descr is not None else "Sorry, no description"
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def build_enum(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f_out = open("fields_enum.py", "w")
        f_out.write("#\n# Generated : " + datetime.datetime.now().isoformat().replace('T',' ')[:19] + "\n#\n\n")
        f_out.write("from enum import Enum\n\n")
        f_out.write("class Fields(str, Enum):\n")
        for k in self.fld_dic.keys():
            f_out.write("\t" + k.replace("-","_").upper() + " = \"" + k + "\"\n")
        f_out.write("\n\n")
        f_out.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def build_help_page(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # read HTML template
        f=open("fields_help_page.template.html","r")
        template = f.read()
        f.close()
        
        # build final help file from template and fld def
        rows = ""
        for tag in self.fld_dic.keys():
            #print("tag",tag)
            #print("descr",self.get_description(tag))
            row = """<tr><td class="parameters-col_name" style="padding-right: 10px;">""" +  tag + """</td><td class="parameters-col_description">""" +  self.get_description(tag) + "</td></tr>\n"
            rows += row
        content = template.replace("$rows", rows).replace("$version",CELLAPI_VERSION)
        f_out = open("static/fields_help.html", "w")
        f_out.write(content)
        f_out.close()
        
        # f_out.write("#\n# Generated : " + datetime.datetime.now().isoformat().replace('T',' ')[:19] + "\n#\n\n")
        # f_out.write("from enum import Enum\n\n")
        # f_out.write("class Fields(str, Enum):\n")

# ===========================================================================================
if __name__ == "__main__":
# ===========================================================================================

    fldDef = FldDef(None)
    
    fldDef.build_enum()
    print("Built file fields_enum.py")
    
    fldDef.build_help_page()
    print("Built file static/fields_help.py")
    
    print("End")

    if 1==2:
        # some basic tests
    
        cd = FldDef(None)
        for k in cd.keys():
            for pr in cd.get_prefixes(k):
                print(k, "->", pr)
    
        print("-----")
        s1 = cd.get_prefixes("IDSY,CC-group,RA")
        s2 = cd.get_prefixes(["IDSY","CC-group","RA"])
        s3 = cd.get_prefixes("IDSY")
        print(s1)
        print(s2)
        print(s3)
        s1 = cd.get_xpaths("IDSY,CC-group,RA")
        s2 = cd.get_xpaths(["IDSY","CC-group","RA"])
        s3 = cd.get_xpaths("IDSY")
        print(s1)
        print(s2)
        print(s3)

