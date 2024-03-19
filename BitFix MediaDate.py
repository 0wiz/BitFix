from os import listdir, rename, system
from os.path import isfile, getmtime
from pathlib import Path
from time import strftime, gmtime
from PIL import Image
from datetime import datetime
import sys

#   Geometric Constants
MENU_WIDTH = 51
RECORD_DIMENSIONS = [5, 2] # Rows and Columns of record media per day to be displayed when printing stats
RECORD_COUNT = sum(RECORD_DIMENSIONS)

system('mode con: cols=' +str(MENU_WIDTH) + ' lines=3 & title BitFix MediaDate')
Video_formats = ['mkv', 'm4v', 'm2v', 'avi', 'mov', 'qt', 'mod', 'wmv', 'mp4', 'm4p', 'mp3', 'mp2', 'mpg', 'mpeg',
        'mpe', 'mpv', '3gp', '3g2', 'wav', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'drc', 'svi', 'vob', 'ogv', 'ogg',
        'mng', 'mts','m2ts', 'ts', 'webm', 'rm', 'rmvb', 'viv', 'amv', 'yuv']
Image_formats = ['png', 'jpeg', 'jpg', 'gif', 'bmp',
        '3fr', 'air', 'arw', 'bay', 'crw', 'cr2', 'cr3', 'cap', 'data', 'dcs', 'dcr', 'dng', 'drf', 'eip', 'erf',
        'fff', 'gpr', 'iiq', 'k25', 'kdc', 'mdc', 'mef', 'mos', 'mrw', 'nef', 'nrw', 'obm', 'orf', 'pef', 'ptx',
        'pxn', 'r3d', 'raf', 'raw', 'rwl', 'rw2', 'rwz', 'sr2', 'srf', 'srw', 'tif', 'x3f'] # Last 3 rows are raws
Media_formats = Video_formats+Image_formats # Supported file formats

#   Counters
Half_dated = 0 # Number of files with valid date but not time
Mod_dated = 0 # Number of files with only the file's modified datetime
Null_dated = 0 # Number of filenames without valid date (Moved to folder "Unknown Date")
Locations = [[],[],[]] # All valid location-tags found in the names of files

Rename_files = True # If true, all files will be renamed to include a date
Force_tag = None # If given a string, all files will have the tag appended to their names
Unique_tags = 0 # The unique number of valid tags found
Total_tags = 0 # The total number of valid tags found
Record_format = ' %2d: %04d-%02d-%02d (%d Files) '
Record_length = len(Record_format%(0, 0, 0, 0, 10))
Table_format = '      | Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec | '
Start_year = 1996 # The first year included in media collection
Total_years = datetime.now().year+1-Start_year
Files_per_year = [[[0]*31 for _ in range(12)] for _ in range(Total_years)]
Width, Height = max(len(Table_format), Record_length*RECORD_DIMENSIONS[1]), 6+Total_years+RECORD_DIMENSIONS[0]
Progress_date = 33
Progress_name = 100-Progress_date
Progress_bars = MENU_WIDTH-6

#   Declare Functions
def print_at(row, col, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (row, col, text))
    sys.stdout.flush()
def is_date_valid(date):
    try:
        dtime = datetime(*date)
    except:
        return False
    return date[0] >= Start_year and dtime <= datetime.now()

#   Inquire setting to execute
while True:
    system('cls')
    print_at(2, 4, ']    1. Normal   2. Only Stats   3. Force Tag')
    mode = input('\n [')
    if mode in ('1', '2', '3'):
        if mode == '2':
            Rename_files = False
        elif mode == '3':  
            system('cls')
            print('Enter tag')
            Force_tag = input()
            Unique_tags = 1
        break
system('cls')
print_at(2, 3, '|'+' '*int(Progress_bars/2-1)+'0%'+' '*int(Progress_bars/2)+'|')

#   Load files and their modified dates
files = [f for f in listdir('.') if isfile(f) and f[f.rfind('.')+1:].lower() in Media_formats]
dates = [strftime("%Y-%m-%d %H.%M.%S", gmtime(getmtime(f)+7200)) for f in files]

