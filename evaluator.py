from smileval.loaders import Loader, Experiment, ExperimentOutcome, ExperimentContext
from smileval.models import ChatCompletionModel, ChatCompletionOptions
from smileval.sessions import initalize_session_persistence

from jsonargparse import ArgumentParser, ActionConfigFile

import random
import asyncio
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

import time

import os

async def main():
    parser = ArgumentParser(prog="smileval", description="Smiley Evaluator for LLMs command line interface.")
    parser.add_argument("--config", action=ActionConfigFile) 
    parser.add_argument("--seed", type = int, default = None, help="Seed used to make things reproducible.")
    parser.add_argument("--namespace", type = str, default = "default", help="experiments labeled with the same namespace will be included in the same report.")
    parser.add_argument("--id", type = str, help = "ID to refer to the experiment with. Must be unique and will overwrite previous experiment with same id.")
    # parser.add_class_arguments(Loader, "loader")
    parser.add_argument("--loader", type = Loader)
    parser.add_argument("--model", type = ChatCompletionModel)
    parser.add_argument("--options", type = ChatCompletionOptions)
    parser.add_argument("--sleep", type = float, default = 0, help="Sleep this long per experiment in serial mode for OpenRouter ratelimits.")
    parser.add_argument("--parallel", type = int, default = 1, help="Max parallel async experiments to run. You may want to set this to 1 if you don't have a batching endpoint.")
    parser.add_argument("--model-name", type = str, default = None, help="Quickly specify chat model name to test using env variables to guess.")
    parser.add_argument("--run-name", type = str, default = None, help="Nickname the run.")

    args = parser.parse_args()
    print(args.get_sorted_keys())
    init_args = parser.instantiate_classes(args)
    print(args)
    loader: Loader = init_args.get("loader")
    chat_model: ChatCompletionModel = init_args.get("model")

    context = ExperimentContext(chat_model)

    initalize_session_persistence()

    sleep_time = args.get("sleep")

    if args.get("seed"):
        seed = args.get("seed")
        print("Using seed", seed)
        random.seed(seed)
        context.set_seed(seed)

    if args.get("options"):
        context.chat_model_options = init_args.get("options")

    parallel = args.get("parallel")

    # TODO: move this into the module perhaps
    index = -1
    if loader.is_determinisitic():
        index = 0
    
    # surely we will never have more experiments than we can store in memory
    # for now?

    experiments: list[Experiment] = list(loader)
    semaphore = asyncio.Semaphore(parallel)
    total = len(experiments)

    async def exec_experiment(exp: Experiment) -> ExperimentOutcome:
        outcome = None
        async with semaphore:
            outcome = await exp.execute(context = context)
        return outcome
    
    # seamphore abuse?
    coroutines = [
        exec_experiment(exp) for exp in experiments
    ]

    results: list[ExperimentOutcome] = []

    if parallel == 1:
        print("Using serial mode.")
        tqdmer = tqdm(coroutines, total = total, desc = "Running experiments in serial mode.")
        for coroutine in tqdmer:
            results.append(await coroutine)
            exp_max_score = sum([result.exp_meta.weight for result in results])
            exp_total_score = sum([result.score for result in results])
            tqdmer.set_description(f"Experiments Serial Mode: Cur results {exp_total_score}/{exp_max_score}")
            if sleep_time > 0:
                time.sleep(sleep_time)
    else:
        results: list[ExperimentOutcome]  = await tqdm_asyncio.gather(*coroutines, total = total, desc = "Running experiments in batches of " + str(parallel))
    

    # print(results)
    exp_max_points = [result.exp_meta.weight for result in results]
    exp_scores = [result.score for result in results]
    max_possible_score = sum(exp_max_points)
    total_score = sum(exp_scores)
    print("ID Printouts")
    for outcome in results:
        print(outcome.exp_meta.name)
    print("Scoring Distribution")
    for outcome in results:
        print(outcome.score)
    print("Scored", total_score, " out of ", max_possible_score, " possible points.")
    print("Distribution", exp_scores)

if __name__ == "__main__":
    asyncio.run(main())