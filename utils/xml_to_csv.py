#!/usr/bin/python3
import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(path):
    xml_list = []
    try:
        for xml_file in glob.glob(path + '/*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for member in root.findall('object'):
                value = ('/home/kamiar/projects/opervu/images/labeled/' + root.find('filename').text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text),
                        member[0].text,
                        )
                xml_list.append(value)
    except:
        print(xml_file)
        raise
    column_name = ['path', 'xmin', 'ymin', 'xmax', 'ymax', 'class']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main():
    image_path = '/home/kamiar/projects/opervu/images/labeled/'
    xml_df = xml_to_csv(image_path)
    xml_df.to_csv((image_path + 'annotations.csv'), header = False, index=None)
    print('Successfully converted xml\'s to csv.')


main()
