def get_numbers() -> list[int]:
    return [1, 2, 3]

for number in get_numbers():
    print(number)


def make_numbers():
    yield 1
    yield 2
    yield 3

for number in make_numbers():
    print(number)