import textwrap
from PIL import Image, ImageDraw, ImageFont

from utils import alpha_composite, replace_colors
from data import Data, Font, Color
from save import Save


def max_size(draw, text, textsize, fonttext):
    size = 200
    w = 99999
    while(w > textsize):
        size -= 1
        font = ImageFont.truetype(fonttext, size)
        w, h = draw.textsize(text, font=font)
    return size


def add_text_on_image(draw, text, x, y, size=20, font=Font.IMPACT, fill=Color.BLACK,
                      center=False, centerh=False, textsize=0):
    if textsize:
        size = max_size(draw, text, textsize, font)
    font = ImageFont.truetype(font, size)
    w, h = draw.textsize(text, font=font)
    draw.text((x - w / 2 if center else x, y - h / 2 if centerh else y), text, fill=fill, font=font)
    return w, h


def add_group_text(draw, text, x, y, h=25, size=20, font=Font.IMPACT, fill=Color.BLACK,
                   center=False, centerh=False, textsize=0, some=False):
    if textsize:
        maxlen = 0
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font, size))
            if maxlen < width:
                maxlen = width
                bigtext = line
        size = max_size(draw, bigtext, textsize, font)
    avgheight = 0

    if centerh and len(text) > 1:
        centerhsize = 0
        sizes = list()
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font, size))
            centerhsize += height + (height - h)
            sizes.append(height)
        avgheight = sum(sizes) / float(len(sizes))
        y -= centerhsize / 2 - (avgheight - h) - avgheight / 2 * (len(text) - 2)
        if some:        
            y += avgheight / 2

    for line in text:
        tempw, temph = add_text_on_image(draw, line, x, y, size, font, fill, center, centerh)
        y += h
        if some:
            y += avgheight


