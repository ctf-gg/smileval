from jsonargparse import ArgumentParser, ActionConfigFile

import os
import csv
import json

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
    session_ids = []
    session_kv = {}

    for session_file_path in session_files:
        with open(session_file_path, "r") as f:
            session_data = json.load(f)
            sid = session_data["id"]
            session_ids.append(sid)
            namespace = session_data["namespace"]
            serialized_outcomes = session_data["outcomes"]
            session_kv[sid] = {}
            total = 0
            for outcome in serialized_outcomes:
                exp_id = outcome["name"]
                session_kv[sid][exp_id] = outcome
                total += outcome["score"]
                # TODO: tag counting?    
                if not exp_id in seen_exp_ids:
                    seen_exp_ids.add(exp_id)
                    exp_ids.append(exp_id)
    output_csv_file_path = os.path.join(sessions_path, "report.csv")
    with open(output_csv_file_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames = ["Experiment or Metric"] + list(session_ids))
        writer.writeheader()
        row = {
            "Experiment or Metric": exp_id
        }
        for sid in session_ids:



if __name__ == "__main__":
    main()