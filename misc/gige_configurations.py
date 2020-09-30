"""
 This sample shows how to setup the IP address and heartbeat timeout of GigE camera.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Acquire image data
 - Check and update IP address of GigE camera
 - Update heartbeat timeout of GigE camera
"""

import time
import ipaddress
import stapipy as st

# Number of images to grab
number_of_images_to_grab = 100

# Feature names
GEV_INTERFACE_SUBNET_IP_ADDRESS = "GevInterfaceSubnetIPAddress"
GEV_INTERFACE_SUBNET_MASK = "GevInterfaceSubnetMask"

DEVICE_SELECTOR = "DeviceSelector"
GEV_DEVICE_IP_ADDRESS = "GevDeviceIPAddress"
GEV_DEVICE_SUBNET_MASK = "GevDeviceSubnetMask"

GEV_DEVICE_FORCE_IP_ADDRESS = "GevDeviceForceIPAddress"
GEV_DEVICE_FORCE_SUBNET_MASK = "GevDeviceForceSubnetMask"
GEV_DEVICE_FORCE_IP = "GevDeviceForceIP"
DEVICE_LINK_HEARTBEAT_TIMEOUT = "DeviceLinkHeartbeatTimeout"
GEV_HEARTBEAT_TIMEOUT = "GevHeartbeatTimeout"


def update_device_ip_address(nodemap):
    """
    Function for checking and updating device IP address.

    :param nodemap: node map of the device.
    """
    # Display the IP address of the host side.
    iface_ip = nodemap.get_node(GEV_INTERFACE_SUBNET_IP_ADDRESS).get()
    print("Interface IP address =", iface_ip.to_string())

    # Display the subnet mask of the host side.
    iface_mask = nodemap.get_node(GEV_INTERFACE_SUBNET_MASK).get()
    print("Interface Subnet mask =", iface_mask.to_string())

    while True:
        # Select the first device.
        device_selector = nodemap.get_node(DEVICE_SELECTOR)
        device_selector.value = 0

        # Display the current IP address of the device.
        device_ip = nodemap.get_node(GEV_DEVICE_IP_ADDRESS).get()
        print("Device IP Address =", device_ip.to_string())

        # Display the current subnet mask of the device.
        device_mask = nodemap.get_node(GEV_DEVICE_SUBNET_MASK).get()
        print("Device Subnet Mask =", device_mask.to_string())

        new_ip_str = input("Input new device IP address (x.x.x.x) : ")
        new_ip_int = int(ipaddress.ip_address(new_ip_str))
        iface_ip_int = iface_ip.value
        iface_mask_int = iface_mask.value

        # Ensure the subnet address of the host and the device are matched
        # and the host and the device have different IP address.
        if (iface_ip_int & iface_mask_int) == (new_ip_int & iface_mask_int)\
                and iface_ip_int != new_ip_int:
            # Specify the new ip address of the device.
            force_ip = nodemap.get_node(GEV_DEVICE_FORCE_IP_ADDRESS)
            force_ip.value = new_ip_int

            # Specify the new subnet mask of the device.
            force_mask = nodemap.get_node(GEV_DEVICE_FORCE_SUBNET_MASK)
            force_mask.value = iface_mask_int

            # Update the device setting.
            force_ip_cmd = nodemap.get_node(GEV_DEVICE_FORCE_IP).get()
            force_ip_cmd.execute()
            return


def update_heartbeat_timeout(nodemap):
    """
    Function for reading and updating heartbeat timeout.

    :param nodemap: nodemap of the device.
    """
    while True:
        heartbeat = nodemap.get_node(DEVICE_LINK_HEARTBEAT_TIMEOUT).get()
        if heartbeat:
            unit = "[us]"
        else:
            heartbeat = nodemap.get_node(GEV_HEARTBEAT_TIMEOUT).get()
            if heartbeat:
                unit = "[ms]"
            else:
                print("Unable to get the current heartbeat value")
                return

        print()
        print("Warning: the heartbeat sending interval is fixed when the device "
              "is initialized (opened).")
        print("Thus, changing the heartbeat timeout smaller than the current "
              "value may cause timeout.")
        print("In practical situation, please either set environment variable "
              "STGENTL_GIGE_HEARTBEAT before opening the device")
        print("or re-open the device after changing the heartbeat value without "
              "setting the environment variable and debugger.")
        print()
        print("Current Heartbeat Timeout%s=%.4f" % (unit, heartbeat.value))

        # Update the HeartbeatTimeout setting.
        new_heartbeat = input("Input new Heartbeat Timeout"+unit+":")
        heartbeat.from_string(new_heartbeat)
        return


def create_ist_device_by_ip(pinterface, ip_address) -> st.PyStDevice:
    """
    Function to connect to device based on the given ip address.

    :param pinterface PyStDevice: interface of the device.
    :param ip_address: IP address of the device in integer.
    :return: connected device (PyStDevice).
    """
    pinterface.update_device_list()
    iface_nodemap = pinterface.port.nodemap
    device_selector = iface_nodemap.get_node("DeviceSelector").get()
    max_index = device_selector.max
    device_ip = iface_nodemap.get_node("GevDeviceIPAddress")
    for index in range(max_index+1):
        device_selector.value = index
        if device_ip.is_available:
            if device_ip.value == ip_address:
                return pinterface.create_device_by_index(index)
    return None


if __name__ == "__main__":
    try:
        # Initialize StApi before using.
        st.initialize()

        # Create a system object for device scan and connection only for GigE.
        st_system = st.create_system(st.EStSystemVendor.Default,
                                     st.EStInterfaceType.GigEVision)
        for index in range(st_system.interface_count):
            st_interface = st_system.get_interface(index)
            if st_interface.device_count > 0:
                break

        # Update the IP address setting of the first detected GigE device.
        update_device_ip_address(st_interface.port.nodemap)

        # Get the updated IP address
        device_force_ip = st_interface.port.nodemap\
            .get_node(GEV_DEVICE_FORCE_IP_ADDRESS)

        # Create a camera device object and connect.
        st_device = None
        for loop in range(30):
            time.sleep(1)
            st_device = create_ist_device_by_ip(st_interface,
                                                device_force_ip.value)
            if st_device:
                break
        if st_device is None:
            raise Exception("A device ip IP address {0} could not be found"\
                            .format(device_force_ip.get().to_string()))

        # Display DisplayName of the device.
        print('Device=', st_device.info.display_name)

        # Update the HeartBeatTimeout settings.
        update_heartbeat_timeout(st_device.remote_port.nodemap)

        # Create a datastream object for handling image stream data.
        st_datastream = st_device.create_datastream()

        # Start the image acquisition of the host (local machine) side.
        st_datastream.start_acquisition(number_of_images_to_grab)

        # Start the image acquisition of the camera side.
        st_device.acquisition_start()

        # A while loop for acquiring data and checking status
        while st_datastream.is_grabbing:
            # Create a localized variable st_buffer using 'with'
            # Warning: if st_buffer is in a global scope, st_buffer must be
            # assign to None to allow Garbage Collector release the buffer
            # properly.
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

        # Stop the image acquisition of the camera side
        st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        st_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)
