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


def metadata_templates_data_object_attach(rule_args, callback, rei):
    # Attach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_attach(callback, logical_path, 'data_object', schema, type)


def metadata_templates_collection_attach(rule_args, callback, rei):
    # Attach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_attach(callback, logical_path, 'collection', schema, type)


def metadata_templates_data_object_detach(rule_args, callback, rei):
    # Detach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_detach(callback, logical_path, 'data_object', schema, type)


def metadata_templates_collection_detach(rule_args, callback, rei):
    # Detach (logical_path, schema, type)
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = mt_detach(callback, logical_path, 'collection', schema, type)


def metadata_templates_data_object_gather(rule_args, callback, rei):
    # Export/Collapse/Rasterize/Gather/Dump (logical_path, recursive, schemas_string)
    # - Find all associated schemas
    # - Recursive gathers schemas on all parents up to root

    logical_path = rule_args[0]
    recursive = rule_args[1]

    # split logical path
    collection_name, data_name = logical_path.rsplit("/", 1)

    # get all schema locations attached to this data object
    schemas = []
    for schema, thetype in Query(callback,
                        "META_DATA_ATTR_VALUE, META_DATA_ATTR_UNITS",
                        "COLL_NAME = '{}' and DATA_NAME = '{}' and META_DATA_ATTR_NAME = '{}'".format(collection_name, data_name, MT_NAMESPACE)):
#        callback.writeLine('serverLog','{} {}'.format(thetype, schema))
        if thetype == 'url':
            try:
                # get the schema content from the location
                r = requests.get(schema)
                # convert to json object
                j = json.loads(r.content)
                # add to schemas array
                schemas.append(j)
            except Exception as e:
                callback.writeLine('serverLog', '{}'.format(type(e)))
        else:
            callback.writeLine('serverLog', 'Type [{}] Not Supported By Metadata Templates'.format(thetype))

    # if recursive,
    # get all schema locations attached to this data object's parent collection, recursively
#    callback.writeLine('serverLog', 'metadata_templates_data_object_gather: before recursive flag')
#    callback.writeLine('serverLog', 'length of schemas [{0}]'.format(len(schemas)))
    if int(recursive):
#        callback.writeLine('serverLog', 'metadata_templates_data_object_gather: inside recursive flag [{0}]'.format(logical_path))
        ret = callback.metadata_templates_collection_gather(collection_name, recursive, '')
        parents_schemas_string = ret['arguments'][2]
#        callback.writeLine('serverLog', 'parents_schemas_string [{0}]'.format(parents_schemas_string))
        parents_schemas = json.loads(parents_schemas_string)
        schemas.extend(parents_schemas)
#        callback.writeLine('serverLog', 'length of schemas [{0}]'.format(len(schemas)))

    # return serialized string
#    callback.writeLine('serverLog', 'metadata_templates_data_object_gather: after recursive flag')
#    callback.writeLine('serverLog', 'end of data_object_gather - length of schemas [{0}]'.format(len(schemas)))
    rule_args[2] = json.dumps(schemas)


def metadata_templates_collection_gather(rule_args, callback, rei):
    # Export/Collapse/Rasterize/Gather/Dump (logical_path, recursive, schemas_string)
    # - Find all associated schemas
    # - Recursive gathers schemas on all parents up to root

    logical_path = rule_args[0]
    recursive = rule_args[1]

    # get all schema locations attached to this collection
    schemas = []
    for schema, thetype in Query(callback,
                        "META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS",
                        "COLL_NAME = '{}' and META_COLL_ATTR_NAME = '{}'".format(logical_path, MT_NAMESPACE)):
#        callback.writeLine('serverLog','{} {}'.format(thetype, schema))
        if thetype == 'url':
            try:
                # get the schema content from the location
                r = requests.get(schema)
                # convert to json object
                j = json.loads(r.content)
                # add to schemas array
                schemas.append(j)
            except Exception as e:
                callback.writeLine('serverLog', '{}'.format(type(e)))
        else:
            callback.writeLine('serverLog', 'Type [{}] Not Supported By Metadata Templates'.format(thetype))

    # if recursive (and not the root),
    # get all schema locations attached to this collection's parent collection, recursively
#    callback.writeLine('serverLog', 'metadata_templates_collection_gather: before recursive flag')
#    callback.writeLine('serverLog', 'length of schemas [{0}]'.format(len(schemas)))
    if int(recursive) and logical_path not in ['', '/']:
#        callback.writeLine('serverLog', 'metadata_templates_collection_gather: inside recursive flag [{0}]'.format(logical_path))

        # clean and split logical path
        parent_name, this_collection_name = logical_path.strip().rstrip('/').rsplit("/", 1)

        ret = callback.metadata_templates_collection_gather(parent_name, recursive, '')
        parents_schemas_string = ret['arguments'][2]
#        callback.writeLine('serverLog', 'parents_schemas_string [{0}]'.format(parents_schemas_string))
        parents_schemas = json.loads(parents_schemas_string)
        schemas.extend(parents_schemas)

    # return serialized string
