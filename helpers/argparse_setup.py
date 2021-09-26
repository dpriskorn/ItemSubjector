import argparse


def setup_argparse_and_return_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
ItemSubjector enables working main subject statements on items based on a 
heuristic matching the subject with the title of the item. 

It also enables your to delete main subjects on items if they have at least
one other main subject. 

Example adding one QID:
'$ itemsubjector.py Q1234'

Example adding one QID and prepare a job list to be run non-interactively later:
'$ itemsubjector.py Q1234 -p'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles:
'$ itemsubjector.py -m'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles 
and prepare a job list:
'$ itemsubjector.py -m -p'

Example removing a QID from a P921 on items that have another (more specific QID in P921):
'$ itemsubjector.py -d Q1234 -f Q1'
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
        '-d', '--delete',
        nargs='?',
        help=('Delete a specific QID from P921 on the items that have a P921 '
              'with one of the values specified with --has-main-subject')
    )
    parser.add_argument(
        '-f', '--from-items-with', '--has-main-subject',
        nargs='+',
        default=None,
        help='Work on a subset of items having any of these P921-values'
    )
    return parser.parse_args()
