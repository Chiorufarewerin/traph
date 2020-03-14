import re
import os
import textwrap
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

from utils import alpha_composite, replace_color
from data import Data, Font, Color


def add_text_on_image(draw, text, x, y, size=20, font=Font.IMPACT, fill=Color.BLACK, center=False,centerh=False, textsize=0):
    if textsize: size = max_size(draw, text, textsize, font)
    font = ImageFont.truetype(font, size)
    w, h = draw.textsize(text, font=font)
    draw.text((x-w/2 if center else x, y-h/2 if centerh else y), text, fill=fill, font=font)
    return w,h


def add_group_text(draw, text, x, y, h=25, size=20, font=Font.IMPACT, fill=Color.BLACK, center=False, centerh=False, textsize=0, some=False):
    if textsize:
        maxlen=0
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font,size))
            if maxlen < width:
                maxlen = width
                bigtext=line
        size = max_size(draw, bigtext, textsize, font)
    avgheight = 0
    if centerh and len(text)>1:
        centerhsize = 0
        sizes = list()
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font,size))
            centerhsize += height + (height-h)
            sizes.append(height)
        avgheight = sum(sizes) / float(len(sizes))
        y -=centerhsize/2 - (avgheight-h) - avgheight/2 * (len(text) - 2)
        if some:        
            y += avgheight/2
        
    for line in text:
        tempw, temph = add_text_on_image(draw, line, x, y, size, font, fill, center, centerh)
        y += h
        if some:
            y += avgheight

def max_size(draw, text,textsize,fonttext):
    size = 200
    w=99999
    while(w>textsize):
        size-=1
        font = ImageFont.truetype(fonttext, size)
        w, h = draw.textsize(text, font=font)
    return size

def add_composition(draw, what, name, composition, fats):
    sizetext = 19
    hightext = 17
    widthwrap=79
    if len(list(textwrap.wrap('{}'.format(what)+'. Состав: '+ composition+' '+ fats,widthwrap-4)))>6:
       sizetext=17
       hightext=15
       widthwrap=88
    composition = 'Состав: '+composition
    tempfont = ImageFont.truetype(TIMES, sizetext)
    w,h = add_text_on_image(draw, '{}'.format(what) + '.', 364, 141, font=TIMESBOLD)
    kol = 1
    while True:
        wd, hd = draw.textsize('A'+'a'*(kol+1), font=tempfont)
        if wd >= 1060-355-w:
            break
        kol+=1
    firsttext = textwrap.wrap(composition,kol)[0]
    add_text_on_image(draw, firsttext, 365+w, 142, font=TIMES,size=sizetext)
    wrappedcomposition = textwrap.wrap((composition[len(firsttext):]).strip(),widthwrap)
    add_group_text(draw, wrappedcomposition, 365, 142+hightext, font=TIMES, h=hightext)
    if not wrappedcomposition:
        return
    w,h = draw.textsize(wrappedcomposition[-1], font=tempfont)
    tempbold = ImageFont.truetype(TIMESBOLD)
    count = len(wrappedcomposition)-1
    if not fats:
        return
    Image.alpha_composite()
    for jir in fats.split(' '):
        jir = ' '+jir
        wo,h = draw.textsize(jir, font=tempbold)
        if w+wo>725:
            w=0
            count+=1
            jir = jir.strip()
            wo,h = draw.textsize(jir, font=tempbold)
        add_text_on_image(draw, jir, 365+w, 142+hightext+hightext*count, font=TIMESBOLD)
        w+=wo
    #add_text_on_image(draw, '.', 365+w, 142+hightext+hightext*count, font=TIMES,size=sizetext)
    
