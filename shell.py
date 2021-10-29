import cloudylang.interpreter as cloudy

print("Welcome to cloudy! [type \"__quit__\" to quit the shell]")

while True:
    text = input("cloudy>>> ")
    if text.rstrip() == "": continue
    if text == "__quit__": break
    result, error = cloudy.run("<stdin>", text)

    if error:
        print(error)
    elif result:
        if len(result.elements) <= 1:
            print(result.elements[0])
        else:
            print(result)