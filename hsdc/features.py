"""
Extract additional domain features from cards.
"""

import pandas as pd

import fireplace
import fireplace.cards
from fireplace.cards import db
from hearthstone.enums import CardType


def augment_cards(cards):
    """
    :cards: A pandas.Series containing card name to card count.
    :return: A multilevel pandas.Series with card counts and card costs
    """
    cost_features = {}
    for card_name in cards.index:
        card = db[fireplace.cards.filter(
            name=card_name,
            collectible=True)[0]]
        assert CardType(card.type) in [CardType.MINION, CardType.SPELL, CardType.WEAPON]
        card_type = CardType(card.type).name
        try:
            cost = card.cost
        except AttributeError as e:
            if card_name == 'Crush':
                cost = 7
            else:
                raise Exception(card_name) from e

        index_tuple = (card_type, cost)
        cost_features[index_tuple] = (
            cost_features.get(index_tuple, 0) + cards[card_name])

    results = cards.copy()
    results.index = pd.MultiIndex.from_product([['CARD'], results.index])
    costs = pd.Series(list(cost_features.values()),
                      index = pd.MultiIndex.from_tuples(
                          cost_features.keys(),
                          names = ['Card Type', 'Card Cost']))
    return results.append(costs).sort_index()
