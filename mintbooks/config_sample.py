
APP = {
  'title': '2013 financials',
  'disclaimer': 'PS: fuck taxes.',
  'url': 'http://github.com:gregorynicholas/mint-books',
  'version': '0.0.1',
  'release_date': '2014-03-11',
  'prepared_for': 'gregory nicholas',
}

YEAR = '2013'

COLUMNS = [
  'Date',
  'Description',
  'Original Description',
  'Amount',
  'Transaction Type',
  'Category',
  'Account Name',
  'Labels',
  'Notes',
]

GROUPING_LABELS = [
]

DEFAULT_GROUP_LABELS = [
  'taxrelated',
  'deductible',
]

INCOME_CATEGORIES = [
  '1099-INCOME',
  'EXIT',
  'INCOME',
  'INTEREST INCOME',
  'REIMBURSEMENT',
  'RENTAL INCOME',
  'STOCK-REPURCHASE',
  'STUDIO-BOOKING',
  'TAX-RETURN',
]

IGNORE_LABELS = [
  'family',
  'partycash',
]

IGNORE_MERCHANTS = [
]

IGNORE_NOTE_STRINGS = [
  'vacation',
  # '#spain',
  # special tag, allows us to keep some txns in mint categorized + tagged
  # thoroughly, but skips being output in groupings (aka good for hiding drugs)
  '#HIDE',
]
