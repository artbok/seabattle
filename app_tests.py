from app import getPos, EditField
def unitTestA1():
    ans = getPos(1, 1)
    expected = "А1"
    if ans == expected:
        print(f"test1: OK")
    else:
        print(f"Error on test1:\nGot: {ans} Expected: {expected}")

def unitTestShipA1():
    obj = EditField("test", 2)
    obj.placeShip(1, 1)
    ans = obj.field
    expected = [["", "А", "Б"], ["1", 1, 0], ["2", 0, 0]]
    if ans == expected:
        print(f"test2: OK")
    else:
        print(f"Error on test2:\nGot: {ans} Expected: {expected}")
    del obj

def unitTestClosePlacing():
    obj2 = EditField("test", 2, [], set())
    obj2.placeShip(1, 1)
    ans = obj2.placeShip(2, 2)
    expected = False
    if ans == expected:
        print(f"test3: OK")
    else:
        print(f"Error on test3:\nGot: {ans} Expected: {expected}")

def runTests():
    print("Running UnitTests...")
    unitTestA1()
    unitTestShipA1()
    unitTestClosePlacing()