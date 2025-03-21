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

############################################################
#
# classes
#
class Query:

  def __init__(self, row):
    self.queryid = row[0]
    self.querytext = row[1]
    self.status = row[2]
    self.textkey = row[3]
    self.scriptkey = row[4]
    self.audiokey = row[5]
class Article:

  def __init__(self, row):
    self.articleid = row[0]
    self.url = row[1]
    self.headline = row[2]



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
    print("   2 => list articles")
    print("   3 => reset database")
    print("   4 => fetch articles")
    print("   5 => summarize articles")
    print("   6 => generate podcast")
    print("   7 => fetch and generate")

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
# helpers
#
def make_post_request(url, json_data={}):
    """
    Helper function to make a POST request and return the response
    """
    try:
        res = requests.post(url, json=json_data)
        if res is None:
            print("**ERROR: No response from server.")
            return None
        
        return res
    
    except Exception as e:
        logging.error(f"**ERROR: Request failed: {str(e)}")
        return None

def validate_query(query):
    """
    Validates that the query is a string and not numeric
    """
    if query.isdigit():
        print("**ERROR: Invalid query. Please enter a string.")
        return False
    return True

def validate_queryid(queryid):
    """
    Validates that the query ID is a number
    """
    if not queryid.isdigit():
        print("**ERROR: Invalid query ID. Please enter a numeric value.")
        return False
    return True

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
    print(">> Here are all of the queries that were made:")
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
      print("\tQuery: ", query.querytext)
      print("\tStatus: ", query.status)
      print("\tBucket key: ", query.textkey)
      print("\tScript key: ", query.scriptkey)
      print("\tAudio key:", query.audiokey)
    #
    return

  except Exception as e:
    logging.error("**ERROR: queries() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# list_podcasts
#
def list_podcasts(baseurl):
  """
  Prints out all the list_podcasts in the database

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
    api = '/podcasts'
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
    # deserialize and extract list_podcasts:
    #
    body = res.json()

    #
    # let's map each row into a podcast object:
    #
    podcasts = []
    for row in body:
      podcast = Podcast(row)
      podcasts.append(podcast)
    #
    # Now we can think OOP:
    #
    if len(podcasts) == 0:
      print("no podcasts...")
      return

    for podcast in podcasts:
      print(podcast.audiokey)
    #
    return

  except Exception as e:
    logging.error("**ERROR: podcasts() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# list_articles
#
def list_articles(baseurl):
  """
  Prints out all the list_articles in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    print(">> Articles that were fetched to generate podcasts 📰:")
    #
    # call the web service:
    #
    api = '/articles'
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
    # deserialize and extract list_articles:
    #
    body = res.json()
    #
    # let's map each row into a article object:
    #
    articles = []
    for row in body:
      article = Article(row)
      articles.append(article)
    #
    # Now we can think OOP:
    #
    if len(articles) == 0:
      print("no articles...")
      return

    for article in articles:
      print(article.articleid)
      print("\tTitle: ", article.headline)
      print("\tURL: ", article.url)
    #
    return

  except Exception as e:
    logging.error("**ERROR: articles() failed:")
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
    
    if not validate_query(query):
      return
    
    print(f"Fetching articles for query: {query}\n(This may take a few seconds...)")
    url = f"{baseurl}/fetch/{query}"
    
    # make request and return response
    res = make_post_request(url)

    if res and res.status_code == 200:
        print("Articles successfully fetched")
        data = res.json()
        queryid = data.get("queryid")
        print("Your query id:", queryid, "\n")
        article_headlines = data.get("article_headlines")
        print ("We fetched the following articles: \n")
        for headline in article_headlines:
           print(headline)
    else:
        print(f"Failed with status code: {res.status_code}\nURL: {url}")
        if res.status_code == 500:
            print("Error message:", res.json())

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

    if not validate_queryid(queryid):
      return

    print(f"Generating podcast script for query ID: {queryid}\n(This may take a few seconds...)")
    url = f"{baseurl}/summarize/{queryid}"
    
    # make request and return response
    res = make_post_request(url)

    if res and res.status_code == 200:
        print("Summary successfully generated")
        data = res.json()
        script = data.get("script")
        answer = input("Do you want to read the generated script? (y/n)")
        if answer == "y":
          print (script)
    else:
        print(f"**ERROR: Failed with status code {res.status_code}\nURL: {url}")
        if res.status_code == 500:
            print("Error message:", res.json())

  except Exception as e:
    logging.error("**ERROR: summarize() failed:")
    logging.error(f"URL: {url}")
    logging.error(str(e))
    return


############################################################
#
# generate_podcast
#
import requests
import base64
import os

def generate_podcast(baseurl):
  try:
    queryid = input("Enter a query ID> ")

    if not validate_queryid(queryid):
        return
    
    print(f"Generating podcast for query ID: {queryid}\n(This may take a few seconds...)")
    url = f"{baseurl}/podcast/{queryid}"
    res = make_post_request(url)

    if res and res.status_code == 200:
        data = res.json()
        audiokey = data.get("audiokey")
        audiodata = data.get("audiodata")
        filename = data.get("querytext") + ".mp3"

        if not audiokey or not audiodata:
            print("**ERROR: Missing audio data in response.")
            return
        
        with open(filename, "wb") as audio_file:
            audio_file.write(base64.b64decode(audiodata))
        
        print(f"Podcast generated and downloaded successfully as {filename}")
    else:
        print("no audio found...")

  except Exception as e:
    logging.error("**ERROR: generate_podcast() failed:")
    logging.error(f"URL: {url}")
    logging.error(str(e))
    return

############################################################
#
# fetch_and_generate
#
def fetch_and_generate(baseurl):
  
  try:
    query = input("Enter a query (e.g. technology, climate,...)> ")

    if not validate_query(query):
        return

    print(f"Fetching articles for query: {query}\n(This may take a few seconds...)\n")
    url = f"{baseurl}/fetch/{query}"
    
    res = make_post_request(url)
    if not res or res.status_code != 200:
        print(f"Failed with status code: {res.status_code}\nURL: {url}")
        if res.status_code == 500:
            print("Error message:", res.json())
        return

    body = res.json()
    queryid = body.get("queryid")
    print(f"Generating podcast script for query ID: {queryid}\n(This may take a few seconds...)\n")

    # Summarize
    url = f"{baseurl}/summarize/{queryid}"
    res = make_post_request(url)
    if not res or res.status_code != 200:
        print(f"**ERROR: Failed with status code {res.status_code}\nURL: {url}")
        if res.status_code == 500:
            print("Error message:", res.json())
        return

    print("Summary successfully generated :)")

    # Generate Podcast
    print(f"Generating podcast for query ID: {queryid}\n(This may take a few seconds...)\n")
    url = f"{baseurl}/podcast/{queryid}"
    res = make_post_request(url)
    if not res or res.status_code != 200:
        print("No audio found...")
        return
    
    data = res.json()
    audiokey = data.get("audiokey")
    audiodata = data.get("audiodata")
    filename = data.get("querytext") + ".mp3"

    if not audiokey or not audiodata:
        print("**ERROR: Missing audio data in response.")
        return

    with open(filename, "wb") as audio_file:
        audio_file.write(base64.b64decode(audiodata))

    print(f"Podcast generated and downloaded successfully as {filename}")

  except Exception as e:
    logging.error("**ERROR: fetch_and_generate() failed:")
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
      list_articles(baseurl)
    elif cmd == 3:
      reset_database(baseurl)
    elif cmd == 4:
      fetch_articles(baseurl)
    elif cmd == 5:
      summarize(baseurl)
    elif cmd == 6:
      generate_podcast(baseurl)
    elif cmd == 7:
      fetch_and_generate(baseurl)
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