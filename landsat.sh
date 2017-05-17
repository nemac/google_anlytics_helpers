#!/bin/bash
rm client_secrets.json > /dev/null
rm analytics.dat > /dev/null
cp analytics-landsatfact.dat analytics.dat > /dev/null
cp client_secrets-landsatfact.json client_secrets.json > /dev/null
./cohorts_overall.py  ga:110560328 ga_filter_generic ga_metric_simple ga_dimension_weeks /dev/null > /dev/null
cp analytics.dat analytics-landsatfact.dat
echo "switched to landsatfact secrets"
