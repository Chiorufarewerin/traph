from PIL import Image, ImageDraw, ImageFont
import sys
import textwrap
import re
import os
from fpdf import FPDF

Width = 0
Height = 0
IMPACT = 'font/impact.ttf'
ARIAL = 'font/arial.ttf'
TIMES = 'font/times.ttf'
TIMESBOLD = 'font/timesbold.ttf'
BLACK = (27, 27, 27)
WHITE = (255, 255, 255)


def AddTextOnImage(draw, text, x, y, size=20, font=IMPACT, fill=BLACK, center=False,centerh=False, textsize=0):
    if textsize: size = maxsize(draw, text, textsize, font)
    font = ImageFont.truetype(font, size)
    w, h = draw.textsize(text, font=font)
    draw.text((x-w/2 if center else x, y-h/2 if centerh else y), text, fill=fill, font=font)
    return w,h

#КОСТЫЛЬ ЫЫЫЫЫЫЫЫЫЫЫЫЫ
def addgrouptext4(draw, text, x, y, h=25, size=20, font=IMPACT, fill=BLACK, center=False, centerh=False, textsize=0, some=False):
    if textsize:
        maxlen=0
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font,size))
            if maxlen < width:
                maxlen = width
                bigtext=line
        size = maxsize(draw, bigtext, textsize, font)
    width, height = draw.textsize('1', ImageFont.truetype(font,size))
    centerhsize = height*len(text) + (height-h)*(len(text)-1)
    y -=centerhsize/2 - height/2
    if some:        # PLEASE
        y+=height/2   # DON'T
        
    for line in text:
        tempw, temph = AddTextOnImage(draw, line, x, y, size, font, fill, center, centerh)
        y += h
        if some:        # SEE
            y += temph  # HERE

            
def addgrouptext(draw, text, x, y, h=25, size=20, font=IMPACT, fill=BLACK, center=False, centerh=False, textsize=0, some=False):
    if textsize:
        maxlen=0
        for line in text:
            width, height = draw.textsize(line, ImageFont.truetype(font,size))
            if maxlen < width:
                maxlen = width
                bigtext=line
        size = maxsize(draw, bigtext, textsize, font)
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
        tempw, temph = AddTextOnImage(draw, line, x, y, size, font, fill, center, centerh)
        y += h
        if some:
            y += avgheight

def maxsize(draw, text,textsize,fonttext):
    size = 200
    w=99999
    while(w>textsize):
        size-=1
        font = ImageFont.truetype(fonttext, size)
        w, h = draw.textsize(text, font=font)
    return size

def addsostav(draw, what, name, sostav, jirs):
    sizetext = 19
    hightext = 17
    widthwrap=79
    if len(list(textwrap.wrap('{}'.format(what)+'. Состав: '+ sostav+' '+ jirs,widthwrap-4)))>6:
       sizetext=17
       hightext=15
       widthwrap=88
    sostav = 'Состав: '+sostav
    tempfont = ImageFont.truetype(TIMES, sizetext)
    w,h = AddTextOnImage(draw, '{}'.format(what) + '.', 364, 141, font=TIMESBOLD)
    kol = 1
    while True:
        wd, hd = draw.textsize('A'+'a'*(kol+1), font=tempfont)
        if wd >= 1060-355-w:
            break
        kol+=1
    firsttext = textwrap.wrap(sostav,kol)[0]
    AddTextOnImage(draw, firsttext, 365+w, 142, font=TIMES,size=sizetext)
    wrappedsostav = textwrap.wrap((sostav[len(firsttext):]).strip(),widthwrap)
    addgrouptext(draw, wrappedsostav, 365, 142+hightext, font=TIMES, h=hightext)
    if not wrappedsostav:
        return
    w,h = draw.textsize(wrappedsostav[-1], font=tempfont)
    tempbold = ImageFont.truetype(TIMESBOLD)
    count = len(wrappedsostav)-1
    if not jirs:
        return
    Image.alpha_composite()
    for jir in jirs.split(' '):
        jir = ' '+jir
        wo,h = draw.textsize(jir, font=tempbold)
        if w+wo>725:
            w=0
            count+=1
            jir = jir.strip()
            wo,h = draw.textsize(jir, font=tempbold)
        AddTextOnImage(draw, jir, 365+w, 142+hightext+hightext*count, font=TIMESBOLD)
        w+=wo
    #AddTextOnImage(draw, '.', 365+w, 142+hightext+hightext*count, font=TIMES,size=sizetext)
    
