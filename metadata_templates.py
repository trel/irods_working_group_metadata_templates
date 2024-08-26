#################################
# add this one line to core.py
#################################
#
# from metadata_templates import *
#
#################################

"""iRODS Metadata Templates

This module assumes a metadata template is a valid JSON-Schema document.

This module provides standardized metadata template functionality for an iRODS Server:
- attach
- detach
- gather
- validate

This module does not provide functionality to manage JSON-Schema documents themselves.

Metadata templates can be located at:
- an iRODS logical path
- a local filesystem
- a public URL

Metadata templates can be attached, or associated, with iRODS Data Objects and Collections via AVUs.

A Data Object and Collections of Data Objects can be validated against any associated templates.

A request for validation will return any validation errors found by the JSON-Schema validator.
"""

import json
import jsonschema
import requests

from genquery import *
import irods_types

MT_NAMESPACE = 'irods::metadata_templates'

def _mt_build_json_input(entity_name, entity_type, operation, value, units):
    """Utility function to build a JSON input stanza for msi_atomic_apply_metadata_operations()

    Inputs:
    - entity_name - string of absolute path of data object or collection
    - entity_type - string of 'data_object' or 'collection'
    - operation - string of 'add' or 'remove'
    - value - string of AVU value
    - units - string of AVU units
    Returns:
    - JSON-string - ready for use by msi_atomic_apply_metadata_operations()
    """
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


def _mt_attach(callback, entity_name, entity_type, value, units):
    """Utility function to attach a metadata template to a data object or collection

    Inputs:
    - callback - callback handle to iRODS Rule Engine Framework
    - entity_name - string of absolute path of data object or collection
    - entity_type - string of 'data_object' or 'collection'
    - value - string of AVU value
    - units - string of AVU units
    Returns:
    - nothing
    """
    # build JSON input for atomic payload
    json_input = _mt_build_json_input(entity_name, entity_type, 'add', value, units)
    # call atomic, assume any errors will show up in the serverLog
    callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), '')


def _mt_detach(callback, entity_name, entity_type, value, units):
    """Utility function to detach a metadata template from a data object or collection

    Inputs:
    - callback - callback handle to iRODS Rule Engine Framework
    - entity_name - string of absolute path of data object or collection
    - entity_type - string of 'data_object' or 'collection'
    - value - string of AVU value
    - units - string of AVU units
    Returns:
    - nothing
    """
    # build JSON input for atomic payload
    json_input = _mt_build_json_input(entity_name, entity_type, 'remove', value, units)
    # call atomic, assume any errors will show up in the serverLog
    callback.msi_atomic_apply_metadata_operations(json.dumps(json_input), '')


def metadata_templates_data_object_attach(rule_args, callback, rei):
    """Attaches a metadata template to a data object

    Inputs:
    - logical_path - absolute iRODS logical path
    - schema - location of schema
    - type - type of schema location ['irods', 'local', 'url']
    Output:
    - None
    """
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = _mt_attach(callback, logical_path, 'data_object', schema, type)


def metadata_templates_collection_attach(rule_args, callback, rei):
    """Attaches a metadata template to a collection

    Inputs:
    - logical_path - absolute iRODS logical path
    - schema - location of schema
    - type - type of schema location ['irods', 'local', 'url']
    Output:
    - None
    """
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = _mt_attach(callback, logical_path, 'collection', schema, type)


def metadata_templates_data_object_detach(rule_args, callback, rei):
    """Detaches a metadata template from a data object

    Inputs:
    - logical_path - absolute iRODS logical path
    - schema - location of schema
    - type - type of schema location ['irods', 'local', 'url']
    Output:
    - None
    """
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = _mt_detach(callback, logical_path, 'data_object', schema, type)


def metadata_templates_collection_detach(rule_args, callback, rei):
    """Detaches a metadata template from a collection

    Inputs:
    - logical_path - absolute iRODS logical path
    - schema - location of schema
    - type - type of schema location ['irods', 'local', 'url']
    Output:
    - None
    """
    logical_path = rule_args[0]
    schema = rule_args[1]
    type = rule_args[2]
    result = _mt_detach(callback, logical_path, 'collection', schema, type)


