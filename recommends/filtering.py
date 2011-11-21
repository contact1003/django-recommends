from collections import defaultdict
from .distances import sim_distance, sim_pearson

# Most of this is adapted from: Programming collective intelligence, Toby Segaran, 2007


def top_matches(prefs, person, similarity=sim_pearson):
    """
    Returns the best matches for person from the prefs dictionary.
    Number of results and similarity function are optional params.
    """

    return [(similarity(prefs, person, other), other) for other in prefs if other != person]


def get_recommendations(prefs, person, similarity=sim_pearson):
    """
    Gets recommendations for a person by using a weighted average
    of every other user's rankings
    """

    totals = defaultdict(int)
    simSums = defaultdict(int)

    for other in prefs:
        # don't compare me to myself
        if other != person:
            sim = similarity(prefs, person, other)
            # ignore scores of zero or lower
            if sim > 0:
                for item in prefs[other]:
                    # only score movies I haven't seen yet
                    if item not in prefs[person] or prefs[person][item] == 0:
                        # Similarity * Score
                        totals[item] += prefs[other][item] * sim
                        # Sum of similarities
                        simSums[item] += sim
    # Create the normalized list
    return ((total / simSums[item], item) for item, total in totals.iteritems())


def transform_prefs(prefs):
    result = defaultdict(dict)
    for person in prefs:
        for item in prefs[person]:
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculate_similar_items(prefs, similarity=sim_distance, verbose=0):
    """
    Create a dictionary of items showing which other items they
    are most similar to.

    Output:

    ::

        {
            "<object_id>": [
                            (<score>, <related_object_id>),
                            (<score>, <related_object_id>),
            ],
            "<object_id>": [
                            (<score>, <related_object_id>),
                            (<score>, <related_object_id>),
            ],
        }
    """

    itemMatch = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transform_prefs(prefs)
    #[itemMatch.set(item, top_matches(itemPrefs, item, similarity=similarity)) for item in itemPrefs]
    for item in itemPrefs:
        # Find the most similar items to this one
        itemMatch[item] = top_matches(itemPrefs, item, similarity=similarity)
    return itemMatch


def get_recommended_items(prefs, itemMatch, user):
    """
    itemMatch is supposed to be the result of ``calculate_similar_items()``

    Output:

    ::

        [
            (<score>, '<object_id>'),
            (<score>, '<object_id>'),
        ]
    """
    if user in prefs:
        userRatings = prefs[user]
        scores = defaultdict(int)
        totalSim = defaultdict(int)

        # Loop over items rated by this user
        for (item, rating) in userRatings.iteritems():
            # Loop over items similar to this one
            for (similarity, item2) in itemMatch[item]:
                # Ignore if this user has already rated this item
                if item2 not in userRatings:
                    # Weighted sum of rating times similarity
                    scores[item2] += similarity * rating

                    # Sum of all the similarities
                    totalSim[item2] += similarity

        # Divide each total score by total weighting to get an average
        rankings = ((score / totalSim[item], item) for item, score in scores.iteritems() if totalSim[item] != 0)
        return rankings
    return []
