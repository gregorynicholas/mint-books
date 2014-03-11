mintbooks
~~~~~~~~~

a python command line app to use mint.com transaction exports to package
financials for, let's say, an accountant.


### SETUP:

    $ mkvirtualenv mint-books
    $ pip install -r mintbooks/requirements.txt


### RUNNING:

    $ workon mint-books
    $ paver --help
    $ paver parse_2013_txns  -e "mint-transactions.csv"  -o "mint-transactions-packaged.csv"



copyright (c) 2014 gregorynicholas
