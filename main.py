# 
# 
# 

import requests
import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser
from fetch_article import fetch_guardian_articles
from summarize import summarize_articles


############################################################
#
# classes
#
class Query:

  def __init__(self, row):
    self.queryid = row[0]
    self.querytext = row[1]
    self.status = row[2]


###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break;

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => list queries")
    print("   2 => list audio files")
    print("   3 => list bucket keys")
    print("   4 => reset database")
    print("   5 => get articles")
    print("   6 => summarize articles")
    print("   7 => make podcast")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


############################################################
#
# list_queries
#
def list_queries(baseurl):
  """
  Prints out all the list_queries in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/queries'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract list_queries:
    #
    body = res.json()

    #
    # let's map each row into a Query object:
    #
    queries = []
    for row in body:
      query = Query(row)
      queries.append(query)
    #
    # Now we can think OOP:
    #
    if len(queries) == 0:
      print("no queries...")
      return

    for query in queries:
      print(query.queryid)
      print(" ", query.querytext)
      print(" ", query.status)
    #
    return

  except Exception as e:
    logging.error("**ERROR: queries() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# reset
#
def reset_database(baseurl):
  """
  Resets the database back to initial state.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/reset'
    url = baseurl + api

    res = requests.delete(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and print message
    #
    body = res.json()

    msg = body

    print(msg)
    return

  except Exception as e:
    logging.error("**ERROR: reset() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# fetch_articles
#
def fetch_articles(baseurl):
  """
  Fetches articles from the guardian api.

  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """
  try:
    query = input("Enter a query (e.g. technology, climate,...)> ")

    if query.isdigit():
      print("**ERROR: Invalid query. Please enter a string.")
      return
    
    # get articles
    url = baseurl + "/fetch" + "/" + query
    res = requests.post(url)
    
    body = res.json()
    print(body)
    
  except Exception as e:
    logging.error("**ERROR: get_articles() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# summarize
#
def summarize(baseurl):
  """
  Summarizes the articles and turns them into a podcast script.

  Parameters
  ----------
  baseurl: base URL for the web service
  
  Returns
  -------
  nothing
  """
  try:
    queryid = input("Enter a query ID> ")

    # if not queryid.isdigit():
    #   print("**ERROR: Invalid query ID. Please enter a numeric value.")
    #   return

    url = f"{baseurl}/summarize/{int(queryid)}"
    res = requests.post(url)

    if res is None:
      print("**ERROR: No response from the web service.")
      return

    if res.status_code == 200:
      print("Summary successfully generated:")
      print(res.json())
    else:
      print(f"**ERROR: Failed with status code {res.status_code}")
      print("URL:", url)
      if res.status_code == 500:
        print("Error message:", res.json())

  except Exception as e:
    logging.error("**ERROR: summarize() failed:")
    logging.error(f"URL: {url}")
    logging.error(str(e))
    return

############################################################
# main
#
try:
  print('** ⭐ Welcome to Amazing Podcast ⭐ **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'podcast-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      list_queries(baseurl)
    elif cmd == 2:
      # list_audio_files(baseurl)
      pass
    elif cmd == 3:
      # list_bucket_keys(baseurl)
      pass
    elif cmd == 4:
      reset_database(baseurl)
    elif cmd == 5:
      fetch_articles(baseurl)
    elif cmd == 6:
      summarize(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
