import numpy as np
from PIL import Image

from data import COLOR_REPLACES


def alpha_composite(src, dst):
    """Накладывает одно изображение на другое"""

    src = np.asarray(src)
    dst = np.asarray(dst)
    out = np.empty(src.shape, dtype='float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha] / 255.0
    dst_a = dst[alpha] / 255.0
    out[alpha] = src_a + dst_a * (1 - src_a)
    old_setting = np.seterr(invalid='ignore')
    out[rgb] = (src[rgb] * src_a + dst[rgb] * dst_a * (1 - src_a)) / out[alpha]
    np.seterr(**old_setting)
    out[alpha] *= 255
    np.clip(out, 0, 255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Image.fromarray(out, 'RGBA')
    return out


def replace_colors(image):
    """Заменяет одни цвета на картинке на другие, указанные в COLOR_REPLACES"""

    data = np.array(image)
    red, green, blue, _ = data.T

    for source_color, replacement_color in COLOR_REPLACES.items():
        area = (red == source_color[0]) & (blue == source_color[1]) & (green == source_color[2])
        data[..., :-1][area.T] = replacement_color
    im2 = Image.fromarray(data)
    return im2