def getdonetraph(name, shortname, what, netto, brutto, belki, jir, uglevodi, kkal, TU, category, composition, srok, code, fats, *args):
    template = Image.open('data/template.jpg')
    template.paste(Image.open('data/logo.jpg', 'r'), (50, 135))
    if code:
        imgcode = Image.open('codes/{}.png'.format(code)).convert('RGBA')
        white = Image.new('RGBA', size=imgcode.size, color=(255, 255, 255, 255))
        imgcode = alpha_composite(imgcode, white)
        imgcode = imgcode.crop((1, 5, imgcode.size[0]-1, imgcode.size[1]))
        imgcode.paste(Color.WHITE, (0, imgcode.size[1]-28,imgcode.size[0],imgcode.size[1]))
        imgcode = replace_color(imgcode, (0, 0, 0), Color.BLACK)
        imgcode = replace_color(imgcode, (173, 173, 173), Color.WHITE)
        codesize = 330
        wpercent = (codesize / float(imgcode.size[0]))
        hsize = int((float(imgcode.size[1]) * float(wpercent)))
        second = imgcode.crop((0, imgcode.size[1]-13, imgcode.size[0], imgcode.size[1]))
        second = second.resize((codesize, int(second.size[1]*float(wpercent))))

        one = imgcode.crop((0, 118, 4, 125))
        one = one.resize((int(one.size[0]*wpercent), int(one.size[1]*wpercent)), Image.ANTIALIAS)
        two = imgcode.crop((13, 118, 90, 125))
        two = two.resize((int(two.size[0] * wpercent), int(two.size[1] * wpercent)), Image.ANTIALIAS)
        three = imgcode.crop((107, 118, 187, 125))
        three = three.resize((int(three.size[0] * wpercent), int(three.size[1] * wpercent)), Image.ANTIALIAS)

        imgcode = imgcode.resize((codesize, hsize+20))

        imgcode.paste(second, (0, imgcode.size[1] - int(13 * wpercent)))
        if len(code)!=13:
            imgcode.paste(one, (0, int(118*wpercent)))
            imgcode.paste(two, (int(13 * wpercent)+1, int(118 * wpercent)))
            imgcode.paste(three, (int(107 * wpercent) + 1, int(118 * wpercent)))
        else:
            template.paste(imgcode, (530, 477))
            template.paste(Color.BLACK, (290, 648,1123,681))
            for i,c in enumerate(code):
                add_text_on_image(ImageDraw.Draw(template),c,int(13 * wpercent)+535+i*22,687,size=25,font=TIMES)

    image = ImageDraw.Draw(template) 
    if len(args) == 0 or len(args[0]) == 0:
        add_text_on_image(image, ''.join([letter + ' ' for letter in name.upper()]), Width / 2, 15, size=80, center=True, fill=Color.WHITE)
    else:
        template.paste(Image.open('images/{}'.format(args[0]), 'r'), (0, 0))
    add_group_text(image, open('data/made.txt', encoding='windows-1251'), 630, 265, font=TIMES)

    if len(netto) < 8:
        add_text_on_image(image, netto, 130, 280, size=50)
    else:
        add_text_on_image(image, netto, 130, 285, size=40)
    if len(brutto) < 8:
        add_text_on_image(image, brutto, 130, 360, size=50)
    else:
        add_text_on_image(image, brutto, 130, 365, size=40)
        
    add_text_on_image(image, belki+ ' г', 480, 285, font=TIMES, size=17)
    add_text_on_image(image, jir+ ' г', 480, 305, font=TIMES, size=17)
    add_text_on_image(image, uglevodi+ ' г', 480, 323, font=TIMES, size=17)
    add_text_on_image(image, kkal, 480, 353, font=TIMES, size=17)
    add_text_on_image(image, TU, 487, 406, font=TIMES, size=16, center=True) #Тут пишется текст в том месте, где ТУ
    add_text_on_image(image, category, 140, 520, center=True, fill=Color.WHITE, size=50, textsize=200, centerh=True)
    add_text_on_image(image, srok, 140, 608, center=True, size=38, font=ARIAL)
    #add_text_on_image(image, '{} «{}»'.format(what, name) + '.', 364, 141, font=TIMESBOLD)

    shortnamewrap = textwrap.wrap(shortname.upper(),14)
    #print(shortnamewrap)

    if len(shortnamewrap) < 4:
        add_group_text(image, shortnamewrap, 1250, 289, font=Font.IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    elif len(shortnamewrap) < 5:
        add_group_text(image, shortnamewrap, 1250, 289, font=Font.IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    else:
        add_group_text(image, shortnamewrap, 1250, 289, font=Font.IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    #add_group_text(image, textwrap.wrap('Состав: '+composition,81), 365, 160, font=TIMES, h=17, size=19)
    add_composition(image,what,name,composition, fats)
    
    template.save('save/{}/{} {} {} {}.jpg'.format(category, name, shortname, category, netto).replace('"', ''), 'JPEG', quality=100)
    template.save('save/{}/1/{} {} {} {}.pdf'.format(category, name, shortname, category, netto).replace('"', ''), 'PDF', resolution=100.0)

    pdf = FPDF()
    pdf.add_page()
    pdf.image('save/{}/{} {} {} {}.jpg'.format(category, name, shortname, category, netto).replace('"', ''),
              25.66875, 10.63316582, 161.25445544, 90.712209302)
    pdf.image('save/{}/{} {} {} {}.jpg'.format(category, name, shortname, category, netto).replace('"', ''),
              25.66875, 102.23316582, 161.25445544, 90.712209302)
    pdf.image('save/{}/{} {} {} {}.jpg'.format(category, name, shortname, category, netto).replace('"', ''),
              25.66875, 193.83316582, 161.25445544, 90.712209302)
    pdf.output('save/{}/3/{} {} {} {}.pdf'.format(category, name, shortname, category, netto).replace('"', ''), 'F')
    
    
def main():
    if not os.path.exists('save'):
        os.makedirs('save')
    for dir1 in ['ВЕСОВОЕ', 'ВЕСОВОЕ У', 'ФАСОВАННОЕ']:
        if not os.path.exists('save/{}'.format(dir1)):
            os.makedirs('save/{}'.format(dir1))
        for dir2 in ['1', '3']:
            if not os.path.exists('save/{}/{}'.format(dir1,dir2)):
                os.makedirs('save/{}/{}'.format(dir1,dir2))
    template = Image.open('data/template.jpg')
    global Width, Height
    Width, Height = template.size
    template.close()
    for i in list(open('example.csv', encoding='windows-1251'))[1:]:
        getdonetraph(*[re.sub('(?:""([^>]*)"")(?!>)', '«\\1»', (elem if len(elem) < 2 or (elem[0] != '"' and elem[-1] != '"') else
                                                                elem[1:-1])).strip('\n') for elem in i.split(';')])
    print('Done!')


if __name__ == '__main__':
    main()
