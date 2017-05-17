#!/bin/bash
rm client_secrets.json > /dev/null
rm analytics.dat > /dev/null > /dev/null
cp client_secrets_nemac.json client_secrets.json > /dev/null
cp analytics-nemac.dat analytics.dat > /dev/null
./cohorts_overall.py  ga:110560328 ga_filter_generic ga_metric_simple ga_dimension_weeks /dev/null > /dev/null
cp analytics.dat analytics-nemac.dat > /dev/null
echo "switched to nemac secrets"
