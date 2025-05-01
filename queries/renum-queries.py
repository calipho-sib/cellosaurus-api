fname = "query-list.txt"
f_in = open(fname)
f_ou = open(fname + ".renum", "w")
num = 100 # initial query id value
linesep = "\r\n"
while True:
    line = f_in.readline()
    if line=="": break
    line = line.rstrip()
    if line.startswith("ID: "):
        num += 1
        line = f"ID: {num}"
    line = "".join([line, linesep])
    f_ou.write(line)
f_in.close()
f_ou.close()
print("End")
