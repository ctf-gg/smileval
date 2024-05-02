from smileval.loaders import Loader

from jsonargparse import ArgumentParser

def main():
    parser = ArgumentParser(prog="smileval", description="Smiley Evaluator for LLMs command line interface.")
    parser.add_argument("--seed", type = int, default = None, help="Seed used to make things reproducible.")
    parser.add_class_arguments(Loader, "loader")
    parser.add_argument("--parellel", type = int, default = 2, help="Max parellel async experiments to run.")

    args = parser.parse_args()
    loader: Loader = args.loader

    # TODO: move this into the module
    if loader.is_determinisitc():
        

if __name__ == "__main__":
    main()