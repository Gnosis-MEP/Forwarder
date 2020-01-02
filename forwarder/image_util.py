import base64

import cv2

COLORS_10 =[(144,238,144),(178, 34, 34),(221,160,221),(  0,255,  0),(  0,128,  0),(210,105, 30),(220, 20, 60),
            (192,192,192),(255,228,196),( 50,205, 50),(139,  0,139),(100,149,237),(138, 43,226),(238,130,238),
            (255,  0,255),(  0,100,  0),(127,255,  0),(255,  0,255),(  0,  0,205),(255,140,  0),(255,239,213),
            (199, 21,133),(124,252,  0),(147,112,219),(106, 90,205),(176,196,222),( 65,105,225),(173,255, 47),
            (255, 20,147),(219,112,147),(186, 85,211),(199, 21,133),(148,  0,211),(255, 99, 71),(144,238,144),
            (255,255,  0),(230,230,250),(  0,  0,255),(128,128,  0),(189,183,107),(255,255,224),(128,128,128),
            (105,105,105),( 64,224,208),(205,133, 63),(  0,128,128),( 72,209,204),(139, 69, 19),(255,245,238),
            (250,240,230),(152,251,152),(  0,255,255),(135,206,235),(  0,191,255),(176,224,230),(  0,250,154),
            (245,255,250),(240,230,140),(245,222,179),(  0,139,139),(143,188,143),(255,  0,  0),(240,128,128),
            (102,205,170),( 60,179,113),( 46,139, 87),(165, 42, 42),(178, 34, 34),(175,238,238),(255,248,220),
            (218,165, 32),(255,250,240),(253,245,230),(244,164, 96),(210,105, 30)]


def get_event_data_image_ndarray(event_data, fs_client):
    img_key = event_data['image_url']
    width = event_data['width']
    height = event_data['height']
    color_channels = event_data['color_channels']
    n_channels = len(color_channels)
    nd_shape = (int(height), int(width), n_channels)
    image_nd_array = fs_client.get_image_ndarray_by_key_and_shape(img_key, nd_shape)

    return image_nd_array


def draw_bboxes(img, bbox, labels, offset):
    for i, box in enumerate(bbox):
        x1, y1, x2, y2 = [int(i) for i in box]
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        label = labels[i]
        # box text and bar
        color = COLORS_10[1 % len(COLORS_10)]
        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 2, 2)[0]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        centre_point = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        cv2.circle(img, centre_point, 2, color, 3)
        cv2.putText(img, label, (x1, y1 + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [255, 255, 255], 2)

    return img


def get_image_in_base64(image_ndarray):
    retval, buffer = cv2.imencode('.jpg', image_ndarray)
    base64_image = base64.b64encode(buffer).decode('utf-8')
    return base64_image