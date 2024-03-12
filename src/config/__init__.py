import os
import yaml

opt_config_path = os.path.dirname(os.path.abspath(__file__)) + "/optimization_vars.yaml"

pso_setup_path = os.path.dirname(os.path.abspath(__file__)) + "/pso_setup.yaml"

simulation_path = os.path.dirname(os.path.abspath(__file__)) + "/simulation.yaml"

eco_path = os.path.dirname(os.path.abspath(__file__)) + "/economics.yaml"

inv_path = os.path.dirname(os.path.abspath(__file__)) + "/investiments.csv"


def get_config(config_file_path):
    with open(config_file_path, "r") as yaml_file:
        cfg = yaml.safe_load(yaml_file)

    return cfg


settings = {}
settings.update(get_config(opt_config_path))
settings.update(get_config(pso_setup_path))
settings.update(get_config(simulation_path))
settings.update(get_config(eco_path))
