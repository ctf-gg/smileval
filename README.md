# smileval
funny evaluator for llms, possibly crossplatform.
## usage
A test config is included as an example.
```bash
python evaluator.py --config test_config.yml
```
An evaluation matrix is done per namespace which can also be changed in the config. Each test should have it's unique name which will be a column header which should be changed in config. Don't like yaml files? We use `jsonargparse` so you can pass a bunch of cli args as well.
## generate csv to import into spreadsheet
Run 
```bash
python generate-report.py experiments/yournamespace
```
and check your namespace folder after
