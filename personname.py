import sys

'''
firstname can be:
Jean                => J.
Jean Pierre         => J.P.
Jean P.             => J.P.
J.P.                => J.P.
Jean-Pierre         => J.-P.
J.-P.               => J.-P.
'''

# --------------------------------
class PersonName:
# --------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, new_format: str):
    # - - - - - - - - - - - - - - - - - - - - - - - - 
        self.new_format = new_format
        self.old_format = None
        self.lastname = None
        self.firstnames = None
        self.suffix = None
        self.invalid = False
        name_parts = new_format.split(", ")
        if len(name_parts) != 2:
            self.invalid = True
            print("ERROR: unexpected format for author name:", new_format)
            return
        self.lastname = name_parts[0]
        firstname_list = list()
        for elem in name_parts[1].split(" "):
            if elem in ["Jr.", "Sr.", "II", "III", "IV", "2nd", "3rd", "4th"]:
                self.suffix = elem
            else:
                firstname_list.append(elem)
        self.firstnames = " ".join(firstname_list)
        self.old_format = self.revert_format(new_format)


    # - - - - - - - - - - - - - - - - - - - - - - - - 
    def revert_format(self, new_format: str):
    # - - - - - - - - - - - - - - - - - - - - - - - - 
        (lastname, firstnames) = new_format.split(", ")
        parts = list()
        parts.append(lastname + " ")
        for elem in firstnames.split(" "):
            subel_no = 0
            for subelem in elem.split("-"):
                subel_no += 1
                if subel_no > 1: parts.append("-")
                if subelem in ["Jr.", "Sr.", "II", "III", "IV", "2nd", "3rd", "4th"]:
                    parts.append(" " + subelem)
                elif "." in subelem: 
                    parts.append(subelem) 
                else:
                    parts.append(subelem[0:1] + ".")
        return "".join(parts)

    # - - - - - - - - - - - - - - - - - - - - - - - - 
    def __repr__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - 
        return f"Author( new={self.new_format}, old={self.old_format}, last={self.lastname}, first={self.firstnames}, sfx={self.suffix}, invalid={self.invalid} )"



if __name__ == '__main__':

    new_names = ["Martinez, Ramon 3rd"]
    for new_name in new_names:
        print(new_name)
        print(PersonName(new_name))
        print("-----")

    if 1==1: sys.exit(0)
    # the files are supposed to contain the same number of lines and the same name at each line, resp in old and in new format.
    f_old = open("ra-old.txt")
    f_new = open("ra-new.txt")
    line_no=0
    while True:
        line_old = f_old.readline()
        line_new = f_new.readline()
        if line_old == "": break
        line_no +=1
        auth_old = line_old.strip()
        auth_new = line_new.strip()
        author = PersonName(auth_new)
        auth_rev = author.old_format
        if auth_old != auth_rev:
            print("line", line_no, ":", auth_new, "=>", auth_rev, "but expected", auth_old)
            print("author", author)
    f_old.close()
    f_new.close()