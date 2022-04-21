# opsgenie-alerts-stats

Service to calculate opsgenie alerts stats

## build

~~~~
docker login
docker-compose -f docker-compose-build.yml build
docker-compose -f docker-compose-build.yml push
~~~~

## configuration

customize your configuration via environment variables (see example in `docker-compose.yml`)

## run

~~~~
docker-compose up
~~~~

## dependencies if want to run without container

~~~~
pip3 install --user pyaml prometheus_client
~~~~

## example run

~~~~
docker-compose exec opsgenie-alerts-stats bash -c "python /opt/exporter/exporter.py" | sort  -t '|' -k2 -h -r | grep -v ^\|1 > alerts_stats_sorted
~~~~

