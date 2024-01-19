def create_table(data):
    html = "<table>\n"
    
    for row in data:
        html += "<tr>\n"
        for column in row:
            html += f"<td>{column}</td>\n", 

        html += "</tr>\n"
    html += "</table>"
    return html
    
# использование функции
n = int(input())
data = [[int(j)for j in input().split()] for i in range(n)]
html_table = create_table(data)
print(html_table)