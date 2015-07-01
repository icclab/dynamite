#!/bin/sh

ROOT_DIR=../../../../..

echo "Execute scaling engine"
python ${ROOT_DIR}/Dynamite.py --config_file dynamite.yaml &

sleep 5

echo "Execute Generator"
python ${ROOT_DIR}/MetricsGenerator.py --config generator_config.json
echo "Generated fake log events"
