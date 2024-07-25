import os
import json
import pathlib

from .loaders import ExperimentOutcome

class SessionStorage:
    def write_session_outcome(namespace: str, sid: str, outcomes: list[ExperimentOutcome]):
        raise NotImplementedError()

class SessionFilesystemStorage(SessionStorage):
    def __init__(self, experiments_dir: str):
        super()
        self.experiments_path = pathlib.Path(experiments_dir)
    
    def ensure_namespace_setup(self, namespace: str):
        namespace_path = self.experiments_path / namespace
        if not namespace_path.exists():
            namespace_path.mkdir()

    def ensure_session_setup(self, namespace: str, sid: str):
        # session_dir = self.experiments_path / namespace / id
        # if not session_dir.exists():
        #     session_dir.mkdir()
        pass

    def write_session_outcome(self, namespace: str, sid: str, outcomes: list[ExperimentOutcome]):
        self.ensure_namespace_setup(namespace)
        self.ensure_session_setup(namespace, sid)
        with open(self.experiments_path / namespace / f"{sid}.session.json", "w") as f:
            json.dump({
                "namespace": namespace,
                "id": sid,
                "outcomes": [
                    outcome.serialize() for outcome in outcomes
                ],
                "version": 1
            }, f)

def initalize_session_persistence(directory = None) -> SessionFilesystemStorage:
    if not directory:
        directory = os.getcwd()

    experiments_dir = os.path.join(directory, "experiments")
    data_dir = os.path.join(directory, "data")
    # TODO: error handle these?
    if not os.path.isdir(experiments_dir):
        os.mkdir(experiments_dir)
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    return SessionFilesystemStorage(experiments_dir)