import urllib2
import sys
from HTMLParser import HTMLParser

class InnerParser(HTMLParser):
  def __init__(self): 
    HTMLParser.__init__(self)
    self.mail = []

  def handle_starttag(self, tag, attrs):
    if tag == "a" and [item for item in attrs if item == ('class', 'email-business')]:
      mail = [item[1] for item in attrs if item[0] == 'href'][0]
      self.mail.append(mail.replace('mailto:', ''))

  def get_mail(self):
    return self.mail

class MyHTMLParser(HTMLParser):
  def __init__(self): 
    HTMLParser.__init__(self)
    self.in_title = False
    self.in_span = False
    self.street_address = False
    self.address_locality = False
    self.adress_region = False
    self.postal_code = False
    self.cur_agency = {}
    self.agencies = []

  def handle_starttag(self, tag, attrs):
    if tag == "h2" and [item for item in attrs if item == ('class', 'n')]:
      self.in_title = True

    elif self.in_title and tag == "span":
      self.in_span = True

    elif self.in_title and tag == "a":
      url = [item[1] for item in attrs if item[0] == 'href'][0]
      self.cur_agency['url'] = url
      self.cur_agency['street_address'] = ''
      self.cur_agency['address_locality'] = ''
      self.cur_agency['address_region'] = ''
      self.cur_agency['postal_code'] = ''

    else:
      if tag != 'span':
        return

      if [item for item in attrs if item == ('itemprop', 'streetAddress')]:
        self.street_address = True
      elif [item for item in attrs if item == ('itemprop', 'addressLocality')]:
        self.address_locality = True
      elif [item for item in attrs if item == ('itemprop', 'addressRegion')]:
        self.adress_region = True
      elif [item for item in attrs if item == ('itemprop', 'postalCode')]:
        self.postal_code = True

  def handle_endtag(self, tag):
    self.in_title = False
    self.in_span = False
    self.street_address = False
    self.address_locality = False
    self.adress_region = False
    self.postal_code = False

  def handle_data(self, data):
    if self.in_span:
      self.cur_agency['name'] = data

      parser = InnerParser()
      response = urllib2.urlopen('https://www.yellowpages.com' + self.cur_agency['url'])
      parser.feed(response.read().decode('utf8'))
      parser.close()
      self.cur_agency['mail'] = parser.get_mail()
      
    if self.street_address:
      self.cur_agency['street_address'] = data
      
    if self.address_locality:
      self.cur_agency['address_locality'] = data
      
    if self.adress_region:
      self.cur_agency['address_region'] = data

    if self.postal_code:
      self.cur_agency['postal_code'] = data
      # print self.cur_agency
      self.agencies.append(self.cur_agency)
      self.cur_agency = {}

  def get_agencies(self):
    return self.agencies

def extract_mails(url):
  parser = MyHTMLParser()
  response = urllib2.urlopen(url)
  parser.feed(response.read().decode('utf8'))
  parser.close()
  return parser.get_agencies()

states = [ 
  "AZ"
  # "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID",
  # "IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS",
  # "MO","MT","NE","NV","NH","NJ","NM",
  # "NY","NC","ND","OH","OK",
  # "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV",
  # "WI","WY"
]

json = {}

def extract_from_states():
  for state in states:
    json[state] = []
    print state
    for i in range(1, 6):
      print 'page', i
      sys.stdout.flush()
      json[state] = extract_mails('https://www.yellowpages.com/search?search_terms=digital+agency&geo_location_terms=' + state + '&page=' + str(i))
      for agency in json[state]:
        if len(agency['mail']) == 0:
          print state + ",", agency['name'], ", \"" + agency['street_address'], \
            agency['address_locality'], agency['address_region'], agency['postal_code'] + "\""
        else:
          print state + ",", agency['name'], ", \"" + agency['street_address'], \
            agency['address_locality'], agency['address_region'], agency['postal_code'] + "\",", \
            ", ".join(agency['mail'])

  # print json

extract_from_states()
