from sys import argv
import cloudylang.interpreter as cloudy

if len(argv) <= 1:
    import shell
    quit()

# fn = argv[1]
fn = "first.cdy"

if (t:=fn.split('.')[-1]) != "cdy":
    print(f"Unsupported file type '.{t}'")

else:
    try:
        with open(fn, "r") as f:
            script = f.read()

    except Exception as e:
        print(e, "\n Failed to load script.")

    _, error = cloudy.run(fn, script)

    if error:
        print("Could not finish running script.\n", error)