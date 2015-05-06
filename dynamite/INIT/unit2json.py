__author__ = 'brnr'

import json
import os
import logging

logging.basicConfig(format='%(asctime)s %(message)s')

# Takes a >> PATH/unit_file_name << as argument
# Returns a python list-object (which can then be encoded to json)


def unit2list(unit_file_w_path):
    logging.info('Starting Converting Fleet-Unit File into Python-List')
    logging.info('File to be converted:' + unit_file_w_path)

    data = {}
    data["desiredState"] = "loaded"
    data["options"] = []

    with open(unit_file_w_path, 'r') as infile:
        section = ""
        for line in infile:
            if line.rstrip() == "[Unit]":
                section = "Unit"
                logging.info("[Unit]")
                continue
            elif line.rstrip() == "[Service]":
                section = "Service"
                logging.info("[Service]")
                continue
            elif line.rstrip() == "[X-Fleet]":
                section = "X-Fleet"
                logging.info("[X-Fleet]")
                continue
            elif line.rstrip() == "":
                continue

            line = line.rstrip()
            name,value = line.split("=")
            logging.info(name, "=", value)

            option = {}
            option["section"]=section
            option["name"]=name
            option["value"]=value

            data["options"].append(option)

    return data
#
# Takes a >> PATH/unit_file_name << as argument
# Returns a json-object
def unit2json(unit_file_w_path):
    python_object = unit2list(unit_file_w_path)
    json_object = json.dumps(python_object)
    return json_object

if __name__ == "__main__":
    # if nothing else was stated in the configuration, Fleet Unit Files are assumed to be
    # in the current working directory
    unit_file_directory = os.getcwd()

    res = None

    # Get all the Fleet Unit-Files from the current working directory
    for filename in os.listdir(unit_file_directory):
        if filename.endswith(".service"):
            file_path = os.path.join(unit_file_directory, filename)
            res = unit2json(file_path)

    print(res)

    # with open('data.txt', 'w') as outfile:
    #     json.dump(data, outfile)
    #
    # data_string = json.dumps(data)
    # print 'JSON:', data_string