#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Simple EPL2 lib for Python.
Copyright (c) 2018 Paul Beltyukov (beltyukov.p.a@gmail.com)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from enum import Enum
from PIL import Image

#Codepage
class epl2_cp(Enum):
    DOS437  = ('0',  'cp437')# English - US
    DOS850  = ('1',  'cp850')# Latin 1
    DOS852  = ('2',  'cp852')# Latin 2 (Cyrillic II/Slavic)
    DOS860  = ('3',  'cp860')# Portuguese
    DOS863  = ('4',  'cp863')# French, Canadian
    DOS865  = ('5',  'cp865')# Nordic
    DOS857  = ('6',  'cp857')# Turkish
    DOS861  = ('7',  'cp861')# Icelandic
    DOS862  = ('8',  'cp862')# Hebrew
    DOS855  = ('9',  'cp855')# Cyrillic
    DOS866  = ('10', 'cp866')# Cyrillic CIS 1
    DOS737  = ('11', 'cp737')# Greek
    DOS851  = ('12', 'cp851')# Greek 1
    DOS869  = ('13', 'cp869')# Greek 2
    WIN1252 = ('A', 'cp1252')# Latin 1
    WIN1250 = ('B', 'cp1250')# Latin 2
    WIN1251 = ('C', 'cp1251')# Cyrillic
    WIN1253 = ('D', 'cp1253')# Greek
    WIN1254 = ('E', 'cp1254')# Turkish
    WIN1255 = ('F', 'cp1255')# Hebrew

#KDU Country Code
class epl2_cc(Enum):
    Belgium      = '032'
    Canada       = '002'
    Denmark      = '045'
    Finland      = '358'
    France       = '033'
    Germany      = '049'
    Netherlands  = '031'
    Italy        = '039'
    LatinAmerica = '003'
    Norway       = '047'
    Portugal     = '351'
    SouthAfrica  = '027'
    Spain        = '034'
    Sweden       = '046'
    Swizerland   = '041'
    UK           = '044'
    USA          = '001'
    
class epl2_rot(Enum):
    r0   = 0
    r90  = 1
    r180 = 2
    r270 = 3
    
class epl2_font(Enum):
    #203dpi
    d203_8x12      = '1'
    d203_10x16     = '2'
    d203_12x20     = '3'
    d203_14x24     = '4'
    d203_32x48     = '5'
    d203_n14x19_1  = '6' #Numeric 1
    d203_n14x19_2  = '7' #Numeric 2
    #Asian printers only
    d203_scjk24x24 = '8' #Simplified Chinese, Japanese, Korean
    #300dpi
    d300_8x12      = '1'
    d300_10x16     = '2'
    d300_12x20     = '3'
    d300_14x24     = '4'
    d300_32x48     = '5'
    d300_n14x19_1  = '6' #Numeric 1
    d300_n14x19_2  = '7' #Numeric 2
    #Asian printers only
    d300_scjk24x24 = '8' #Simplified Chinese, Japanese, Korean
    d300_scjk      = '9' #Simplified Chinese, Japanese, Korean 24x36/36x36

#Horisontal image crop
class epl2_crop(Enum):
    L = 1 #Left
    R = 2 #Right
    C = 3 #Center

class epl2_gen(object):
    def __init__(self, cp, cc, h, w, d, s):
        self.cp = cp #Codepage
        self.cc = cc #country code
        self.h  = h  #(H, h) where h is spacing
        self.w  = w  #w
        self.d  = d  #Darkness
        self.s  = s  #speed
        
    def _enc(self, c):
        return c.encode(self.cp[1])
    
    def _cmd(self, c):
        self._enc(c + '\n')
        
    def text(self, x,y,rot,font,sx,sy,inv,txt):
        '''
        TODO: add arg check
        '''
        command = 'A%d,%d,%d,%s,%d,%d,%s,%s\n' % (
                int(x),
                int(y),
                int(rot),
                str(font),
                int(sx),
                int(sy),
                str(inv),
                str(txt)
                )
        return self._cmd(command)
    
    def img(self, x, y, im, crop):
        '''
        TODO: add arg check
        '''
        w,h = im.size
        #Printer needs octets 
        #PIL may give us one extra octet per line with black dots on the rigth
        w_epl = (w // 8) * 8
        
        if crop == epl2_crop.L:
            #Left
            s = 0
        elif crop == epl2_crop.C:
            #Center
            s = (w - w_epl)//2
        else:
            #Right
            s = (w - w_epl)
        
        e = s + w_epl
        #Image width in octets
        w_epl //= 8
        #Crop an image part to have a multiple of 8 width
        crop = im.crop((s,0,e,h))
        
        cmd  = self._enc('GW%d,%d,%d,%d,'%(int(x), int(y), int(w_epl), int(h)))
        cmd += crop.tobytes()
        cmd += self._enc('\n')
        
        return cmd
    
    def new(self):
        return self._cmd('\nN')
    
    def pr(self,n):
        return self._cmd('P%d' % int(n))
        
    def setup(self):
        cmd  = self._cmd('q%d' % int(self.w))
        cmd += self._cmd('Q%d%d' % (int(self.h[0]), int(self.h[1])))
        cmd += self._cmd('ZT')
        cmd += self._cmd('S%d' % int(self.s))
        cmd += self._cmd('D%d' % int(self.d))
        cmd += self._cmd('O')
        cmd += self._cmd('UN')
        cmd += self._cmd('I8,%s,%s' % (str(self.cp[0]), str(self.cc)))
        cmd += self._cmd('JF')
        
        return cmd
