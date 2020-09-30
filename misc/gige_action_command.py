"""
 This sample shows how to use GigE Action command.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to GigE camera
 - Set and send action command
"""

import time
import stapipy as st

DEVICE_KEY = 0x12345678
GROUP_KEY = 0x00000001
GROUP_MASK = 0xFFFFFFFF
SCHEDULED_TIME_ENABLE = False

scheduled_time = 0


class CActionCommandEvent:
    def __init__(self, iface):
        self.iface = iface
        self.callback_func_sent = self.on_command_sent
        self.callback_func_recv = self.on_ack_received

        nodemap = self.iface.port.nodemap
        self.event_action_cmd = nodemap.get_node("EventActionCommand")
        self.cb_command_sent = self.event_action_cmd.register_callback(
            self.callback_func_sent, self.iface, st.EGCCallbackType.OutsideLock)

        self.event_action_cmd_req_id = \
            nodemap.get_node("EventActionCommandRequestID")

        self.event_action_cmd_ack = \
            nodemap.get_node("EventActionCommandAcknowledge")
        self.cb_ack_received = self.event_action_cmd_ack.register_callback(
            self.callback_func_recv, self.iface, st.EGCCallbackType.OutsideLock)

        self.event_action_cmd_ack_src_ip = \
            nodemap.get_node("EventActionCommandAcknowledgeSourceIPAddress")
        self.event_action_cmd_ack_status = \
            nodemap.get_node("EventActionCommandAcknowledgeStatus")
        self.event_action_cmd_ack_id = \
            nodemap.get_node("EventActionCommandAcknowledgeAcknowledgeID")

        self.gev_action_dest_ip = \
            nodemap.get_node("GevActionDestinationIPAddress")

    def __del__(self):
        self.event_action_cmd.deregister_callbacks()
        self.event_action_cmd_ack.deregister_callbacks()

    def on_command_sent(self, node, context):
        """Callback function triggered when action command is sent."""
        print("Sent action command[{0}]: {1}".format(
            self.event_action_cmd_req_id.value,
            self.gev_action_dest_ip.get().to_string()
        ))

    def on_ack_received(self, node, context):
        """Callback function triggered when action command ack is received."""
        print("Received action command[{0}] : {1}({2})".format(
            self.event_action_cmd_ack_id.value,
            self.event_action_cmd_ack_src_ip.get().to_string(),
            self.event_action_cmd_ack_status.get().current_entry.display_name
        ))


class CActionCommandInterface:
    def __init__(self, iface):
        self._iface = iface
        self._action_cmd_event = CActionCommandEvent(self._iface)
        nodemap = self._iface.port.nodemap
        self.action_cmd = nodemap.get_node("ActionCommand")

    def get_interface(self):
        return self._iface

    def execute(self):
        self.action_cmd.get().execute()


def send_action_command(action_interfaces):
    """Send action command."""
    while True:
        selection = input("Input (0: Action Command, 1: Exit) : ")
        if selection == "0":
            for item in action_interfaces:
               item.execute()
            time.sleep(0.5)
        elif selection == '1':
            break


def adjust_gev_scpd(device_list):
    """Adjust GevSCPD for the devices in the device_list."""
    packet_size = device_list[0].remote_port.nodemap.get_node(
        "GevSCPSPacketSize")
    if packet_size is None:
        return

    timestamp_latch = device_list[0].remote_port.nodemap.get_node(
        "TimestampLatchValue")
    if timestamp_latch is None:
        return

    max_bps = 100000000
    each_packet_time_ns = packet_size.value * 1000000000 * \
                          (len(device_list) - 1) / max_bps
    timestamp_unit = timestamp_latch.get().inc
    if timestamp_unit == 0:
        timestamp_unit = 40
    for device in device_list:
        device.remote_port.nodemap.get_node("GevSCPD").value = \
            each_packet_time_ns / timestamp_unit


def datastream_callback(handle=None, context=None):
    """
    Callback to handle events from DataStream.

    :param handle: handle that trigger the callback.
    :param context: user data passed on during callback registration.
    """
    st_datastream = handle.module
    if st_datastream:
        with st_datastream.retrieve_buffer() as st_buffer:
            # Check if the acquired data contains image data.
            if st_buffer.info.is_image_present:
                # Create an image object.
                st_image = st_buffer.get_image()
                # Display the information of the acquired image data.
                print("BlockID={0} Size={1} x {2} First Byte={3}".format(
                      st_buffer.info.frame_id,
                      st_image.width, st_image.height,
                      st_image.get_image_data()[0]))
            else:
                # If the acquired data contains no image data.
                print("Image data does not exist.")


