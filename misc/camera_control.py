"""
 This program connects and gets images from all available cameras using the
 trigger mode of the camera.
 - Initialize StApi
 - Connect to all available cameras
 - Set trigger mode and send trigger
 - Acquire image from the list of camera
"""

import cv2
import threading
import queue
import numpy as np
import stapipy as st
import os
import time
import shutil
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Image scale when displaying using OpenCV.
DISPLAY_RESIZE_FACTOR = 0.3

TRIGGER_SELECTOR = "TriggerSelector"
TRIGGER_SELECTOR_FRAME_START = "FrameStart"
TRIGGER_MODE = "TriggerMode"
TRIGGER_MODE_ON = "On"
TRIGGER_MODE_OFF = "Off"
TRIGGER_SOURCE = "TriggerSource"
TRIGGER_SOURCE_SOFTWARE = "Software"
TRIGGER_SOFTWARE = "TriggerSoftware"


class XCameraControl(threading.Thread):

    STOPPED = "Stopped"
    RECORDING = "Recording"
    PREVIEWING = "Previewing"
    RECORD_WAITING = "RecordWaiting"
    PREVIEW_WAITING = "PreviewWaiting"
    STOPPED_WAITING = "StoppedWaiting"
    QUITING = "Quiting"
    QUIT_WAITING = "QuitWaiting"

    STOP_CMND = "StopCmnd"
    RECORD_CMND = "RecordCmnd"
    PREVIEW_CMND = "PreviewCmnd"
    QUIT_CMND = "QuitCmnd"

    st_devices = []
    st_datastreams = []
    trigger_softwares = []
    my_callbacks = []
    cb_funcs = []
    cam_state = CameraControl.STOPPED

    def __init__(self, cam_q, status_q):
        threading.Thread.__init__(self)
        self.cmnd_q = cam_q
        self.status_q = status_q
        init_cameras(self)

    def run(self):
        logging.debug('running')
        while True:
            if not self.cmnd_q.empty():
                cmnd = self.cmnd_q.get()
                self.cmnd_q.task_done()
                set_cam_state(self, cmnd)

            if self.cam_state == self.PREVIEWING:
                self.trigger_camera()
                self.cam_state = self.PREVIEW_WAITING
            elif self.cam_state == self.PREVIEW_WAITING:
                for my_callback in self.my_callbacks:
                    if not my_callback.img_processed:
                        my_callback.process_image(self.PREVIEW_CMND)
                        break
                else:
                    # all cameras processed their images
                    for my_callback in self.my_callbacks:
                        my_callback.img_processed = False
                    self.cam_state = self.PREVIEWING
            elif cself.am_state == self.RECORDING:
                self.trigger_camera(self)
                self.cam_state = self.RECORD_WAITING
            elif self.cam_state == self.RECORD_WAITING:
                for my_callback in self.my_callbacks:
                    if not my_callback.img_processed:
                        my_callback.process_image(self.RECORD_CMND)
                        break
                else:
                    # all cameras processed their images
                    for my_callback in self.my_callbacks:
                        my_callback.img_processed = False
                        if my_callback.image_num % 10 == 0:
                            imgName = os.path.join(my_callback.cam_path, str(my_callback.image_num - 1) + ".jpg")
                            shutil.copyfile(imgName, "camera_" + str(my_callback.cam_num) + "/image.jpg")
                    self.cam_state = self.RECORDING
            elif self.cam_state == self.STOPPED_WAITING:
                # Stopped waiting for image to be processed
                for my_callback in self.my_callbacks:
                    if not my_callback.img_processed:
                        my_callback.process_image(self.STOP_CMND)
                        break
                else:
                    # all cameras processed their images
                    for my_callback in self.my_callbacks:
                        my_callback.img_processed = False
                    self.cam_state = self.STOPPED
            elif self.cam_state == self.QUIT_WAITING:
                # waiting for image to be processed
                for my_callback in self.my_callbacks:
                    if not my_callback.img_processed:
                        my_callback.process_image(self.STOP_CMND)
                        break
                else:
                    # all cameras processed their images
                    for my_callback in self.my_callbacks:
                        my_callback.img_processed = False
                    self.cam_state = self.QUITING
            elif self.cam_state == self.QUITING:
                self.close_cameras(self)
                break

    except Exception as exc:
        print(exc)
        raise

    finally:
        self.close_cameras(self)

    def init_cameras(self):
        try:
            # Initialize StApi before using.
            st.initialize()

            # Create a system object for device scan and connection.
            st_system = st.create_system()

            while True:
                try:
                    self.st_devices.append(st_system.create_first_device())
                except:
                    if len(self.st_devices) == 0:
                        raise
                    break

                # Display the DisplayName of the device.
                print("Device {0} = {1}".format(len(self.st_devices),
                      self.st_devices[len(self.st_devices)-1].info.display_name))

                # Create a DataStream object
                self.st_datastreams.append(self.st_devices[len(self.st_devices)-1].create_datastream())

                # setup the image transfer callback functions
                my_callback = CMyCallback(len(self.st_devices),
                        self.st_devices[len(self.st_devices)-1].info.display_name)
                self.my_callbacks.append(my_callback)
                self.cb_funcs.append(my_callback.datastream_callback)

                # Get the nodemap for the camera settings.
                nodemap = self.st_devices[len(self.st_devices)-1].remote_port.nodemap

                # Set the TriggerSelector for FrameStart or ExposureStart.
                try:
                    set_enumeration(
                        nodemap, TRIGGER_SELECTOR, TRIGGER_SELECTOR_FRAME_START)
                except st.PyStError:
                    set_enumeration(
                        nodemap, TRIGGER_SELECTOR, TRIGGER_SELECTOR_EXPOSURE_START)

                # Set the TriggerMode to On.
                set_enumeration(nodemap, TRIGGER_MODE, TRIGGER_MODE_ON)

                # Set the TriggerSource to Software
                set_enumeration(nodemap, TRIGGER_SOURCE, TRIGGER_SOURCE_SOFTWARE)

                # Get and cast to Command interface of the TriggerSoftware mode
                self.trigger_softwares.append(st.PyICommand(nodemap.get_node(TRIGGER_SOFTWARE)))

        # Start the image acquisition of the host side.
        for counter, st_datastream in enumerate(self.st_datastreams):
            # Register callback for datastream
            callback = self.st_datastream.register_callback(self.cb_funcs[counter])

            # Start the image acquisition of the host (local machine) side.
            st_datastream.start_acquisition()

        # Start the image acquisition of the camera side.
        for device in self.st_devices:
            device.acquisition_start()
    except Exception as exception:
        print(exception)

    def trigger_camera(self):
        try:
            for trigger_software in self.trigger_softwares:
                trigger_software.execute()
        except Exception as exception:
            print(exception)

    def close_cameras():
        try:
            # Stop the image acquisition of the camera side.
            for device in self.st_devices:
                device.acquisition_stop()

            # Stop the image acquisition of the host side.
            for datastream in self.st_datastreams:
                datastream.stop_acquisition()

        except Exception as exception:
            print(exception)

    def num_cameras(self):
        return len(self.st_devices)

    def camera_info(self, num):
            return (self.my_callbacks[num - 1].cam_num,
                    self.my_callbacks[num - 1].cam_name)

    def set_cam_state(self, cmnd):
        try:
            if cmnd == self.RECORD_CMND:
                for my_callback in self.my_callbacks:
                    my_callback.cam_path = os.path.join("camera_" + str(my_callback.cam_num),
                                            time.strftime("%m_%d_%H_%M_%S", time.localtime()))
                    os.makedirs(my_callback.cam_path)
                if self.cam_state == self.RECORD_WAITING or self.cam_state == self.PREVIEW_WAITING:
                    self.cam_state = self.RECORD_WAITING
                else:
                    self.cam_state = self.RECORDING
            elif cmnd == self.PREVIEW_CMND:
                if self.cam_state == self.RECORD_WAITING or self.cam_state == self.PREVIEW_WAITING:
                    self.cam_state = self.PREVIEW_WAITING
                else:
                    self.cam_state = self.PREVIEWING
            elif cmnd == self.STOP_CMND:
                if self.cam_state == self.RECORD_WAITING or self.cam_state == self.PREVIEW_WAITING:
                    self.cam_state = self.STOPPED_WAITING
                else:
                    self.cam_state = self.STOPPED
            elif cmnd == self.QUIT_CMND:
                if self.cam_state == self.RECORD_WAITING or self.cam_state == self.PREVIEW_WAITING:
                    self.cam_state = self.QUIT_WAITING
                else:
                    self.cam_state = self.QUITING

        except Exception as exception:
            print(exception)

