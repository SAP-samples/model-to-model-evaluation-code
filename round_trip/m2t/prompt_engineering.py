bpmn_desc = """
    Tasks: Represent each activity or step in the process. They may include name and type.
    Events: They define the start and end points of the process. They may include name and type.
    Gateways: They define decision points or splits in the process, define gateways. They may include name and type.
    Events: They define the start and end points of the process as events. They may include name and type.
    Pools: If the process involves multiple participants or organizations, they are referred to as pools.
    They can include multiple lanes. Lanes can refer to other elements in the process such as tasks and events.
    Sequence Flows: Indicate the flow or order of tasks and events. They include a source and target element.
    Message Flows: If the process involves communication between different participants (across pools), message flows are defined.
    They include a source and target element.
    All the above elements have unique ids.
"""
