def main():
    hw = "Hello World!"
    print(hw)
    return ["this", "is", "a", "test"]

def returndict():
    return {"this": 1, "is": 2, "a": 3, "test": 4}


class dynamic_object(object):
    pass

def returnobject():
    retn = dynamic_object()
    retn.first = "this"
    retn.second = "is"
    retn.third = "a"
    retn.fourth = "test"
    return retn
