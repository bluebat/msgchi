#!/usr/bin/python3
# -*- coding: utf-8 -*-

name = 'msgchi'
version = '1.5'
copyright = 'GPL (C) Wei-Lun Chao <bluebat@member.fsf.org>, 2020'

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Creating a translation catalog for chinese locales.
The input file is a template POT file, or a translated PO file for another chinese language.
Dictionaries are UTF-8 encoded text files with the format in each line:
Source Words|Translated Words
(Source Words are lower case; Source Words with pre/surfix '-' or '"' for internal use.)
(Excluded single word: be,being,been,am,are,is,was,were;have,having,has,had)
"""

import sys, os, re, time, optparse, gettext

class MyHelpFormatter(optparse.IndentedHelpFormatter):
    def __init__(self):
        optparse.IndentedHelpFormatter.__init__(self,max_help_position=48)

class Knowns:
    def __init__(self):
        self.credit = os.environ['USER']+' <'+os.environ['LOGNAME']+'@'+re.sub(r'^[^\.]*\.','',os.environ['HOSTNAME'])+'>'
        self.confpath = os.environ['HOME']+'/.config/msgchi/'
        self.wrapcolumn = 76
        self.xmltag = r'(^[^<]*)(<[^>]*>)(.*$)'
        self.locale = re.sub(r'([a-z_A-Z]*).*', r'\1', os.environ['LANG'])
        self.localedic = {}
        self.localedic['zh_TW'] = ['zht','Chinese (traditional)','zh-l10n@linux.org.tw']
        self.localedic['zh_CN'] = ['zhc','Chinese (simplified)','i18n-zh@googlegroups.com']
        self.localedic['zh_HK'] = ['zhh','Chinese (Hongkong)','hant-l10n@freelists.org']
        self.localedic['cmn_TW'] = ['cmn','Mandarin Chinese','hant-l10n@freelists.org']
        self.localedic['hak_TW'] = ['hak','Hakka Chinese','hant-l10n@freelists.org']
        self.localedic['nan_TW'] = ['nan','Min Nan Chinese','hant-l10n@freelists.org']
        self.localedic['lzh_TW'] = ['lzh','Literary Chinese','hant-l10n@freelists.org']
        self.localedic['yue_HK'] = ['yue','Yue Chinese','hant-l10n@freelists.org']

class Arguments:
    def __init__(self):
        parser = optparse.OptionParser(usage=_('%prog [options] [input files]')+'\nv'+version+', '+copyright,formatter=MyHelpFormatter())
        parser.add_option('-a','--accelerator',dest='accelerator',metavar='""|_|&|"~"',default='',help=_('define keyboard accelerator'))
        parser.add_option('-c','--credit',dest='credit',metavar='"NAME <EMAIL>"',default=knowns.credit,help=_('credit of the translator'))
        parser.add_option('-d','--dictionary',dest='dicFile',action='append',metavar='FILE',default=[],help=_('name of the dictionary file'))
        parser.add_option('-e','--expression',dest='expression',metavar='"(^)(.*)($)"',default='',help=_('message regular expression'))
        parser.add_option('-F','--fuzzyfree',dest='fuzzyfree',action='store_true',default=False,help=_('force messages fuzzy-free'))
        parser.add_option('-k','--keep',dest='keep',action='store_true',default=False,help=_('keep translated msgstr'))
        parser.add_option('-l','--language',dest='lang',metavar='ABC2XYZ',default='',help=_('source and target languages'))
        parser.add_option('-m','--mapped',dest='mapped',action='store_true',default=False,help=_('full-mapped messages only'))
        parser.add_option('-n','--msgno',dest='msgno',action='store_true',default=False,help=_('number all messages'))
        parser.add_option('-o','--output',dest='outputFile',metavar='FILE',default='',help=_('name of the output file'))
        parser.add_option('-p','--package',dest='package',metavar='NAME-VERSION',default='',help=_('package name and version'))
        parser.add_option('-s','--skip',dest='skip',action='store_true',default=False,help=_('skip completed msgid'))
        parser.add_option('-t','--type',dest='type',metavar='po|prg|ini|txt',default='',help=_('message file type'))
        parser.add_option('-w','--wrap',dest='wrap',action='store_true',default=False,help=_('wrap long messages'))
        parser.add_option('-x','--exclude',dest='exclude',metavar='RE',default='',help=_('excluded regular expression'))
        parser.add_option('-X','--xmltag',dest='xmltag',action='store_false',default=True,help=_('text in XML tags not excluded'))
        (self.opts, self.pars) = parser.parse_args()

        if not os.path.isdir(os.environ['HOME']+'/.config'):
            os.mkdir(os.environ['HOME']+'/.config')
        if not os.path.isdir(knowns.confpath):
            os.mkdir(knowns.confpath)
        if self.opts.credit != knowns.credit:
            handle = open(knowns.confpath+'credit', 'w', encoding='utf-8')
            handle.write(self.opts.credit)
            handle.close()
        elif os.path.isfile(knowns.confpath+'credit'):
            handle = open(knowns.confpath+'credit', 'r', encoding='utf-8')
            self.opts.credit = handle.read()
            handle.close()
        if self.opts.lang:
            knowns.locale = [k for k,v in knowns.localedic.items() if v[0]==self.opts.lang[-3:]]
            if knowns.locale:
                knowns.locale = knowns.locale[0]
            else:
                sys.exit(_('invalid option format %s for languages') % self.opts.lang)
        elif knowns.locale in knowns.localedic:
            self.opts.lang = 'eng2'+knowns.localedic[knowns.locale][0]
        else:
            knowns.locale = 'cmn_TW'
            self.opts.lang = 'eng2cmn'
        for directory in ['./',knowns.confpath,'/usr/share/msgchi/']:
            if os.path.isfile(directory+self.opts.lang+'.dic'):
                self.opts.dicFile.append(directory+self.opts.lang+'.dic')
        if not self.opts.dicFile:
            sys.exit(_('desired %s or the specified dictionary not found') % self.opts.lang)
        if self.opts.expression:
            if self.opts.type:
                sys.exit(_('can not use both --expression and --type'))
            if not re.match(r'\(.*\)\(.*\)\(.*\)', self.opts.expression):
                sys.exit(_('invalid message regular expression %s') % self.opts.expression)
        elif self.opts.type == 'po' or not self.opts.type:
            self.opts.accelerator = self.opts.accelerator if self.opts.accelerator else '_&'
        elif self.opts.type == 'prg':
            self.opts.expression = '(^.*=>? ?[\'\"])(.*)([\'\"][^\'\"A-Za-z]*$)'
        elif self.opts.type == 'ini':
            self.opts.expression = '(^[_A-Za-z].*= *)(.*)($)'
        elif self.opts.type == 'txt':
            self.opts.expression = '(^)(.*)($)'
#        elif self.opts.type == 'ts' and self.opts.lang[:3] != 'eng':
#            self.opts.expression = '(^\s*<translation>)(.*)(</translation>$)'
        else:
            sys.exit(_('invalid message file type %s') % self.opts.type)
        if self.pars:
            for inputFile in self.pars:
                if not os.path.isfile(inputFile):
                    sys.exit(_('input file %s not found') % inputFile)
        else:
            self.pars.append('')

class Translator:
    def __init__(self):
        self.dictionary = {}
        for dictionary in arguments.opts.dicFile:
            handle = open(dictionary, 'r', encoding='utf-8')
            for line in handle:
                if not line.startswith('#') and line.count('|') == 1:
                    [key, value] = line.strip('\n').split('|')
                    if arguments.opts.lang[:3] == 'eng':
                        key = re.sub(r'([^ \\\'\._\-A-Za-z%\$])([A-Za-z\']{2,})', r'\1 \2', key)
                        key = re.sub(r'([A-Za-z\']{2,})([^ _\'\-0-9A-Za-z%])', r'\1 \2', key)
                        key = tuple(key.split())
                    if key[0] not in self.dictionary:
                        self.dictionary[key[0]] = []
                    length = len(key)
                    for i in range(length-len(self.dictionary[key[0]])):
                        self.dictionary[key[0]].append({})
                    self.dictionary[key[0]][length-1][key] = value
                elif not line.startswith('#') and len(line) != 1:
                     sys.stderr.write(_('Unformated entry: %s (use | as separator)') % line)
            handle.close()
    def chi2chi(self, content):
        if arguments.opts.exclude:
            content = re.sub(arguments.opts.exclude, r'', content) #remove excluded RE
        if -1 < content.find('(_') < len(content)-3:
            replacement = r'(_'+content[content.find('(_')+2].upper()+')'
            content = re.sub(r'\(_[a-z]\)', replacement, content) #upper shortcut key
        elif -1 < content.find('(&') < len(content)-3:
            replacement = r'(&'+content[content.find('(&')+2].upper()+')'
            content = re.sub(r'\(&[a-z]\)', replacement, content) #upper shortcut key
        if arguments.opts.lang[:3] == 'zht':
            content = re.sub(r'([^\.\w])\.$', r'\1. ', content) #add space after end point
            content = re.sub(r'(\w)\.', r'\1.-', content) #protect point after alpha-numeric
            content = re.sub(r' ?(`|\')([^\']*?)\' ?', r'`-\2-`', content) #replace single quote
            content = re.sub(r' ?\\"([^"]*?)\\" ?', r'`-\1-`', content) #replace double quote
            content = re.sub(r'(\w),', r'\1,-', content) #protect comma after alpha-numeric
        result, i, lastSign, mapped = '', 0, -1, True
        while i < len(content):
            notDone = True
            keyHead = content[i]
            if keyHead in self.dictionary and keyHead != '"':
                for j in range(len(self.dictionary[keyHead]),0,-1):
                    key = content[i:i+j]
                    if (len(key) == j) and (key in self.dictionary[keyHead][j-1]):
                        if '"' in self.dictionary and len(content) == 1 and j+1<len(self.dictionary['"']) and '"'+key+'"' in self.dictionary['"'][j+1]: #just one
                            value = self.dictionary['"'][j+1]['"'+key+'"']
                        elif '"' in self.dictionary and i == 0 and j<len(self.dictionary['"']) and '"'+key in self.dictionary['"'][j]: #BOL
                            value = self.dictionary['"'][j]['"'+key]
                        elif (i+j == len(content) or ord(content[i+j])<13312 or ord(content[i+j])>40959) and j<len(self.dictionary[keyHead]) and key+'"' in self.dictionary[keyHead][j]: #EOL
                            value = self.dictionary[keyHead][j][key+'"']
                        else:
                            value = self.dictionary[keyHead][j-1][key]
                        if value: #not empty
                            if ord(value[0]) == 12295 or 13312 <= ord(value[0]) <= 40959:
                                result += ' '+value if lastSign>0 else value
                            else:
                                result += value
                            if ord(value[-1]) == 12295 or 13312 <= ord(value[-1]) <= 40959:
                                lastSign = 0
                            else:
                                lastSign = -1
                        i += j
                        notDone = False
                        break
            if notDone:
                if ord(keyHead) == 12295 or 13312 <= ord(keyHead) <= 40959:
                    result += ' '+keyHead if lastSign>0 else keyHead
                    lastSign = 0
                    mapped = False
                elif ord(keyHead) > 128 or keyHead in '()[]{}<>\/=.:|@+ "' or content[i-1] == '\\':
                    result += keyHead
                    lastSign = -1
                else:
                    result += ' '+keyHead if lastSign==0 else keyHead
                    lastSign = 1
                    if not keyHead.isupper():
                        mapped = False
                i += 1
        return '' if arguments.opts.mapped and not mapped else result
    def desurfix(self, word):
        if word.endswith(("'s","s'")):
            return word[:-2]
        elif word.endswith('i'):
            return word[:-1]
        elif word.endswith('ian'):
            return word[:-3]
        elif word.endswith('ies'):
            return word[:-3]+'y'
        elif word.endswith(('ches','shes','sses','xes','zes')):
            return word[:-2]
        elif word.endswith('s') and len(word) > 2:
            return word[:-1]
        else:
            return word
    def eng2chi(self, content):
        if arguments.opts.exclude:
            content = re.sub(arguments.opts.exclude, r'', content) #remove excluded RE
        content = content.replace("’","'").replace("annot","an not").replace("\u2026","...")
        if re.search(r'\'', content):
            content = content.replace("I'm","I am").replace("won't","will not").replace("an't","an not").replace("n%'t"," not").replace("n't"," not").replace("'re"," are").replace("ou've","ou have").replace("I've","I have")
        content = re.sub(r'(Do |Does )([^\?]*[^\? ]) ?\?', r'\2 -do ?', content) #relocate do
        content = re.sub(r'([%\w][ %\w\-]*) not found([^ \w]+|$)', r'not found \1 \2', content) #relocate not found
        content = re.sub(r'(?i)\bno (.*) found', r'not found any \1', content) #relocate no found
        content = re.sub(r'(?i)\bnot (.*) yet', r'not yet \1', content) #relocate not yet
        content = re.sub(r'(?i)\b(list|number|collection|one) of ([a-z ]{3,}?)s([^\w]+|$)', r'\2s \1 of\3', content) #relocate of plural
        content = re.sub(r'(?i)^(error occurred while|error occurred on|error while|error when|error) ([ %\w\-\(\)`\'"_&]*[\w\)\'"])', r'\2 -Error', content) #relocate head words
        content = re.sub(r'(?i)^(failed to|failure to|delay before) ([ %\w\-\(\)`\'"_&]*[\w\)\'"])', r'\2 -\1', content) #relocate head words
        if re.search(r'(`|\'|\\").*?(\'|\\")', content):
            content = re.sub(r'(`|\')([^\']*?)\'', r'`- \2 -`', content) #replace single quote
#            content = re.sub(r'(`|\')([^\']*?)\'', r'\2', content) #remove single quote
            content = re.sub(r'\\"([^"]*?)\\"', r'`- \1 -`', content) #replace double quote
            content = re.sub(r'([^ ])`- ', r'\1 `- ', content) #split end quote
            content = re.sub(r' -`([^ ])', r' -` \1', content) #split front quote
        if re.search(r', (\w{3,} and |and |\w{3,} or |or |\w{3,}, etc)', content): #replace list comma
            content = re.sub(r', (\w{3,} and |and |\w{3,} or |or |\w{3,}, etc)', r',- \1', content)
            for i in range(content.count(', ')-2):
                content = re.sub(r', (\w{3,},)', r',- \1', content)
        if re.search(r'\w{2,};\w{2,};\w{2,};', content): #protect semicolon separator
            content = re.sub(r';', r';;', content)
        content = re.sub(r'([a-z])\(s\)', r'\1', content) #remove plural mark
        content = re.sub(r'^_n?:[^\\]*\\n', r'', content) #remove comment
        if arguments.opts.accelerator:
            if '_' in arguments.opts.accelerator and re.match(r'(_[A-Za-z]|[^_]*[A-Za-z]_|[^_]*\W_[A-Za-z])[Ka-z][^_]*$', content) and re.search(r'[A-Z]', content) and not re.search(r'%\([a-z]*_[a-z]*\)|\$[a-z]*_[a-z]*', content):
                replacement = r'\1\2 (_'+content[content.find('_')+1].upper()+')'
                content = re.sub(r'_([A-Za-z])([^<>\?:,;\.\\]*)', replacement, content) #relocate shortcut key
            content = re.sub(r'&([a-z]{2,});', r'& \1 ;', content) #split html mark
            if '&' in arguments.opts.accelerator and re.match(r'(&[A-Za-z]|[^&]*[A-Za-z]&|[^&]*\W&[A-Za-z])[Ka-z][^&]*$', content) and re.search(r'[A-Z]', content):
                replacement = r'\1\2 (&'+content[content.find('&')+1].upper()+')'
                content = re.sub(r'&([A-Za-z])([^<>\?:,;\.\\]*)', replacement, content) #relocate shortcut key
            if '~' in arguments.opts.accelerator and re.match(r'(~[A-Za-z]|[^~]*[A-Za-z]~|[^~]*\W~[A-Za-z])[Ka-z][^~]*$', content) and re.search(r'[A-Z]', content):
                replacement = r'\1\2 (~'+content[content.find('~')+1].upper()+')'
                content = re.sub(r'~([A-Za-z])([^<>\?:,;\.\\]*)', replacement, content) #relocate shortcut key
        content = re.sub(r' ?([,;:!\?\.]+)( *|\\n)$', r' \1\2', content) #split punctuation at end
        content = re.sub(r'([^ \\\'\._\-A-Za-z\u00c0-\u02af%\$])([A-Za-z\u00c0-\u02af\']{2,})', r'\1 \2', content) #split words at start
        content = re.sub(r'([A-Za-z\u00c0-\u02af\']{2,})([^ _\'\-0-9A-Za-z\u00c0-\u02af%])', r'\1 \2', content) #split words at end
        content = re.sub(r'([^ "]|^[ a])\\n', r'\1 \\n', content) #split escape sequence at end
        content = re.sub(r'(\\t|\\n|\\\\|\\\\\\t)([^"\\])', r'\1 \2', content) #split escape sequence at start
        content = re.sub(r'%\( (\w*) \)([dirsu\-0-9])', r'%(\1)\2', content) #repair substituted variable
        content = re.sub(r'(>|\]|\)|%[a-z]|%[0-9][a-z]|%\([a-z]*\)[a-z])(, |\. |: |;|\?|!)', r'\1 \2', content) #split others before punctuation
        content = re.sub(r'\{ (\w*) \}', r'{\1}', content) #repair substituted variable
        content = re.sub(r'%([\-\.0-9]{0,4}) ([dfilu]{1,3})', r'%\1\2', content) #repair substituted variable
        content = re.sub(r'& ([a-z]{2,}) ;', r'&\1;', content) #repair html mark
        content = re.sub(r'([a-z_A-Z]{4,}) (\(\)[ ,;:$])', r'\1\2', content) #repair function name
        content = content.split(' ')
        result, i, onceDone, contentHead, lastSign, mapped = '', 0, True, '', -1, True
        while i < len(content):
            if onceDone:
                contentHead = content[i]
                onceDone = False
            contentLower = tuple([x.lower() for x in content])
            keyHead = contentLower[i]
            if keyHead in self.dictionary:
                keyLength = min(len(contentLower)-i, len(self.dictionary[keyHead]))
                for j in range(keyLength,0,-1):
                    keyLower = contentLower[i:i+j]
                    keyDesurfix = contentLower[i:i+j-1] + (self.desurfix(contentLower[i+j-1]),)
                    key = ''
                    if keyLower in self.dictionary[keyHead][j-1]:
                        key = keyLower
                    elif keyDesurfix in self.dictionary[keyHead][j-1]:
                        key = keyDesurfix
                    if key: #found
                        if '"' in self.dictionary and len(content) == 1 and j+1<len(self.dictionary['"']) and ('"',)+key+('"',) in self.dictionary['"'][j+1]: #just one
                            value = self.dictionary['"'][j+1][('"',)+key+('"',)]
                        elif '"' in self.dictionary and i == 0 and j<len(self.dictionary['"']) and ('"',)+key in self.dictionary['"'][j]: #BOL
                            value = self.dictionary['"'][j][('"',)+key]
                        elif (i+j == len(content) or re.match(r'[^A-Za-z]',content[i+j])) and j<len(self.dictionary[keyHead]) and key+('"',) in self.dictionary[keyHead][j]: #EOL
                            value = self.dictionary[keyHead][j][key+('"',)]
                        else:
                            value = self.dictionary[keyHead][j-1][key]
                        if value: #not empty
                            if re.match(r'[A-Za-z\'\-][A-Za-z\'\-\.,]*$',keyHead): #word-like?
                                if ord(value[0]) < 128: #ascii at begin?
                                    result += ' '+value if lastSign>=0 else value
                                else:
                                    result += ' '+value if lastSign>0 else value
                                lastSign = 1 if ord(value[-1]) < 128 else 0
                            else:
                                result += ' '+value if lastSign>=0 and value[0] in '%' else value
                                lastSign = 1 if 'a' <= value[-1] <= 'z' else -1
                        i += j
                        onceDone = True
                        break
            if not onceDone:
                if '-' in keyHead:
                    key = tuple(keyHead.lower().split('-'))
                    if 0 < len(key[0]) < 4:
                        key = (''.join(key),)
                    keyHead = key[0]
                    j = len(key)
                    if keyHead in self.dictionary and j <= len(self.dictionary[keyHead]) and key in self.dictionary[keyHead][j-1]:
                        result += ' '+self.dictionary[keyHead][j-1][key] if lastSign>0 else self.dictionary[keyHead][j-1][key]
                        lastSign = 0 #depend space
                    else:
                        result += ' '+contentHead if lastSign>=0 else contentHead
                        lastSign = 1 #with space
                        mapped = False
                    i += 1
                    onceDone = True
                elif keyHead in ('having','has','had'):
                    content[i] = 'have'
                elif keyHead == 'have':
                    content[i] = '-have'
                    j = i+1 if i < len(content)-1 and content[i+1] == 'not' else i
                    if j < len(content)-1 and content[j+1] != 'been' and content[j+1].endswith(('ed','en')):
                        content.insert(j+1,'-en')
                elif keyHead in ('being','been','am','are','is','was','were'):
                    content[i] = 'be'
                elif keyHead == 'be':
                    content[i] = '-be'
                    j = i+1 if i < len(content)-1 and content[i+1] == 'not' else i
                    if j < len(content)-1 and content[j+1].endswith(('ed','en')):
                        content.insert(j+1,'-en')
                    elif j < len(content)-1 and content[j+1].endswith('ing'):
                        content.insert(j+1,'-ing')
                elif keyHead != self.desurfix(keyHead):
                    content[i] = self.desurfix(keyHead)
                elif keyHead.endswith('ion'):
                    content[i] = keyHead[:-3]
                elif keyHead.endswith('ly'):
                    content[i] = keyHead[:-2]
                    if arguments.opts.type == 'txt':
                        content.insert(i+1,'-ly')
                elif keyHead.endswith('ing'):
                    if keyHead[-5:-4] == keyHead[-4:-3] and keyHead[-5:-4] != 's':
                        content[i] = keyHead[:-4]
                    else:
                        content[i] = keyHead[:-3]+'e'
#                    if i == len(content)-1 or not content[i+1].isalpha():
#                        content.insert(i+1,'-ing')
                elif keyHead.endswith('ed'):
                    if keyHead[-4:-3] == keyHead[-3:-2] and keyHead[-4:-3] != 's':
                        content[i] = keyHead[:-3]
                    elif keyHead[-3:-2] == 'i':
                        content[i] = keyHead[:-3]+'y'
                    else:
                        content[i] = keyHead[:-1]
                    if i < len(content)-1 and content[i+1].isalpha() and (i == 0 or content[i-1] != '-en'):
                        content.insert(i+1,'-en')
                elif keyHead.endswith('e'):
                    content[i] = keyHead[:-1]
                elif not keyHead:
                    result += ' '+contentHead if lastSign>=0 else contentHead
                    i += 1
                    onceDone = True
                    lastSign = 1
#                elif ord(keyHead[0]) > 128 or re.match(r'&[a-z]{2,};',contentHead):
#                    result += contentHead
#                    i += 1
#                    onceDone = True
#                    lastSign = -1
#                    if ord(keyHead[0]) > 128:
#                        mapped = False
                elif re.match(r'&[a-z]{2,};',contentHead):
                    result += contentHead
                    i += 1
                    onceDone = True
                    lastSign = -1
                else:
                    if keyHead.startswith('(_') or keyHead.startswith('(&') or keyHead.startswith('(~') or keyHead.startswith('()') or keyHead[0] in ')]}<>\\/=.:|@+':
                        result += contentHead
                    else:
                        result += ' '+contentHead if lastSign>=0 else contentHead
                        if not re.match(r'[A-Z]*$',contentHead):
                            mapped = False
                    i += 2 if i < len(content)-1 and content[i+1] in ['-ly','-ing','-en'] else 1
                    onceDone = True
                    lastSign = -1 if keyHead[-1] in '([{<>\\/=.:|@+' or keyHead[-2:-1] == '\\' else 1
        return '' if arguments.opts.mapped and not mapped else result

class PO:
    class Message:
        def __init__(self):
            self.comments = []
            self.fuzzy = False
            self.domain = ''
            self.msgctxt = ''
            self.msgid = ''
            self.msgid_plural = ''
            self.msgstr = ''
            self.obsolete = False
        def output(self):
            if re.search(r'\\n([^"\\])', self.msgid):
                self.msgid = re.sub(r'^(msgid)\s', r'\1 ""\n', self.msgid)
            if re.search(r'\\n([^"\\])', self.msgid_plural):
                self.msgid_plural = re.sub(r'^(msgid_plural)\s', r'\1 ""\n', self.msgid_plural)
            if re.search(r'\\n([^"\\])', self.msgstr):
                self.msgstr = re.sub(r'^(msgstr|msgstr\[0\])\s', r'\1 ""\n', self.msgstr)
            resultStr = re.sub(r'\\n([^"\\])', r'\\n"\n"\1', self.msgid + self.msgid_plural + self.msgstr) #break lines by newline
            resultList = resultStr.split('\n')
            if arguments.opts.wrap:
                for i in range(len(resultList)):
                    if not resultList[i].startswith('#'):
                        resultList[i] = re.sub(r'([\u2e80-\ufaff\U00020000-\U0002ffff])', r'\1\000', resultList[i]) #expand chinese character width
                        if len(resultList[i]) > knowns.wrapcolumn:
                            resultList[i] = re.sub(r'(.{70}[ \000])([^"])', r'\1"\n"\2', resultList[i]) #break lines by width
                        resultList[i] = resultList[i].replace('\000', '') #restore chinese character width
            if arguments.opts.fuzzyfree:
                if '#, fuzzy\n' in self.comments:
                    self.comments.remove('#, fuzzy\n')
                self.fuzzy = False    
            elif self.fuzzy and not [x for x in self.comments if 'fuzzy' in x]:
                self.comments.append('#, fuzzy\n')
            result = ''.join(self.comments) + self.domain + self.msgctxt + '\n'.join(resultList)
            if self.obsolete:
                result = re.sub(r'(?m)^(.)', r'#~ \1', result)
            return result
    def __init__(self):
        self.inputName = ''
        self.messages = []
        self.outputName = ''
    def readIn(self, filename):
        if filename:
            handle = open(filename, 'r', encoding='utf-8')
            self.inputName = filename
        else:
            handle = open(sys.stdin.fileno(), 'r', encoding='utf-8')
            self.inputName = 'STDIN'
        message = self.Message()
        section = ''
        for line in handle:
            if line.startswith('#~'):
                message.obsolete = True
                line = line[3:]
            else:
                line = line.lstrip()
            if section == 'MSGSTR' and not line.startswith(('"','msgstr[')):
                self.messages.append(message)
                message = self.Message()
            if line.startswith('#'):
                if line.startswith('#, fuzzy'):
                    message.fuzzy = True
                message.comments.append(line)
                section = 'COMMENTS'
            elif line.startswith('domain '):
                message.domain = line
                section = 'DOMAIN'
            elif line.startswith('msgctxt '):
                message.msgctxt = line
                section = 'MSGCTXT'
            elif line.startswith(('msgid ','msgid\t')):
                message.msgid = line
                section = 'MSGID'
            elif line.startswith('msgid_plural '):
                message.msgid_plural = line
                section = 'MSGID_PLURAL'
            elif line.startswith(('msgstr ','msgstr[0] ','msgstr\t','msgstr[0]\t')):
                message.msgstr = line
                section = 'MSGSTR'
            elif line.startswith('"'):
                if section == 'MSGCTXT':
                    message.msgctxt = message.msgctxt[:message.msgctxt.rfind('"')] + line[line.find('"')+1:]
                elif section == 'MSGID':
                    message.msgid = message.msgid[:message.msgid.rfind('"')] + line[line.find('"')+1:]
                elif section == 'MSGID_PLURAL':
                    message.msgid_plural = message.msgid_plural[:message.msgid_plural.rfind('"')] + line[line.find('"')+1:]
                elif section == 'MSGSTR':
                    message.msgstr = message.msgstr[:message.msgstr.rfind('"')] + line[line.find('"')+1:]
            elif not line:
                section = ''
        if message.comments or message.domain or message.msgctxt or message.msgid or message.msgstr:
            self.messages.append(message)
        handle.close()
        self.outputName = arguments.opts.outputFile
    def translate(self):
        if not arguments.opts.package:
            arguments.opts.package = re.sub(r'([\w-]+-[0-9].*)\.[^0-9]*',r'\1',os.path.basename(self.outputName if self.outputName else self.inputName))
        if not re.match(r'[\w-]+-[0-9]',arguments.opts.package):
            packageVersion = ''
            packageName = arguments.opts.package[:arguments.opts.package.find('.')] if arguments.opts.package.find('.') > -1 else arguments.opts.package
        else:
            packageVersion = re.sub(r'[\w-]+-([0-9].*)',r'\1',arguments.opts.package)
            packageName = re.sub(r'([\w-]+)-[0-9].*',r'\1',arguments.opts.package)
        self.messages[0].comments = [x.replace("THE PACKAGE'S COPYRIGHT HOLDER",'The '+packageName+' Project (msgids).').replace("ORGANIZATION",'The '+packageName+' Project (msgids).') for x in self.messages[0].comments]
        self.messages[0].comments = [x.replace('YEAR',time.strftime('%Y')).replace('PACKAGE',packageName) for x in self.messages[0].comments]
        if knowns.locale in knowns.localedic:
            for i in range(len(self.messages[0].comments)):
                self.messages[0].comments[i] = re.sub('SOME DESCRIPTIVE TITLE.', knowns.localedic[knowns.locale][1]+' translation for '+packageName+'.', self.messages[0].comments[i])
                self.messages[0].comments[i] = re.sub('(?i)chinese \((traditional|simplified|hongkong)\)', knowns.localedic[knowns.locale][1], self.messages[0].comments[i])
                self.messages[0].comments[i] = re.sub('(?i)(traditional|simplified|hongkong) chinese', knowns.localedic[knowns.locale][1], self.messages[0].comments[i])
                self.messages[0].comments[i] = re.sub('[a-z]{2,3}_(CN|HK|TW)', knowns.locale, self.messages[0].comments[i])
        if not [x for x in self.messages[0].comments if '# This file is distributed under the same license' in x]:
            self.messages[0].comments.insert(2,'# This file is distributed under the same license as the '+packageName+' package.\n')
        if self.messages[0].fuzzy:
            self.messages[0].comments.remove('#, fuzzy\n')
            self.messages[0].fuzzy = False
        if arguments.opts.credit:
            if [x for x in self.messages[0].comments if 'FIRST AUTHOR' in x]:
                self.messages[0].comments = [x.replace('FIRST AUTHOR <EMAIL@ADDRESS>',arguments.opts.credit) for x in self.messages[0].comments]
            else:
                if self.messages[0].comments and self.messages[0].comments[-1].strip() != '#':
                    self.messages[0].comments.append('#\n')
                lastCredit = '# '+re.sub(r'.*Last-Translator: ([^\\]*).*', r'\1', self.messages[0].msgstr).strip()+', '+re.sub(r'.*PO-Revision-Date: ([^-]*).*', r'\1', self.messages[0].msgstr).strip()
                if not [x for x in self.messages[0].comments if lastCredit in x] and not ('NAME' in lastCredit):
                    self.messages[0].comments.insert(-1,lastCredit+'.\n')
                if not [x for x in self.messages[0].comments if arguments.opts.credit in x]:
                    self.messages[0].comments.insert(-1,'# '+arguments.opts.credit+time.strftime(', %Y.\n'))
        if packageVersion:
            self.messages[0].msgstr = re.sub(r'Project-Id-Version: [^\\"]*', r'Project-Id-Version: '+packageName+' '+packageVersion, self.messages[0].msgstr)
        else:
            self.messages[0].msgstr = re.sub(r'Project-Id-Version: [^\\"]*', r'Project-Id-Version: '+packageName, self.messages[0].msgstr)
        self.messages[0].msgstr = re.sub(r'PO-Revision-Date: [^\\"]*', r'PO-Revision-Date: '+time.strftime('%Y-%m-%d %H:%M%z'), self.messages[0].msgstr)
        if arguments.opts.credit:
            self.messages[0].msgstr = re.sub(r'Last-Translator: [^\\"]*', r'Last-Translator: '+arguments.opts.credit, self.messages[0].msgstr)
        self.messages[0].msgstr = re.sub(r'Language-Team: [^\\"]*', r'Language-Team: '+knowns.localedic[knowns.locale][1]+' <'+knowns.localedic[knowns.locale][2]+'>', self.messages[0].msgstr)
        language = knowns.locale if len(knowns.locale)==5 else knowns.locale[:3]
        if 'Language:' in self.messages[0].msgstr:
            self.messages[0].msgstr = re.sub(r'Language: [^\\"]*', r'Language: '+language, self.messages[0].msgstr)
        else:
            self.messages[0].msgstr = re.sub(r'MIME-Version:', r'Language: '+language+'\\\\n"\n"MIME-Version:', self.messages[0].msgstr)
        self.messages[0].msgstr = re.sub(r'MIME-Version: [^\\"]*', r'MIME-Version: 1.0', self.messages[0].msgstr)
        self.messages[0].msgstr = re.sub(r'Content-Type: text/plain; charset=[^\\"]*', r'Content-Type: text/plain; charset=UTF-8', self.messages[0].msgstr)
        self.messages[0].msgstr = re.sub(r'Content-Transfer-Encoding: [^\\"]*', r'Content-Transfer-Encoding: 8bit', self.messages[0].msgstr)
        if 'Plural-Forms:' in self.messages[0].msgstr:
            self.messages[0].msgstr = re.sub(r'Plural-Forms: [^\\"]*', r'Plural-Forms: nplurals=1; plural=0;', self.messages[0].msgstr)
        else:
            self.messages[0].msgstr += '"Plural-Forms: nplurals=1; plural=0;\\n"\n'
        sourceNo = 1
        for message in self.messages[1:]:
            if message.msgid_plural:
                sourceId = message.msgid_plural[message.msgid_plural.find('"')+1:message.msgid_plural.rfind('"')]
            else:
                sourceId = message.msgid[message.msgid.find('"')+1:message.msgid.rfind('"')]
            strHead = message.msgstr[:message.msgstr.find('"')]
            sourceStr = message.msgstr[message.msgstr.find('"')+1:message.msgstr.rfind('"')]
            if not (message.obsolete or arguments.opts.skip and not message.fuzzy and sourceStr):
                if arguments.opts.msgno:
                    message.comments = [x for x in message.comments if '#. msgno ' not in x]
                    message.comments.insert(0, '#. msgno %d\n' % sourceNo)
                    sourceNo += 1
                if arguments.opts.credit and re.match(r'translator[_-]credits', sourceId):
                    resultStr = sourceStr+'\\n'+arguments.opts.credit if sourceStr else arguments.opts.credit
                elif arguments.opts.lang[:3] == 'eng':
                    resultStr = ''
                    while arguments.opts.xmltag and re.search(r'</?[a-zA-Z].*>', sourceId):
                        resultStr += translator.eng2chi(re.sub(knowns.xmltag, r'\1', sourceId))+re.sub(knowns.xmltag, r'\2', sourceId)
                        sourceId = re.sub(knowns.xmltag, r'\3', sourceId)
                    resultStr += translator.eng2chi(sourceId)
                else:
                    sourceId = sourceStr
                    resultStr = ''
                    while arguments.opts.xmltag and re.search(r'</?[a-zA-Z].*>', sourceId):
                        resultStr += translator.chi2chi(re.sub(knowns.xmltag, r'\1', sourceId))+re.sub(knowns.xmltag, r'\2', sourceId)
                        sourceId = re.sub(knowns.xmltag, r'\3', sourceId)
                    resultStr += translator.chi2chi(sourceId)
                if arguments.opts.keep and sourceStr and resultStr != sourceStr:
                    message.comments.append('# "%s"\n' % re.sub(r'\\n([^"\\])', r'\\n"\n# "\1', sourceStr))
                message.fuzzy = bool(resultStr) and (message.fuzzy or not bool(sourceStr) and not message.fuzzy)
                message.msgstr = '%s"%s"\n' % (strHead, resultStr)
    def writeOut(self):
        if not self.outputName:
            handle = open(sys.stdout.fileno(), 'w', encoding='utf-8')
        elif len(arguments.pars) == 1:
            handle = open(self.outputName, 'w', encoding='utf-8')
        else:
            handle = open(self.outputName, 'a', encoding='utf-8')
        for message in self.messages[:-1]:
            handle.write(message.output() + '\n')
        if self.messages:
            handle.write(self.messages[-1].output())
        if not handle.isatty():
            handle.close()

class NPO:
    class Message:
        def __init__(self):
            self.head = ''
            self.msgid = ''
            self.msgstr = ''
            self.tail = ''
        def output(self):
            result = self.head + self.msgstr + self.tail
            return result
    def __init__(self):
        self.inputName = ''
        self.messages = []
        self.outputName = ''
    def readIn(self, filename):
        if filename:
            handle = open(filename, 'r', encoding='utf-8')
            self.inputName = filename
        else:
            handle = open(sys.stdin.fileno(), 'r', encoding='utf-8')
            self.inputName = 'STDIN'
        newMessage = True
        expressionHead = re.sub(r'\([^\)]*\)$', r'', arguments.opts.expression)
        expressionTail = re.sub(r'^\([^\)]*\)', r'', arguments.opts.expression)
        for line in handle:
            message = self.Message()
            newLine = line[-1] == '\n'
            line = line.rstrip()
            if re.match(arguments.opts.expression, line):
                message.head = re.sub(arguments.opts.expression, r'\1', line)
                message.msgid = re.sub(arguments.opts.expression, r'\2', line)
                message.tail = re.sub(arguments.opts.expression, r'\3', line)
                newMessage = True
            elif newMessage and re.match(expressionHead, line) and not arguments.opts.wrap:
                message.head = re.sub(expressionHead, r'\1', line)
                message.msgid = re.sub(expressionHead, r'\2', line)
                newMessage = False
            elif not newMessage and re.match(expressionTail, line):
                message.msgid = re.sub(expressionTail, r'\1', line)
                message.tail = re.sub(expressionTail, r'\2', line)
                newMessage = True
            elif not newMessage:
                message.msgid = line
                newMessage = False
            else:
                message.tail = line
            message.tail += '\n' if newLine else ''
            self.messages.append(message)
        handle.close()
        self.outputName = arguments.opts.outputFile
    def translate(self):
        for message in self.messages:
            sourceId = message.msgid
            message.msgstr = ''
            if arguments.opts.lang[:3] == 'eng':
                while arguments.opts.xmltag and re.search(r'</?[a-zA-Z].*>', sourceId):
                    message.msgstr += translator.eng2chi(re.sub(knowns.xmltag, r'\1', sourceId))+re.sub(knowns.xmltag, r'\2', sourceId)
                    sourceId = re.sub(knowns.xmltag, r'\3', sourceId)
                message.msgstr += translator.eng2chi(sourceId)
            else:
                while arguments.opts.xmltag and re.search(r'</?[a-zA-Z].*>', sourceId):
                    message.msgstr += translator.chi2chi(re.sub(knowns.xmltag, r'\1', sourceId))+re.sub(knowns.xmltag, r'\2', sourceId)
                    sourceId = re.sub(knowns.xmltag, r'\3', sourceId)
                message.msgstr += translator.chi2chi(sourceId)
            if arguments.opts.keep and message.msgid and message.msgstr != message.msgid:
                if arguments.opts.type == 'prg':
                    message.tail = message.tail.strip('\n') + ' //' + message.msgid + '\n'
                else:
                    message.tail += '# ' + message.msgid + '\n'
    def writeOut(self):
        if not self.outputName:
            handle = open(sys.stdout.fileno(), 'w', encoding='utf-8')
        elif len(arguments.pars) == 1:
            handle = open(self.outputName, 'w', encoding='utf-8')
        else:
            handle = open(self.outputName, 'a', encoding='utf-8')
        for message in self.messages:
            handle.write(message.output())
        if not handle.isatty():
            handle.close()

if __name__ == '__main__':
    gettext.textdomain(name)
    _ = gettext.gettext
    knowns = Knowns()
    arguments = Arguments()
    translator = Translator()
    for inputFile in arguments.pars:
        handleIn = NPO() if arguments.opts.expression else PO()
        try:
            handleIn.readIn(inputFile)
        except:
            sys.exit(_('Error reading %s. Not UTF-8 encoded?') % inputFile)
        if handleIn.messages:
            handleIn.translate()
        handleIn.writeOut()
