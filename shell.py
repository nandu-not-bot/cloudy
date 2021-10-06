import cloudy

print("\nWelcome to cloudy! [type \"__quit__\" to quit the shell]")

while True:
    text = input("cloudy>>> ")
    if text.strip() == "": continue
    if text == "__quit__": break
    result, error = cloudy.run("<stdin>", text)

    if error:
        print(error)
    elif result:
        print(result)