class Traph:
    """Трафаретка"""

    def __init__(self, name, short_name, what, netto, brutto, proteins, fats, carbohydrates, kkal,
                 tu, category, composition, shelf_life, code, bold_text=None, top_image=None):
        self.name = name
        self.short_name = short_name
        self.what = what
        self.netto = netto
        self.brutto = brutto
        self.proteins = proteins
        self.fats = fats
        self.carbohydrates = carbohydrates
        self.kkal = kkal
        self.tu = tu
        self.category = category
        self.composition = composition
        self.shelf_life = shelf_life
        self.code = code
        self.bold_text = bold_text
        self.top_image = top_image

        self.template = Data.get_template()
        self.image = ImageDraw.Draw(self.template)
        self.logo = Data.get_logo()

    def make_traph(self):
        self.paste_logo()
        self.paste_code()
        self.paste_top()
        self.paste_made()
        self.paste_composition()
        self.paste_data()
        self.save()

    def paste_logo(self):
        """Поместить лого на трафаретку"""

        coords = (50, 135)
        self.template.paste(self.logo, coords)

    def paste_code(self):
        """Поместить штрихкод"""

        if not self.code or len(self.code) != 13:
            return
        imgcode = Data.get_code(self.code).convert('RGBA')
        white = Image.new('RGBA', size=imgcode.size, color=(255, 255, 255, 255))
        imgcode = alpha_composite(imgcode, white)
        imgcode = imgcode.crop((1, 5, imgcode.size[0] - 1, imgcode.size[1]))
        imgcode.paste(Color.WHITE, (0, imgcode.size[1] - 28, imgcode.size[0], imgcode.size[1]))
        imgcode = replace_colors(imgcode)
        codesize = 330
        wpercent = (codesize / float(imgcode.size[0]))
        hsize = int((float(imgcode.size[1]) * float(wpercent)))
        second = imgcode.crop((0, imgcode.size[1] - 13, imgcode.size[0], imgcode.size[1]))
        second = second.resize((codesize, int(second.size[1] * float(wpercent))))

        one = imgcode.crop((0, 118, 4, 125))
        one = one.resize((int(one.size[0] * wpercent), int(one.size[1] * wpercent)), Image.ANTIALIAS)
        two = imgcode.crop((13, 118, 90, 125))
        two = two.resize((int(two.size[0] * wpercent), int(two.size[1] * wpercent)), Image.ANTIALIAS)
        three = imgcode.crop((107, 118, 187, 125))
        three = three.resize((int(three.size[0] * wpercent), int(three.size[1] * wpercent)), Image.ANTIALIAS)

        imgcode = imgcode.resize((codesize, hsize + 20))

        imgcode.paste(second, (0, imgcode.size[1] - int(13 * wpercent)))
        self.template.paste(imgcode, (530, 477))
        self.template.paste(Color.BLACK, (290, 648, 1123, 681))
        for i, char in enumerate(self.code):
            add_text_on_image(self.image,
                              char,
                              int(13 * wpercent) + 535 + i * 22, 687,
                              size=25,
                              font=Font.TIMES)

    def paste_top(self):
        """Поместить верхнее изображение или название"""

        if self.top_image:
            self.template.paste(Data.get_image(self.top_image), (0, 0))
            return
        top_text = ' '.join(self.name.upper())  # Текст разделен пробелами
        add_text_on_image(self.image, top_text, self.template.width / 2, 15,
                          size=80, center=True, fill=Color.WHITE)

    def paste_made(self):
        """Поместить текст кем сделано"""

        add_group_text(self.image, Data.get_made_text(), 630, 265, font=Font.TIMES)

    def paste_composition(self):
        """Поместить состав"""

        sizetext = 19
        hightext = 17
        widthwrap = 79
        composition = 'Состав: {}'.format(self.composition)
        if len(list(textwrap.wrap('{}. {} {}'.format(self.what, composition, self.bold_text), widthwrap - 4))) > 6:
            sizetext = 17
            hightext = 15
            widthwrap = 88
        tempfont = ImageFont.truetype(Font.TIMES, sizetext)
        w, h = add_text_on_image(self.image, '{}'.format(self.what) + '.', 364, 141, font=Font.TIMESBOLD)
        kol = 1
        while True:
            wd, hd = self.image.textsize('A{}'.format('a' * (kol + 1)), font=tempfont)
            if wd >= 1060 - 355 - w:
                break
            kol += 1
        firsttext = textwrap.wrap(composition, kol)[0]
        add_text_on_image(self.image, firsttext, 365 + w, 142, font=Font.TIMES, size=sizetext)
        wrappedcomposition = textwrap.wrap((composition[len(firsttext):]).strip(), widthwrap)
        add_group_text(self.image, wrappedcomposition, 365, 142 + hightext, font=Font.TIMES, h=hightext)
        if not wrappedcomposition:
            return
        w, h = self.image.textsize(wrappedcomposition[-1], font=tempfont)
        tempbold = ImageFont.truetype(Font.TIMESBOLD)
        count = len(wrappedcomposition) - 1
        if not self.bold_text:
            return
        for fat in self.bold_text.split(' '):
            fat = ' ' + fat
            wo, h = self.image.textsize(fat, font=tempbold)
            if w + wo > 725:
                w = 0
                count += 1
                fat = fat.strip()
                wo, h = self.image.textsize(fat, font=tempbold)
            add_text_on_image(self.image, fat, 365 + w, 142 + hightext + hightext * count, font=Font.TIMESBOLD)
            w += wo

    def paste_data(self):
        """Разместить прочую информацию"""

        # Нетто
        add_text_on_image(self.image, self.netto, 130, 280, size=50 if len(self.netto) < 8 else 40)

        # Брутто
        add_text_on_image(self.image, self.brutto, 130, 360, size=50 if len(self.brutto) < 8 else 40)

        # Белки
        add_text_on_image(self.image, self.proteins + ' г', 480, 285, font=Font.TIMES, size=17)

        # Жиры
        add_text_on_image(self.image, self.fats + ' г', 480, 305, font=Font.TIMES, size=17)

        # Углеводы
        add_text_on_image(self.image, self.carbohydrates + ' г', 480, 323, font=Font.TIMES, size=17)

        # Килокалории
        add_text_on_image(self.image, self.kkal, 480, 353, font=Font.TIMES, size=17)

        # ТУ/TU
        add_text_on_image(self.image, self.tu, 487, 406, font=Font.TIMES, size=16, center=True)

        # Категория
        add_text_on_image(self.image, self.category, 140, 520, center=True, fill=Color.WHITE, size=50, textsize=200, centerh=True)

        # Срок годности
        add_text_on_image(self.image, self.shelf_life, 140, 608, center=True, size=38, font=Font.ARIAL)

        # Разбивается имя (которое справа) на коротки слова
        shortnamewrap = textwrap.wrap(self.short_name.upper(), 14)

        # И добавляется
        add_group_text(self.image, shortnamewrap, 1250, 289, font=Font.IMPACT,
                       center=True, centerh=True, size=40, h=0, textsize=313, some=True)

    def save(self):
        """Сохранить трафаретку"""

        save_name = '{} {} {} {}'.format(self.name, self.short_name, self.category, self.netto).replace('"', '')
        Save.save_template(self.template, self.category, save_name)
