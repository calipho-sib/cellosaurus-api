set -e


if [[ "$1" != "local" && "$1" != "test" && "$1" != "prod" ]]; then
  echo "Error, invalid platorm name, expected local, test or prod"
  exit 3
fi

platform=$1

cd ~/work/cellosaurus-api
python cellapi_builder.py --platform=$platform RDF
python cellapi_builder.py --platform=$platform LOAD_RDF data
python cellapi_builder.py --platform=$platform ONTO
python cellapi_builder.py --platform=$platform LOAD_RDF onto
python cellapi_builder.py --platform=$platform QUERIES
python cellapi_builder.py --platform=$platform LOAD_RDF queries
python cellapi_builder.py --platform=$platform MODEL 
python cellapi_builder.py --platform=$platform INFERRED 

if [ "$2" != "novoid" ]; then
  cd ~/work/void-generator
  ./doit-cello.sh
  cp void-cello.ttl ~/work/cellosaurus-api/rdf_data/
  cd ~/work/cellosaurus-api
fi

python cellapi_builder.py --platform=$platform LOAD_RDF void

./sparql_service checkpoint

cd ~/work/widoco
./doit-cello.sh $platform
cd ~/work/cellosaurus-api
python cellapi_builder.py --platform=$platform SPARQL_PAGES


