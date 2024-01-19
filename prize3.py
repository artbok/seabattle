def create_table(data):
    html = "<table>\n"
    for row in data:
        html += "<tr>\n"
        for column in row:
            html += f"<td>{column}</td>\n"
        html += "</tr>\n"
    html += "</table>"
    return html

# использование функции
data = priz = [['vvytgt7',"24"],['huhyu','34'],['wgcr','34'],['whccjh.e','34'],['ecjh22c','34']]
html_table = create_table(data)
print(html_table)