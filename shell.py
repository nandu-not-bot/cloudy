import cloudy

while True:
    text = input("cloudy>>> ")
    if text == "": continue
    result, error = cloudy.run("<stdin>", text)

    if error:
        print(error)
    elif result:
        print(result)
