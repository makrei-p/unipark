import matplotlib.pyplot as plt

# color map for the likert scale questions
cmap = plt.get_cmap('RdYlGn')

# known likert scales
scales = {
    'agreement': ['Fully disagree', 'Rather disagree', 'Neutral', 'Rather agree', 'Fully agree'],
    'likelihood': ['Unlikely', 'Rather unlikely', 'Neither unlikely nor likely', 'Rather likely', 'Likely']
}

# determine the likert scale which has the most overlap with a given scale


def determine_scale(scale):
    overlap_count = {}
    for s in scales.keys():
        overlap = list(set(scales[s]) & set(scale))
        overlap_count[s] = len(overlap)

    # determine the scale (dict key) with the largest overlap with the given scale
    bestfitscale = max(overlap_count, key=overlap_count.get)

    # in case the "maximum overlap" is zero, the scale was not a known likert scale
    if overlap_count[bestfitscale] == 0:
        return None

    likertscale = scales[bestfitscale]
    return likertscale
