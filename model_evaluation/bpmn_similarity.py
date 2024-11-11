# similarity functions for comparing two bpmn instances


from bpmn_schema_helper import get_flows_with_values, get_lanes
from list_similarity import similarity_SFA
from statistics import mean


def weighted_score(array_of_scores_with_weights):
    """Calculates a weighted score.
    Takes an array like this: [{"score": 0.3, "weight": 5},{"score": 0.8, "weight": 6}]
    """
    numerator, denominator = 0, 0
    for score_with_weight in array_of_scores_with_weights:
        score = score_with_weight["score"]
        weight = score_with_weight["weight"]
        numerator += score * weight
        denominator += weight

    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def get_list(bpmn_object, sublist, attribute):
    """Returns a list of attributes within a sublist of a bpmn_object.
    For example sublist="tasks", attribute="name" returns the list of task names"""
    return list(
        map(lambda t: t[attribute], filter(lambda x: x.get(attribute), bpmn_object[sublist]))
    )


def extract_bpmn_sets(bpmn_object):
    """Extracts various sets from a BPMN object."""
    sets = {}
    sets["task_names"] = get_list(bpmn_object, "tasks", "name")
    sets["task_types"] = get_list(bpmn_object, "tasks", "type")
    sets["event_names"] = get_list(bpmn_object, "events", "name")
    sets["event_types"] = get_list(bpmn_object, "events", "type")
    sets["gateway_names"] = get_list(bpmn_object, "gateways", "name")
    sets["gateway_types"] = get_list(bpmn_object, "gateways", "type")

    seq_flow_with_values, mes_flow_with_values = get_flows_with_values(bpmn_object)
    sets["seq_flows_str"] = list(map(lambda e: " ".join(e), seq_flow_with_values))
    sets["mes_flows_str"] = list(map(lambda e: " ".join(e), mes_flow_with_values))

    lanes, lanes_with_refs = get_lanes(bpmn_object)
    sets["lanes"] = lanes
    sets["lanes_with_refs"] = lanes_with_refs

    return sets


