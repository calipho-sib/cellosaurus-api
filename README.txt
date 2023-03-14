# - - - - - - - - - - - - - - - - - 
# Prerequisites
# - - - - - - - - - - - - - - - - - 

1. Linux or Mac platofrm 
2. git installed
3. curl or equivalent installed
4. python 3.9 installed, see cellapi_builder.py and main.py for modules to be installed
5. solr 8.11.1 or later installed

# - - - - - - - - -
# Installation
# - - - - - - - - -

1. Install latest cellosaurus-api code

code_source="https://github.com/calipho-sib/cellosaurus-api.git" 
git checkout $code_source
cd cellosaurus-api

2. Setup of solr collection for cellosaurus api  (only on first installation)
2.1 Create a symbolic link 'solr' in the api directory pointing to your to your solr install directory

ln -s /your/solr8.11.1-or-later/home/directory/ solr

2.2 start solr service, create cellosaurus solr collection 'pamcore1'

./solr_service.sh start
./solr/bin/solr create -c pamcore1

2.3 Link cellosaurus api solr config to 'pamcore1' collection

cd solr/server/solr/poumcore1/conf
mv managed-schema managed-schema.ori 
mv solrconfig.xml solrconfig.xml.ori
ln -s ../../../../../solr_config/schema.xml
ln -s ../../../../../solr_config/solrconfig.xml

2.4 Back to cellapi base directory and restart service to take into account new schema of 'pamcore1' collection

cd ../../../../../
./solr_service.sh restart

3. Retrieve latest cellosaurus data

data_source="https://ftp.expasy.org/databases/cellosaurus"
mkdir data_in
cd data_in
curl "$code_source/cellosaurus.txt" > cellosaurus.txt
curl "$code_source/cellosaurus_refs.txt" > cellosaurus_refs.txt
curl "$code_source/cellosaurus.xml" > cellosaurus.xml

# - - - - - - - - - - - - - - - - - - - - - - -
# Build api indexes and solr data
# - - - - - - - - - - - - - - - - - - - - - - -

1. Go back to cellosaurus-api base directory

cd .. 

2. Build api index files in serial directory

mkdir -p serial
python3.9 cellapi_builder.py BUILD

3. Build solr input files in solr_data directory (long process, few minutes)

mkdir -p solr_data
python3.9 cellapi_builder.py SOLR

4. Reload solr data in solr 'pamcore1' collection

./solr_service.sh restart
./solr/bin/post -c pamcore1 -d "<delete><query>*:*</query></delete>"
./solr/bin/post -c pamcore1 solr_data/data*.xml

# - - - - - - - - - - - - -
# How to restart services
# - - - - - - - - - - - - -
./api_service.sh stop
./api_service.sh start
./solr_service.sh stop
./solr_service.sh start

# - - - - - - - - - - - - - - -
# How to connect to services
# - - - - - - - - - - - - - - -

# API
http://localhost:8088/

# Solr
http://localhost:8983/solr

