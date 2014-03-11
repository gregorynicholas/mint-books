"""
  mintbooks.pavement
  ~~~~~~~~~~~~~~~~~~

  a python + command line app to use mint.com transaction exports to package
  financials for, let's say, an accountant.


  copyright (c) 2014 gregorynicholas
"""
# system imports
import os
import sys
sys.path.insert(0, os.path.abspath("."))

# local csv processing module
from mintbooks import config
from mintbooks import csvutils
from mintbooks import grouping
from mintbooks import transactions

# paver cli imports
from paver.easy import task, cmdopts

# aggregation imports
from collections import defaultdict


export_opt = (
  "export=", "e",
  "the csv export to load data from. is the relative filename of the csv.")

export_out_opt = (
  "out=", "o",
  "the relative filename to output to.")


@task
@cmdopts([
  export_opt,
  export_out_opt,
])
def parse_2013_txns(options):
  """
  parse + output groupings of mint.com transactions for a specified year.
  """
  csvdata = csvutils.open_csv(options.export)
  txns = csvutils.parse_csv(csvdata, config.COLUMNS)
  group_labels = config.DEFAULT_GROUP_LABELS + config.GROUPING_LABELS

  # build list of transactions
  txns = filter_duplicate_txns(txns)

  for label in config.IGNORE_LABELS:
    txns = filter_txns_by_label(
      txns, label)

  for cat in config.HARD_IGNORE_CATEGORIES:
    txns = filter_txns_by_category(
      txns, cat)

  for cat in config.IGNORE_CATEGORIES:
    txns = filter_txns_by_category(
      txns, cat, skip_labels=group_labels)

  for note_str in config.IGNORE_NOTE_STRINGS:
    txns = filter_txns_by_notes_containing(
      txns, note_str, skip_labels=group_labels)

  for merch in config.IGNORE_MERCHANTS:
    txns = filter_txns_by_merchant(
      txns, merch)

  # filter by specified year
  txns = filter_txns_by_year(txns, config.YEAR)

  # normalize + make updates
  assign_txn_ids(txns)
  fix_amounts(txns)

  #
  # create data tables + aggregations based on combos of tags + categories.
  #
  grouping_mgr = GroupingMgr(txns)

  print '''

{title}
prepared for: {prepared_for}
version: {version}
release date: {release_date}
source code url: {url}
disclaimer: {disclaimer}


                        GROUPINGS BY LABEL
-----------------------------------------------------------------
  '''.format(**config.APP)

  #
  # grouped txn's..
  #
  for grouping_label in config.GROUPING_LABELS:
    grouping_mgr.create_grouping(grouping_label)

  #
  # txn's not in any grouping..
  #
  # print out txns that aren't in the `grouping_mgr.grouped_txn_ids`
  print '''

                          UN-GROUPED
-----------------------------------------------------------------
  '''
  grouping_mgr.create_ungrouped_txns()

  print '''
-----------------------------------------------------------------
'''
  print 'totals:'
  print '    * txns: {}'.format(grouping_mgr.totals['txns'])
  print '    * income: {}'.format(grouping_mgr.totals['income'])
  print '    * expenses: {}'.format(grouping_mgr.totals['expenses'])

  # write the final output..
  csvutils.write_csv(config.COLUMNS, txns, options.out)


# grouping + aggregation methods..
# ---------------------------------------------------------------------------

class GroupingMgr(object):
  """
  class for managing a bucket of transaction groupings.
  """

  def __init__(self, txns):
    """
    constructor.
    """
    self.txns = txns or []
    self.grouped_txn_ids = []
    self._non_grouped_txns = None
    self.groupings = {}
    self.grouping_totals = {
      'expenses': defaultdict(int),
      'income': defaultdict(int),
    }
    self.totals = defaultdict(int)

  def create_grouping(self, label, txns=None):
    if txns is None:
      txns = self.txns
    self.groupings[label] = grouping.Grouping(label, txns)
    self.groupings[label].group_txns(self)

  def create_ungrouped_txns(self):
    """
    create a grouping for non-grouped tax-related transactions
    """
    self.create_grouping('ungrouped', self.non_grouped_txns)

  @property
  def non_grouped_txns(self):
    """
    returns a list of transactions not grouped
    """
    if self._non_grouped_txns is None:
      txns = [
        _ for _ in self.txns if _['TxnId'] not in self.grouped_txn_ids
      ]
      # filter non-grouped transactions for tax-related status
      self._non_grouped_txns = transactions.get_labeled_txns(
        txns, ['taxrelated', 'deductible', 'expense'])
      # print "self._non_grouped_txns:", self._non_grouped_txns
    return self._non_grouped_txns


