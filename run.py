from pymend import run
from pathlib import Path


def cli():
    while True:
        inp = input('> ').strip().casefold()
        if inp in ('exit', 'quit'): break
        elif inp == 'help':
            print("\n'exit/quit': exits the program\n" +
                  "'help': print this message\n" +
                  "'run [path]': runs the given file")
        elif inp.startswith('run '):
            file = Path(inp.removeprefix('run ').removesuffix(".mend") + ".mend")
            if not file.exists(): print(f"path '{file}' does not exist"); continue
            with open(file, 'rt') as f: content = f.read()
            run(content)



if __name__ == "__main__":
    cli()