#!/usr/bin/env python2

import ConfigParser
import os
import argparse 
import urlparse
import requests
import json
import sys
from pprint import pprint


def get_report(report, cloudhealth_api_token, cloudhealth_api_url):
    uri = urlparse.urljoin(cloudhealth_api_url, report)
    uri += "?api_key=%s" % cloudhealth_api_token
    print uri 
    json_response = json.loads(requests.get(uri, headers={"Accept" : "application/json"}).text)
    return json_response 

def main():
    """main function"""

    # parse cmdline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='enable debugging')
    parser.add_argument('-c', metavar='config', dest='config', required=True,
                        help='config file')
    args, _ = parser.parse_known_args()

    # check if config file is present
    if not os.path.isfile(args.config):
        print >> sys.stderr, "ERROR. Config file %s could not be found." % args.config
        sys.exit(1)

    cfg = ConfigParser.ConfigParser()
    cfg.read(args.config)

    try:
        cloudhealth_api_url = cfg.get('default', 'cloudhealth_api_url')
        cloudhealth_api_token = cfg.get('default', 'cloudhealth_api_token')
    except ConfigParser.NoSectionError, error:
        print >> sys.stderr, "ERROR. Config file invalid: %s" % error
        sys.exit(1)
    except ConfigParser.NoOptionError, error:
        print >> sys.stderr, "ERROR. Config file invalid: %s" % error
        sys.exit(1)

    
    try:
        data = get_report("cost/history", cloudhealth_api_token, cloudhealth_api_url)
        # Get list of dimension names
     
        dimensions = [dim.keys()[0] for dim in data["dimensions"]]

        # Output a CSV for this report
        print "Month,%s" % ",".join( [member["label"] for member in data['dimensions'][1][dimensions[1]]])
        index = 0
        for month in data["dimensions"][0][dimensions[0]]:
            row = data['data'][index]
            if row == None:
                continue

        # We have only selected 1 measure so just take first element of every array
        row_as_array = [str(item[0]) for item in row]
        print "%s,%s" % (month["label"], ",".join(row_as_array))
        index+=1

    except Exception as e:
        print e 
        print >> sys.stderr, "ERROR. Unable to retrieve status"
        sys.exit(1)

if __name__ == '__main__':
    main()
