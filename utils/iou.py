def calc_iou(box_a, box_b):
    # x & y of intersection rect.
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    #cal intersection area
    inter_area = max(0, x_b - x_a) * max(0, y_b - y_a)

    #cal area of both boxes
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])

    #cal iou
    return inter_area / (box_a_area + box_b_area - inter_area)

def calc_ioa(box_a, box_b):
    #calculate intersection over box_a

    # x & y of intersection rect.
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    #cal intersection area
    inter_area = max(0, x_b - x_a) * max(0, y_b - y_a)
    print(inter_area)

    #cal area of box a
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    print(box_a_area)

    #cal iou
    return inter_area / box_a_area

print(calc_iou([2, 2, 6, 6], [5, 1, 7, 3]))
