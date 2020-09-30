/home/kamiar/keras-retinanet/keras_retinanet/bin/train.py\
            --steps 9996 --snapshot-path '/home/kamiar/projects/opervu/snapshots'\
            --tensorboard-dir '/home/kamiar/projects/opervu/logs'\
            --random-transform --image-max-side 2048\
            csv '/home/kamiar/projects/opervu/images/labeled/annotations.csv'\
            '/home/kamiar/projects/opervu/images/labeled/classes.txt'


/home/kamiar/keras-retinanet/keras_retinanet/bin/convert_model.py /home/kamiar/projects/opervu/snapshots/resnet50_csv_50.h5 /home/kamiar/projects/opervu/inference/model.h5
