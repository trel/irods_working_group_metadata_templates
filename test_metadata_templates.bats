############################################
# Metadata Templates test file
#
# $ git clone https://github.com/bats-core/bats-core
# $ bash bats-core/bin/bats test_metadata_templates.bats
############################################

TEST_COLLECTION=/tempZone/home/rods/mt_test_coll
SUBCOLLECTION=subcoll
LOGICAL_PATH=${TEST_COLLECTION}/${SUBCOLLECTION}
DATA_OBJECT_A=${LOGICAL_PATH}/a.txt
DATA_OBJECT_B=${LOGICAL_PATH}/b.txt

GOOD_SCHEMA_A=https://raw.githubusercontent.com/fge/sample-json-schemas/master/jsonrpc2.0/jsonrpc-request-2.0.json
GOOD_SCHEMA_B=https://raw.githubusercontent.com/irods/irods/main/schemas/configuration/v4/plugin.json.in
GOOD_SCHEMA_IRODS=/tempZone/home/rods/sample.json
BAD_SCHEMA=https://example.org
############

setup () {
#    imkdir -p ${LOGICAL_PATH}
#    itouch ${DATA_OBJECT_A}
#    itouch ${DATA_OBJECT_B}
    echo "noop"
}

teardown () {
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
}

@test "data object - attach, gather, detach template" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach and confirm AVU
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${DATA_OBJECT_A}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -d ${DATA_OBJECT_A}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" =~ "attribute: irods::metadata_templates" ]]
    [[ "${lines[2]}" =~ "value: ${GOOD_SCHEMA_A}" ]]
    [[ "${lines[3]}" =~ "units: url" ]]
    # gather and confirm output has parsed JSON
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${DATA_OBJECT_A}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "json-schema.org" ]]
    # detach and confirm no AVUs
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_detach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${DATA_OBJECT_A}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -d ${DATA_OBJECT_A}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" = "None" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "data object - attach, gather, detach template from iRODS" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach and confirm AVU
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_attach('*logical_path', '*schema_location', 'irods')" \
        '*logical_path='${DATA_OBJECT_A}'%*schema_location='${GOOD_SCHEMA_IRODS} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -d ${DATA_OBJECT_A}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" =~ "attribute: irods::metadata_templates" ]]
    [[ "${lines[2]}" =~ "value: ${GOOD_SCHEMA_IRODS}" ]]
    [[ "${lines[3]}" =~ "units: irods" ]]
    # gather and confirm output has parsed JSON
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${DATA_OBJECT_A}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "json-schema.org" ]]
    # detach and confirm no AVUs
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_detach('*logical_path', '*schema_location', 'irods')" \
        '*logical_path='${DATA_OBJECT_A}'%*schema_location='${GOOD_SCHEMA_IRODS} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -d ${DATA_OBJECT_A}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" = "None" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "collection - attach, gather, detach template" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach and confirm AVU
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" =~ "attribute: irods::metadata_templates" ]]
    [[ "${lines[2]}" =~ "value: ${GOOD_SCHEMA_A}" ]]
    [[ "${lines[3]}" =~ "units: url" ]]
    # gather and confirm output has parsed JSON
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "json-schema.org" ]]
    # detach and confirm no AVUs
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_detach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" = "None" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "collection - attach, gather, detach template from iRODS" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach and confirm AVU
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'irods')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_IRODS} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" =~ "attribute: irods::metadata_templates" ]]
    [[ "${lines[2]}" =~ "value: ${GOOD_SCHEMA_IRODS}" ]]
    [[ "${lines[3]}" =~ "units: irods" ]]
    # gather and confirm output has parsed JSON
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "json-schema.org" ]]
    # detach and confirm no AVUs
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_detach('*logical_path', '*schema_location', 'irods')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_IRODS} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" = "None" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "data object - attach bad schema" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach bad schema
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${DATA_OBJECT_A}'%*schema_location='${BAD_SCHEMA} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -d ${DATA_OBJECT_A}
    echo "output = ${output}"
    [ $status -eq 0 ]
    # gather and confirm no JSON parsed correctly
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${DATA_OBJECT_A}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" = "[]" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "collection - attach bad schema" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach bad schema
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${BAD_SCHEMA} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    # gather and confirm no JSON parsed correctly
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" = "[]" ]]
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "data object - validate" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validate, expect to fail
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=leuven.build_fancy_dict%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "required property" ]]
    # add required field, but with wrong value
    run imeta add -d ${DATA_OBJECT_A} jsonrpc apples
    [ $status -eq 0 ]
    run imeta ls -d ${DATA_OBJECT_A}
    echo $output
    [ $status -eq 0 ]
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "is not one of" ]]
    # update with correct value
    run imeta set -d ${DATA_OBJECT_A} jsonrpc 2.0
    [ $status -eq 0 ]
    run imeta ls -d ${DATA_OBJECT_A}
    echo $output
    [ $status -eq 0 ]
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "required property" ]]
    # add second required field
    run imeta set -d ${DATA_OBJECT_A} method bananas
    [ $status -eq 0 ]
    run imeta ls -d ${DATA_OBJECT_A}
    echo $output
    [ $status -eq 0 ]
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validator is happy
    [[ "${lines[0]}" = "" ]]
    # additional schema on parent collection
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${TEST_COLLECTION}'%*schema_location='${GOOD_SCHEMA_B} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    run imeta ls -C ${TEST_COLLECTION}
    echo $output
    [ $status -eq 0 ]
    # validate with recursion, should fail
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_data_object_gather('*data_object_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=1%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validator is not yet satisfied
    [[ "${lines[0]}" =~ "required property" ]]
    # add avu, should pass with recursion
    run imeta set -d ${DATA_OBJECT_A} checksum_sha256 a
    run imeta set -d ${DATA_OBJECT_A} name b
    run imeta set -d ${DATA_OBJECT_A} type c
    run imeta set -d ${DATA_OBJECT_A} version d
    [ $status -eq 0 ]
    run imeta ls -d ${DATA_OBJECT_A}
    echo $output
    [ $status -eq 0 ]
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_data_object_validate('*data_object_path', *schemas, '*avu_function', *rc); \
            writeLine('stdout', *rc)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=1%*schemas=%*data_object_path='${DATA_OBJECT_A}'%*avu_function=%*rc=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validator is happy
    [[ "${lines[0]}" = "" ]]

    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}

@test "collection - validate" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_B}
    [ $status -eq 0 ]
    run imeta set -d ${DATA_OBJECT_A} jsonrpc 2.0
    [ $status -eq 0 ]
    run imeta set -d ${DATA_OBJECT_A} method cherries
    [ $status -eq 0 ]
    run imeta set -d ${DATA_OBJECT_B} jsonrpc 2.0
    [ $status -eq 0 ]
    # attach
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA_A} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validate and fail on method on DATA_OBJECT_B
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_collection_validate('*logical_path', *schemas, '*avu_function', *errors); \
            writeLine('stdout', *errors)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*avu_function=%*errors=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "required property" ]]
    # add it
    run imeta set -d ${DATA_OBJECT_B} method darkchocolate
    [ $status -eq 0 ]
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_collection_validate('*logical_path', *schemas, '*avu_function', *errors); \
            writeLine('stdout', *errors)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=%*avu_function=%*errors=' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validator is happy
    [[ "${lines[0]}" = "" ]]

    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}
