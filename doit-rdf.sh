set -e

cd ~/work/cellosaurus-api
python cellapi_builder.py RDF
python cellapi_builder.py LOAD_RDF data
python cellapi_builder.py ONTO
python cellapi_builder.py LOAD_RDF onto
python cellapi_builder.py QUERIES
python cellapi_builder.py LOAD_RDF queries

if [ "$1" != "novoid" ]; then
  cd ~/work/void-generator
  ./doit-cello.sh
  cp void-cello.ttl ~/work/cellosaurus-api/rdf_data/
  cd ~/work/cellosaurus-api
fi

python cellapi_builder.py LOAD_RDF void
cd ~/work/widoco
./doit-cello.sh
cd ~/work/cellosaurus-api
python cellapi_builder.py SPARQL_PAGES


