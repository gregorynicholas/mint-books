"""
  mintbooks.grouping_collection
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  a collection of Groupings.


  copyright (c) 2014 gregorynicholas
"""
from collections import defaultdict
from mintbooks import grouping
from mintbooks import transactions


class GroupingCollection(object):
  """
  a collection of transaction Groupings.
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