def set_device_action_cmd_param(device):
    """Set device action command parameters."""
    nodemap = device.remote_port.nodemap
    trigger_selector = nodemap.get_node("TriggerSelector").get()
    trigger_selector.set_symbolic_value("FrameStart")
    print(" TriggerSelector = FrameStart")

    trigger_mode = nodemap.get_node("TriggerMode").get()
    trigger_mode.set_symbolic_value("On")
    print(" TriggerMode = On")

    trigger_source = nodemap.get_node("TriggerSource").get()
    trigger_source_list = ["Action0", "Action1"]
    for trigger_src_name in trigger_source_list:
        try:
            trigger_source.set_symbolic_value(trigger_src_name)
            print(" TriggerSource =", trigger_src_name)
            break
        except st.PyStError:
            pass

    action_device_key = nodemap.get_node("ActionDeviceKey")
    action_device_key.value = DEVICE_KEY
    print(" ActionDeviceKey =", hex(DEVICE_KEY))

    action_selector = nodemap.get_node("ActionSelector")
    action_selector.value = action_selector.get().min
    print(" ActionSelector =", action_selector.get().min)

    action_group_key = nodemap.get_node("ActionGroupKey")
    action_group_key.value = GROUP_KEY
    print(" ActionGroupKey =", hex(GROUP_KEY))

    action_group_mask = nodemap.get_node("ActionGroupMask")
    action_group_mask.value = GROUP_MASK
    print(" ActionGroupMask =", hex(GROUP_MASK))


def set_host_action_cmd_param(iface):
    """Set host action command parameters."""
    nodemap = iface.port.nodemap
    event_selector = nodemap.get_node("EventSelector").get()
    event_notification = nodemap.get_node("EventNotification").get()

    event_names = ["ActionCommand", "ActionCommandAcknowledge"]
    for item in event_names:
        event_selector.set_symbolic_value(item)
        print(" EventSelector =", item)
        event_notification.set_symbolic_value("On")
        print(" EventNotification = On")

    action_device_key = nodemap.get_node("ActionDeviceKey")
    action_device_key.value = DEVICE_KEY
    print(" ActionDeviceKey =", hex(DEVICE_KEY))

    action_group_key = nodemap.get_node("ActionGroupKey")
    action_group_key.value = GROUP_KEY
    print(" ActionGroupKey =", hex(GROUP_KEY))

    action_group_mask = nodemap.get_node("ActionGroupMask")
    action_group_mask.value = GROUP_MASK
    print(" ActionGroupMask =", hex(GROUP_MASK))

    action_scheduled_time_enable = nodemap.get_node("ActionScheduledTimeEnable")
    action_scheduled_time_enable.value = SCHEDULED_TIME_ENABLE
    print(" ActionScheduledTimeEnable =", SCHEDULED_TIME_ENABLE)
    if SCHEDULED_TIME_ENABLE:
        action_scheduled_time = nodemap.get_node("ActionScheduledTime")
        action_scheduled_time.value = scheduled_time
        print(" ActionScheduledTIme =", scheduled_time)


if __name__ == "__main__":
    try:
        # Initialize StApi before using.
        st.initialize()

        # Create a system object for device scan and connection.
        st_system = st.create_system(st.EStSystemVendor.Default,
                                     st.EStInterfaceType.GigEVision)

        st_action_interfaces = []

        # Check if there is no GigE device, raise Exception.
        for index in range(st_system.interface_count):
            iface = st_system.get_interface(index)
            try:
                iface_subnet_ip = iface.port.nodemap.get_node(
                    "GevInterfaceSubnetIPAddress").get()
                print("Interface {0} = {1} [{2}]".format(
                    index, iface.info.display_name,
                    iface_subnet_ip.to_string()))
                set_host_action_cmd_param(iface)
                iface.start_event_acquisition()
                action_interface = CActionCommandInterface(iface)
                st_action_interfaces.append(action_interface)
            except Exception as exception:
                print("An exception occurred.", exception)

        if len(st_action_interfaces) == 0:
            raise RuntimeError("There is no GigE interface found.")

        # Try to connect to all possible device:
        st_devices = []
        st_datastreams = []
        while True:
            try:
                st_devices.append(st_system.create_first_device())
            except:
                if len(st_devices) == 0:
                    raise
                break

            # Display the DisplayName of the device.
            print("Device {0} = {1} [{2}]".format(len(st_devices),
                  st_devices[len(st_devices)-1].info.display_name,
                  st_devices[len(st_devices)-1].local_port.nodemap.get_node(
                      "GevDeviceIPAddress").get().to_string()))

            # Set action command parameter.
            set_device_action_cmd_param(st_devices[len(st_devices)-1])

            # Create a DataStream object.
            st_datastreams.append(
                st_devices[len(st_devices)-1].create_datastream())

            # Register callback for grabbing.
            st_datastreams[len(st_datastreams)-1].register_callback(
                datastream_callback)

        # Start the image acquisition of the host side.
        for datastream in st_datastreams:
            datastream.start_acquisition()

        # Start the image acquisition of the camera side.
        for device in st_devices:
            device.acquisition_start()

        # Adjust GevSCPD and send action command.
        adjust_gev_scpd(st_devices)
        send_action_command(st_action_interfaces)

        # Stop the image acquisition of the camera side.
        for device in st_devices:
            device.acquisition_stop()

        # Stop the image acquisition of the host side.
        for datastream in st_datastreams:
            datastream.stop_acquisition()

        # Stop event acquisition thread.
        for action_interface in st_action_interfaces:
            action_interface.get_interface().stop_event_acquisition()

    except Exception as exception:
        print(exception)