def metadata_templates_data_object_gather(rule_args, callback, rei):
    """Gathers all schemas associated with a data object

    Inputs:
    - logical_path - absolute iRODS logical path
    - recursive - whether to gather schemas on all parents up to root [0=no, 1=yes]
    Output:
    - schemas_string - JSON-string of array containing all collected schemas
    """
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
        elif thetype == 'irods':
            # get schema contents from iRODS full logical path
            ret = callback.msiDataObjOpen(schema, 0)
            fd = ret['arguments'][1] # iRODS file descriptor
            maxsize = (1<<31)-1 # maximum size - only contents of filesize will actually be read
            ret = callback.msiDataObjRead(fd, maxsize, irods_types.BytesBuf())
            buf = ret['arguments'][2] # bytesbuf
            byteslist = buf.get_bytes() # schema contents as list of bytes as integers
            callback.msiDataObjClose(fd, 0)
            # convert to json object
            j = json.loads(bytes(byteslist).decode("utf-8"))
            # add to schemas array
            schemas.append(j)
        elif thetype == 'local':
            # get contents
            with open(schema, 'r') as f:
                content = f.read()
                # convert to json object
                j = json.loads(content)
                # add to schemas array
                schemas.append(j)
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
    """Gathers all schemas associated with a collection

    Inputs:
    - logical_path - absolute iRODS logical path
    - recursive - whether to gather schemas on all parents up to root [0=no, 1=yes]
    Output:
    - schemas_string - JSON-string of array containing all collected schemas
    """
    logical_path = rule_args[0]
    recursive = rule_args[1]

    # clean the logical path
    if logical_path == '/':
        # don't touch it, already the root
        clean_logical_path = logical_path
    else:
        # remove any trailing slash
        clean_logical_path = logical_path.rstrip('/')

    # get all schema locations attached to this collection
    schemas = []
    for schema, thetype in Query(callback,
                        "META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS",
                        "COLL_NAME = '{}' and META_COLL_ATTR_NAME = '{}'".format(clean_logical_path, MT_NAMESPACE)):
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
        elif thetype == 'irods':
            # get length of iRODS full logical path
            ret = callback.msiObjStat(schema, irods_types.RodsObjStat())
            objstat = ret['arguments'][1]
            # get schema contents from iRODS full logical path
            ret = callback.msiDataObjOpen(schema, 0)
            fd = ret['arguments'][1] # iRODS file descriptor
            ret = callback.msiDataObjRead(fd, objstat.objSize, irods_types.BytesBuf())
            buf = ret['arguments'][2] # bytesbuf
            byteslist = buf.get_bytes() # schema contents as list of bytes as integers
            callback.msiDataObjClose(fd, 0)
            # convert to json object
            j = json.loads(bytes(byteslist).decode("utf-8"))
            # add to schemas array
            schemas.append(j)
        elif thetype == 'local':
            # get contents
            with open(schema, 'r') as f:
                content = f.read()
                # convert to json object
                j = json.loads(content)
                # add to schemas array
                schemas.append(j)
        else:
            callback.writeLine('serverLog', 'Type [{}] Not Supported By Metadata Templates'.format(thetype))

    # if recursive (and not the root),
    # get all schema locations attached to this collection's parent collection, recursively
#    callback.writeLine('serverLog', 'metadata_templates_collection_gather: before recursive flag')
#    callback.writeLine('serverLog', 'length of schemas [{0}]'.format(len(schemas)))
    if int(recursive):
        callback.writeLine('serverLog', 'metadata_templates_collection_gather: inside recursive flag [{0}]'.format(clean_logical_path))

        if clean_logical_path.count('/') == 0:
            callback.writeLine('serverLog', 'metadata_templates_collection_gather: no forward slashes found, stopping')
        elif clean_logical_path[0] != '/':
            callback.writeLine('serverLog', 'metadata_templates_collection_gather: not an absolute path, stopping')
        elif clean_logical_path == '/':
            callback.writeLine('serverLog', 'metadata_templates_collection_gather: found /, complete')
        elif clean_logical_path.count('/') == 1:
            # found the top level zone, call gather on root (/)
            ret = callback.metadata_templates_collection_gather('/', recursive, '')
            root_schemas_string = ret['arguments'][2]
