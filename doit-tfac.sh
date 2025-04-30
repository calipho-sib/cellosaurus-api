./solr/bin/post -c pamtfac -d "<delete><query>*:*</query></delete>"
./solr_service.sh stop
python termfinder.py $1 http://localhost:8890/sparql test.xml
sleep 3
./solr_service.sh start
sleep 3
./solr/bin/post -c pamtfac -d "<delete><query>*:*</query></delete>"
sleep 3
./solr/bin/post -c pamtfac test.xml



