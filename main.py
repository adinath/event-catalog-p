import os
import re
import csv

from jinja2 import Environment, FileSystemLoader

from models.ros_message import Field
from models.ros_message import RosMessage


def render_templates(ros_message: RosMessage, target_directory: str):
    environment = Environment(loader=FileSystemLoader("event-templates/"))
    index_template = environment.get_template("index.md.jinja")

    index_content = index_template.render(msg=ros_message)
    with open(os.path.join(target_directory, "index.md"), "w") as f:
        f.write(index_content)

    schema_template = environment.get_template("schema.json.jinja")

    schema_content = schema_template.render(msg=ros_message)
    with open(os.path.join(target_directory, "schema.json"), "w") as f:
        f.write(schema_content)


def scan_msg_files(path: str, target_path: str):
    files = os.scandir(path)

    for entry in files:
        if entry.is_file():
            if entry.name.endswith(".msg"):
                print("found msg file. loading", entry.name)
                f = open(entry.path)
                lines = f.readlines()
                non_empty_line = [l for l in lines if l.strip() != ""]
                sanitized_lines = [l.strip().replace("\n", "") for l in non_empty_line]
                fields = []
                target_msg_directory = os.path.join(target_path, entry.name.split(".")[0])
                os.mkdir(target_msg_directory)
                msg_description = ""
                for line in sanitized_lines:
                    if line.startswith("#"):
                        last_hash_char = line.rfind('#') + 1
                        msg_description += line[last_hash_char:].strip()
                    else:
                        if "=" not in line:
                            values = line.split(" ")
                            fields.append(Field(name=values[1], datatype=values[0]))
                render_templates(RosMessage(name=entry.name.split(".")[0], fields=fields, description=msg_description),
                                 target_msg_directory)

        else:  # assume it's a directory
            scan_msg_files(path=entry.path, target_path="event-catalog")

def split_string(input_string):
    # Find the index of the capital letter
    capital_indices = [i for i, c in enumerate(input_string) if c.isupper()]
    if len(capital_indices) < 2:
        return [input_string]
    
    result = input_string[:capital_indices[1]].lower()+"_msgs"

    return result

def scan_task_files(path: str):
    files = os.scandir(path)
    channels = []
    for entry in files:
        if entry.is_file():
            if entry.name.endswith(".rb"):
                print("found task file. loading", entry.name)
                f = open(entry.path)
                lines = f.read()
                matches = re.findall(r'Interfaces\.update\s*\(\s*\{\s*([\s\S]+?)\s*\}\s*\)', lines)
                for match in matches:
                    channels.extend(re.findall(r'(?:InterfaceDefs::)(\w+)(?=(?:Input|Output)\b)', match))

    interfaces = set()
    with open(os.path.join("core_interfaces", "app_config", "channel_names.csv"), mode ='r') as file:    
       csv_file = csv.DictReader(file)
       for data in csv_file:
            if data["Channel"] in channels:
                interfaces.add(data["Type"])

    msg_files_path = []
    for interface in interfaces:
        folder_name = split_string(interface)
        msg_files_path.append(os.path.join("core_interfaces", "core_interfaces", folder_name, "msg"))
    
    for msg_files in msg_files_path:
        scan_msg_files(msg_files, "pbsa_msgs")

if __name__ == "__main__":
    scan_task_files("pbsa")
