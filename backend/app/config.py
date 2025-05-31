from omegaconf import OmegaConf
import os

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.yaml'))
config = OmegaConf.load(CONFIG_PATH)
backend_config = config.backend 