from mini_redis import MiniRedis


def main():
    redis = MiniRedis()

    while True:
        try:
            line = input("mini-redis> ")
        except EOFError:
            print()
            break

        stripped = line.strip()
        if stripped.lower() == "exit" or stripped.lower() == "quit":
            break

        result = redis.execute(stripped)
        if result != "":
            print(result)


if __name__ == "__main__":
    main()
