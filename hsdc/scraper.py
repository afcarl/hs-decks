"""
Methods to scrape deck data from web.
"""

import pandas as pd
import requests
from lxml import html
from lxml import etree
from hsdc.parallel import parallelize

HEARTHPWN_BASE_URL = "http://www.hearthpwn.com/decks?filter-is-forge=2&filter-deck-tag=1"

def _get_page(page_idx):
    """Gets decks from a single page."""
    print('Scraping decks from page %d' % page_idx)
    tree = html.fromstring(
        requests.get(
            "%s&page=%d" %
            (HEARTHPWN_BASE_URL, page_idx)).text)
    links = [a.get("href")
             for a in tree.cssselect('table#decks tbody span.tip > a')]
    table = etree.tostring(tree.cssselect(
        'table#decks')[0], encoding='UTF-8')

    decks_df = pd.read_html(table)[0].dropna(
        axis=1, how='all')  # Drop bad results
    decks_df['Link'] = links  # Add back links
    # Strip whitespace in column names
    decks_df.rename(columns=lambda s: s.strip(), inplace=True)
    return decks_df

def get_hearthpwn_decks(pages=10):
    """Scrapes HearthPwn and get decks.
    :pages: Number of pages to scrape; there are 25 decks per page
    :return: A pandas.DataFrame containing deck information
    """
    parallel_get_page = parallelize(_get_page)
    return pd.concat(parallel_get_page(range(1, pages + 1)),
        ignore_index=True)


def get_hearthpwn_deck(rel_url, drop_incomplete=False):
    """Scrapes a HearthPwn deck page
    :param rel_url: Relative url of the deck under hearthpwn.com
    :return: A pandas.Series containing card name to card count
    """
    print('Scraping deck list from %s' % rel_url)
    tree = html.fromstring(requests.get(
        'http://www.hearthpwn.com' + rel_url).text)
    card_nodes = tree.cssselect(
        'div.details.t-deck-details table.listing.listing-cards-tabular td.col-name')
    cards = {}
    for node in card_nodes:
        name = node.cssselect('a')[0].text.strip()
        count = int(list(node.itertext())[-1].strip()[-1])
        cards[name] = count

    if sum(cards.values()) != 30 and drop_incomplete:
        return None

    return pd.Series(cards)
