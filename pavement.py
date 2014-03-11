"""
  mintbooks.pavement
  ~~~~~~~~~~~~~~~~~~

  a python + command line app to use mint.com transaction exports to package
  financials for, let's say, an accountant.


  copyright (c) 2014 gregorynicholas
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))  # something lame in my python env.

from mintbooks import config
from mintbooks import csvutils
from mintbooks import grouping_collection
from mintbooks import transaction_collection

# paver cli imports
from paver.easy import task, cmdopts


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
  group_labels = config.DEFAULT_GROUP_LABELS + config.GROUPING_LABELS
  csvdata = csvutils.open_csv(options.export)
  txns = transaction_collection.TransactionCollection(
    csvutils.parse_csv(csvdata, config.COLUMNS))

  # build sanitized + normalized transactions collection..

  for label in config.IGNORE_LABELS:
    txns.filter_by_label(label)

  for cat in config.HARD_IGNORE_CATEGORIES:
    txns.filter_by_category(cat)

  for cat in config.IGNORE_CATEGORIES:
    txns.filter_by_category(
      cat, skip_labels=group_labels)

  for note_str in config.IGNORE_NOTE_STRINGS:
    txns.filter_by_notes_containing(
      note_str, skip_labels=group_labels)

  for merch in config.IGNORE_MERCHANTS:
    txns.filter_by_merchant(merch)

  # filter by specified year
  txns.filter_by_year(config.YEAR)

  # normalize + make updates
  config.COLUMNS.insert(0, 'TxnId')

  # TODO: move to a jinja template..

  #
  # create data tables + aggregations based on combos of tags + categories.
  #
  grouping_coll = grouping_collection.GroupingCollection(txns)

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
    grouping_coll.create_grouping(grouping_label)

  #
  # txn's not in any grouping..
  #
  # print out txns that aren't in the `grouping_coll.grouped_txn_ids`
  print '''

                          UN-GROUPED
-----------------------------------------------------------------
  '''
  grouping_coll.create_ungrouped_txns()

  print '''
-----------------------------------------------------------------
'''
  print 'totals:'
  print '    * txns: {}'.format(grouping_coll.totals['txns'])
  print '    * income: {}'.format(grouping_coll.totals['income'])
  print '    * expenses: {}'.format(grouping_coll.totals['expenses'])

  # write the final output..
  csvutils.write_csv(config.COLUMNS, txns, options.out)
