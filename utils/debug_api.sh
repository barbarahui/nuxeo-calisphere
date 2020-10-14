#!/bin/bash

collectionUid='466fe320-0d22-4a66-a62c-56e1e1500c2b' # parent uid for collection 27012. UCCE Merced
#collectionUid='aa8c78cc-9e5f-4738-81e0-03e73952a0ac' # 26943 Klein
pageSize=100
numPages=30 # TODO get this programmatically. UCCE has 30 pages.
uids=()
duplicates=()

uniqueCount=0
dupCount=0

echo -n "Nuxeo API password (user Administrator):"
read -s pass
echo

for ((i = 0 ; i < $numPages ; i++)); do

    curl -X GET 'https://nuxeo.cdlib.org/Nuxeo/site/api/v1/search/lang/NXQL/execute?query=SELECT+%2A+FROM+Document+WHERE+ecm%3AparentId+%3D+%27'"$collectionUid"'%27+AND+ecm%3AcurrentLifeCycleState+%21%3D+%27deleted%27+ORDER+BY+ecm%3Apos&pageSize='"$pageSize"'&currentPageIndex='"$i"'' -H 'X-NXproperties: *' -H 'X-NXRepository: default' -H 'content-type: application/json' -u Administrator:"$pass" > ./workspace/nxql_results_$i.json

    currPageSize=`jq .currentPageSize ./workspace/nxql_results_$i.json`

    for ((j = 0 ; j < $currPageSize ; j++)); do

        currUid=`jq .entries[$j].uid ./workspace/nxql_results_$i.json`

        if [[ " ${uids[@]} " =~ " ${currUid} " ]]; then
            echo "duplicate! page: $i, position: $j, id: $currUid"   
            dupCount=$((dupCount+1))
        else
            uids+=($currUid) 
            count=$((count+1))
        fi
    done

done

echo "dupCount: $dupCount"
echo "count: $count"

