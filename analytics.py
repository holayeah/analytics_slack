"""
Hello Analytics Reporting API V4,
Modifying google analytics example for some extra functionality.
"""

import os

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from slacker import Slacker


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = os.environ['ANALYTICS_KEY_FILE']
VIEW_ID = os.environ['ANALYTICS_VIEW_ID']


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analytics', 'v4', credentials=credentials)

  return analytics


def get_daily_session_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': 'today', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions'}],
          'dimensions': [{'name': 'ga:country'}]
        }]
      }
  ).execute()

def generate_daily_sessions_msg(response):
    """Generates a message for daily sessions received.
    Args:
      response: An analytics Reporting API V4 response
    Returns:
      pretty_message: A string contain a pretty description of the analytics.
    """
    for report in response.get('reports', []):

        number_of_sessions = report.get('data', {}).get('rowCount', 'No')

        msg = "Daily     analytics report, \n"
        msg += "We have got sessions from %s Countries Today.\n\n" % number_of_sessions

        for row in report.get('data', []).get('rows', []):
            country = row['dimensions'][0]
            sessions = row['metrics'][0]['values'][0]

            msg += "%s: %s \n" % (country, sessions)

        return msg


def send_slack(message):
    """
    Sends message to a slack general channel,
    """
    slack = Slacker(os.environ['ANALYTICS_SLACK_API_TOKEN'])
    slack.chat.post_message('#general', message)


def main():
  analytics = initialize_analyticsreporting()
  response = get_daily_session_report(analytics)
  send_slack(generate_daily_sessions_msg(response))

if __name__ == '__main__':
  main()
