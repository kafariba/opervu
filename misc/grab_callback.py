"""
 This sample shows how to use callback function to acquire image data from camera.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Register and use callback function with StApi
 - Acquire image data via callback function
"""

import stapipy as st


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


if __name__ == "__main__":
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
        callback = st_datastream.register_callback(datastream_callback)

        # Start the image acquisition of the host (local machine) side.
        st_datastream.start_acquisition()

        # Start the image acquisition of the camera side.
        st_device.acquisition_start()

        # Press enter to terminate.
        input("Press enter to terminate")

        # Stop the image acquisition of the camera side
        st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        st_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)
