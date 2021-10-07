import argparse


def setup_argparse_and_return_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
ItemSubjector enables working main subject statements on items based on a 
heuristic matching the subject with the title of the item. 

Example adding one QID:
'$ itemsubjector.py -l Q1234'

Example adding one QID and prepare a job list to be run non-interactively later:
'$ itemsubjector.py -l Q1234 -p'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles:
'$ itemsubjector.py -m'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles 
and prepare a job list:
'$ itemsubjector.py -m -p'

Example working on all diseases:
'$ itemsubjector.py --sparql "SELECT ?item WHERE {?item wdt:P31 wd:Q12136.}"'
    """)
    parser.add_argument(
        '-a', '--add', '--qid-to-add',
        nargs='+',
        help=('List of QIDs or URLs to Q-items that '
              'are to be added as '
              'main subjects on scientific articles. '
              'Always add the most specific ones first. '
              'See the README for examples')
    )
    parser.add_argument(
        '-na', '--no-aliases',
        action='store_true',
        help='Turn off alias matching'
    )
    parser.add_argument(
        '-nc', '--no-confirmation',
        action='store_false',
        default=True,
        help='Turn off confirmation after displaying the search expressions, before running the queries.'
    )
    parser.add_argument(
        '-p', '--prepare-jobs',
        action='store_true',
        help='Prepare a job for later execution, e.g. in a job engine'
    )
    parser.add_argument(
        '-r', '--run-prepared-jobs',
        action='store_true',
        help='Run prepared jobs non-interactively'
    )
    parser.add_argument(
        '-rm', '--remove-prepared-jobs',
        action='store_true',
        help='Remove prepared jobs'
    )
    parser.add_argument(
        '-m', '--match-existing-main-subjects',
        action='store_true',
        help=('Match from list of 136.000 already used '
              'main subjects on other scientific articles')
    )
    parser.add_argument(
        '-w', '--limit-to-items-without-p921',
        action='store_true',
        help='Limit matching to scientific articles without P921 main subject'
    )
    parser.add_argument(
        '-su', '--show-search-urls',
        action='store_true',
        help='Show an extra column in the table of search strings with links'
    )
    parser.add_argument(
        '-iu', '--show-item-urls',
        action='store_true',
        help='Show an extra column in the table of items with links'
    )
    parser.add_argument(
        '--sparql',
        nargs='?',
        help='Work on main subject items returned by this SPARQL query. '
             'Note: "?item" has to be in selected for it to work.'
    )
    parser.add_argument(
        '--debug-sparql',
        action='store_true',
        help='Enable debugging of SPARQL queries.',
        default=False
    )
    return parser.parse_args()
