import cloudy

while True:
    text = input("cloudy>>> ")
    if text.strip() == "": continue
    if text == "__quit__": break
    result, error = cloudy.run("<stdin>", text)

    if error:
        print(error)
    elif result:
        print(result)
