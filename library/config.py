
from pathlib import Path
from typing import Dict, Any, List
from caldav import DAVClient
import yaml


def quit_on_fatal():
    print('FATAL: fix your config first, program exit')
    exit(1)


def to_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if not isinstance(value, list):
        return [value,]

    return value


def read_config(
    env_path: Path | str,
    template_dict: Dict[str, Any],
) -> Dict[str, Any] | None:
    configs = {}
    env_path_str = (
        env_path
        if isinstance(env_path, str)
        else
        str(env_path.resolve())
    )

    with open(env_path_str, 'r') as fin:
        configs_raw = yaml.safe_load(fin) or {}

    for config_key in template_dict:
        config_raw = configs_raw.get(config_key)

        if isinstance(template_dict[config_key], list):
            config_raw = to_list(config_raw)

            if not isinstance(configs[config_key], list):
                configs[config_key] = []

            configs[config_key].extend(config_raw)

        else:
            configs[config_key] = config_raw

        # Check if current config_key got valid value
        if (
            not isinstance(configs[config_key], list) and
            not configs[config_key]
        ):
            print(f"FATAL: config key '{config_key}' has no valid value")
            return None

    return configs
