### some helper function to get data from the bpmn_schema or transform it into different formats


from typing import Any, Dict, List, Tuple, Union

from sapsam_mapping import sapsam_mapping
import json


# Define types for better readability

BPMNElement = Dict[str, Any]
BPMNShape = Dict[str, Any]
FlattenedBPMN = Dict[str, List[BPMNElement]]


class BPMNProcessor:
    """This class is used to flatten a Signavio BPMN diagram into a minimal json with the necessary elements found in the BPMN schema file."""

    def __init__(self):

        self.elements: FlattenedBPMN = {
            "tasks": [],
            "events": [],
            "gateways": [],
            "pools": [],
            "messageFlows": [],
            "sequenceFlows": [],
        }

    def extract_element_info(self, shape: BPMNShape, parent_lane: str = "") -> BPMNElement:

        element = {
            "id": shape["resourceId"],
            "name": shape["properties"].get("name", "").replace("\n", " ").strip(),
            "outgoing": shape.get("outgoing", []),
        }

        if parent_lane:
            element["parent_lane"] = parent_lane

        return element

    def process_element(self, shape: BPMNShape, element: BPMNElement, element_type: str):
        if element_type == "Events":
            assert len(shape.get("childShapes", [])) == 0, "Events don't have child shapes"
            element["type"] = shape["stencil"]["id"]
            self.elements["events"].append(element)

        elif element_type == "Activities":
            assert len(shape.get("childShapes", [])) == 0, "Activities don't have child shapes"
            task_type = shape["properties"].get("tasktype", None)

            if task_type == "None":
                task_type = None

            element["type"] = task_type if task_type else shape["stencil"]["id"]
            self.elements["tasks"].append(element)

        elif element_type == "Gateways":
            assert len(shape.get("childShapes", [])) == 0, "Gateways don't have child shapes"

            gateway_type = (
                shape["stencil"]["id"]
                .replace("InclusiveGateway", "Inclusive")
                .replace("Exclusive_Databased_Gateway", "Exclusive")
                .replace("ParallelGateway", "Parallel")
                .replace("EventbasedGateway", "Eventbased")
                .replace("ComplexGateway", "Complex")
            )

            element["type"] = gateway_type

            if not element["name"]:
                del element["name"]

            self.elements["gateways"].append(element)

        elif element_type == "Sequence Flows":
            assert len(shape.get("childShapes", [])) == 0, "Sequence Flows don't have child shapes"
            element["targetRef"] = shape.get("target").get("resourceId")
            name = element.pop("name")

            if name:
                element["condition"] = name
            self.elements["sequenceFlows"].append(element)

        elif element_type == "Message Flows":
            assert len(shape.get("childShapes", [])) == 0, "Message Flows don't have child shapes"
            element["targetRef"] = shape.get("target").get("resourceId")
            name = element.pop("name")

            if name:
                element["label"] = name
            self.elements["messageFlows"].append(element)

        elif element_type == "Pools":
            element["lanes"] = []
            for lane in shape.get("childShapes", []):

                assert (
                    sapsam_mapping[lane["stencil"]["id"]] == "Lanes"
                ), "Pools should only have lanes as children"

                assert (
                    len(lane.get("outgoing", [])) == 0
                ), "Lanes should not have any outgoing elements"

                lane_info = {
                    "id": lane["resourceId"],
                    "name": lane["properties"].get("name", "").strip(),
                }

                element["lanes"].append(lane_info)

                for child in lane.get("childShapes", []):
                    self.flatten_bpmn_rec(child, lane["resourceId"])
            self.elements["pools"].append(element)

    def flatten_bpmn_rec(self, shape: Union[str, BPMNShape], parent_lane: str = ""):
        if isinstance(shape, str):
            shape = json.loads(shape)

        try:
            element = self.extract_element_info(shape, parent_lane)

        except:
            print("Error in shape: ", shape["stencil"]["id"])

        element_type = sapsam_mapping[shape["stencil"]["id"]]

        if element_type == "Diagram":
            for shapeRec in shape.get("childShapes", []):
                self.flatten_bpmn_rec(shapeRec)

        else:
            self.process_element(shape, element, element_type)

    def polish_schema(self, flatted_bpmn: FlattenedBPMN):
        for flow in flatted_bpmn.get("sequenceFlows", []) + flatted_bpmn.get("messageFlows", []):
            for list in flatted_bpmn.values():
                for item in list:
                    for outgoing in item.get("outgoing", []):
                        if flow.get("id") == outgoing.get("resourceId"):
                            flow["sourceRef"] = item.get("id")

        for list in flatted_bpmn.values():
            for item in list:
                item.pop("outgoing", None)

        for pool in flatted_bpmn.get("pools", []):
            for lane in pool.get("lanes", []):
                elementRefs = [
                    item.get("id")
                    for list in flatted_bpmn.values()
                    for item in list
                    if lane.get("id") == item.get("parent_lane", "")
                ]

                lane["elemRefs"] = elementRefs

        for list in flatted_bpmn.values():
            for item in list:
                item.pop("parent_lane", None)


