def genField(n):
    btn = '<td><button type="button" class="sea" onclick="updateCell({x},{y},0)"></button></td>'
    code = ""
    for x in range(1, n+1):
        code += "<tr>"
        for y in range(1, n+1):
            code += btn.format(x = x, y = y)
        code += "</tr>"
    return code
print(genField(10))