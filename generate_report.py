from jsonargparse import ArgumentParser, ActionConfigFile

import os
import csv

def main():
    parser = ArgumentParser(prog="smilevalreport", description="Smiley evaluation report generator")
    parser.add_argument("path")

    args = parser.parse_args()

    sessions_path = args.get("path")

    # TODO: refactor this to use the module
    files = os.listdir(sessions_path)
    session_files = []
    for filename in files:
        if filename.endswith(".session.json"):
            session_files.append(os.path.join(sessions_path, filename))

    seen_exp_ids = set()
    exp_ids = []
    

if __name__ == "__main__":
    main()