from __future__ import annotations

import argparse
from typing import List
import jinja2
import pathlib

from rpclite.input_parser import InputYamlCollection


class _ApiGenerator:
    def __init__(self, input_yaml_file: str, output_folder: str) -> None:
        all_inputs = InputYamlCollection([input_yaml_file])

        # Ensure the output directory exists
        self._output_root_path = pathlib.Path(output_folder)

        # Set up the Jinja2 environment
        self._env = jinja2.Environment(
            loader=jinja2.PackageLoader("rpclite"),
            autoescape=jinja2.select_autoescape(["python"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self._data = {
            "package_name": f"{all_inputs.get_api_name()}",
            "enums": all_inputs.enums,
            "structs": all_inputs.structs,
            "devices": all_inputs.devices
        }

        # Render
        self._render_to_file(f"client.py", "python_client.jinja2")
        self._render_to_file(f"server.py", "python_server.jinja2")
        self._render_to_file(f"api_types.py", "python_types.jinja2")
        self._render_to_file(f"__init__.py", "python_root_init.jinja2")

        print(f"Python project generated successfully in \"{output_folder}/\" directory.")

    def _render_to_file(self, path, template_name):
        template = self._env.get_template(template_name)
        content = template.render(self._data)
        destination = self._output_root_path.joinpath(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w") as f:
            f.write(content)


def generate(input_yamls, output_dir):
    api_generator = _ApiGenerator(input_yamls, output_dir)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", action="store")
    parser.add_argument("--input_yamls", action="store", nargs="+")

    args = parser.parse_args()

    inputs_yamls = args.input_yamls
    output_dir = args.output_folder
    generate(inputs_yamls, output_dir)


if __name__ == "__main__":
    _main()