def calculate_similarity_scores(
    bpmn_object1, bpmn_object2, method="dice", similarity_threshold=0.7
):
    """Calculates similarity scores for two BPMN instances using dice_SFA."""
    sets1 = extract_bpmn_sets(bpmn_object1)
    sets2 = extract_bpmn_sets(bpmn_object2)

    def safe_similarity_SFA(set1, set2, method, threshold):
        try:
            return similarity_SFA(set1, set2, method=method, threshold=threshold)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0, 0

    def calculate_weighted_score(scores):
        return weighted_score([{"score": score, "weight": weight} for score, weight in scores])

    task_names_sim, task_names_n_union = safe_similarity_SFA(
        sets1["task_names"], sets2["task_names"], method, similarity_threshold
    )

    task_types_sim, task_types_n_union = safe_similarity_SFA(
        sets1["task_types"], sets2["task_types"], method, similarity_threshold
    )

    tasks_overall_sim = calculate_weighted_score(
        [(task_names_sim, task_names_n_union), (task_types_sim, task_types_n_union)]
    )

    event_names_sim, event_names_n_union = safe_similarity_SFA(
        sets1["event_names"], sets2["event_names"], method, similarity_threshold
    )

    event_types_sim, event_types_n_union = safe_similarity_SFA(
        sets1["event_types"], sets2["event_types"], method, similarity_threshold
    )

    events_overall_sim = calculate_weighted_score(
        [(event_names_sim, event_names_n_union), (event_types_sim, event_types_n_union)]
    )

    gateway_names_sim, gateway_names_n_union = safe_similarity_SFA(
        sets1["gateway_names"], sets2["gateway_names"], method, similarity_threshold
    )

    gateway_types_sim, gateway_types_n_union = safe_similarity_SFA(
        sets1["gateway_types"], sets2["gateway_types"], method, similarity_threshold
    )

    gateways_overall_sim = calculate_weighted_score(
        [(gateway_names_sim, gateway_names_n_union), (gateway_types_sim, gateway_types_n_union)]
    )

    sequence_flows_sim, sequence_flows_n_union = safe_similarity_SFA(
        sets1["seq_flows_str"], sets2["seq_flows_str"], method, similarity_threshold
    )

    message_flows_sim, message_flows_n_union = safe_similarity_SFA(
        sets1["mes_flows_str"], sets2["mes_flows_str"], method, similarity_threshold
    )

    flows_overall_sim = calculate_weighted_score(
        [(sequence_flows_sim, sequence_flows_n_union), (message_flows_sim, message_flows_n_union)]
    )

    lanes_without_refs_sim, lanes_without_refs_n_union = safe_similarity_SFA(
        sets1["lanes"], sets2["lanes"], method, similarity_threshold
    )

    lanes_with_refs_sim, lanes_with_refs_n_union = safe_similarity_SFA(
        sets1["lanes_with_refs"], sets2["lanes_with_refs"], method, similarity_threshold
    )

    lanes_overall_sim = calculate_weighted_score(
        [
            (lanes_without_refs_sim, lanes_without_refs_n_union),
            (lanes_with_refs_sim, lanes_with_refs_n_union),
        ]
    )

    overall = calculate_weighted_score(
        [
            (task_names_sim, task_names_n_union),
            (task_types_sim, task_types_n_union),
            (event_names_sim, event_names_n_union),
            (event_types_sim, event_types_n_union),
            (gateway_names_sim, gateway_names_n_union),
            (gateway_types_sim, gateway_types_n_union),
            (sequence_flows_sim, sequence_flows_n_union),
            (message_flows_sim, message_flows_n_union),
            (lanes_without_refs_sim, lanes_without_refs_n_union),
            (lanes_with_refs_sim, lanes_with_refs_n_union),
        ]
    )

    similarity_scores = {
        "overall": overall,
        "tasks_overall": tasks_overall_sim,
        "task_names": task_names_sim,
        "task_types": task_types_sim,
        "events_overall": events_overall_sim,
        "event_names": event_names_sim,
        "event_types": event_types_sim,
        "gateways_overall": gateways_overall_sim,
        "gateway_names": gateway_names_sim,
        "gateway_types": gateway_types_sim,
        "flows_overall": flows_overall_sim,
        "sequence_flows": sequence_flows_sim,
        "message_flows": message_flows_sim,
        "lanes_overall": lanes_overall_sim,
        "lanes_without_refs": lanes_without_refs_sim,
        "lanes_with_refs": lanes_with_refs_sim,
    }
    return similarity_scores, overall


