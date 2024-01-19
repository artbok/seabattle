size = int(input('Размер '))
name = input("Название ")
x = int(input())
y = int(input())

class Battle_field:
    field = []
    def __init__(self, n):

        for i in range(n+1):
            self.field.append([0] * (n+ 1))
            
    
    def __repr__(self) -> str:
        visualisation = ""
        for i in self.field:
            visualisation += str(i) + '\n'
        return visualisation
    def editing(self, x, y):
        if self.field[x][y]:
            self.field[x][y] = 0
        else:
            can_place = ((self.field[x - 1][y-1] == 0) and (self.field[x - 1][y+1] == 0) 
                    and (self.field[x + 1][y-1] == 0) and (self.field[x + 1][y+1] == 0)
                    and (self.field[x][y-1] == 0) and (self.field[x + 1][y] == 0)
                    and (self.field[x][y+1]) and (self.field[x - 1][y] == 0))
            if can_place:
                self.field[x][y] = 1
        data = set()
        data.add((x, y))
        data.remove((x, y))
field = Battle_field(size)

while True:
    print(field.editing(x, y))
    print(field)
    x = int(input())
    y = int(input())
