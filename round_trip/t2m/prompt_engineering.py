
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

