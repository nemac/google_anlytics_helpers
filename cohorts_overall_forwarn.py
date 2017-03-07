#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reference command-line example for Google Analytics Core Reporting API v3.

This application demonstrates how to use the python client library to access
all the pieces of data returned by the Google Analytics Core Reporting API v3.

The application manages autorization by saving an OAuth2.0 token in a local
file and reusing the token for subsequent requests.

Before You Begin:

Update the client_secrets.json file

  You must update the clients_secrets.json file with a client id, client
  secret, and the redirect uri. You get these values by creating a new project
  in the Google APIs console and registering for OAuth2.0 for installed
  applications: https://code.google.com/apis/console

  Learn more about registering your analytics application here:
  http://developers.google.com/analytics/devguides/reporting/core/v3/gdataAuthorization

Supply your TABLE_ID

  You will also need to identify from which profile to access data by
  specifying the TABLE_ID constant below. This value is of the form: ga:xxxx
  where xxxx is the profile ID. You can get the profile ID by either querying
  the Management API or by looking it up in the account settings of the
  Google Anlaytics web interface.

Sample Usage:

  $ python core_reporting_v3_reference.py ga:xxxx

Where the table ID is used to identify from which Google Anlaytics profile
to retrieve data. This ID is in the format ga:xxxx where xxxx is the
profile ID.

Also you can also get help on all the command-line flags the program
understands by running:

  $ python core_reporting_v3_reference.py --help
"""
from __future__ import print_function

__author__ = 'api.nickm@gmail.com (Nick Mihailovski)'

import argparse
import sys
from datetime import datetime, timedelta

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('table_id', type=str,
                     help=('The table ID of the profile you wish to access. '
                           'Format is ga:xxx where xxx is your profile ID.'))

argparser.add_argument('filter_file', type=str,
                     help=('a trext file containing the filter for ga. '
                     'Format is path/filename .'))

argparser.add_argument('output_textfile', type=str,
                     help=('The out put text file your wish to write. '
                     'Format is path/filename .'))

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)

def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/analytics.readonly')

  # Try to make a request to the API. Print the results or handle errors.
  try:
    # results = get_api_query(service, flags.table_id).execute()

    #get current date so we know when to stop
    start_date = datetime(2014, 1, 1)
    date_format = "%Y-%m-%d"
    today = datetime.today()
    this_month_start = today.replace(day=1)
    end_date = last_day_of_month(today) #end date

    #count so we can do things insert column headers
    cohort_start_date_str = datetime.strftime(start_date, date_format)
    cohort_end_date_str = datetime.strftime(end_date, date_format)
    cohort = cohort_start_date_str + '_' + cohort_end_date_str

    print('range')
    print(start_date, end_date)
    print(cohort)

    next_month_first_day = start_date.replace(day=1)  #next months first day
    next_month_last_day = last_day_of_month(next_month_first_day) #next months last day

    count = 1
    file = open(flags.output_textfile, "w")

    start_date_str = datetime.strftime(next_month_first_day, date_format)
    end_date_str = datetime.strftime(next_month_last_day, date_format)

    print('str')
    print(start_date_str, end_date_str)

    results = get_cohorts(cohort_start_date_str, cohort_end_date_str, cohort, service, flags.table_id, flags.filter_file).execute()

    column_headers = get_column_headers(results)
    column_meteric_headers = get_totals_names_all_results(results)
    column_headers_str = ('cohort' + '\t' + '\t'.join(column_headers))
    column_meteric_headers_str = ('\t'.join(column_meteric_headers))
    file.write(column_headers_str + '\t' + column_meteric_headers_str + '\n')

    # get totals for cohort
    totals_values = get_totals_values_all_results(results)

    # print_rows(results, totals_values, cohort)
    rows = get_rows(results, totals_values, cohort)
    for row in rows:
        rows_str = ('\t'.join(row) + '\n')
        file.write(rows_str)

    file.close()

  except HttpError as error:
    # Handle API errors.
    print(('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason())))

  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')


def get_cohorts(start_date, end_date, cohort, service, table_id, filter_file):
  """Returns a query object to retrieve data from the Core Reporting API.

  Args:
    service: The service object built by the Google API Python client library.
    table_id: str The table ID form which to retrieve data.
  """

  file = open(filter_file,"r")
  filter = file.readline().replace('\n', '')
  print (filter)
  if(filter):
      return service.data().ga().get(
          ids=table_id,
          start_date=start_date,
          end_date=end_date,
          metrics='ga:sessions, ga:users, ga:bounceRate, ga:avgSessionDuration, ga:newUsers',
          dimensions='ga:networkDomain, ga:yearMonth, ga:networkLocation, ga:pagePath, ga:source, ga:ga:pagePath',
          filters=filter,
          start_index='1',
          max_results='10000')
  else:
      return service.data().ga().get(
          ids=table_id,
          start_date=start_date,
          end_date=end_date,
          metrics='ga:sessions, ga:users, ga:bounceRate, ga:avgSessionDuration, ga:newUsers',
          dimensions='ga:networkDomain, ga:yearMonth, ga:networkLocation, ga:pagePath, ga:source, ga:ga:pagePath',
          start_index='1',
          max_results='10000')

def get_api_query(service, table_id):
  """Returns a query object to retrieve data from the Core Reporting API.

  Args:
    service: The service object built by the Google API Python client library.
    table_id: str The table ID form which to retrieve data.
  """

  return service.data().ga().get(
      ids=table_id,
      start_date='2015-04-01',
      end_date='2015-04-30',
      metrics='ga:sessions, ga:users, ga:bounceRate, ga:avgSessionDuration',
      dimensions='ga:networkDomain, ga:yearMonth',
      segment='users::condition::dateOfSession<>2015-04-01_2015-04-30;ga:userType==New Visitor',
      start_index='1',
      max_results='10000')


def print_results(results):
  """Prints all the results in the Core Reporting API Response.

  Args:
    results: The response returned from the Core Reporting API.
  """

  # print_report_info(results)
  # print_pagination_info(results)
  # print_profile_info(results)
  # print_query(results)
  # print_column_headers(results)
  # print_totals_for_all_results(results)
  print_rows(results)


def print_report_info(results):
  """Prints general information about this report.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Report Infos:')
  print('Contains Sampled Data = %s' % results.get('containsSampledData'))
  print('Kind                  = %s' % results.get('kind'))
  print('ID                    = %s' % results.get('id'))
  print('Self Link             = %s' % results.get('selfLink'))
  print()


