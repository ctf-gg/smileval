from smileval.loaders import Loader, Experiment, ExperimentOutcome

from jsonargparse import ArgumentParser

import random
import asyncio

def main():
    parser = ArgumentParser(prog="smileval", description="Smiley Evaluator for LLMs command line interface.")
    parser.add_argument("--seed", type = int, default = None, help="Seed used to make things reproducible.")
    parser.add_class_arguments(Loader, "loader")
    parser.add_argument("--parellel", type = int, default = 2, help="Max parellel async experiments to run. You may want to set this to 1 if you don't have a batching endpoint.")

    args = parser.parse_args()
    loader: Loader = args.loader

    if arg.seed:
        print("Using seed", args.seed)
        random.seed(args.seed)

    # TODO: move this into the module perhaps
    index = -1
    if loader.is_determinisitic():
        index = 0
    
    # surely we will never have more experiments than we can store in memory
    # for now?

    experiments: list[Experiment] = list(loader)
    semaphore = asyncio.Semaphore(args.parellel)
    total = len(experiments)

    async def exec_experiment(exp: Experiment) -> ExperimentOutcome:
        async with semaphore:
            await exp.execute()

if __name__ == "__main__":
    main()