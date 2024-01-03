#################################
# add this one line to core.py
#################################
#
# from metadata_templates import *
#
#################################

import json

def metadata_templates_attach(rule_args, callback, rei):
    # Attach (logical_path, schema, type)
    # - Initially, type will just be 'url', and collection only
    # - Could later be 'irods_schema' and store the id from the new table
    # - Or 'form' for ManGO wrapper/form information

    # parameter error checking
    # - type is part of enum

    # build JSON input for atomic payload
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]

    json_input = {
        "entity_name": logical_path,
        "entity_type": 'collection',
        "operations": [
            {
                "operation": 'add',
                "attribute": 'irods::metadata_templates',
                "value": schema,
                "units": type
            }
        ]
    }

    # call atomic
    result = callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), "")

    # check for errors
    ### something something ... result['arguments'][0]


def metadata_templates_detach(rule_args, callback, rei):
    # Detach (logical_path, schema, type)

    # query to find/match the object
    # remove the AVU
    # A: irods::metadata_templates
    # V: <url>|<filename>|<data_id>/<logical_path>
    # U: type (url|local|irods) or 'form' too?

    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]

    json_input = {
        "entity_name": logical_path,
        "entity_type": 'collection',
        "operations": [
            {
                "operation": 'rm',
                "attribute": 'irods::metadata_templates',
                "value": schema,
                "units": type
            }
        ]
    }

    # call atomic
    result = callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), "")

    # check for errors
    ### something something ... result['arguments'][0]


def metadata_templates_gather(rule_args, callback, rei):
    # Export/Collapse/Rasterize/Gather/Dump (logical_path, recursive)
    # - Find all associated schemas and construct effective schema
    # - Recursive would check/gather all parents up to root

    logical_path = rule_args[0]
    recursive = rule_args[1]


def metadata_templates_validate(rule_args, callback, rei):
    # Validate (logical_path, recursive)
    # - Run gather (above) to build the effective json schema
    # - Get and build json payload with all current AVUs
    # - Run payload and schema through validator
    # - Return result (OK or failure/explanation)

    logical_path = rule_args[0]
    recursive = rule_args[1]


