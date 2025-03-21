#
# Resets the contents of the Podcast App database
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: reset**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'podcast-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')

    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # delete all rows from queries and articles:
    #
    print("**Disabling foreign key checks**")
    sql = "SET FOREIGN_KEY_CHECKS = 0;"
    datatier.perform_action(dbConn, sql)

    print("**Deleting queries**")
    sql = "TRUNCATE TABLE queries;"
    datatier.perform_action(dbConn, sql)

    sql = "ALTER TABLE queries AUTO_INCREMENT = 10001;"
    datatier.perform_action(dbConn, sql)

    print("**Deleting articles**")
    sql = "TRUNCATE TABLE articles;"
    datatier.perform_action(dbConn, sql)

    sql = "ALTER TABLE articles AUTO_INCREMENT = 20001;"
    datatier.perform_action(dbConn, sql)

    print("**Re-enabling foreign key checks**")
    sql = "SET FOREIGN_KEY_CHECKS = 1;"
    datatier.perform_action(dbConn, sql)

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning success**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("success")
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
