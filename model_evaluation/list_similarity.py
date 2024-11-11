# similarity functions for comparing two lists

from string_similarity import bert_cosine_optimized


def dice_list(list1, list2):
    """Dice similarity is a common similarity metrics for two sets. Defining Dice Similarity function for two lists"""
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1) + len(set2)
    if union == 0:
        return 1, 0
    dice = float(2 * intersection) / union
    weight = (
        (2 * len(set1) * len(set2)) / (len(set1) + len(set2)) if (len(set1) + len(set2)) != 0 else 0
    )
    return dice, weight  # len(set1) + len(set2)


def jaccard_list(list1, list2):
    """Jaccard similarity is a common similarity metrics for two sets. Defining Jaccard Similarity function for two lists"""
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = (len(set1) + len(set2)) - intersection
    if union == 0:
        return 1, 0
    jaccard = float(intersection) / union
    weight = (
        (2 * len(set1) * len(set2)) / (len(set1) + len(set2)) if (len(set1) + len(set2)) != 0 else 0
    )

    return jaccard, weight  # len(set1) + len(set2)


def scores(list_1, list_2, score_type="precision"):
    """list_1 is the ground truth, list_2 is the generated list"""
    # Convert lists to sets
    set1, set2 = set(list_1), set(list_2)

    # Compute the intersection of the sets
    intersection = set1.intersection(set2)
    # Calculate precision
    precision = len(intersection) / len(set2) if set2 else 0

    # Calculate recall
    recall = len(intersection) / len(set1) if set1 else 0

    weight = (
        (2 * len(set1) * len(set2)) / (len(set1) + len(set2)) if (len(set1) + len(set2)) != 0 else 0
    )
    # Calculate the F1 score
    if precision + recall == 0:
        f1 = 0  # To handle the case when both precision and recall are zero
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    if score_type == "precision":
        return precision, weight  # len(set1) + len(set2)
    elif score_type == "recall":
        return recall, weight  # len(set1) + len(set2)
    elif score_type == "f1":
        return f1, weight  # len(set1) + len(set2)
    else:
        raise ValueError("Invalid score type. Use 'precision', 'recall', or 'f1'.")


def make_similar_items_equal(list1, list2, similarity_func=bert_cosine_optimized, threshold=0.7):
    """Takes two lists, makes similar items beyond a similarity threshold in list 2 identical to list 1.

    Two items are considered similar if the value of them passed to the similarity_func is above the threshold.
    Furthermore an item can be matched as similar only ones and is matched similar with the item from the opponent list
    which has the highest available similairty score. That prevents an inflation of replacements."""

    # compute a matrix of comparisons with the similairty function
    comparison_matrix = {}
    for i1 in range(len(list1)):
        for i2 in range(len(list2)):
            if (i1, i2) or (i2, i1) not in comparison_matrix:
                comparison_matrix[(i1, i2)] = similarity_func(list1[i1], list2[i2])

    # sort matrix by highest scores
    sorted_comparison_matrix = sorted(
        comparison_matrix.items(), key=lambda item: item[1], reverse=True
    )

    # indexes of already matched items
    already_matched_list1, already_matched_list2 = [], []

    # calculate matches from List 1 and 2
    for (i_item1, i_item2), score in sorted_comparison_matrix:

        # an item can be matched only ones
        if i_item1 in already_matched_list1 or i_item2 in already_matched_list2:
            continue

        # if the score is bigger than the threshold, the item in list 2 is replaced by the item of list 1
        if score >= threshold:
            list2[i_item2] = list1[i_item1]
            already_matched_list1.append(i_item1)
            already_matched_list2.append(i_item2)

    return list1, list2


# def make_similar_items_equal(list1, list2, similarity_func = bert_cosine_optimized, threshold = 0.7):
#     """Takes two lists, makes similar items beyond a similarity threshold in list 2 identical to list 1."""

#       # compute a matrix of comparisons with the similairty function
#     comparison_matrix = {}

#     for i in list1:
#         for j in list2:
#             if (i, j) or (j, i) not in comparison_matrix:
#                 comparison_matrix[(i, j)] = similarity_func(i, j)

#     adjusted_list2 = []

#     for element in list2:

#         dicted = {k[0]:v for k,v in comparison_matrix.items() if k[1] == element and v > threshold}

#         if dicted:
#             adjusted_list2.append(max(dicted, key=dicted.get))
#         else:
#             adjusted_list2.append(element)

#     return list1, adjusted_list2


def index_list(list):
    """takes a list and adds an index for every item in the list.
    for example takes ["a", "b", "c", "c", "d", "b"]
    and produces ["a1", "b1", "c1", "c2", "d1", "b2"]"""

    count = {}
    indexed_list = []
    for item in list:
        index = count.get(item, 0)
        indexed_list.append(f"{item}{index}")
        count[item] = index + 1
    return indexed_list


def similarity_SFA(list1, list2, method="dice", threshold=0.7):
    """similairty metric for lists which is semantic and frequency aware.

    it applies first the function make_similar_items_equal which enables semantic awareness
    then it applies the function index_list which enables frequency awareness
    and then it computes the similarity of the two transformed lists, either with dice or jaccard

    list1: list of strings (ground truth)
    list2: list of strings
    method: "dice" or "jaccard" or "precision" or "recall" or "f1" """

    list1, list2 = make_similar_items_equal(list1, list2, threshold=threshold)
    list1, list2 = index_list(list1), index_list(list2)
    if method == "dice":
        return dice_list(list1, list2)
    elif method == "jaccard":
        return jaccard_list(list1, list2)
    elif method == "precision" or method == "recall" or method == "f1":
        return scores(list1, list2, score_type=method)
