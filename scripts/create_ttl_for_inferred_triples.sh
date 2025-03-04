#!/bin/bash

set -e

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..
cd $base_dir 
base_dir=$(pwd)

# -----------------------------------------------------------
query=$(<./queries/transitive_subclasses.rq )
outfile=./rdf_data/materialized_transitive_subclasses.ttl
# -----------------------------------------------------------

echo "running SPARQL query $query ..."

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "query=$query" \
     --data-urlencode "format=application/x-nice-turtle" \
     http://localhost:8890/sparql > $outfile

echo "saved query result in $outfile"


# -----------------------------------------------------------
query=$(<./queries/transitive_subproperties.rq )
outfile=./rdf_data/materialized_transitive_subproperties.ttl
# -----------------------------------------------------------

echo "running SPARQL query $query ..."

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "query=$query" \
     --data-urlencode "format=application/x-nice-turtle" \
     http://localhost:8890/sparql > $outfile

echo "saved query result in $outfile"

# -----------------------------------------------------------
query=$(<./queries/transitive_more_specific_than.rq )
outfile=./rdf_data/materialized_transitive_more_specific_than.ttl
# -----------------------------------------------------------

echo "running SPARQL query $query ..."

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "query=$query" \
     --data-urlencode "format=application/x-nice-turtle" \
     http://localhost:8890/sparql > $outfile

echo "saved query result in $outfile"