#   Specify one date per file
progress = 0
for i, file in enumerate(files):

    # Gather date from file name
    name_digits = ''.join([char for char in file if char.isdigit()])
    name_date = ()
    if len(name_digits) >= 8:
        name_date += (int(name_digits[:4]), int(name_digits[4:6]), int(name_digits[6:8]))
        if len(name_digits) >= 14:
            name_date += (int(name_digits[8:10]), int(name_digits[10:12]), int(name_digits[12:14]))
    
    # Gather date from image metadata (Date taken)
    exif_date = ()
    try:
        exif = Image.open(file)._getexif()
        exif_date += (int(exif[36867][:4]), int(exif[36867][5:7]), int(exif[36867][8:10]))
        exif_date += (int(exif[36867][11:13]), int(exif[36867][14:16]), int(exif[36867][17:19]))
    except:
        pass

    # Gather date from file metadata (Last modified)
    file_date = (int(dates[i][:4]), int(dates[i][5:7]), int(dates[i][8:10]))
    file_date += (int(dates[i][11:13]), int(dates[i][14:16]), int(dates[i][17:19]))

    # Classify validity of dates
    name_date_valid = len(name_date) > 0 and is_date_valid(name_date[:3])
    name_time_valid = len(name_date) == 6 and name_date[3] < 24 and name_date[4] < 60 and name_date[5] < 60
    exif_date_valid = len(exif_date) > 0 and is_date_valid(exif_date)
    file_date_valid = is_date_valid(file_date)

    # Decide which date to use
    if name_date_valid:
        if name_time_valid:
            dates[i] = '%04d-%02d-%02d %02d.%02d.%02d' % name_date
            if file.find('\'') == 19: # The file have previously been named using file date
                dates[i] += '\''
                Mod_dated += 1
        else:
            dates[i] = '%04d-%02d-%02d' % name_date[:3] + ' NT%d' % Half_dated
            Half_dated += 1
    elif exif_date_valid:
            dates[i] = '%04d-%02d-%02d %02d.%02d.%02d' % exif_date
    elif file_date_valid:
            dates[i] = '%04d-%02d-%02d %02d.%02d.%02d\'' % file_date
            Mod_dated += 1
    else:
        dates[i] = '?'
        Null_dated += 1
        continue
    Files_per_year[int(dates[i][:4])-1996][int(dates[i][5:7])-1][int(dates[i][8:10])-1] += 1
    
    # Print out progression
    if progress != int(Progress_date*(i+1)/len(files)):
        progress = int(Progress_date*(i+1)/len(files))
        bars = int(Progress_bars*progress/100)
        print_at(2, 3, '|'+'-'*bars+' '*(Progress_bars-bars)+'|')
        print_at(2, int(MENU_WIDTH/2-1), '%2d%%'%progress)

#   Rename files
for i, file in enumerate(files):

    if Rename_files and dates[i] == '?':
        Path('Unknown Date/').mkdir(exist_ok=True)
        rename(file, Path('Unknown Date/'+file))

    else:
        # Find any tag for file
        tag = file.replace(')', '(').split('(')
        if Force_tag != None:
            tag = ' (' + Force_tag + ')'
            Total_tags += 1
        elif len(tag) > 2:
            location = tag[1].split(', ')
            area, region = location[:2] if len(location) > 1 else ['', location[0]]
            if Locations[0] != [] and region in Locations[0] and area != '':
                areas = Locations[1][Locations[0].index(region)]
                if area in areas[0]:
                    areas[1][areas[0].index(area)] += 1
                else:
                    areas[0].append(area)
                    areas[1].append(1)
                    Unique_tags += 1
            elif area != '':
                Locations[0].append(region)
                Locations[1].append([[area], [1]])
                Unique_tags += 1
            Total_tags += 1
            tag = ' (' + area + ', ' + region + ')'
        else:
            tag = ''

        # Adjust in case of duplicates
        j = 0
        while j < len(dates):
            if j != i and dates[j] == dates[i]:
                dates[i] = dates[i][:17] + ('%02d' % (int(dates[i][17:19])+1 if dates[i][17:19] != '59' else 0)) + dates[i][19:]
                j = -1
            j += 1

        if Rename_files:
            rename(file, dates[i]+tag+file[file.rfind('.'):].lower())

    # Print out progression
    if progress != Progress_date+int(Progress_name*(i+1)/len(files)):
        progress = Progress_date+int(Progress_name*(i+1)/len(files))
        bars = int(Progress_bars*progress/100)
        print_at(2, 3, '|'+'-'*bars+' '*(Progress_bars-bars)+'|')
        print_at(2, int(MENU_WIDTH/2-1), '%2d%%'%progress)

#   Print table of files per month
system('cls & mode con: cols=' + str(Width) + ' lines=' + str(Height))
table_col = (1+Width-len(Table_format))//2
print_at(1, table_col, Table_format) # Header
record_days = [(0, 0, 0, 0) for _ in range(RECORD_COUNT)]
for year, files_per_month in enumerate(Files_per_year):
    year_str = ' ' + str(Start_year+year) + ' |                                                 |'
    print_at(2+year, table_col, year_str) # Year and background
    for month, files_per_day in enumerate(files_per_month):
        files_in_month = sum(files_per_day)
        month_str = '%2d'%files_in_month if files_in_month > 0 else ' -'
        print_at(2+year, table_col+9+4*month, month_str) # Files in month (Foreground)
        for day, files_in_day in enumerate(files_per_day):
            for i in range(RECORD_COUNT):
                if files_in_day > record_days[i][-1]:
                    record_days[i+1:RECORD_COUNT] = record_days[i:RECORD_COUNT-1]
                    record_days[i] = (Start_year+year, month+1, day+1, files_in_day)
                    break

#   Print list of days with record number of files and misc stats
for row in range(RECORD_DIMENSIONS[0]):
    for col in range(RECORD_DIMENSIONS[1]):
        num = row+RECORD_DIMENSIONS[0]*col
        if record_days[num][-1] > 0:
            record_str = Record_format % ((num+1,)+record_days[num])
            record_col = (1+Width-Record_length*RECORD_DIMENSIONS[1])//2+Record_length*col
            print_at(3+Total_years+row, record_col, record_str)
dated_str = 'No time: %d   File date: %d   No date: %d' % (Half_dated, Mod_dated, Null_dated)
tagged_str = 'Tagged: %d/%d (%d Unique)' % (Total_tags, len(files), Unique_tags)
print_at(Height-2, (Width+1-len(dated_str))//2, dated_str)
print_at(Height-1, (Width+1-len(tagged_str))//2, tagged_str)
input()