def print_pagination_info(results):
  """Prints common pagination details.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Pagination Infos:')
  print('Items per page = %s' % results.get('itemsPerPage'))
  print('Total Results  = %s' % results.get('totalResults'))

  # These only have values if other result pages exist.
  if results.get('previousLink'):
    print('Previous Link  = %s' % results.get('previousLink'))
  if results.get('nextLink'):
    print('Next Link      = %s' % results.get('nextLink'))
  print()


def print_profile_info(results):
  """Prints information about the profile.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Profile Infos:')
  info = results.get('profileInfo')
  print('Account Id      = %s' % info.get('accountId'))
  print('Web Property Id = %s' % info.get('webPropertyId'))
  print('Profile Id      = %s' % info.get('profileId'))
  print('Table Id        = %s' % info.get('tableId'))
  print('Profile Name    = %s' % info.get('profileName'))
  print()


def print_query(results):
  """The query returns the original report query as a dict.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Query Parameters:')
  query = results.get('query')
  for key, value in query.iteritems():
    print('%s = %s' % (key, value))
  print()

def get_column_headers(results):
  """gets column for a row.

  The main data from the API is returned as rows of data. The column
  headers describe the names and types of each column in rows.


  Args:
    results: The response returned from the Core Reporting API.
    row index.
  """
  headers = results.get('columnHeaders')
  column_headers = []
  for header in headers:
      header_name = 'none' if header.get('name') is None else header.get('name')
      column_headers.append(header_name)

  return column_headers

def get_column_header(results, row_index):
  """gets column for a row.

  The main data from the API is returned as rows of data. The column
  headers describe the names and types of each column in rows.


  Args:
    results: The response returned from the Core Reporting API.
    row index.
  """
  headers = results.get('columnHeaders')
  count = 0
  for header in headers:
      if(count == row_index):
          return 'none' if header.get('name') is None else header.get('name')
      count += 1

def print_column_headers(results):
  """Prints the information for each column.

  The main data from the API is returned as rows of data. The column
  headers describe the names and types of each column in rows.


  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Column Headers:')
  headers = results.get('columnHeaders')
  for header in headers:
    # Print Dimension or Metric name.
    print('\t%s name:    = %s' % (header.get('columnType').title(),
                                  header.get('name')))
    print('\tColumn Type = %s' % header.get('columnType'))
    print('\tData Type   = %s' % header.get('dataType'))
    print()


def print_totals_for_all_results(results):
  """gets the total metric value for all pages the query matched.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print('Total Metrics For All Results:')
  print('This query returned %s rows.' % len(results.get('rows')))
  print(('But the query matched %s total results.' %
         results.get('totalResults')))
  print('Here are the metric totals for the matched total results.')

  totals = results.get('totalsForAllResults')

  for metric_name, metric_total in totals.iteritems():
    print('Metric Name  = %s' % metric_name)
    print('Metric Total = %s' % metric_total)
    print()

def get_totals_values_all_results(results):
  """Prints the total metric value for all pages the query matched.

  Args:
    results: The response returned from the Core Reporting API.
  """

  totals = results.get('totalsForAllResults')

  totals_values = []
  for metric in totals.iteritems():
    totals_values.append(metric[1])

  # print(totals_values)
  return totals_values

def get_totals_names_all_results(results):
  """Prints the total metric value for all pages the query matched.

  Args:
    results: The response returned from the Core Reporting API.
  """

  totals = results.get('totalsForAllResults')

  totals_names = []
  for metric in totals.iteritems():
    totals_names.append('totals_' + metric[0])

  # print(totals_names)
  return totals_names


def get_total_for_meteric(results, the_metric_name):
  """gets the total metric value or specific meteric.

  Args:
    results: The response returned from the Core Reporting API.
  """


  totals = results.get('totalsForAllResults')

  for metric_name, metric_total in totals.iteritems():
    if(metric_name == the_metric_name):
        return metric_total

  return

def get_rows(results, totals_values, cohort):
  """Prints all the rows of data returned by the API.

  Args:
    results: The response returned from the Core Reporting API.
  """
  rows = []
  if results.get('rows', []):
    for row in results.get('rows'):
        row.insert(0,cohort)
        for totals in totals_values:
            row.append(totals)
        rows.append(row)

  return rows

def print_rows(results, totals_values, cohort):
  """Prints all the rows of data returned by the API.

  Args:
    results: The response returned from the Core Reporting API.
  """

  if results.get('rows', []):
    for row in results.get('rows'):
        print(cohort + '\t' + '\t'.join(row) + '\t' + '\t'.join(totals_values))
        #  print()
        # for i in range(len(row)):
            # column = get_column_header(results, i)
            # metric_total = get_total_for_meteric(results, column)
            # print( column, metric_total, row[i])
            # print(row[i] + '\t')
    #   print('\t'.join(row))
  # else:
  #   print('No Rows Found')


if __name__ == '__main__':
  main(sys.argv)
