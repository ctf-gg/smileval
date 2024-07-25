from jsonargparse import ArgumentParser, ActionConfigFile

import os

def main():
    parser = ArgumentParser(prog="smilevalreport", description="Smiley evaluation report generator")
    parser.add_argument("path")
    # TODO: refactor this to use the module
    os.listdir("")
    

if __name__ == "__main__":
    main()