#    callback.writeLine('serverLog', 'metadata_templates_collection_gather: after recursive flag')
#    callback.writeLine('serverLog', 'end of collection_gather - length of schemas [{0}]'.format(len(schemas)))
    rule_args[2] = json.dumps(schemas)


def mt_validate(callback, json_to_validate, schemas_string):
    # run json_to_validate through each schema, collecting any errors
    errors = []
#    callback.writeLine('serverLog', 'TYPE: ::{}:: SCHEMAS: ::{}::'.format(type(schemas_string), schemas_string))
    schemas = json.loads(schemas_string)
#    callback.writeLine('serverLog', 'TYPE: ::{}:: SCHEMAS_ARRAY: ::{}::'.format(type(schemas), schemas))
    for s in schemas:
#        callback.writeLine('serverLog', 'VALIDATING: ::{}::'.format(s))
        try:
            jsonschema.validate(json_to_validate, s)
        except Exception as e:
            errors.append(e)
    # if anything failed, log the errors
    if errors:
        callback.writeLine('serverLog', 'VALIDATE_ERRORS: {}'.format(repr(errors)))
        return errors
    # success
    return []


def mt_get_avus(logical_path, callback):
    # Naive implementation to get AVUs for a logical path
    # - Will stomp on identical attributes with multiple values
    # - Will stomp on identical a/v combinations with different units

    # get AVUs
    collection_name, data_name = logical_path.rsplit("/", 1)
#    callback.writeLine('serverLog', 'mt_get_avus - collection_name [{0}] data_name [{1}]'.format(collection_name, data_name))
    the_metadata = {}
    for a, v in Query(callback,
                        "META_DATA_ATTR_NAME, META_DATA_ATTR_VALUE",
                        "COLL_NAME = '{}' AND DATA_NAME = '{}'".format(collection_name, data_name)):
        the_metadata[a] = v # stomping here
#        callback.writeLine('serverLog', 'in avu loop... the_metadata [{0}]'.format(the_metadata))

    # return dict
#    callback.writeLine('serverLog', 'mt_get_avus - the_metadata [{0}]'.format(the_metadata))
    return the_metadata

def metadata_templates_data_object_validate(rule_args, callback, rei):
    # Validate data object (logical_path, schemas_string, avu_builder_function, errors)
    # - Get and build json payload with all current AVUs
    # - Run payload and schemas through validator
    # - Return result (OK or failure/explanation)

    logical_path = rule_args[0]
    schemas_string = rule_args[1]
    avu_builder_function = rule_args[2]

    the_metadata = {}
    errors = []
    if avu_builder_function:
        # function defined
        try:
            # import and execute the defined function
#            callback.writeLine('serverLog', 'trying to load module [{0}]'.format(avu_builder_function))
            modulename, funcname = avu_builder_function.split('.', 1)
            module = __import__(modulename)
            func = getattr(module, funcname)
            the_metadata = func(logical_path, callback)
        except (ModuleNotFoundError, AttributeError, ValueError):
#            callback.writeLine('serverLog', 'except triggered, function [{0}] not found'.format(avu_builder_function))
            errors = ['function [{0}] not found'.format(avu_builder_function)]
    else:
        # no function defined, call naive implementation
#        callback.writeLine('serverLog', 'function name empty, executing mt_get_avus [{0}]'.format(logical_path))
        the_metadata = mt_get_avus(logical_path, callback)
#        callback.writeLine('serverLog', 'just after mt_get_avus - the_metadata [{0}]'.format(the_metadata))

#    callback.writeLine('serverLog', 'the_metadata [{0}]'.format(the_metadata))
    if not errors:
        # no exception occurred
        # validate, catch validation errors
        errors = mt_validate(callback, the_metadata, schemas_string)

#    callback.writeLine('serverLog', 'AFTER_VALIDATION_ERRORS: [{}]'.format(errors))
    if errors:
        rule_args[3] = repr(errors)


def metadata_templates_collection_validate(rule_args, callback, rei):
    # Validate collection (logical_path, schemas_string, avu_builder_function, errors)
    # - Loop through data objects, validate each
    # - Return result (OK or failure/explanation)

    logical_path = rule_args[0]
    schemas_string = rule_args[1]
    avu_builder_function = rule_args[2]

    # find all data objects in this collection
    # TODO: or gather all at once, then validate each object individually (in parallel?)
    data_objects = []
    for coll_name, data_name in Query(callback,
                                "COLL_NAME, DATA_NAME",
                                "COLL_NAME like '{}%'".format(logical_path)):
        data_objects.append("{}/{}".format(coll_name, data_name))

    # loop through data_objects, validate each
    callback.writeLine('serverLog', repr(data_objects))
    for data_object_path in data_objects:
        ret = callback.metadata_templates_data_object_validate(data_object_path, schemas_string, avu_builder_function, '')
        errors = ret['arguments'][3]
        callback.writeLine('serverLog', 'metadata_templates_data_object_validate_ERRORS: [{}]'.format(errors))
        # if anything failed, log and error out
        if errors:
            callback.writeLine('serverLog', 'metadata_templates_collection_validate failed for [{}]'.format(logical_path))
            rule_args[3] = errors
