"""
 This sample shows how to setup and detect device connection lost.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Detect the disconnection of camera
 """

# Import stapipy package
import stapipy as st

EVENT_SELECTOR = "EventSelector"
EVENT_NOTIFICATION = "EventNotification"
EVENT_NOTIFICATION_ON = "On"
TARGET_EVENT_NAME = "DeviceLost"
CALLBACK_NODE_NAME = "EventDeviceLost"

def node_callback(node=None, st_device=None):
    """
    Callback to handle events from GenICam node.

    :param node: node that triggered the callback.
    :param st_device: PyStDevice object passed on at callback registration.
    """
    if node.is_available:
        if st_device.is_device_lost:
            print("OnNodeEvent: {0}: DeviceLost".format(node.display_name))
        else:
            print("OnNodeEvent: {0}: Invalidated".format(node.display_name))


def do_grabbing(st_device):
    """Perform grabbing using the given st_device. """

    # Display DisplayName of the device.
    print('Device=', st_device.info.display_name)

    # Get host side device setting (nodemap)
    st_nodemap = st_device.local_port.nodemap

    # Get EventDeviceLost node
    st_event_node = st_nodemap.get_node(CALLBACK_NODE_NAME)

    # Register callback for EventDeviceLost
    # To ensure the device lost flag is already updated when fired, here we
    # use OutsideLock flag (executed on leaving outside the lock-guarded
    # GenApi node.
    st_event_node.register_callback(node_callback, st_device,
                                    st.EGCCallbackType.OutsideLock)

    # Enable the transmission of the target event
    st_event_selector = st.PyIEnumeration(st_nodemap.get_node(EVENT_SELECTOR))
    st_event_selector.set_symbolic_value(TARGET_EVENT_NAME)

    st_event_notification = \
        st.PyIEnumeration(st_nodemap.get_node(EVENT_NOTIFICATION))
    st_event_notification.set_symbolic_value(EVENT_NOTIFICATION_ON)

    # Start event handling thread
    st_device.start_event_acquisition()

    # Create a datastream object for handling image stream data.
    st_datastream = st_device.create_datastream()

    # Start the image acquisition of the host (local machine) side.
    st_datastream.start_acquisition()

    # Start the image acquisition of the camera side.
    st_device.acquisition_start()

    # A while loop for acquiring data and checking status
    while st_datastream.is_grabbing:
        # Create a localized variable st_buffer using 'with'
        # Warning: if st_buffer is in a global scope, st_buffer must be
        #          cleared to None to allow Garbage Collector release the buffer
        #          properly.
        with st_datastream.retrieve_buffer(5000) as st_buffer:
            # Check if the acquired data contains image data.
            if st_buffer.info.is_image_present:
                # Create an image object.
                st_image = st_buffer.get_image()
                # Display the information of the acquired image data.
                print("BlockID={0} Size={1} x {2} First Byte={3} "
                      "(Unplug the camera to trigger device lost).".format(
                      st_buffer.info.frame_id,
                      st_image.width, st_image.height,
                      st_image.get_image_data()[0]))
            else:
                # If the acquired data contains no image data.
                print("Image data does not exist.")

    # Stop the image acquisition of the camera side
    st_device.acquisition_stop()

    # Stop the image acquisition of the host side
    st_datastream.stop_acquisition()

    # Stop event acquisition thread
    st_device.stop_event_acquisition()


try:
    # Initialize StApi before using.
    st.initialize()

    # Create a system object for device scan and connection.
    # If StApi has not been initialized, StApi will automatically initialize
    # itself.
    st_system = st.create_system()

    device_id = ''

    repeat = True
    while repeat:
        st_device = None
        if device_id == '':
            # Connect to first detected device.
            st_device = st_system.create_first_device()

            # Hold the device ID for re-open
            device_id = st_device.info.device_id
        else:
            # Get the number of interfaces
            interface_count = st_system.interface_count
            for interface_index in range(interface_count):
                st_interface = st_system.get_interface(interface_index)
                try:
                    st_device = st_interface.create_device_by_id(device_id)
                except:
                    pass

        if st_device:
            try:
                do_grabbing(st_device)
            except:
                if not st_device.is_device_lost:
                    raise

        print("0 : Reopen the same device")
        print("    Warning: for GigEVision device, you may need to set the "
              "camera IP to persistent before running this example")
        print("Else : Exit")
        selection = input("Selection :")
        if str(selection) != "0":
            break

except Exception as exception:
    print(exception)
