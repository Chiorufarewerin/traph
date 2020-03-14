import numpy as np
from PIL import Image


def alpha_composite(src, dst):
    """Накладывает одно изображение на другое"""

    src = np.asarray(src)
    dst = np.asarray(dst)
    out = np.empty(src.shape, dtype = 'float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha]/255.0
    dst_a = dst[alpha]/255.0
    out[alpha] = src_a+dst_a*(1-src_a)
    old_setting = np.seterr(invalid = 'ignore')
    out[rgb] = (src[rgb]*src_a + dst[rgb]*dst_a*(1-src_a))/out[alpha]
    np.seterr(**old_setting)
    out[alpha] *= 255
    np.clip(out,0,255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Image.fromarray(out, 'RGBA')
    return out


def replace_color(image, replace=(255, 255, 255), color=(0, 0, 0)):
    """Заменяет один цвет на изображении на другой"""

    data = np.array(image)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    area = (red == replace[0]) & (blue == replace[1]) & (green == replace[2])
    data[..., :-1][area.T] = color  # Transpose back needed
    im2 = Image.fromarray(data)
    return im2
