mermaid = """
Rules for mermaid js flowcharts:
The graph must use the LR (Left to Right) direction.
Each mermaid js node must have the following structure:
id:type:shape and text
    id - it is a unique identifier. Integer from 1 to n. Each node has a unique identifier
    type - defines the type of the element regarding to BPMN 2.0 notation.
        possible types are: start event, end event, task, exclusive gateway and parallel gateway.
        Based on the type of the node following shapes and texts are to be used:
        startevent: ((startevent))     i.e., id:startevent:((startevent))
        endevent: ((endevent))	     i.e., id:endevent:((endevent))
        task: (task label)             i.e., id:task:(task label)
        exclusivegateway: {x}          i.e., id:exclusivegateway:{x}
        parallelgateway: {AND}         i.e., id:exclusivegateway:{AND}

All nodes that have occurred more than once should have following structure: id:type: (i.e., 2:task: ) by further occurrence.
It is strictly prohibited to use only id (i.e. 2) as a reference.

    all elements are connected with each other with the help of the direction.
        direction: -->
    if there are some conditions or annotations it is necessary to use text on links (i.e., edge labels)
        edge label: |condition or annotation|
    edge label is always located between 2 nodes: id:exclusivegateway:{x} --> |condition or annotation|id:task:(task label)
"""

graphviz = """
Graphviz rules:
Each graph must have LR (Left to Right) direction and consists of nodes and edges.
Each node has following structure: "name"[attributes]
There are 5 diferent types of nodes: start event, end event, task, exclusive gateway and parallel gateway.
Each node has its specific attributes based on the type of the node.
  start node:        "start_1"[shape=circle label=""];
  end node:          "end_1"[shape=doublecircle label=""];
In both start and end nodes labels are always empty.
  task:              "task label"[shape=rectangle];
Task labels are always unique.
  exclusive gateway: "seg_1"[shape=diamond label="X"];
  parallel gateway:  "spg_1"[shape=diamond label="AND"];

Gateways are not tasks, they just indicate that the control flow of the process is splitted or merged.
Following names "seg_1" and "meg_1" should be used for splitting and merging exclusive gateways.
Following names "spg_1" and "mpg_1" should be used for splitting and merging parallel gateways.

Each time when new start, end or gateways node is used, the counter should be incrimented at 1.

all elements are connected with each other with the help of the edges.
  edge: ->
examples:
"start" -> "task 1"
"task 1" -> "task 2"

if there are some conditions or annotations it is necessary to use text on links (i.e., edge labels)
    edge label:  "task 1" -> "task 2"[label="condition 1"]
"""

json_format = """
To create a JSON representation of a BPMN2.0 process, follow these guidelines:
1. Define the Process Elements:
    Tasks: Represent each activity or step in the process as a task. Include the following properties:
        id: A unique identifier for the task.
        name: A brief description of the task.
        type: The type of task, such as "User", "Service", "Manual", etc.

    Events: Define the start and end points of the process as events. Include:
        id: A unique identifier for the event.
        name: The name of the event (e.g., "start", "end").
        type: The type of event, such as "StartNoneEvent" for a start event, or "EndNoneEvent" for a simple end event.

    Gateways: If decisions or splits in the process occur, define gateways. Include:
        id: A unique identifier for the gateway.
        name: A brief description of the decision point.
        type: The type of gateway, such as "Exclusive" or "Parallel".

    Pools: If the process involves multiple participants or organizations, define pools. Include:
        id: A unique identifier for the pool.
        name: The name of the participant or organization.
        Lanes: Define Lanes within Each Pool if necessary:
            Assign a unique id and name for each lane.
            Include elemRefs to list all the ids of the elements (tasks, events, etc.) that are part of the lane.

2. Define the Sequence Flows:
    Sequence Flows: Indicate the flow or order of tasks and events. For each sequence flow, include:
        id: A unique identifier for the sequence flow.
        sourceRef: The id of the element where the flow starts.
        targetRef: The id of the element where the flow ends.

3. Define the Message Flows (if needed):
    Message Flows: If the process involves communication between different participants (across pools), define message flows. Include:
        id: A unique identifier for the message flow.
        sourceRef: The id of the element sending the message.
        targetRef: The id of the element receiving the message.

4. Structure the JSON:
    Whole json should be a dictionary with followings keys:
    tasks, events, gateways, pools, sequenceFlows, messageFlows
Return only json object and nothing else.
"""

json_desc= """
***Guidelines***
1. Define the Process Elements:
    Tasks: Represent individual units of work or steps within a process.
      Each task encapsulates a specific activity performed by either a participant or system:.

        id: A unique identifier for the task. (ex: id1, id2, etc.)
        name: A brief description of the task. (ex: "Approve Loan Application")
        type: The type of task, such as "User", "Service", "Manual", etc.
        (A "User" task is performed by a human, a "Manual" task is conducted without software
        or system intervention, often performed manually and etc)

    Events: Define the start and end points of the process as events. Include:

        id: A unique identifier for the event.
        name: The name of the event (e.g., "start", "end").
        type: The type of event, such as "StartNoneEvent" for a start event, or "EndNoneEvent" for a simple end event.

    Gateways: When there are decision points in the process, define gateways. Include:

        id: A unique identifier for the gateway.
        name: A brief description of the decision point.(optional)
        type: The type of gateway, such as "Exclusive" or "Parallel".(required)

    Pools: represent distinct participants or entities in a process, such as different organizations or departments.
        pools act as a container for the entire process flow for that participant, defining its boundaries.
        Each pool may have one or multiple lanes. Lanes are subdivisions within pools that organize tasks, events, and other
        elements based on specific roles within a participant.

            id: A unique identifier for the pool.
            name: The name of the pool.
            Lanes: Define Lanes within Each Pool if necessary:
                Assign a unique id and name for each lane.
                Include elemRefs to list all the ids of the elements (tasks, events, etc.) that are within the lane.
        (ex: In a scenario where a customer goes to a bank, Pools could be: "Customer" and "Bank"
            lanes in the "Bank" pool could be: "Teller" and "loan department")

        If the textual descripton does not mention the entities or participant involved explicitely, output an empty list for pools.
2. Define the Sequence Flows (required):
    Sequence Flows: Indicate the flow or order of tasks, events, gateways etc. For each sequence flow, include:

        id: A unique identifier for the sequence flow.
        sourceRef: The id of the element where the flow starts.
        targetRef: The id of the element where the flow ends.

3. Define the Message Flows (if needed):
    Message Flows: If the process involves communication between different pools, define message flows. Include:

        id: A unique identifier for the message flow.
        sourceRef: The id of the element sending the message.
        targetRef: The id of the element receiving the message.

4. Structure the JSON:
    Whole json should be a dictionary with the followings keys:
    tasks, events, gateways, pools, sequenceFlows, messageFlows
Return only a json object with double quotes and use no code formatting.
"""

