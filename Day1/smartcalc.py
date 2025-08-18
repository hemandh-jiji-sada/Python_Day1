

x = int(input("Enter the first number: "))
y = int(input("Enter the second number: "))
print("""+: Addition
-: Subtraction
*: Multiplication
/: Division
**: Exponentiation
% Modulus""")
while True :
    c = input("Enter a choice: 1/2/3/4/quit :")
    if c == "+":
        print("Result: ",x," + ",y,"= ",x+y)
    elif c == "-":
        print("Result: ",x," - ",y,"= ", x - y)
    elif c == "*":
        print("Result: ",x," * ",y,"= ", x * y)
    elif c == "/":
        print("Result: ",x," / ",y,"= ", x / y)
    elif c == "**":
        print("Result: ",x," ** ",y,"= ", x ** y)
    elif c == "%":
        print("Result: ",x," % ",y,"= ", x % y)
    elif c == "q" or c == "quit":
        print("Calculator shutting down")
        break
    else:
        print("Invalid Input")
