"""
  mintbooks.transaction_collection
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  a collection of transactions.


  copyright (c) 2014 gregorynicholas
"""
from collections import MutableSequence
from mintbooks import csvutils
from mintbooks import transactions


class TransactionCollection(MutableSequence):
  """
  list mixin class for a collection of transactions.
  """

  def __init__(self, data=None):
    super(TransactionCollection, self).__init__()
    if data is not None:
      self._list = data
      print 'creating transaction collection:', len(data)
    else:
      self._list = list()
    self.filter_duplicates()
    self.fix_amounts()
    self.assign_txn_ids()

  def __len__(self):
    return len(self._list)

  def __getitem__(self, ii):
      return self._list[ii]

  def __delitem__(self, ii):
      del self._list[ii]

  def __setitem__(self, ii, val):
      return self._list[ii]

  def __str__(self):
      return self.__repr__()

  def __repr__(self):
      return """<TransactionCollection {}>""".format(self._list)

  def insert(self, ii, val):
      self._list.insert(ii, val)

  def append(self, val):
      list_idx = len(self._list)
      self.insert(list_idx, val)

  def assign_txn_ids(self):
    """
    manually assign id to each txn row, so we can build a table of keys.
    """
    idx = 0
    for r in self._list:
      r['TxnId'] = idx
      idx += 1

  def fix_amounts(self):
    """
    mint exports all transactions without regard of credit vs debit. this
    converts debit txns to be prefixed with "-".
    """
    for r in self._list:
      txntype = csvutils.strval(r['Transaction Type'].lower())
      txnamount = csvutils.strval(r['Amount'])
      if txntype == "debit" and not txnamount.startswith('-'):
        r['Amount'] = prefix(txnamount, '-')

  def filter_duplicates(self):
    """
    filter out paypal instant transfers + temp holds
    """
    rv = []
    for txn in self._list:
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
    self._list = rv

  def filter_by_label(self, label):
    """
    removes transactions with the specified label.
    """
    rv = []
    for txn in self._list:
      has_label = False

      if transactions.is_txn_labeled(txn, label):
        has_label = True

      if not has_label:
        rv.append(txn)
    self._list = rv

  def filter_by_category(self, category, skip_labels=None):
    """
    removes transactions with the specified category.
    """
    rv = []
    for txn in self._list:
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
    self._list = rv

  def filter_by_merchant(self, merchant):
    """
    removes transactions with the specified merchant.
    """
    rv = []
    for txn in self._list:
      is_merchant = False
      val = csvutils.strval(txn['Description'])
      if merchant == val:
        is_merchant = True

      if not is_merchant:
        rv.append(txn)
    self._list = rv

  def filter_by_notes_containing(self, contains, skip_labels=None):
    """
    removes transactions when notes contains the specified string.
    """
    rv = []
    for txn in self._list:
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
    self._list = rv

  def filter_by_year(self, year):
    """
    returns only transactions within the specified year.
    """
    self._list = [_ for _ in self if year in _['Date']]


def prefix(string, prefix):
  return "{}{}".format(prefix, string)
