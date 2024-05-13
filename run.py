from pymend import run
from pathlib import Path
import os



def parse_simplesettings(rawfile: str):
    return [l.split('--', 1)[0].strip() for l in rawfile.strip().splitlines() if not l.startswith('--')]


searchfolder = ''
if os.path.exists('./searchfolder.txt'):
    with open('./searchfolder.txt', 'rt') as sff:
        sff_content = parse_simplesettings(sff.read())
        if len(sff_content) > 0:
            searchfolder = sff_content[0]
            print(f"searchfolder opened with value '{searchfolder}'")
        del sff


def cli():
    print("Python Mend Interpreter")
    while True:
        inp = input('> ').strip().casefold()
        if inp in ('exit', 'quit'): break
        elif inp == 'help':
            print("\n'exit/quit': exits the program\n" +
                  "'help': print this message\n" +
                  "'run [path]': runs the given file"# +
                  #"'code [code]': runs the given code"
                  )
        elif inp.startswith('run '):
            file = Path(searchfolder, inp.removeprefix('run ').removesuffix(".mend") + ".mend")
            if not file.exists(): print(f"path '{file}' does not exist"); continue
            with open(file, 'rt') as f: content = f.read()
            run(content, searchfolder)
        #elif inp.startswith('code '):
        #    run(inp.removeprefix('code '))



if __name__ == "__main__":
    cli()