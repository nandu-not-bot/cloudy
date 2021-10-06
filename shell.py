import cloudy

while True:
    text = input("cloudy>>> ")
    result, error = cloudy.run("<stdin>", text)

    if error:
        print(error)
    elif result:
        print(result)
