#!/usr/bin/env python

# Inspired by: https://github.com/irods/irods/issues/3020

import json
import sys

rule_engines = {'python':
    {
        "instance_name": "irods_rule_engine_plugin-python-instance",
        "plugin_name": "irods_rule_engine_plugin-python",
        "plugin_specific_configuration": {}
    }
}


def main(path_to_server_config, name_of_rule_engine_to_add, position):
    position = int(position)

    if name_of_rule_engine_to_add not in rule_engines:
        sys.exit('Rule engine "%s" does not exist. Possible option are "%s"'
                 % (name_of_rule_engine_to_add, ",".join(rule_engines.keys())))
    rule_engine = rule_engines[name_of_rule_engine_to_add]

    with open(path_to_server_config, 'r+') as f:
        server_config = json.load(f)
        size = len(server_config['plugin_configuration']['rule_engines'])
        if position >= size:
            server_config['plugin_configuration']['rule_engines'].insert(size, rule_engine)
        else:
            server_config['plugin_configuration']['rule_engines'].insert(position, rule_engine)

        # Rewrite the server_config file
        f.seek(0)
        json.dump(server_config, f, indent=4, sort_keys=True)
        f.truncate()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('Usage: {0} path_to_server_config name_of_rule_engine_to_add position'.format(sys.argv[0]))
    main(sys.argv[1], sys.argv[2], sys.argv[3])
