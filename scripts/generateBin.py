import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_PATH = os.path.join(BASE_DIR, "test.bin")


def main():
    print(f"Writing to: {BIN_PATH}")
    with open(BIN_PATH, "wb") as f:
        f.write(b"A" * 600)


if __name__ == "__main__":
    main()
