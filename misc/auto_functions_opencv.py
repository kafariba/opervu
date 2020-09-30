"""
 This sample demostrates how to set AWB, AGC, and AE function.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Register and use callback function with StApi
 - Acquire image via callback function
 - Set AWB, AGC, AE
 - Copy image data for OpenCV
 - Convert Bayer image format to RGB using OpenCV
 - Preview image using OpenCV
 Note: opencv-python and numpy packages are required:
    pip install numpy
    pip install opencv-python
"""

import cv2
import threading
import numpy as np
import stapipy as st

# Image scale when displaying using OpenCV.
DISPLAY_RESIZE_FACTOR = 0.3

# Feature names
EXPOSURE_AUTO = "ExposureAuto"
GAIN_AUTO = "GainAuto"
BALANCE_WHITE_AUTO = "BalanceWhiteAuto"

AUTO_LIGHT_TARGET = "AutoLightTarget"
GAIN = "Gain"
GAIN_RAW = "GainRaw"

EXPOSURE_MODE = "ExposureMode"
EXPOSURE_TIME = "ExposureTime"
EXPOSURE_TIME_RAW = "ExposureTimeRaw" # Custom

BALANCE_RATIO_SELECTOR = "BalanceRatioSelector"
BALANCE_RATIO = "BalanceRatio"


class CMyCallback:
    """
    Class that contains a callback function.
    """

    def __init__(self):
        self._image = None
        self._lock = threading.Lock()

    @property
    def image(self):
        """Property: return PyIStImage of the grabbed image."""
        duplicate = None
        self._lock.acquire()
        if self._image is not None:
            duplicate = self._image.copy()
        self._lock.release()
        return duplicate

    def datastream_callback(self, handle=None, context=None):
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

                    # Check the pixelformat of the input image.
                    pixel_format = st_image.pixel_format
                    pixel_format_info = st.get_pixel_format_info(pixel_format)

                    # Only mono or bayer is processed.
                    if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
                        return

                    # Get raw image data.
                    data = st_image.get_image_data()

                    # Perform pixel value scaling if each pixel component is
                    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                    if pixel_format_info.each_component_total_bit_count > 8:
                        nparr = np.frombuffer(data, np.uint16)
                        division = pow(2, pixel_format_info
                                       .each_component_valid_bit_count - 8)
                        nparr = (nparr / division).astype('uint8')
                    else:
                        nparr = np.frombuffer(data, np.uint8)

                    # Process image for display.
                    nparr = nparr.reshape(st_image.height, st_image.width, 1)

                    # Perform color conversion for Bayer.
                    if pixel_format_info.is_bayer:
                        bayer_type = pixel_format_info.get_pixel_color_filter()
                        if bayer_type == st.EStPixelColorFilter.BayerRG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGR:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGB:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerBG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                    # Resize image and store to self._image.
                    nparr = cv2.resize(nparr, None,
                                       fx=DISPLAY_RESIZE_FACTOR,
                                       fy=DISPLAY_RESIZE_FACTOR)
                    self._lock.acquire()
                    self._image = nparr
                    self._lock.release()


def edit_enumeration(nodemap, enum_name):
    """
    Display and allow user to modify the enumeration value.

    :param nodemap: node map.
    :param enum_name: name of the enumeration node.
    """
    node = nodemap.get_node(enum_name)
    if not node.is_writable:
        return

    # Cast to PyIEnumeration from PyNode
    enum_node = st.PyIEnumeration(node)

    while True:
        print(enum_name)
        enum_entries = enum_node.entries
        for index in range(len(enum_entries)):
            enum_entry = enum_entries[index]
            if enum_entry.is_available:
                print("{0} : {1} {2}".format(index,
                      st.PyIEnumEntry(enum_entry).symbolic_value,
                      "(Current)" if enum_node.value == enum_entry.value
                                             else ""))
        selection = int(input("Select : "))
        if selection < len(enum_entries):
            enum_entry = enum_entries[selection]
            enum_node.set_int_value(enum_entry.value)
            break


def edit_setting(nodemap, node_name):
    """
    Edit setting which has numeric type.

    :param nodemap:  Node map.
    :param node_name: Node name.
    """
    node = nodemap.get_node(node_name)
    if not node.is_writable:
        return
    if node.principal_interface_type == st.EGCInterfaceType.IFloat:
        node_value = st.PyIFloat(node)
    elif node.principal_interface_type == st.EGCInterfaceType.IInteger:
        node_value = st.PyIInteger(node)
    while True:
        print(node_name)
        print(" Min={0} Max={1} Current={2}{3}".format(
              node_value.min, node_value.max, node_value.value,
              " Inc={0}".format(node_value.inc) if\
                    node_value.inc_mode == st.EGCIncMode.FixedIncrement\
                    else ""))
        new_value = input("New value : ")
        print()
        if node.principal_interface_type == st.EGCInterfaceType.IFloat:
            new_numeric_value = float(new_value)
        else:
            new_numeric_value = int(new_value)
        if node_value.min <= new_numeric_value <= node_value.max:
            node_value.value = new_numeric_value
            return


