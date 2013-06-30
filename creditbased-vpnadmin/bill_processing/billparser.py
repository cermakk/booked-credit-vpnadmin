# -*- coding: utf-8 -*-
import re
import csv


class TMobileCSVBillParser(object):
    """
    Reads the given CSV file and creates python structures for further
    processing.
    """
    
    personinfo_re = '(?P<tel>[0-9]{3} [0-9]{3} [0-9]{3}) / Firma 3000 - mobil'
    
    def __init__(self, datafile):
        self.reader = csv.reader(datafile, delimiter=';')
        self.parsed = {}
        line = self.reader.next()
        while not self._is_person_header(line):
            line = self.reader.next()
        self.parse_person(line)
            
    def parse_person(self, line):
        service_consumed = {}
        tel = re.search(self.personinfo_re, line[0]).group('tel')
        tel = int(tel.replace(' ', ''))
        
        line = self.reader.next()
        # TODO: parse other items of the person
        
        self.parsed[tel] = service_consumed

    def _is_person_header(self, line):
        return len(line) == 1 and re.match(self.personinfo_re, line[0])

if __name__ == '__main__':
    with open('sumsheet_3672461713.csv', 'r') as f:
        p = TMobileCSVBillParser(f)
        
    print p.parsed
