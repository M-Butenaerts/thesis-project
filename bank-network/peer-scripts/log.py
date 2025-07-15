def log(text, file="/tmp/log.txt"):
    with open(file, "a") as f:
        f.write(text + "\n")