# ---------------------------------------------------------------------------

def prefix(string, prefix):
  return "{}{}".format(prefix, string)


def assign_txn_ids(txns):
  """
  manually assign id to each txn row, so we can build a table of keys.
  """
  idx = 0
  for r in txns:
    r['TxnId'] = idx
    idx += 1
  config.COLUMNS.insert(0, 'TxnId')


def fix_amounts(csvdata):
  """
  mint exports all transactions without regard of credit vs debit. this
  converts debit txns to be prefixed with "-".
  """
  for r in csvdata:
    txntype = csvutils.strval(r['Transaction Type'].lower())
    txnamount = csvutils.strval(r['Amount'])
    if txntype == "debit" and not txnamount.startswith('-'):
      r['Amount'] = prefix(txnamount, '-')


def filter_txns_by_year(csvdata, year):
  """
  returns only transactions within the specified year.
  """
  return [x for x in csvdata if year in x['Date']]


def filter_duplicate_txns(csvdata):
  """
  * currently not possible
  """
  # filter out paypal instant transfers + temp holds
  rv = []
  for txn in csvdata:
    duplicate = False
    orig_desc = csvutils.strval(txn['Original Description']).upper()
    if 'PAYPAL DES:INST XFER ID' in orig_desc:
      duplicate = True
    if 'PAYPAL DES:TRANSFER ID' in orig_desc:
      duplicate = True
    if 'TEMPORARY HOLD BY PAYPAL' in orig_desc:
      duplicate = True
    if 'TEMPORARY HOLDBY PAYPAL' in orig_desc:
      duplicate = True
    if 'AUTHORIZATIONTO ' in orig_desc:
      duplicate = True
    if 'AUTHORIZATION TO ' in orig_desc:
      duplicate = True

    if not duplicate:
      rv.append(txn)
  return rv


def filter_txns_by_merchant(csvdata, merchant):
  """
  removes transactions with the specified merchant.
  """
  rv = []
  for txn in csvdata:
    is_merchant = False
    val = csvutils.strval(txn['Description'])
    if merchant == val:
      is_merchant = True

    if not is_merchant:
      rv.append(txn)
  return rv


def filter_txns_by_category(csvdata, category, skip_labels=None):
  """
  removes transactions with the specified category.
  """
  rv = []
  for txn in csvdata:
    in_category = False
    val = csvutils.strval(txn['Category'])
    if category == val:
      in_category = True

      # nested logic..
      if skip_labels:
        txn_labels = transactions.parse_labels(txn['Labels'])
        for skip_label in skip_labels:
          if skip_label in txn_labels:
            in_category = False
            break

    if not in_category:
      rv.append(txn)
  return rv


def filter_txns_by_notes_containing(csvdata, contains, skip_labels=None):
  """
  removes transactions when notes contains the specified string.
  """
  rv = []
  for txn in csvdata:
    skip = False
    val = csvutils.strval(txn['Notes']).upper()
    if contains.upper() in val:
      skip = True

      # nested logic..
      if skip_labels:
        txn_labels = transactions.parse_labels(txn['Labels'])
        for skip_label in skip_labels:
          if skip_label in txn_labels:
            skip = False
            break

    if skip is False:
      rv.append(txn)
  return rv


def filter_txns_by_label(csvdata, label):
  """
  removes transactions with the specified label.
  """
  rv = []
  for txn in csvdata:
    has_label = False

    if transactions.is_txn_labeled(txn, label):
      has_label = True

    if not has_label:
      rv.append(txn)
  return rv
