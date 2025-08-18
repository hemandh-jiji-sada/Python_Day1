

print('''1: Celsius to Fahrenheit
2: Fahrenheit to Celsius
3: Celsius to Kelvin
4: Kelvin to Celsius
q: Quit ''')
c = input("Enter the conversion type:")
while True :
    if c == 1:
        tc = int(input("Enter the temperature(C) :"))
        tf = (tc * 9/5) + 32
        print("Temperature(F) :",tf)
    elif c == 2:
        tf = int(input("Enter the temperature(F) :"))
        tc = (tf - 32) * 5/9
        print("Temperature(C) :",tc)
    elif c == 3:
        tc = int(input("Enter the temperature(C) :"))
        tk = 
