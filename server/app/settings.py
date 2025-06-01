# pylint: disable=line-too-long
# ruff: noqa

from pathlib import Path

import yaml

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the data file
DATA_FILE_PATH = BASE_DIR / 'data' / 'data.json'

# Agent configuration
AGENT_NAME = 'Poligon Smaków Assistant'

# Load prompts from YAML file
PROMPTS_FILE_PATH = BASE_DIR / 'prompts' / 'agents_prompts.yml'
with open(PROMPTS_FILE_PATH, 'r', encoding='utf-8') as f:
    _prompts = yaml.safe_load(f)

TRIAGE_AGENT_INSTRUCTIONS = _prompts['triage_agent_instructions']
INFORMATION_AGENT_INSTRUCTIONS = _prompts['information_agent_instructions']
ORDER_AGENT_INSTRUCTIONS = _prompts['order_agent_instructions']
RESERVATION_AGENT_INSTRUCTIONS = _prompts['reservation_agent_instructions']

# Database settings
DATABASE_URL = 'sqlite:///../restaurant_data.db'
