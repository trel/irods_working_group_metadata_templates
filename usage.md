This demonstrates calling the rules, written in Python, but via the iRODS Rule Language.

# attach

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=http://example.org' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=http://example.org.again' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=https://raw.githubusercontent.com/fge/sample-json-schemas/master/jsonrpc2.0/jsonrpc-request-2.0.json' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_attach('*logical_path', '*schema_location', 'notaurl')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=somethingelse' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_attach('*logical_path', '*schema_location', 'removeme')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=doesnotexist' ruleExecOut
```


```
$ imeta ls -C thedir
AVUs defined for collection /tempZone/home/rods/thedir:
attribute: irods::metadata_templates
value: doesnotexist
units: removeme
----
attribute: irods::metadata_templates
value: http://example.org
units: url
----
attribute: irods::metadata_templates
value: http://example.org.again
units: url
----
attribute: irods::metadata_templates
value: https://raw.githubusercontent.com/fge/sample-json-schemas/master/jsonrpc2.0/jsonrpc-request-2.0.json
units: url
----
attribute: irods::metadata_templates
value: somethingelse
units: notaurl
```

# detach

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_detach('*logical_path', '*schema_location', 'removeme')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=doesnotexist' ruleExecOut
```

```
$ imeta ls -C thedir
AVUs defined for collection /tempZone/home/rods/thedir:
attribute: irods::metadata_templates
value: http://example.org
units: url
----
attribute: irods::metadata_templates
value: http://example.org.again
units: url
----
attribute: irods::metadata_templates
value: https://raw.githubusercontent.com/fge/sample-json-schemas/master/jsonrpc2.0/jsonrpc-request-2.0.json
units: url
----
attribute: irods::metadata_templates
value: somethingelse
units: notaurl
```

# gather, print to stdout

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" '*logical_path=/tempZone/home/rods/thedir%*recursive=0%*schemas=""' ruleExecOut
```

# validate data object

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); metadata_templates_data_object_validate('*data_object_path', *schemas, *avu_function, *rc); writeLine('stdout', *rc)" '*logical_path=/tempZone/home/rods/thedir%*recursive=0%*schemas=""%*data_object_path=/tempZone/home/rods/thedir/a.txt%*avu_function=""%*rc=""' ruleExecOut
```

# validate a collection

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); metadata_templates_collection_validate('*logical_path', *schemas, *avu_function, *recursive, *errors); writeLine('stdout', *errors)" '*logical_path=/tempZone/home/rods/thedir%*recursive=0%*schemas=""%*avu_function=""%*errors=""' ruleExecOut
```
