"""
 This sample shows how to conect and get images from all available cameras.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to all available cameras
 - Acquire image from the list of camera
 You can see how to handle multiple cameras/stream objects in this sample.
"""

import stapipy as st


# Number of images to grab
number_of_images_to_grab = 10

try:
    # Initialize StApi before using.
    st.initialize()

    # Create a system object for device scan and connection.
    st_system = st.create_system()

    # Try to connect to all possible devices
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
        print("Device {0} = {1}".format(len(st_devices),
              st_devices[len(st_devices)-1].info.display_name))

        # Create a DataStream object
        st_datastreams.append(st_devices[len(st_devices)-1].create_datastream())

    # Start the image acquisition of the host side.
    for datastream in st_datastreams:
        datastream.start_acquisition(number_of_images_to_grab)

    # Start the image acquisition of the camera side.
    for device in st_devices:
        device.acquisition_start()

    # Loop for aquiring data and checking status
    still_grabbing = True
    while still_grabbing:
        still_grabbing = False
        for datastream in st_datastreams:
            if datastream.is_grabbing:
                still_grabbing = True
                with datastream.retrieve_buffer() as st_buffer:
                    # Check if the acquired data contains image data.
                    if st_buffer.info.is_image_present:
                        # Create an image object.
                        st_image = st_buffer.get_image()
                        # Display the information of the acquired image data.
                        print("{0} BlockID={1} Size={2} x {3} First Byte={4}"\
                            .format(datastream.device.info.display_name,
                                    st_buffer.info.frame_id,
                                    st_image.width, st_image.height,
                                    st_image.get_image_data()[0]))
                    else:
                        print("Image data does not exist.")

    # Stop the image acquisition of the camera side.
    for device in st_devices:
        device.acquisition_stop()

    # Stop the image acquisition of the host side.
    for datastream in st_datastreams:
        datastream.stop_acquisition()

except Exception as exception:
    print(exception)
