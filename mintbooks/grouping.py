"""
  mintbooks.grouping
  ~~~~~~~~~~~~~~~~~~

  a grouping of transactions.


  copyright (c) 2014 gregorynicholas
"""
from collections import defaultdict
from mintbooks import csvutils
from mintbooks import transactions


class Grouping(object):
  """
  class for a grouping of transactions by label.
  """

  label = None
  txns = None
  grouped_txns = None
  totals = None

  def __init__(self, label, txns):
    """
    constructor.
    """
    self.label = label
    if label == 'ungrouped':
      self.txns = txns
    else:
      self.txns = transactions.get_labeled_txns(txns, [self.label])
    self.totals = {
      'income': defaultdict(int),
      'expenses': defaultdict(int),
    }
    self.income_txns = 0
    self.expenses_txns = 0
    # group transactions by category
    self.grouped_txns = transactions.group_txns_by_cat(self.txns)

  def group_txns(self, mgr):
    """
    returns a dict of transactions by type, grouped by category.
    """
    for cat, _txns in sorted(self.grouped_txns.items()):

      if transactions.is_income_category(cat):
        cat_type = 'income'
      else:
        cat_type = 'expenses'

      # sum aggregations per category
      for txn_id, txn in _txns.items():

        # track the txn_id to dedup across labels..
        if txn_id not in mgr.grouped_txn_ids:
          mgr.grouped_txn_ids.append(txn_id)

          self.totals[cat_type][cat] += csvutils.floatval(txn['Amount'])
          mgr.grouping_totals[cat_type][self.label] += csvutils.floatval(
            txn['Amount'])
          if cat_type is 'income':
            self.income_txns += 1
          else:
            self.expenses_txns += 1

    # update group manager
    mgr.totals['txns'] += len(self.txns)

    # print the output of the grouping to sys.out
    self.output_view(mgr)

  def output_view(self, mgr):
    """
    prints the output of the grouping to sys.out
    """
    self.print_heading(mgr)

    # sum overall totals..
    print ' * expenses:'
    for cat, amt in sorted(self.totals['expenses'].items()):
      mgr.totals['expenses'] += amt
      self.print_transactions(cat, self.grouped_txns[cat])

    print ' * income:'
    for cat, amt in sorted(self.totals['income'].items()):
      mgr.totals['income'] += amt
      self.print_transactions(cat, self.grouped_txns[cat])

    self.print_summary(mgr)

  def print_heading(self, mgr):
    """
    prints a grouping heading.
    """
    print '''
### {}
'''.format(
     self.fmt_col(self.label, 18))

  def print_transactions(self, cat, _txns):
    """
    prints a formatted view of transactions grouped by category to sys.out
    """
    print '    * {} \t\t{} \t\t{}'.format(
      self.fmt_col(cat.lower(), 22), len(_txns), self.get_totals(cat))

  def print_summary(self, mgr):
    """
    print a formatted view of to sys.out
    """
    income_totals = mgr.grouping_totals['income'][self.label]
    expenses_totals = mgr.grouping_totals['expenses'][self.label]
    print '''
grouping totals:
  - txns:  {}
  - expenses: {}  ({} txns)
  - income: {}  ({} txns)

'''.format(
      len(self.txns),
      expenses_totals,
      self.expenses_txns,
      income_totals,
      self.income_txns,
      # TODO: totals
    )

  def get_totals(self, cat):
    if transactions.is_income_category(cat):
      cat_type = 'income'
    else:
      cat_type = 'expenses'
    return self.totals[cat_type][cat]

  def fmt_col(self, val, length):
    """
    pads a string to be at least a specified char length.
    """
    while len(val) < length:
      val += ' '
    return val