def get_element_by_id_from_sublist(bpmn_sublist, id):
    """Returns the element with the passed id. Takes a bpmn sublist like tasks, events, ect. as an argument."""
    for item in bpmn_sublist:
        if item.get("id", "") == id:
            return item
    return ""


def get_flows_with_values(bpmn_instance):
    """Returns sequence and message flows. Replaces the ids with the names (for tasks, events and pools) or types (for gateways) of the references"""

    def get_ref_value(ref_id):
        task_or_event_or_pool = get_element_by_id_from_sublist(
            bpmn_instance["tasks"] + bpmn_instance["events"] + bpmn_instance["pools"], ref_id
        )
        if task_or_event_or_pool:
            return task_or_event_or_pool.get("name", "")
        else:
            gateway = get_element_by_id_from_sublist(bpmn_instance["gateways"], ref_id)
            if gateway:
                return gateway.get("type", "")
            else:
                return ""

    sequence_flows_with_values = []
    for sequence_flow in bpmn_instance["sequenceFlows"]:
        sourceValue = get_ref_value(sequence_flow["sourceRef"])
        targetValue = get_ref_value(sequence_flow["targetRef"])
        sequence_flows_with_values.append(
            [sourceValue, sequence_flow.get("condition", ""), targetValue]
        )

    message_flows_with_values = []
    for sequence_flow in bpmn_instance["messageFlows"]:
        sourceValue = get_ref_value(sequence_flow["sourceRef"])
        targetValue = get_ref_value(sequence_flow["targetRef"])
        message_flows_with_values.append(
            [sourceValue, sequence_flow.get("message", ""), targetValue]
        )

    return sequence_flows_with_values, message_flows_with_values


def get_name_by_id(bpmn_instance, id):
    """Returns the name of the element with the passed id"""
    for list in bpmn_instance.values():
        for item in list:
            if item.get("id", "") == id:
                return item.get("name", "")
    return ""


def get_lanes(bpmn_instance):
    """Returns two lists: lanes_name and lanes_with_refs.
    lanes_name is a list of names from the lanes, where the pool and lane name are concatinated.
    lanes_with_refs has the references concatinated as well. Thereby the reference ids are replaced with the names (for tasks, events and pools)
    or types (for gateways) of the references.
    """

    # helper function
    def get_ref_value_from_task_or_event_or_gateway(bpmn_instance, ref_id):
        task_or_event = get_element_by_id_from_sublist(
            bpmn_instance["tasks"] + bpmn_instance["events"], ref_id
        )
        if task_or_event:
            return task_or_event.get("name", "")
        else:
            gateway = get_element_by_id_from_sublist(bpmn_instance["gateways"], ref_id)
            if gateway:
                return gateway.get("type", "")
            else:
                return ""

    lanes_name = []
    lanes_with_refs = []
    for pool in bpmn_instance["pools"]:
        lanes = pool["lanes"]
        if not lanes:
            lanes_name.append(pool["name"])
        for lane in lanes:
            lane_and_pool_name = pool.get("name", "") + " - " + lane.get("name", "")
            lanes_name.append(lane_and_pool_name)
            for ref in lane.get("elemRefs", []):
                ref_value = get_ref_value_from_task_or_event_or_gateway(bpmn_instance, ref)
                lanes_with_refs.append(f"{lane_and_pool_name} - {ref_value}")

    return lanes_name, lanes_with_refs


def get_tasks_events_gateways_only(bpmn_instance):
    """Returns the task, event and gateway lists of the bpmn_instance"""
    return {
        "tasks": bpmn_instance["tasks"],
        "events": bpmn_instance["events"],
        "gateways": bpmn_instance["gateways"],
    }


def get_tasks_events_gateways_pools_only(bpmn_instance):
    """Returns the task, event and gateway and pool lists of the bpmn_instance"""
    return {
        "tasks": bpmn_instance["tasks"],
        "events": bpmn_instance["events"],
        "gateways": bpmn_instance["gateways"],
        "pools": bpmn_instance["pools"],
    }


def get_seq_and_mes_flow_only(bpmn_instance):
    """Returns the seuqnec and message flow lists of the bpmn_instance"""
    return {
        "sequenceFlows": bpmn_instance["sequenceFlows"],
        "messageFlows": bpmn_instance["messageFlows"],
    }
