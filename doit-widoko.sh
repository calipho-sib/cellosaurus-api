cd ~/work/widoco
./doit-cello.sh $1
cd ~/work/cellosaurus-api
python cellapi_builder.py --platform=$1 SPARQL_PAGES

