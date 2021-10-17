from os import listdir, rename, system
from os.path import isfile, getmtime
from time import strftime, gmtime
import datetime
import sys


def print_at(hor, ver, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (ver, hor, text))
    sys.stdout.flush()


#   Declare Variables
system('mode con: cols=61 lines=3 & title BitFix MediaDate')
media = {'png', 'jpeg', 'jpg', 'gif', 'bmp', 'mkv', 'm4v', 'avi', 'mov', 'mod', 'wmv', 'mp4', '3gp', 'mp3', 'wav',
         '3fr', 'air', 'arw', 'bay', 'crw', 'cr2', 'cr3', 'cap', 'data', 'dcs', 'dcr', 'dng', 'drf', 'eip', 'erf',
         'fff', 'gpr', 'iiq', 'k25', 'kdc', 'mdc', 'mef', 'mos', 'mrw', 'nef', 'nrw', 'obm', 'orf', 'pef', 'ptx',
         'pxn', 'r3d', 'raf', 'raw', 'rwl', 'rw2', 'rwz', 'sr2', 'srf', 'srw', 'tif', 'x3f'}  # Last 3 rows are raws
Tags, NrOfYears, RecRows, RenameOn, ForceTag = [], datetime.datetime.now().year-1995, 5, True, ''
DateCounter, Progress, FileCount, TagCount = [[[0]*31 for _ in range(12)] for _ in range(NrOfYears)], 0, 0, 0

#   Inquire settings to execute
while True:
    system('cls')
    print('1. Normal    2. Only Stats   3. Force Tag')
    x = input()
    if x in ['1', '2', '3']:
        if x == '2':
            RenameOn = False
        elif x == '3':  
            system('cls')
            print('Enter tag')
            ForceTag = input()
        break
system('cls')
print('\n     |                    Setting up                   |')

#   Load files and their dates
files, media = [f for f in listdir('.') if isfile(f) and f[f.rfind('.')+1:].lower() in media], None
dates = [strftime("%Y-%m-%d %H.%M.%S", gmtime(getmtime(f) + 7200)) for f in files]

#   Specify one date per file
for i, f in enumerate(files):
    # Check if file name contains date
    dig = ''.join([c for c in f if c.isdigit()])
    if (dig[0:2] == '19' or dig[0:2] == '20') and len(dig) >= 8 and int(dig[4:6]) <= 12 and int(dig[6:8]) <= 31:
        if len(dig) < 14 or int(dig[8:10]) > 23 or int(dig[10:12]) > 59 or int(dig[12:14]) > 59:
            time = ''.join([c for c in dates[i] if c.isdigit()])[8:14]
            dat = [dig[0:4], dig[4:6], dig[6:8], time[0:2], time[2:4], time[4:6]]
        else:
            dat = [dig[0:4], dig[4:6], dig[6:8], dig[8:10], dig[10:12], dig[12:14]]
        dates[i] = '-'.join(dat[0:3]) + ' ' + '.'.join(dat[3:6])
    DateCounter[int(dates[i][0:4])-1996][int(dates[i][5:7])-1][int(dates[i][8:10])-1] += 1

#   Rename files
for i, f in enumerate(files):
    # Find any tag for file
    tag = f.replace(')', '(').split('(')
    if ForceTag != '':
        tag = ' (' + ForceTag + ')'
    elif len(tag) > 2:
        loc, rgns = tag[1].split(', '), [x[0] for x in Tags] if len(Tags) > 0 else []
        area, rgn = [loc[i] for i in (0, 1)] if len(loc) > 1 else ['', loc[0]]
        if len(Tags) > 0 and rgn in rgns and area != '':
            A = rgns.index(rgn)
            if area in [x[0] for x in Tags[A][1]]:
                Tags[A][1][[x[0] for x in Tags[A][1]].index(area)][1] += 1
            else:
                Tags[A][1].append([area, 1])
        elif area != '':
            Tags.append([rgn, [[area, 1]]])
        TagCount += 1
        tag = ' (' + area + ', ' + rgn + ')'
    else:
        tag = ''

    # Adjust in case of duplicates
    checking = True
    while checking:
        checking = False
        for j in range(0, len(dates)):
            if j != i and dates[j] == dates[i]:
                sec = int(dates[i][17:19]) + 1 if int(dates[i][17:19]) < 59 else 0
                dates[i] = dates[i][0:17] + '%02d' % sec
                checking = True
                break
    if RenameOn:
        rename(f, dates[i] + tag + f[f.rfind('.'):].lower())
    FileCount += 1

    # Print out progression
    if Progress != int((i + 1)/len(files)/.01):
        Progress = int((i + 1)/len(files)/.01)
        system('cls')
        print('\n     |' + ''.join([char*int(Progress*.49) for char in '-']), end='')
        print(''.join([char*(49-int(Progress*.49)) for char in ' ']) + '|')
        print_at(30, 2, '%2d' % Progress + '%')

#   Print stats for processed media
system('cls & mode con: cols=61 lines=' + str(NrOfYears+RecRows+5))
print('     | Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec |')
recs = [[0]*4 for _ in range(RecRows*2)]
for i, y in enumerate(DateCounter):
    print(str(1996 + i) + ' |                                                 |')
    for j, m in enumerate(y):
        print_at(8+4*j, 2+i, ('%2d' % sum(m) if sum(m) > 0 else ' -'))
        for k, d in enumerate(m):
            for x1 in range(len(recs)):
                if d > recs[x1][3]:
                    for x2 in range(len(recs)-1, x1, -1):
                        recs[x2] = recs[x2-1].copy()
                    recs[x1] = [1996+i, j+1, k+1, d]
                    break
print()
for i in range(RecRows):
    print('%2d:%3d' % (i+1, recs[i][3]) + ' Files (%4d-%02d-%02d)' % tuple(recs[i][0:3]), end='     ')
    print('%2d:%3d' % (i+RecRows+1, recs[i+RecRows][3]) + ' Files (%4d-%02d-%02d)' % tuple(recs[i+RecRows][0:3]))
print('\n  Media counted: %d/%d    Unique Tags: %d/%d' % (FileCount, len(files), len(Tags), TagCount))
input()
