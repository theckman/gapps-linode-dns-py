#!/usr/bin/env python2.6
####
# Copyright (c) 2012 Tim Heckman <timothy.heckman@gmail.com> and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the 'Software'), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# **** IMPORTANT PLEASE READ THE FOLLOWING SECTION ****
# This script is not written by, nor maintained by, Linode.  Nor is it affiliated
# with Linode directly in any way.  Do not contact Linode to report any issues or
# file any bug reports regarding this script.
# **** IMPORTANT PLEASE READ THE PREVIOUS SECTION ****
####

import json
import urllib
from sys import argv,exit
from os import environ

mxRecords = [
	'ASPMX.L.GOOGLE.COM',
	'ALT1.ASPMX.L.GOOGLE.COM',
	'ALT2.ASPMX.L.GOOGLE.COM',
	'ASPMX2.GOOGLEMAIL.COM',
	'ASPMX3.GOOGLEMAIL.COM'
]
mxPriority = ['10', '20', '20', '30', '30']
spf = 'v=spf1%20include:_spf.google.com%20~all'
apiUrl = 'https://api.linode.com/'

print """
################################
#        Google Apps MX        #
#    Records Creation Script   #
#        Now in Python!        #
#      (written by llamas)     #
################################

"""

try:
	apiKey = environ['LINODE_API_KEY']
except KeyError:
	apiKey = raw_input("Enter your Linode API key: ")
	print

try:
	myself, domain = argv
except ValueError:
	try:
		myDomain = environ['GDOMAIN']
	except KeyError:
		myDomain = raw_input("Enter domain: ")
		print

params = urllib.urlencode({'api_key': apiKey, 'api_action': 'domain.list'})
jsonList = json.loads( urllib.urlopen(apiUrl, params).read() )

for apiDomain in jsonList['DATA']:
	if apiDomain['DOMAIN'] == myDomain:
		domainID = apiDomain['DOMAINID']
		break

if 'domainID' not in globals():
	print "ERROR: domain (%s) not found!" % myDomain
	exit(1)

addSpf = raw_input("Would you like to add the recommended default SPF record for Google Apps [Y/n]: ")
print

print "You can also add CNAMEs to make navigating to the Google Apps web interface easier."
addCNAME = raw_input("Would you like to add some Google Apps CNAMEs [y/N]: ")
print

if addCNAME == 'Y' or addCNAME == 'y':
	cnameList = ["mail", "calendar", "contacts", "docs"]
	cnameAdd = []
	for cName in cnameList:
		cnameAdd.append( raw_input("Would you like to add a CNAME for " + cName + "." + myDomain + " [y/N]: " ) )

print "\nCreating MX records...\n"
iMx = 0
for record in mxRecords:
	params = urllib.urlencode({'api_key': apiKey, 'api_action': 'domain.resource.create',
		'domainid': domainID, 'type': 'MX', 'target': record, 'priority': mxPriority[iMx]})
	print "%s:\n%s\n" % (record, urllib.urlopen(apiUrl, params).read())
	iMx+=1

if addSpf == "" or addSpf == 'Y' or addSpf == 'y':
	print "\nCreating SPF record...\n"
	params = urllib.urlencode({'api_key': apiKey, 'api_action': 'domain.resource.create',
		'domainid': domainID, 'type': 'TXT', 'target': spf,})
	print "%s\n" % urllib.urlopen(apiUrl, params).read()

if addCNAME == 'Y' or addCNAME == 'y':
	print"\nCreating CNAMEs...\n"
	iCn = 0

	for cName in cnameList:
		if cnameAdd[iCn] == 'Y' or cnameAdd[iCn] == 'y':
			params = urllib.urlencode({'api_key': apiKey, 'api_action': 'domain.resource.create',
				'domainid': domainID, 'type': 'CNAME', 'name': cName, 'target': 'ghs.google.com'})
			print "%s.%s:\n%s\n" % (cName, myDomain, urllib.urlopen(apiUrl, params).read())
		iCn+=1

	print "You'll need to update the URLs for your Google Apps Core Services to the CNAMEs"
	print "that you've just created: https://www.google.com/a/%s\n" % myDomain

print """Everything should be finished at this point (assuming no errors were returned via API)!
Please verify the created records within the Linode DNS Manager:
https://manager.linode.com/dns/domain/%s
<3 heckman
""" % myDomain
