#################################
# add this one line to core.py
#################################
#
# from metadata_templates import *
#
#################################

import json
import jsonschema
import requests

from genquery import *

MT_NAMESPACE = 'irods::metadata_templates'

def mt_build_json_input(entity_name, entity_type, operation, value, units):
    json_input = {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "operations": [
            {
                "operation": operation,
                "attribute": MT_NAMESPACE,
                "value": value,
                "units": units
            }
        ]
    }
    return json_input


def mt_attach(callback, entity_name, entity_type, value, units):
    # build JSON input for atomic payload
    json_input = mt_build_json_input(entity_name, entity_type, 'add', value, units)
    # call atomic
    result = callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), "")
    # check for errors
    ### something something ... result['arguments'][0]


def mt_detach(callback, entity_name, entity_type, value, units):
    # build JSON input for atomic payload
    json_input = mt_build_json_input(entity_name, entity_type, 'remove', value, units)
    # call atomic
    result = callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), "")
    # check for errors
    ### something something ... result['arguments'][0]


def metadata_templates_collection_attach(rule_args, callback, rei):
    # Attach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_attach(callback, logical_path, 'collection', schema, type)


def metadata_templates_collection_detach(rule_args, callback, rei):
    # Detach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_detach(callback, logical_path, 'collection', schema, type)


def metadata_templates_collection_gather(rule_args, callback, rei):
    # Export/Collapse/Rasterize/Gather/Dump (logical_path, recursive)
    # - Find all associated schemas and construct effective schema
    # - Recursive would check/gather all parents up to root

    logical_path = rule_args[0]
    recursive = rule_args[1]

    # get all schema locations attached to this collection
    schemas = []
    for schema, thetype in Query(callback,
                        "META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS",
                        "COLL_NAME = '{}' and META_COLL_ATTR_NAME = '{}'".format(logical_path, MT_NAMESPACE)):
        callback.writeLine('serverLog','{} {}'.format(thetype, schema))
        if thetype == 'url':
            try:
                # get the schema content from the location
                r = requests.get(schema)
#                callback.writeLine('serverLog', r.content)
                # convert to json object
                j = json.loads(r.content)
#                callback.writeLine('serverLog', j)
                # add to schemas array
                # TODO: perhaps we should just store the string? rather than the json object?
                schemas.append(j)
            except Exception as e:
#                callback.writeLine('serverLog', '{}: {}'.format(type(e), e))
                callback.writeLine('serverLog', '{}'.format(type(e)))
        else:
            callback.writeLine('serverLog', 'Type [{}] Not Supported By Metadata Templates'.format(thetype))
#    combinedschema = {"type": object, "allOf": schemas}
#    callback.writeLine('serverLog', type(combinedschema))
    # can we return anything other than a string?  i was hoping for an array...
      # do i have to put it into a rule_arg[]?
    rule_args[2] = repr(schemas)
#    rule_args[2] = schemas
#    return schemas

def metadata_templates_collection_validate(rule_args, callback, rei):
    # Validate (logical_path, recursive)
    # - Run gather (above) to build the effective json schema
    # - Get and build json payload with all current AVUs
    # - Run payload and schema through validator
    # - Return result (OK or failure/explanation)

    logical_path = rule_args[0]
    recursive = rule_args[1]


    # get all metadata on this collection (wait, or are we checking a data object and against the schemas on its parent? hmmm)
    thedata = {}
    for a, v, u in Query(callback, # do we need units?  json-schema is just key/value?
                        "META_COLL_ATTR_NAME, META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS",
                        "COLL_NAME = '{}' and META_COLL_ATTR_NAME != '{}'".format(logical_path, MT_NAMESPACE)):
        themetadata[a] = v # will this stomp on identical a/v combinations, that have different units in the catalog?

    # run metadata through each schema, collecting any errors
    errors = []
    for s in schemas:
        try:
            jsonschema.validate(themetadata, s)
        except Exception as e:
            errors.append(e)
    # if anything failed, return the errors
    if errors:
        callback.writeLine('serverLog', 'SCHEMA ERRORS: {}'.format(repr(errors)))
        return -2
    # we did it
    return 0
