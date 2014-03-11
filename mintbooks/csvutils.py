"""
  mintbooks.csvutils
  ~~~~~~~~~~~~~~~~~~

  helpers for crushing .csv documents.


  copyright (c) 2014 gregorynicholas
"""
import csv
from codecs import getincrementalencoder
from cStringIO import StringIO

__all__ = [
  'strval', 'floatval', 'safeunicode', 'open_csv', 'parse_csv',
]


# string helpers + general utils n' shit..
# ---------------------------------------------------------------------------

def strval(column):
  return str(column.strip())


def floatval(column):
  if column is not None and column != "":
    return float(column)
  else:
    return -0


def safeunicode(val):
  """
  unicode a string safely and without errors.
  """
  return unicode(val, 'utf-8', errors='ignore')


def _unicode(val):
  """
  """
  if val and isinstance(val, basestring):
    return val.encode('utf-8')
  return val


def utf8_csv_reader(data, fieldnames):
  """
  see: stackoverflow.com/questions/904041/reading-a-utf8-csv-file-with-python
  """
  reader = csv.DictReader(
    data, fieldnames=fieldnames, restval='', dialect='excel')
  reader.next()  # offset one row for the header..
  for row in reader:
    yield {k: safeunicode(v) for k, v in row.iteritems()}


# csv reading + parsing utils.
# ---------------------------------------------------------------------------

def open_csv(filename):
  """
  returns an `open().read().splitlines(True)` call to a csv file.

    :param filename: string for the relative filename to open.
  """
  rv = None
  with open(filename, 'r') as f:
    rv = f.read().splitlines(True)
  return rv


def parse_csv(csvdata, fieldnames):
  """
  returns a parsed csv file as a list of dicts for each row.

    :param csvdata: list of string rows.
    :param fieldnames: list of string column names.
  """
  return [row for row in utf8_csv_reader(csvdata, fieldnames)]


# csv writing + output utils.
# ---------------------------------------------------------------------------

def write_csv(fieldnames, row_dicts, out_filename):
  """
    :param fieldnames: list of string column names.
    :param row_dicts: a parsed csv as a list of dicts.
    :param out_filename: string for the relative filename to output to.
  """
  # create a csv writer instance..
  writer = CsvWriter(fieldnames=fieldnames)

  # create a string'ified view of each record..
  writer.writerow({fn: fn for fn in fieldnames})
  [writer.writerow(row) for row in row_dicts]

  csvdata = writer.streamdata()
  # write the file to disk..
  with open(out_filename, 'w') as f:
    f.write(csvdata)

  return csvdata


class CsvWriter:
  """
  A CSV writer which will write rows to CSV file "f", which is encoded in
  the given encoding.
  """

  def __init__(self, fieldnames, dialect=csv.excel, encoding='utf-8',
               stream=None, **kw):
    if stream is None:
      stream = StringStream()
    self.stream = stream
    # Redirect output to a queue
    self.queue = StringIO()
    self.writer = csv.DictWriter(
      self.queue,
      fieldnames,
      restval='',
      # dialect=dialect,
      extrasaction='ignore')
    self.encoder = getincrementalencoder(encoding)()

  def writerow(self, row_dict):
    row_dict = {k: _unicode(v) for k, v in row_dict.iteritems()}
    self.writer.writerow(row_dict)
    # Fetch UTF-8 output from the queue..
    data = self.queue.getvalue()
    data = data.decode('utf-8')
    # ...and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream..
    self.stream.write(data)
    # empty queue..
    self.queue.truncate(0)

  def writerows(self, rows):
    [self.writerow(row) for row in rows]

  def streamdata(self):
    """
    Returned the finalized stream output.
    """
    return self.stream.data


class StringStream:
  def __init__(self):
    self.data = ''

  def write(self, value):
    self.data += value
