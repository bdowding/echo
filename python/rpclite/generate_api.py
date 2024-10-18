from __future__ import annotations

import argparse
import os
from typing import List
import jinja2

from rpclite.input_parser import InputYamlCollection

def generate(input_yaml_file: str, output_folder: str):
    
    all_inputs = InputYamlCollection([input_yaml_file])

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Set up the Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('rpclite'),
        autoescape=jinja2.select_autoescape(['python']),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Load templates
    py_client_template = env.get_template('python_client.jinja2')
    py_server_template = env.get_template('python_server.jinja2')
    py_types_template = env.get_template('python_types.jinja2')
    
    data = {
        "package_name": f"{all_inputs.get_api_name()}",
        "enums": all_inputs.enums,
        "structs": all_inputs.structs,
        "devices": all_inputs.devices
    }

    # Render
    py_client_content = py_client_template.render(data)
    with open(os.path.join(output_folder, f'{all_inputs.get_api_name()}_client.py'), 'w') as f:
        f.write(py_client_content)
    
    py_server_content = py_server_template.render(data)
    with open(os.path.join(output_folder, f'{all_inputs.get_api_name()}_server.py'), 'w') as f:
        f.write(py_server_content)
        
    py_types_content = py_types_template.render(data)
    with open(os.path.join(output_folder, f'{all_inputs.get_api_name()}_types.py'), 'w') as f:
        f.write(py_types_content)

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
