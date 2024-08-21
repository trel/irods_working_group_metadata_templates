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

GOOD_SCHEMA=https://raw.githubusercontent.com/fge/sample-json-schemas/master/jsonrpc2.0/jsonrpc-request-2.0.json
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

@test "collection - attach, gather, detach template" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_B}
    [ $status -eq 0 ]
    # attach and confirm AVU
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    run imeta ls -C ${LOGICAL_PATH}
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[1]}" =~ "attribute: irods::metadata_templates" ]]
    [[ "${lines[2]}" =~ "value: ${GOOD_SCHEMA}" ]]
    [[ "${lines[3]}" =~ "units: url" ]]
    # gather and confirm output has parsed JSON
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); writeLine('stdout', *schemas)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    [[ "${lines[0]}" =~ "json-schema.org" ]]
    # detach and confirm no AVUs
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_detach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA} \
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

@test "attach bad schema" {
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
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""' \
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

@test "validate data object" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    # attach
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_attach('*logical_path', '*schema_location', 'url')" \
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA} \
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
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*data_object_path='${DATA_OBJECT_A}'%*avu_function=leuven.build_fancy_dict%*rc=""' \
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
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*data_object_path='${DATA_OBJECT_A}'%*avu_function=""%*rc=""' \
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
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*data_object_path='${DATA_OBJECT_A}'%*avu_function=""%*rc=""' \
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
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*data_object_path='${DATA_OBJECT_A}'%*avu_function=""%*rc=""' \
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



@test "validate collection" {
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
        '*logical_path='${LOGICAL_PATH}'%*schema_location='${GOOD_SCHEMA} \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validate and fail on method on DATA_OBJECT_B
    run irule -r irods_rule_engine_plugin-irods_rule_language-instance \
        "metadata_templates_collection_gather('*logical_path', '*recursive', *schemas); \
            metadata_templates_collection_validate('*logical_path', *schemas, '*avu_function', *recursive, *errors); \
            writeLine('stdout', *errors)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*avu_function=""%*errors=""' \
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
            metadata_templates_collection_validate('*logical_path', *schemas, '*avu_function', *recursive, *errors); \
            writeLine('stdout', *errors)" \
        '*logical_path='${LOGICAL_PATH}'%*recursive=0%*schemas=""%*avu_function=""%*errors=""' \
        ruleExecOut
    echo $BATS_RUN_COMMAND
    echo $status
    echo "output = ${output}"
    [ $status -eq 0 ]
    # validator is happy    
    [[ "${lines[0]}" = '""' ]]

    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}
