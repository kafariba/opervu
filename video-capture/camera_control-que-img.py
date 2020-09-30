"""
 This program connects and gets images from all available cameras using the
 trigger mode of the camera.
 - Initialize StApi
 - Connect to all available cameras
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

# Number of images to grab
number_of_images_to_grab = 300

# Maximum number of frames in one video file
maximum_frame_count_per_file = 200

# Number of video files
video_files_count = 3

# Frame per second - capture rate
fps = 10

# preview interval in set_cam_state
preview_interval_sec = 1

VIDEO_CAPTURE_PATH = "/home/kamiar/projects/opervu/video-capture"

CAMERA_1_ID = "STC_CMC4MPOE(17C1935)"
CAMERA_2_ID = "STC_CMC4MPOE(17C1937)"
CAMERA_3_ID = "STC_CMC4MPOE(17C1942)"

START = True
STOP = False

def videofiler_callback(handle=None, context=None):
    """
    Callback to handle events from Video Filer.

    :param handle: handle that trigger the callback.
    :param context: user data passed on during callback registration.
    """
    callback_type = handle.callback_type
    videofiler = handle.module
    if callback_type == st.EStCallbackType.StApiIPVideoFilerOpen:
        logging.debug("Open: {}".format(handle.data['filename']))
    elif callback_type == st.EStCallbackType.StApiIPVideoFilerClose:
        logging.debug("Close: {}".format(handle.data['filename']))
    elif callback_type == st.EStCallbackType.StApiIPVideoFilerError:
        logging.debug("Error: {}".format(handle.error[1]))
        context['error'] = True

class Camera:
    """
    container class for camera number/name and image storage loc.
    """
    def __init__(self, cam_num=1):
        self.cam_num = cam_num
        self.cam_name = 'camera_' + str(cam_num)
        self.cam_base_path = os.path.join(VIDEO_CAPTURE_PATH, self.cam_name)
        self.cam_full_path = ''
        if not os.path.isdir(self.cam_base_path):
            os.mkdir(self.cam_base_path)

class CameraControl(threading.Thread):
    """
    Thread class to handle camera control commads.
    """

    STOPPED = "Stopped"
    RECORDING = "Recording"
    PREVIEWING = "Previewing"
    QUITING = "Quiting"

    STOP_CMND = "StopCmnd"
    RECORD_CMND = "RecordCmnd"
    PREVIEW_CMND = "PreviewCmnd"
    QUIT_CMND = "QuitCmnd"

    st_devices = []
    st_datastreams = []
    st_videofilers = []
    cameras = []
    callback_info = [{'error': False}, {'error': False}, {'error': False}]
    videofiler_cbs = []
    first_timestamp = []
    first_frame = []
    cam_state = STOPPED
    fps = 10
    images = []

    def __init__(self, cam_q, status_q):
        threading.Thread.__init__(self)
        self.cmnd_q = cam_q
        self.status_q = status_q
        self.init_cameras()

    def run(self):
        #logging.debug('running')
        while True:
            if not self.cmnd_q.empty():
                cmnd = self.cmnd_q.get()
                self.cmnd_q.task_done()
                if cmnd == self.RECORD_CMND:
                    self.set_video_filer()
                    for i, st_datastream in enumerate(self.st_datastreams):
                        self.cameras[i].cam_full_path = os.path.join(self.cameras[i].cam_base_path,
                                                time.strftime("%m_%d_%H_%M_%S", time.localtime()))
                        os.makedirs(self.cameras[i].cam_full_path)
                        # Register video files tempfile.gettempdir()
                        for file_index in range(video_files_count):
                            file_location = os.path.join(self.cameras[i].cam_full_path,
                                     "recording-" + str(file_index + 1) + ".avi")
                            self.st_videofilers[i].register_filename(file_location)

                    # start acquisition
                    self.acq_control(START)

                    self.first_frame = [True, True, True]
                    self.first_timestamp = [0, 0, 0]
                    self.cam_state = self.RECORDING

                elif cmnd == self.PREVIEW_CMND:
                    self.last_preview_time = time.time()
                    self.cam_state = self.PREVIEWING

                elif cmnd == self.STOP_CMND:
                    if self.cam_state == self.RECORDING:
                        for st_videofiler in self.st_videofilers:
                            st_videofiler.release()

                        # stop acquisition
                        self.acq_control(STOP)


                    self.cam_state = self.STOPPED

                elif cmnd == self.QUIT_CMND:
                    self.close_cameras()
                    break


            if self.cam_state == self.PREVIEWING:
                if time.time() - self.last_preview_time > 0.3: #preview_interval_sec:
                    if len(self.images) != 0:
                        del self.images[:]

                    # start acquisition
                    self.acq_control(START ,1)
                    for i,st_datastream in enumerate(self.st_datastreams):
                        is_image_saved = False
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

                                # Convert image to BGR8 format.
                                st_converter = st.create_converter(st.EStConverterType.PixelFormat)
                                st_converter.destination_pixel_format = \
                                    st.EStPixelFormatNamingConvention.RGB8
                                st_image = st_converter.convert(st_image)
                                #img = cv2.cvtColor(st_image, cv2.COLOR_BAYER_BGR2RGB)

                                self.images.append(st_image)

                                # Create a still image file handling class object (filer)
                                st_stillimage_filer = st.create_filer(st.EStFilerType.StillImage)

                                file_location = os.path.join(self.cameras[i].cam_base_path, 'image.jpg')
                                # Save the image file as StApiRaw file format.
                                print("Saving {0} ... ".format(file_location), end="")
                                st_stillimage_filer.save(st_image,
                                    st.EStStillImageFileFormat.JPEG, file_location)
                                print("done.")
                                st_stillimage_filer.release()
                                is_image_saved = True
                            else:
                                # If the acquired data contains no image data.
                                print("Image data does not exist.")

                    self.status_q.put(self.images)
                    self.last_preview_time = time.time()
                    # stop acquisition
                    self.acq_control(STOP)

            elif self.cam_state == self.RECORDING:
                for i,st_datastream in enumerate(self.st_datastreams):
                    if st_datastream.is_grabbing:
                        if self.callback_info[i]['error']:
                            break
                        with st_datastream.retrieve_buffer() as st_buffer:
                        # Check if the acquired data contains image data.
                            if st_buffer.info.is_image_present:
                                # Create an image object.
                                st_image = st_buffer.get_image()
                                # Display the information of the acquired image data.
                                logging.error("BlockID={0} Size={1} x {2} {3:.2f} fps".format(
                                    st_buffer.info.frame_id,
                                    st_image.width, st_image.height,
                                    st_datastream.current_fps))

                                # Calculate frame number in case of frame drop.
                                frame_no = 0
                                current_timestamp = st_buffer.info.timestamp
                                if self.first_frame[i]:
                                    self.first_frame[i] = False
                                    self.first_timestamp[i] = current_timestamp
                                else:
                                    delta = current_timestamp - self.first_timestamp[i]
                                    tmp = delta * self.fps / 1000000000.0
                                    frame_no = int(tmp + 0.5)

                                # Add the image data to video file.
                                self.st_videofilers[i].register_image(st_image, frame_no)
                            else:
                                # If the acquired data contains no image data.
                                logging.error("Image data does not exist.")


    def acq_control(self, start=True, num_images=number_of_images_to_grab):
        for i,st_datastream in enumerate(self.st_datastreams):
            if start:
                # Start the image acquisition of the host (local machine) side.
                st_datastream.start_acquisition(num_images)

                # Start the image acquisition of the camera side.
                self.st_devices[i].acquisition_start()
            else:
                # Stop the image acquisition of the camera side.
                self.st_devices[i].acquisition_stop()

                # Stop the image acquisition of the host side.
                st_datastream.stop_acquisition()

    def set_video_filer(self):
        for i in range(len(self.st_devices)):
            # Create PyStVideoFiler
            st_videofiler = st.create_filer(st.EStFilerType.Video)

            # Register a callback function.
            self.videofiler_cbs.append(st_videofiler.register_callback(videofiler_callback,
                                    self.callback_info[i]))

            # Configure the video file settings.
            st_videofiler.maximum_frame_count_per_file = \
                maximum_frame_count_per_file
            st_videofiler.video_file_format = st.EStVideoFileFormat.AVI2
            st_videofiler.video_file_compression = \
                st.EStVideoFileCompression.MotionJPEG
            st_videofiler.fps = fps
            if len(self.st_videofilers) == i:
                self.st_videofilers.append(st_videofiler)
            else:
                self.st_videofilers[i] = st_videofiler

    def init_cameras(self):
        try:
            # Initialize StApi before using.
            st.initialize()

            # Create a system object for device scan and connection.
            st_system = st.create_system()

            # discovered camera index
            i = 0

            while True:
                try:
                    st_device = st_system.create_first_device()
                    self.st_devices.append(st_device)
                except:
                    if len(self.st_devices) == 0:
                        raise
                    break

                # Display the DisplayName of the device.
                cam_disp_name = st_device.info.display_name
                logging.debug("Device {0} = {1}".format(len(self.st_devices), cam_disp_name))

                # determine camera Number
                if cam_disp_name == CAMERA_1_ID:
                    cam_num = 1
                elif cam_disp_name == CAMERA_2_ID:
                    cam_num = 2
                elif cam_disp_name == CAMERA_3_ID:
                    cam_num = 3
                else:
                    raise NameError('Unknown Camera ID.')

                # setup the image transfer callback functions
                my_cam = Camera(cam_num)
                self.cameras.append(my_cam)

                acquisition_frame_rate = st_device.remote_port.nodemap.get_node(
                    "AcquisitionFrameRate")
                if acquisition_frame_rate:
                    self.fps = acquisition_frame_rate.value

                # Create a DataStream object
                st_datastream = st_device.create_datastream()
                self.st_datastreams.append(st_datastream)

                i += 1

        except Exception as exception:
            logging.error("init: " + exception)

    def close_cameras(self):
        try:
            # Stop the image acquisition of the camera side.
            for device in self.st_devices:
                device.acquisition_stop()

            # Stop the image acquisition of the host side.
            for datastream in self.st_datastreams:
                datastream.stop_acquisition()

            st.terminate()

        except Exception as exception:
            logging.error("close: " + exception)
