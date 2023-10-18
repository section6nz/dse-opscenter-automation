DSE OpsCenter API automation
===

This script allows provisioning of a declarative definition of a DSE cluster and associated
configuration in a YAML file.

1. Define cluster topology and configuration in `config/config.yaml`. An example has been provided
   in `config/sample_config.yaml`
2. Install python dependencies: `pip install -r requirements.txt`.
3. Run script: `python main.py` to apply the cluster topology and associated configurations.

Optionally:

* Specify a config file to use: `main.py -f config/sample_config.yaml`
* Run an install job and wait for completion using `--install`. This will also
  enable [node sync](https://docs.datastax.com/en/dse/6.8/docs/managing/configure/about-nodesync.html)
  if defined in the cluster configuration.

## Acknowledgements

Based on examples from https://github.com/justinbreese/dse-opscenter-api-examples
