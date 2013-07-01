# -*- coding: utf-8 -*-
import re
import csv
import codecs


class TMobileCSVBillParser(object):
    """
    Reads the given CSV file and creates python structures for further
    processing.
    """
    
    personinfo_re = '(?P<tel>[0-9]{3} [0-9]{3} [0-9]{3}) / Firma 3000 - mobil'
    sluzby_re = 'Služby'
    volani_re = 'Volání (?P<val>.*)'
    
    def __init__(self, datafile, encoding='windows-1250'):
        self.reader = csv.reader(datafile, delimiter=';')
        self.parsed = {}
        for line in self.reader:
            line = [unicode(codecs.decode(f, 'windows-1250')) for f in line]
            if self._is_person_header(line):
                self.on_person_header(line)
            else:
                self.on_regular_line(line)
            
    def on_person_header(self, line):
        if hasattr(self, 'tel'):
            self.parsed[self.tel] = self.service_consumed
        self.service_consumed = {}
        tel = re.search(self.personinfo_re, line[0]).group('tel')
        self.tel = int(tel.replace(' ', ''))
        
    def on_regular_line(self, line):
        if len(line) < 1:
            return
        if re.search(self.sluzby_re, str(line[0])) and not hasattr(self, 'headers'):
            self.headers = line[1:]
        elif re.search(self.volani_re, str(line[0])):
            operator = re.search(self.volani_re, str(line[0])).group('val')
            self.service_consumed[operator] = line[1:]

    def _is_person_header(self, line):
        return len(line) == 1 and re.match(self.personinfo_re, line[0])

if __name__ == '__main__':
    with open('sumsheet_3672461713.csv', 'r') as f:
        p = TMobileCSVBillParser(f)
        
    for tel, services in p.parsed.items():
        print '%s:\n%s' % (tel, services)
