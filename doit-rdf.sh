cd ~/work/cellosaurus-api
python cellapi_builder.py RDF
python cellapi_builder.py LOAD_RDF data
python cellapi_builder.py ONTO
python cellapi_builder.py LOAD_RDF onto
cd ~/work/void-generator
./doit-cello.sh
cp void-cello.ttl ~/work/cellosaurus-api/rdf_data/
cd ~/work/cellosaurus-api
python cellapi_builder.py LOAD_RDF void
#./sparql_service restart
# cd ./private/scripts; ./start-stop-virtuoso.sh restart # old version
cd ~/work/widoco
./doit-cello.sh
cd ~/work/cellosaurus-api


