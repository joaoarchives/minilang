import sys


def main():
    if len(sys.argv) < 2:
        print("uso: python -m minilang arquivo.mini", file=sys.stderr)
        sys.exit(2)
    caminho = sys.argv[1]
    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()
    print(fonte)            # por enquanto, só ecoa


if __name__ == "__main__":
    main()
