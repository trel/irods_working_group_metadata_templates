This demonstrates calling the rules, written in Python, but via the iRODS Rule Language.

# attach

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=http://example.org' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=http://example.org.again' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_attach('*logical_path', '*schema_location', 'url')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=https://raw.githubusercontent.com/fge/sample-json-schemas/master/geojson/geojson.json' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_attach('*logical_path', '*schema_location', 'notaurl')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=somethingelse' ruleExecOut
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_attach('*logical_path', '*schema_location', 'removeme')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=doesnotexist' ruleExecOut
```

```
$ imeta ls -C thedir
AVUs defined for collection /tempZone/home/rods/thedir:
attribute: irods::metadata_templates
value: doesnotexist
units: deleteme
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
value: https://raw.githubusercontent.com/fge/sample-json-schemas/master/geojson/geojson.json
units: url
----
attribute: irods::metadata_templates
value: somethingelse
units: notaurl
```

# detach

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_detach('*logical_path', '*schema_location', 'removeme')" '*logical_path=/tempZone/home/rods/thedir%*schema_location=doesnotexist' ruleExecOut
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
value: https://raw.githubusercontent.com/fge/sample-json-schemas/master/geojson/geojson.json
units: url
----
attribute: irods::metadata_templates
value: somethingelse
units: notaurl
```

# gather

```
$ irule -r irods_rule_engine_plugin-irods_rule_language-instance "metadata_templates_gather('*logical_path', *recursive)" '*logical_path=/tempZone/home/rods/thedir%*recursive=0' ruleExecOut
```

# validate
