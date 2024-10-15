from __future__ import annotations

import argparse
import os
from typing import List
import jinja2

from rpclite.input_parser import InputYamlCollection


def generate(output_folder: str, input_yamls: List[str]):
    
    all_inputs = InputYamlCollection(input_yamls)

    # Define the output directory

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Set up the Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('rpclite'),
        autoescape=jinja2.select_autoescape(['python']),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load templates
    models_template = env.get_template('python_module.jinja2')
    
    data = {
        "enums": all_inputs.enums,
        "structs": all_inputs.structs,
        "devices": all_inputs.devices
    }

    # Render models.py
    models_content = models_template.render(data)
    with open(os.path.join(output_folder, 'models.py'), 'w') as f:
        f.write(models_content)

    print(f"Python project generated successfully in '{output_folder}/' directory.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", action="store")
    parser.add_argument("--input_yamls", action="store", nargs="+")

    args = parser.parse_args()

    inputs_yamls = args.input_yamls
    output_dir = args.output_folder
    generate(inputs_yamls, output_dir)


if __name__ == "__main__":
    main()