def getdonetraph(name, shortname, what, netto, brutto, belki, jir, uglevodi, kkal, TU, category, sostav, srok, code, jirs, *args):
    template = Image.open('data/template.jpg')
    template.paste(Image.open('data/logo.jpg', 'r'), (50, 135))
    if code:
        imgcode = Image.open('codes/{}.png'.format(code)).convert('RGBA')
        white = Image.new('RGBA', size=imgcode.size, color=(255, 255, 255, 255))
        imgcode = alpha_composite(imgcode, white)
        imgcode = imgcode.crop((1, 5, imgcode.size[0]-1, imgcode.size[1]))
        imgcode.paste(WHITE, (0, imgcode.size[1]-28,imgcode.size[0],imgcode.size[1]))
        imgcode = replaceColor(imgcode, (0, 0, 0), BLACK)
        imgcode = replaceColor(imgcode, (173, 173, 173), WHITE)
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
            #one.paste( WHITE, [0,0,one.size[0],one.size[1]])
            #two.paste( WHITE, [0,0,two.size[0],two.size[1]])
            #three.paste( WHITE, [0,0,three.size[0],three.size[1]])
            #imgcode.paste(WHITE, (0, int(118*wpercent),one.size[0]+2,one.size[1]+int(118*wpercent)))
            #imgcode.paste(two, (int(13 * wpercent)+1, int(118 * wpercent)))
            #imgcode.paste(three, (int(107 * wpercent) + 1, int(118 * wpercent)))
            #AddTextOnImage(ImageDraw.Draw(imgcode),code[0],0,int(118*wpercent)-7,size=19,font=TIMES)
            #for i, c in enumerate(code[1:7]):
            #   AddTextOnImage(ImageDraw.Draw(imgcode),c,int(13 * wpercent)+2+i*22,int(118*wpercent)-7,size=19,font=TIMES)
            #for i, c in enumerate(code[7:]):
            #   AddTextOnImage(ImageDraw.Draw(imgcode),c,int(107 * wpercent) + 2+i*22,int(118*wpercent)-7,size=19,font=TIMES)
            template.paste(imgcode, (530, 477))
            template.paste(BLACK, (290, 648,1123,681))
            for i,c in enumerate(code):
                AddTextOnImage(ImageDraw.Draw(template),c,int(13 * wpercent)+535+i*22,687,size=25,font=TIMES)

    image = ImageDraw.Draw(template) 
    if len(args) == 0 or len(args[0]) == 0:
        AddTextOnImage(image, ''.join([letter + ' ' for letter in name.upper()]), Width / 2, 15, size=80, center=True, fill=WHITE)
    else:
        template.paste(Image.open('images/{}'.format(args[0]), 'r'), (0, 0))
    addgrouptext(image, open('data/made.txt', encoding='windows-1251'), 630, 265, font=TIMES)

    if len(netto) < 8:
        AddTextOnImage(image, netto, 130, 280, size=50)
    else:
        AddTextOnImage(image, netto, 130, 285, size=40)
    if len(brutto) < 8:
        AddTextOnImage(image, brutto, 130, 360, size=50)
    else:
        AddTextOnImage(image, brutto, 130, 365, size=40)
        
    AddTextOnImage(image, belki+ ' г', 480, 285, font=TIMES, size=17)
    AddTextOnImage(image, jir+ ' г', 480, 305, font=TIMES, size=17)
    AddTextOnImage(image, uglevodi+ ' г', 480, 323, font=TIMES, size=17)
    AddTextOnImage(image, kkal, 480, 353, font=TIMES, size=17)
    AddTextOnImage(image, TU, 487, 406, font=TIMES, size=16, center=True) #Тут пишется текст в том месте, где ТУ
    AddTextOnImage(image, category, 140, 520, center=True, fill=WHITE, size=50, textsize=200, centerh=True)
    AddTextOnImage(image, srok, 140, 608, center=True, size=38, font=ARIAL)
    #AddTextOnImage(image, '{} «{}»'.format(what, name) + '.', 364, 141, font=TIMESBOLD)

    shortnamewrap = textwrap.wrap(shortname.upper(),14)
    #print(shortnamewrap)

    if len(shortnamewrap) < 4:
        addgrouptext(image, shortnamewrap, 1250, 289, font=IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    elif len(shortnamewrap) < 5:
        addgrouptext(image, shortnamewrap, 1250, 289, font=IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    else:
        addgrouptext(image, shortnamewrap, 1250, 289, font=IMPACT,
                 center=True, centerh=True, size=40, h=0, textsize=313, some=True)
    #addgrouptext(image, textwrap.wrap('Состав: '+sostav,81), 365, 160, font=TIMES, h=17, size=19)
    addsostav(image,what,name,sostav, jirs)
    
    template.save('save/{}/{} {} {} {}.jpg'.format(category, name, shortname, category, netto).replace('"', ''), 'JPEG', quality=100)
    template.save('save/{}/1/{} {} {} {}.pdf'.format(category, name, shortname, category, netto).replace('"', ''), 'PDF', resolution=100.0)

    '''
    SIZEA, SIZEB = 3307, 4677
    template = template.resize((int(template.size[0]*(1417/template.size[1])), 1417))
    imagepaste = Image.new('RGB', (SIZEA, SIZEB//3), WHITE)
    leftx, lefty = imagepaste.size[0]//2 - template.size[0]//2, imagepaste.size[1]//2 - template.size[1]//2
    imagepaste.paste(template, (leftx, lefty))
    drawimagepaste = ImageDraw.Draw(imagepaste)
    drawimagepaste.line((leftx+1, 0 , leftx+1, lefty - 30), fill=BLACK, width=2)
    drawimagepaste.line((leftx-80, lefty +1, leftx - 30, lefty+1), fill=BLACK, width=2)
    drawimagepaste.line((leftx + template.size[0]-1, 0 , leftx +template.size[0]-1, lefty - 30), fill=BLACK, width=2)
    drawimagepaste.line((leftx+80+ template.size[0], lefty+1 , leftx + 30+ template.size[0], lefty+1), fill=BLACK, width=2)
    drawimagepaste.line((leftx+1, lefty + 30+ template.size[1], leftx+1, imagepaste.size[1]), fill=BLACK, width=2)
    drawimagepaste.line((leftx-80, lefty + template.size[1]-1, leftx - 30, lefty+ template.size[1] -1), fill=BLACK, width=2)
    drawimagepaste.line((leftx + template.size[0]-1, lefty + 30+ template.size[1], leftx + template.size[0]-1, imagepaste.size[1]), fill=BLACK, width=2)
    drawimagepaste.line((leftx + template.size[0] + 80, lefty + template.size[1]-1, leftx + 30+ template.size[0], lefty+ template.size[1]-1), fill=BLACK, width=2)
    a4image = Image.new('RGB', (SIZEA, SIZEB), WHITE)
    a4image.paste(imagepaste, (0,0))
    a4image.paste(imagepaste, (0,SIZEB//3))
    a4image.paste(imagepaste, (0,SIZEB//3 * 2))

    a4image.save('save/{}/3/{} {} {} {}.pdf'.format(category, name, shortname, category, netto).replace('"', ''), 'PDF', resolution=100.0)
    '''
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