#            callback.writeLine('serverLog', 'root_schemas_string [{0}]'.format(root_schemas_string))
            root_schemas = json.loads(root_schemas_string)
            schemas.extend(root_schemas)
        else:
            # call gather on parent
            parent_name, _ = clean_logical_path.rsplit('/', 1)
            ret = callback.metadata_templates_collection_gather(parent_name, recursive, '')
            parents_schemas_string = ret['arguments'][2]
#            callback.writeLine('serverLog', 'parents_schemas_string [{0}]'.format(parents_schemas_string))
            parents_schemas = json.loads(parents_schemas_string)
            schemas.extend(parents_schemas)

    # return serialized string
#    callback.writeLine('serverLog', 'metadata_templates_collection_gather: after recursive flag')
#    callback.writeLine('serverLog', 'end of collection_gather - length of schemas [{0}]'.format(len(schemas)))
    rule_args[2] = json.dumps(schemas)


def _mt_validate(callback, json_to_validate, schemas_string):
    """Utility function to validate the passed JSON through each passed schema

    Inputs:
    - json_to_validate - JSON-string representing AVUs to be validated
    - schemas_string - JSON-string of array of schemas to be used for validation
    Returns:
    - errors - list of accumulated schema validation errors
    """
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


def _mt_get_avus(callback, logical_path):
    """Utility function to naively get AVUs for a logical path

    Inputs:
    - callback - callback handle to iRODS Rule Engine Framework
    - logical_path - absolute iRODS logical path
    Returns:
    - the_metadata - python dict containing the naive AVU-to-JSON conversion
    Side Effects:
    - This function will stomp AVUs with identical attributes and multiple values
    """
    # get AVUs
    collection_name, data_name = logical_path.rsplit("/", 1)
#    callback.writeLine('serverLog', '_mt_get_avus - collection_name [{0}] data_name [{1}]'.format(collection_name, data_name))
    the_metadata = {}
    for a, v in Query(callback,
                        "META_DATA_ATTR_NAME, META_DATA_ATTR_VALUE",
                        "COLL_NAME = '{}' AND DATA_NAME = '{}'".format(collection_name, data_name)):
        the_metadata[a] = v # stomping here
#        callback.writeLine('serverLog', 'in avu loop... the_metadata [{0}]'.format(the_metadata))

    # return dict
#    callback.writeLine('serverLog', '_mt_get_avus - the_metadata [{0}]'.format(the_metadata))
    return the_metadata

def metadata_templates_data_object_validate(rule_args, callback, rei):
    """Validates a data object's metadata against a set of schemas

    Inputs:
    - logical_path - absolute iRODS logical path
    - schemas_string - JSON-string of array of schemas
    - avu_builder_function - dotted name of custom module.function for AVU-to-JSON conversion
    Output:
    - errors - string of list of any accumulated validation errors
    """
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
            the_metadata = func(callback, logical_path)
        except (ModuleNotFoundError, AttributeError, ValueError):
#            callback.writeLine('serverLog', 'except triggered, function [{0}] not found'.format(avu_builder_function))
            errors = ['function [{0}] not found'.format(avu_builder_function)]
    else:
        # no function defined, call naive implementation
#        callback.writeLine('serverLog', 'function name empty, executing _mt_get_avus [{0}]'.format(logical_path))
        the_metadata = _mt_get_avus(callback, logical_path)
#        callback.writeLine('serverLog', 'just after _mt_get_avus - the_metadata [{0}]'.format(the_metadata))

#    callback.writeLine('serverLog', 'the_metadata [{0}]'.format(the_metadata))
    if not errors:
        # no exception occurred
        # validate, catch validation errors
        errors = _mt_validate(callback, the_metadata, schemas_string)

#    callback.writeLine('serverLog', 'AFTER_VALIDATION_ERRORS: [{}]'.format(errors))
    if errors:
        rule_args[3] = repr(errors)


def metadata_templates_collection_validate(rule_args, callback, rei):
    """Validates the metadata of a collection's data objects against a set of schemas

    Inputs:
    - logical_path - absolute iRODS logical path
    - schemas_string - JSON-string of array of schemas
    - avu_builder_function - dotted name of custom module.function for AVU-to-JSON conversion
    Output:
    - errors - string of list of any accumulated validation errors
    """
    logical_path = rule_args[0]
    schemas_string = rule_args[1]
    avu_builder_function = rule_args[2]

    # find all data objects in this collection
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
