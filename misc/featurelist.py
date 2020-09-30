"""
 This sample will list all support functions of connected camera.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Access Nodes of NodeMap for displaying camera's features
"""

import stapipy as st


def display_nodes(node):
    """
    Function to display node

    :param node: node to display
    """
    if not node.is_implemented:
        return
    # Display the interface type and name
    print("{0} : {1}".format(node.principal_interface_type.name, node.name))
    if node.principal_interface_type == st.EGCInterfaceType.ICategory:
        # Display all the features that belong to the category
        feature_list = st.PyICategory(node).feature_list
        for feature in feature_list:
            display_nodes(feature)
    elif node.principal_interface_type == st.EGCInterfaceType.IEnumeration:
        # Display all entries if the type is Enumeration
        entry_list = st.PyIEnumeration(node).entries
        for entry in entry_list:
            display_nodes(entry)

try:
    # Initialize StApi before using.
    st.initialize()

    # Create a system object for device scan and connection.
    st_system = st.create_system()

    # Connect to first detected device.
    st_device = st_system.create_first_device()

    # Display DisplayName of the device.
    print('Device=', st_device.info.display_name)

    # Display nodes
    display_nodes(st_device.remote_port.nodemap.get_node("Root"))

except Exception as exception:
    print(exception)
