import os
from functools import lru_cache
from PIL import Image


# Кодировка, в которой открывается текст
CODING = 'widnows-1251'

# Самая главная папка
MAIN_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))

# Папка data
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'data')

# Папка со штрих кодами
CODES_FOLDER = os.path.join(DATA_FOLDER, 'codes')

# Папка со шрифтами
FONT_FOLDER = os.path.join(DATA_FOLDER, 'font')

# Папка с картинками которые подставляются сверху
IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'images')

# Папка, куда будет все сохранятся
SAVE_FOLDER = os.path.join(MAIN_FOLDER, 'save')

# Некоторые файлы, которые нужны для работы
LOGO_PATH = os.path.join(DATA_FOLDER, 'logo.jpg')
TEMPLATE_PATH = os.path.join(DATA_FOLDER, 'template.jpg')
MADE_PATH = os.path.join(DATA_FOLDER, 'made.txt')

# файлы шрифтов
IMPACT_PATH = os.path.join(FONT_FOLDER, 'impact.ttf')
ARIAL_PATH = os.path.join(FONT_FOLDER, 'arial.ttf')
TIMES_PATH = os.path.join(FONT_FOLDER, 'times.ttf')
TIMESBOLD_PATH = os.path.join(FONT_FOLDER, 'timesbold.ttf')


# Так как bytes не имеет read аргумента, который нужен для чтения из файла, то используем такой враппер
class BytesWrapper(bytes):
    def read(self):
        return self


@lru_cache
def _get_image(path):
    try:
        return Image.open(path)
    except Exception:
        # Если картинка не найдена, возвращает пустую
        print('Картинка {} не найдена'.format(path))
        return Image.new('RGB', (0, 0))


@lru_cache
def _get_text(path):
    try:
        return open(path, 'r', encoding=CODING).read()
    except Exception:
        # Если текст не найден возвращает пустой
        print('Текст {} не найден'.format(path))
        return ''


@lru_cache
def _get_font(path):
    try:
        return BytesWrapper(open(path, 'rb').read())
    except Exception:
        # Если шрифт не найден, райзим эксепшен
        raise FileNotFoundError('Шрифт {} не найден, необходимо его добавить'.format(path))


class Data:
    """Класс для получения данных из папки data"""

    @classmethod
    def get_logo(cls):
        return _get_image(LOGO_PATH).copy()

    @classmethod
    def get_template(cls):
        return _get_image(TEMPLATE_PATH).copy()

    @classmethod
    def get_made_text(cls):
        return _get_text(MADE_PATH)

    @classmethod
    def get_code(cls, code):
        path = os.path.join(CODES_FOLDER, '{}.png'.format(code))
        return _get_image(path).copy()

    @classmethod
    def get_image(cls, image_name):
        path = os.path.join(IMAGES_FOLDER, image_name)
        return _get_image(path).copy()


class Font:
    """Шрифты"""

    IMPACT = _get_font(IMPACT_PATH)
    ARIAL = _get_font(ARIAL_PATH)
    TIMES = _get_font(TIMES_PATH)
    TIMESBOLD = _get_font(TIMESBOLD_PATH)


class Color:
    BLACK = (27, 27, 27)  # Черный
    WHITE = (255, 255, 255)  # Белый


# Какие цвета заментять на какие, пишутся в RGB
# Например нужно заменить в конце на картинке весь черный на сероватый, то пишем:
# (0, 0, 0): (27, 27, 27) - заменить цвет с каналами RED - 0, GREEN - 0, BLUE - 0, на 27, 27, 27
COLOR_REPLACES = {
    (0, 0, 0): Color.BLACK,  # цвет на штрихкоде очень черный, надо сероватый
    (173, 173, 173): Color.WHITE,  # цвет на штрихкоде странный белый, нужно совсем белый
}


# Перечислены категории, с которыми будут создаваться этикетки
CATEGORIES = [
    'ВЕСОВОЕ',
    'ВЕСОВОЕ У',
    'ФАСОВАННОЕ',
]
