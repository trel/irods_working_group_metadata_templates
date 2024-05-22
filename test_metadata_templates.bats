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

@test "attach and detach template to collection" {
    # main
    run imkdir -p ${LOGICAL_PATH}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_A}
    [ $status -eq 0 ]
    run itouch ${DATA_OBJECT_B}
    [ $status -eq 0 ]
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
    # cleanup
    run irm -rf ${TEST_COLLECTION}
    run iadmin rum
    [ $status -eq 0 ]
}