def edit_enum_setting(nodemap, enum_name, numeric_name):
    """
    Display the contents of the current enumeration node and edit settings.

    :param nodemap: Node map.
    :param enum_name: Enumeration name.
    :param numeric_name: Numeric name.
    """
    node = nodemap.get_node(enum_name)
    if not node.is_writable:
        return

    enum_node = st.PyIEnumeration(node)
    enum_entries = enum_node.entries
    for index in range(len(enum_entries)):
        enum_entry = enum_entries[index]
        if enum_entry.is_available:
            enum_node.value = enum_entry.value
            print("{0} = {1}".format(enum_name,
                  st.PyIEnumEntry(enum_entry).symbolic_value))
            edit_setting(nodemap, numeric_name)


def exposure_auto(nodemap):
    """Configure exposure using the given nodemap."""
    # Configure the ExposureMode
    edit_enumeration(nodemap, EXPOSURE_MODE)

    # Configure the ExposureAuto
    edit_enumeration(nodemap, EXPOSURE_AUTO)

    # Configure the AutoLightTarget
    edit_setting(nodemap, AUTO_LIGHT_TARGET)

    if nodemap.get_node(EXPOSURE_TIME):
        edit_setting(nodemap, EXPOSURE_TIME)
    else:
        edit_setting(nodemap, EXPOSURE_TIME_RAW)


def gain_auto(nodemap):
    """Configure gain using the given nodemap."""
    # Configure the GainAuto
    edit_enumeration(nodemap, GAIN_AUTO)

    # Configure the AutoLightTarget
    edit_setting(nodemap, AUTO_LIGHT_TARGET)

    if nodemap.get_node(GAIN):
        edit_setting(nodemap, GAIN)
    else:
        edit_setting(nodemap, GAIN_RAW)


def balance_white_auto(nodemap):
    """Configure balance ratio/white using the given nodemap."""
    # Configure the BalanceWhiteAuto
    edit_enumeration(nodemap, BALANCE_WHITE_AUTO)

    # While switching the BalanceRatioSelector, configure the BalanceRatio
    edit_enum_setting(nodemap, BALANCE_RATIO_SELECTOR, BALANCE_RATIO)


def do_auto_functions(nodemap):
    """Function running in a separate thread for auto function configuration."""
    # Check if features available.
    feature_list = {EXPOSURE_AUTO: False,
                    GAIN_AUTO: False,
                    BALANCE_WHITE_AUTO: False}
    for feature in feature_list:
        with nodemap.get_node(feature) as node:
            feature_list[feature]=True if node.is_writable else False

    while True:
        print()
        print("Auto Functions")
        index = 0
        for feature, is_writable in feature_list.items():
            index = index + 1
            if is_writable:
                print("{0} : {1}".format(index, feature))
        print("Else : Exit")
        selection = int(input("Select : "))
        if selection == 1 and feature_list[EXPOSURE_AUTO] == True:
            exposure_auto(nodemap)
        elif selection == 2 and feature_list[GAIN_AUTO] == True:
            gain_auto(nodemap)
        elif selection == 3 and feature_list[BALANCE_WHITE_AUTO] == True:
            balance_white_auto(nodemap)
        else:
            print("Focus on the OpenCV window and press any key to terminate.")
            break


if __name__ == "__main__":
    my_callback = CMyCallback()
    cb_func = my_callback.datastream_callback
    try:
        # Initialize StApi before using.
        st.initialize()

        # Create a system object for device scan and connection.
        st_system = st.create_system()

        # Connect to first detected device.
        st_device = st_system.create_first_device()

        # Display DisplayName of the device.
        print('Device=', st_device.info.display_name)

        # Create a datastream object for handling image stream data.
        st_datastream = st_device.create_datastream()

        # Register callback for datastream
        callback = st_datastream.register_callback(cb_func)

        # Start the image acquisition of the host (local machine) side.
        st_datastream.start_acquisition()

        # Start the image acquisition of the camera side.
        st_device.acquisition_start()

        # Get device nodemap to access the device settings.
        remote_nodemap = st_device.remote_port.nodemap

        # Create and start a thread for auto function configuration.
        autofunc_thread = threading.Thread(target=do_auto_functions,
                                           args=(remote_nodemap,))
        autofunc_thread.start()

        # Display image using OpenCV.
        while True:
            output_image = my_callback.image
            if output_image is not None:
                cv2.imshow('image', output_image)
            key_input = cv2.waitKey(1)
            if key_input != -1:
                break

        autofunc_thread.join()

        # Stop the image acquisition of the camera side
        st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        st_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)
