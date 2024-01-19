a= [(1, 2), (3, 4), (5, 6)]

def genField(a):
    code = "<table>\n"
    obj = '<tr><td>{pos} </td><td> </td><form name="test" method="post" action="input1.php"><td><input type="text" size="40"><td></p></tr>'
    
    for pos in a:
        code += obj.format(pos = pos)
    
    code += "</table>\n"
    return code
print(genField(a))