def calculate_similarity_alternative(
    bpmn_object1, bpmn_object2, method="dice", similarity_threshold=0.7
):
    """Calculates similarity scores for two BPMN instances using dice_SFA."""
    sets1 = extract_bpmn_sets(bpmn_object1)
    sets2 = extract_bpmn_sets(bpmn_object2)

    def safe_similarity_SFA(set1, set2, method, threshold):
        try:
            return similarity_SFA(set1, set2, method=method, threshold=threshold)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0, 0

    def calculate_weighted_score(scores):
        return weighted_score([{"score": score, "weight": weight} for score, weight in scores])


    task_names_sim, weight_tn = safe_similarity_SFA(
        sets1["task_names"], sets2["task_names"], method, similarity_threshold
    )

    if weight_tn > 0:
        weight_tn = 1

    # print(f"task_names_sim and w: {task_names_sim, weight_tn}")


    task_types_sim, weight_tt = safe_similarity_SFA(
        sets1["task_types"], sets2["task_types"], method, similarity_threshold
    )
    if weight_tt > 0:
        weight_tt = 1
    # print(f"task_type_sim and w: {task_types_sim, weight_tt}")



    tasks_overall_sim = calculate_weighted_score(
        [(task_names_sim, weight_tn), (task_types_sim, weight_tt)]
    )

    event_names_sim, weight_en = safe_similarity_SFA(
        sets1["event_names"], sets2["event_names"], method, similarity_threshold
    )
    if weight_en > 0:
        weight_en = 1

    # print(f"eventn_sim and w: {event_names_sim, weight_en}")


    event_types_sim, weight_et = safe_similarity_SFA(
        sets1["event_types"], sets2["event_types"], method, similarity_threshold
    )
    if weight_et > 0:
        weight_et = 1
    # print(f"event_type_sim and w: {event_types_sim, weight_et}")


    events_overall_sim = calculate_weighted_score(
        [(event_names_sim, weight_en), (event_types_sim, weight_et)]
    )

    gateway_names_sim, weight_gn = safe_similarity_SFA(
        sets1["gateway_names"], sets2["gateway_names"], method, similarity_threshold
    )
    if weight_gn > 0:
        weight_gn = 1

    # print(f"gnames and w: {gateway_names_sim, weight_gn}")

    gateway_types_sim, weight_gt = safe_similarity_SFA(
        sets1["gateway_types"], sets2["gateway_types"], method, similarity_threshold
    )
    if weight_gt > 0:
        weight_gt = 1
    # print(f"gntypes and w: {gateway_types_sim, weight_gt}")


    gateways_overall_sim = calculate_weighted_score(
        [(gateway_names_sim, weight_gn), (gateway_types_sim, weight_gt)]
    )

    sequence_flows_sim, weight_sf = safe_similarity_SFA(
        sets1["seq_flows_str"], sets2["seq_flows_str"], method, similarity_threshold
    )
    if weight_sf > 0:
        weight_sf = 1
    # print(f"sf and w: {sequence_flows_sim, weight_sf}")

    message_flows_sim, weight_mf = safe_similarity_SFA(
        sets1["mes_flows_str"], sets2["mes_flows_str"], method, similarity_threshold
    )
    if weight_mf > 0:
        weight_mf = 1
    # print(f"mf and w: {message_flows_sim, weight_mf}")


    flows_overall_sim = calculate_weighted_score(
        [(sequence_flows_sim, weight_sf), (message_flows_sim, weight_mf)]
    )

    lanes_without_refs_sim, weight_l = safe_similarity_SFA(
        sets1["lanes"], sets2["lanes"], method, similarity_threshold
    )
    if weight_l > 0:
        weight_l = 1
    # print(f"l and w: {lanes_without_refs_sim, weight_l}")

    lanes_with_refs_sim, weight_lr = safe_similarity_SFA(
        sets1["lanes_with_refs"], sets2["lanes_with_refs"], method, similarity_threshold
    )
    if weight_lr > 0:
        weight_lr = 1
    # print(f"lr and w: {lanes_with_refs_sim, weight_lr}")


    lanes_overall_sim = calculate_weighted_score(
        [
            (lanes_without_refs_sim, weight_l),
            (lanes_with_refs_sim, weight_lr),
        ]
    )

    def calulate_overall_score():

        node_count = 0
        if weight_en + weight_et > 0:
            node_count += 1
        if weight_tn + weight_tt > 0:
            node_count += 1
        if weight_gn + weight_gt > 0:
            node_count += 1
        if weight_l + weight_lr > 0:
            node_count += 1
        if node_count == 0:
            overall = 0
        else:
            overall = 0.5 * (flows_overall_sim) + 0.5/node_count * tasks_overall_sim + \
            0.5/node_count * events_overall_sim + 0.5/node_count * gateways_overall_sim + \
            0.5/node_count * lanes_overall_sim

        return overall



    similarity_scores = {
        "overall": calulate_overall_score(),

        "tasks_overall": tasks_overall_sim,

        "events_overall": events_overall_sim,

        "gateways_overall": gateways_overall_sim,

        "flows_overall": flows_overall_sim,

        "lanes_overall": lanes_overall_sim,

    }
    return similarity_scores