class Test:
    pass

class CMyCallback:
    """
    Class that contains a callback function.
    """

    def __init__(self, cam_num="", cam_name=""):
        self._image = None
        self._lock = threading.Lock()
        self.img_processed = False
        self.image_num = 0
        self.cam_num = cam_num
        self.cam_name = cam_name
        self.cam_path = ""

    @property
    def image(self):
        """Property: return PyIStImage of the grabbed image."""
        duplicate = None
        self._lock.acquire()
        if self._image is not None:
            duplicate = self._image.copy()
        self._lock.release()
        return duplicate

    def process_image(self, cmnd):
        """write current image to the file system."""
        self._lock.acquire()
        if self._image is not None:
            if cmnd == RECORD_CMND:
                imgName = os.path.join(self.cam_path, str(self.image_num) + ".jpg")
                cv2.imwrite(imgName, self._image)
                self.image_num = self.image_num + 1
            elif cmnd == PREVIEW_CMND:
                cv2.imwrite("camera_" + str(self.cam_num) + "/image.jpg", self._image)
            self._image = None
            self.img_processed = True
        self._lock.release()

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
                    #nparr = cv2.resize(nparr, None,
                                       #fx=DISPLAY_RESIZE_FACTOR,
                                       #fy=DISPLAY_RESIZE_FACTOR)

                    self._lock.acquire()
                    self._image = nparr
                    self._lock.release()




def set_enumeration(nodemap, enum_name, entry_name):
    """
    Function to set enumeration value.

    :param nodemap: node map.
    :param enum_name:  name of the enumeration node.
    :param entry_name:  symbolic value of the enumeration entry node.
    """
    enum_node = st.PyIEnumeration(nodemap.get_node(enum_name))
    entry_node = st.PyIEnumEntry(enum_node[entry_name])
    # Note that depending on your use case, there are three ways to set
    # the enumeration value:
    # 1) Assign the integer value of the entry with set_int_value(val) or .value
    # 2) Assign the symbolic value of the entry with set_symbolic_value("val")
    # 3) Assign the entry (PyIEnumEntry) with set_entry_value(entry)
    # Here set_entry_value is used:
    enum_node.set_entry_value(entry_node)
