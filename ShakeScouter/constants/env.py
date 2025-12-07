from pathlib import Path

# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

# Environment Values
TELEMETRY_PATH = str(Path(__file__).resolve().parents[2] / '.telemetry' / '{}.json')

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PACKAGE_ROOT / 'templates'
MODELS_DIR = PACKAGE_ROOT / 'models'


def template_path(name: str) -> Path:
	return TEMPLATE_DIR / f'{name}.png'

# Train Environment Values
DIGIT_WIDTH      = 16
DIGIT_HEIGHT     = 20
DIGIT_MODEL_PATH = MODELS_DIR / 'digit-64-9873.pth'

# Development Environment Values
DEV_ASSET_PATH       = '../.dev/{}.png'
DEV_DIGIT_DATA_PATH  = MODELS_DIR / 'dataset.json'
DEV_DIGIT_MODEL_PATH = MODELS_DIR / 'digit-dev.pth'
