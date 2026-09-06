with open("pyproject.toml", "r") as file:
    file.seek(11)
    print(file.read())
    print(file.tell())
