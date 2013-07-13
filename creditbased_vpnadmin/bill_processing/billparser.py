# -*- coding: utf-8 -*-
import re
import csv
import codecs
import datetime


class TMobileCSVBillParser(object):
    """
    Reads the given CSV file and creates python structures for further
    processing.
    """
    
    personinfo_re = '(?P<tel>[0-9]{3} [0-9]{3} [0-9]{3}) / Firma 3000 - mobil'
    sluzby_re = u'Služby'
    
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
        try:
            key, free, paid, fee = self.line_info(line)
            if re.search(self.sluzby_re, key):
                return
            
            self.service_consumed[key] = {
                'free': self._get_val(free),
                'paid': self._get_val(paid),
                'fee': int(float(fee.replace(',', '.')))
            }
        except (IndexError, ValueError):
            return
        
    def _get_val(self, v):
        try:
            return int(v)
        except:
            m, s = v.strip('\'').split(':')
            return datetime.timedelta(minutes=int(m), seconds=int(s))
            
    def line_info(self, line):
        return line[0], line[1], line[2], line[4]

    def _is_person_header(self, line):
        return len(line) == 1 and re.match(self.personinfo_re, line[0])

if __name__ == '__main__':
    with open('sumsheet_3673301813.csv', 'r') as f:
        p = TMobileCSVBillParser(f)
        
    for tel, services in p.parsed.items():
        print '%s:\n' % tel
        for k, v in services.items():
            print '%s=%s\n' % (k, v)
