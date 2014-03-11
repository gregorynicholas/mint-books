"""
  mintbooks.transactions
  ~~~~~~~~~~~~~~~~~~~~~~

  filter + sorting methods for lists of transactions.


  copyright (c) 2014 gregorynicholas
"""
from mintbooks import config
from mintbooks import csvutils


__all__ = [
  'get_labeled_txns', 'is_txn_labeled', 'parse_labels', 'group_txns_by_cat',
  'is_income_category',
]


def get_labeled_txns(csvdata, labels):
  """
  returns transactions that are tagged with the specified label.
  """
  rv = []
  for txn in csvdata:
    has_label = False

    # o(n)2
    for label in labels:
      if is_txn_labeled(txn, label):
        has_label = True  # add the transaction to the ouput
        break

    if has_label:
      rv.append(txn)
  return rv


def is_txn_labeled(txn, label):
  txn_labels = parse_labels(txn['Labels'])
  if label in txn_labels:
    return True
  else:
    return False


def parse_labels(labels):
  if labels is not None and labels != '':
    return sorted(labels.split(' '))
  else:
    return []


def group_txns_by_cat(txns):
  """
  returns a dict of categories, with values a dict of transactions keyed by
  their `TxnId`.
  """
  grouped_txns = {}
  for txn in txns:
    cat = csvutils.strval(txn['Category'])
    if cat not in grouped_txns:
      grouped_txns[cat] = {}

    grouped_txns[cat][txn['TxnId']] = txn
  return grouped_txns


def is_income_category(category):
  """
  returns a boolean if the specified category is an income.
  """
  return category.upper() in config.INCOME_CATEGORIES
