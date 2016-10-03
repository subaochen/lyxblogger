#! /usr/bin/env python
# -*- coding: utf-8 -*-
#######################  L Y X B L O G G E R   #########################
#   This program allows you to post to your WordPress blog right from  #
#   LyX. The input to this script is xhtml.                            #
#   Supported LyX --> xhtml converters:                                #
#                                                                      #
#      LyXHTML output from LyX 2.0.                                    #
#      eLyXer output from LyX 1.6 and later. (Earlier may work too)    #
#                                                                      #
#   This script will connect using xml-rpc.                            #
#                                                                      #
#################     D O C U M E N T A T I O N       ##################
#                                                                      #
#   Please see the docs/ folder for LyXBlogger documentation.          #
#   Alternatively, see the online docs for the latest version of       #
#   LyXBlogger at www.nongnu.org/lyxblogger                            #
#   Please submit any issues or suggestions to the author.             #
#                                                                      #
#####################       A U T H O R       ##########################
#                                                                      #
#   Copyright 2010 Jack Desert                                         #
#   <jackdesert@gmail.com>                                          #
#   http://TwoMoreLines.com                                            #
#                                                                      #
######################      L I C E N S E     ##########################
#                                                                      #
#   This file is part of LyXBlogger.                                   #
#                                                                      #
#   LyXBlogger is free software: you can redistribute it and/or modify #
#   it under the terms of the GNU General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License,  #
#   or (at your option) any later version.                             #
#                                                                      #
#   LyXBlogger is distributed in the hope that it will be useful,      #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the      #
#   GNU General Public License for more details.                       #
#                                                                      #
#   You should have received a copy of the GNU General Public License  #
#   along with LyXBlogger.  If not, see <http://www.gnu.org/licenses>. #
#                                                                      #
########################################################################

import sys, os, re, time
import wordpresslib
import getpass
from socket import gaierror
from wordpresslib import WordPressException
from exceptions import IndexError


import os, sys
import re
import wordpresslib

import sys, time, re

def pr3(input):
    # Use sys.stdout instead of print so results can be used for automated testing
    # For some reason a newline character is required to flush ?
    # That's okay, because we'll use str.rstrip on the other side
    input = str(input)  # This makes sure that anything printable can be passed through
    sys.stdout.write(input + '\n')
    # Each line must be flushed so it can be read by the other side.
    sys.stdout.flush()

def wait_for_consumer():
    if (sys.platform == 'win32'):
        pr3('\nPress ENTER to close LyXBlogger.')
    elif(sys.platform == 'darwin'):
        pr3("\nFN + SHIFT + UP_ARROW scrolls screen        ENTER closes LyXBlogger")
    else:
        pr3("\nSHIFT + PAGE UP scrolls screen        ENTER closes LyXBlogger")
    sys.stdin.readline()
    sys.exit(0)  # Call this to make sure the program ends

def get_format(in_html):
    exp = re.compile('<head>.*</head>', re.DOTALL)   # DOTALL makes '.' match newlines as well
    format_obj = exp.search(in_html)
    if (format_obj):
        html_head = format_obj.group()
        if '<meta name="GENERATOR" content="LyX' in html_head:
            pr3("You are using the LyXHTML format.")
            pr3("LyXBlogger also supports the eLyXer format.")
            pr3("For more information, see the user's guide at lyxblogger.nongnu.org.")
            return False    # False means LyxHTL format
        elif '<meta name="generator" content="http://www.nongnu.org/elyxer/"/>' in html_head:
            pr3("You are using the eLyXer format.")
            pr3("LyXBlogger also supports LyX 2.0's internal LyXHTML format.")
            pr3("For more information, see the user's guide at lyxblogger.nongnu.org.")
            return True     # True means eLyXer format
        elif '<META name="GENERATOR" content="hevea' in html_head:
            pr3('*****   ERROR:   Unsupported format:  Hevea   *****')
        elif '<!--Converted with LaTeX2HTML' in html_head:
            pr3('*****   ERROR:   Unsupported format:  LaTeX2HTML   *****')
        elif '<meta name="GENERATOR" content="TtH' in html_head:
            pr3('*****   ERROR:   Unsupported format:  TtH   *****')
        else:
            pr3('*****   ERROR:   Unknown file format.   *****')
    else:
        pr3('\n\nNo <head> tag found')

    pr3("LyXBlogger supports the eLyXer format and LyX 2.0's internal")
    pr3("LyXHTML format. The input file you provided appears to be neither of")
    pr3("these. For more information, see the user's guide at lyxblogger.nongnu.org.")
    sys.exit(0)     # Halt Program if invalid html found.


def trim_cut_material(html, CUT_FLAG, ELYXER_ENGINE):
    # This function removes after the CUT_FLAG. CUT_FLAG is user-
    # definable. Note that the CUT_FLAG must be found at the beginning
    # of a paragraph to be rcognized
    pr3 ("\nCUT FLAG")
    pr3 ("Anything placed after the cut flag in your document will not be uploaded.")
    pr3 ("This is helpful for keeping notes that you might put back in a later draft.")
    if(ELYXER_ENGINE):
        # ELYXER may put a <span> tag in if you change the size
        exp = re.compile('<div class="[^>]{1,}?">\n(<span class="\D{1,}?">){0,1}?' + CUT_FLAG)
    else:
        # INTERNAL uses a magicparlabel-num
        exp = re.compile('<div class="[^>]{1,}?"><a id=\'magicparlabel-\d{1,}\' />\n' + CUT_FLAG)

    srch_obj = exp.search(html)
    if(srch_obj):
        start_index = srch_obj.start()
        # pr3('start index is: ' + str(start_index))
        # pr3('this expression found at location: ' + str(start_index))
        html = html[0:start_index]
        pr3 ('The Following String was found in your document and was ')
        pr3 ('successfully used as a cut flag: ')
        pr3 (CUT_FLAG + '\n')
    else:
        pr3 ("Place the contents of the following line at the beginning of")
        pr3 ("a paragraph to use it as a cut flag: ")
        pr3 (CUT_FLAG)
    return(html)

import sys, os, traceback
from socket import gaierror

def handle_general_error(name_string = '', suggestion_string = ''):
    pr3('\nAn error has occurred. If this error persists, please ')
    pr3('contact the author at jackdesert@gmail.com.')
    pr3('The nutshell version is listed way down below. But here')
    pr3('are the details if you are interested:')
    print(traceback.print_exc())
    print('\n\n\n\n\n')
    print("\n************************************************************")
    if name_string == '':
        print("*******                     ERROR                    *******\n")
    else:
        print (name_string)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg = traceback.format_exception_only(exc_type, exc_value)[0].replace('\n', '')
    print("System says: " + msg)
    if suggestion_string != '':
        print (suggestion_string + '\n')
    wait_for_consumer()


def handle_gaierror():
    name = ''
    suggestion = ''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg = traceback.format_exc()
    if ('[Errno -2] Name or service not known' in msg):
        name = "*******               CONNECTION ERROR               *******\n"
        suggestion = "Please check your Internet connection and try again.\n"
        suggestion += "If your Internet connection is fine, make sure you typed\n"
        suggestion += "your domain correctly."
    if ('Bad login/pass combination' in msg):
        name = "*******           USERNAME / PASSWORD ERROR          *******\n"
        suggestion = "Make sure you are typing your username and password correctly.\n"
        suggestion += "Hint: is caps lock on?"
        suggestion += "Hint: are you uploading to the correct site?"
    handle_general_error(name, suggestion)

def handle_input_error():
    name = ''
    suggestion = ''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg = traceback.format_exc()
    if ('input_file = sys.argv[1]' in msg) and ('IndexError: list index out of range' in msg):
        name = "*******                 INPUT ERROR                  *******\n"
        suggestion = "Most likely LyXBlogger was called without sufficient arguments.\n"
        suggestion += "Usage is:\n"
        suggestion += "     $ python -m lyxblogger <input_file>."
    handle_general_error(name, suggestion)


def find_local_image_tag(in_html, ELYXER_ENGINE):
    if(ELYXER_ENGINE):
    # eLyXer img tags looks something like this:
    # <img class="embedded" src="rv-8_tiny.jpg" alt="figure rv-8_tiny.jpg" style="max-width: 2048px; max-height: 1536px; "/>
    # Notice ELYXER uses double quotes instead of single quotes within the tag.
        img_exp = re.compile('''
            <img\ class="embedded"\          # The beginning of an <img> tag -- note two escaped spaces
            src="           # Note use of double quotes instead of single
            (?!http://)     # Negative lookahead expression (if it has http:// it's already been changed to web reference)
            ..*?            # Non-greedy (short as possible match) of stuff in middle
            />              # The closing of the <img> tag
            ''', re.VERBOSE)
    else:
    # INTERNAL img tags look something like this:
    # <img style="width:60%;" src='0_home_jd_Escritorio_rv-8_tiny.jpg' alt='image: 0_home_jd_Escritorio_rv-8_tiny.jpg' />
        img_exp = re.compile('''
            <img\ (style=.*)? src='     # The beginning of an <img> tag -- note the escaped space in the verbose regex, style is optional
            (?!http://)     # Negative lookahead expression (if it has http:// it's already been changed to web reference)
            ..*?            # Non-greedy (short as possible match) of stuff in middle
            />              # The closing of the <img> tag
            ''', re.VERBOSE)

    img_obj = img_exp.search(in_html)
    img_tag = ''
    if(img_obj):
        img_tag = img_obj.group()
    return(img_tag)



def up_images(in_html, wp_client_obj, ELYXER_ENGINE, in_DIR_OFFSET):
    # Find local location of a single image within the (x)html file
    img_tag = find_local_image_tag(in_html, ELYXER_ENGINE)
    imageSrc = None
    if(img_tag):
        pr3 ("\nIMAGES\nLet's upload your images")
    while(img_tag):
        local_image_url = get_local_image_url(img_tag, ELYXER_ENGINE)
        valid_local_image_url = validate_url(local_image_url, in_DIR_OFFSET)
        filesize = str(os.path.getsize(valid_local_image_url) / 1024) + ' kB'
        short_name = get_short_name(valid_local_image_url)
        pr3("Uploading image: " + short_name + '.  Size: ' + filesize )
        # upload image for post
        try:
            imageSrc = wp_client_obj.newMediaObject(valid_local_image_url)
        except (gaierror, WordPressException):
            handle_gaierror()
        try:
            assert(imageSrc.startswith('http://'))
        except AssertionError:
            print("There was a problem uploading your image.")
            print("imageSrc should start with http://")
            print("Please contact the author at jackdesert@gmail.com")
            handle_general_error()
        try:
            assert(local_image_url in in_html)
        except AssertionError:
            print("There was a problem uploading your image.")
            print("local_image_url not found in in_html")
            print("Please contact the author at jackdesert@gmail.com")
            handle_general_error()
        snapshot = in_html
        in_html = in_html.replace(local_image_url, imageSrc)
        # remove style='' in html, not tested for elyxer, but should be ok
        in_html = re.sub(r'<img\ (style=.*)?\ src=',"<img src=",in_html)
        try:
            assert(in_html != snapshot)
        except AssertionError:
            print("There was a problem uploading your image.")
            print("local_image_url not replaced with imageSrc in post")
            print("Please contact the author at jackdesert@gmail.com")
            handle_general_error()

        img_tag = find_local_image_tag(in_html, ELYXER_ENGINE)
    return(in_html)

def get_dir_offset(in_input_file):
    directory = ''
    if (sys.platform == 'win32'):
        input_exp = re.compile('..{1,}\\\\')   # Greedy to catch full folder
    else:
        input_exp = re.compile('..{1,}/')   # Greedy to catch full folder
    input_obj = input_exp.match(in_input_file) # Must match at beginning of expression
    if (input_obj):
        directory = input_obj.group()
    return directory


def validate_url(in_url, in_dir_offset):
    # If the url is already absolute (starts with a forward slash or
    # something like c:\ or d:\, leave it as be
    if in_url.startswith('/') or in_url[1:3] == ':\x0c':  # A colon and the unicode for a backslash
        return in_url
    # Otherwise, just append the local url to the dir_offset for a
    else:
        return (in_dir_offset + in_url)


def get_local_image_url(img_tag, ELYXER_ENGINE):
    # Find local address of image
    # The only difference between the two is single vs double quotes
    if (ELYXER_ENGINE):
        add_exp = re.compile('''
            src="   # The beginning of the address
            ..*?    # Non-greedy rest of the address
            "       # The (first) closing (double) quotation mark
            ''', re.VERBOSE)
    else:
        add_exp = re.compile('''
            src='   # The beginning of the address
            ..*?    # Non-greedy rest of the address
            '       # The (first) closing (single) quotation mark
            ''', re.VERBOSE)
    add_obj = add_exp.search(img_tag)
    if (add_obj == None):
        pr3 ("Error parsing img tag: " + img_tag)
        msg = "LyXBlogger failed to find src attribute in <img> tag"
        raise Exception(msg)
    long_address = add_obj.group()
    short_address = long_address[5:-1]  # Strip off the src="
    return(short_address)

def get_short_name(valid_url):
    if (sys.platform == 'win32'):
        separator = '\\\\'
    else:
        separator = '/'
    short_name = valid_url.split(separator)[-1]
    return (short_name)

import sys, os



def new_shell():
    # Determine which operating system is in use
    system = sys.platform
    if (sys.platform == 'win32'):
        pr3('Running on Windows')
        return('start "LyXBlogger" python.exe %s %s %s ')
    elif (sys.platform == 'darwin'):
        pr3('Running on OSX')
    elif (sys.platform == 'linux2'):
        pr3('Running on GNU/Linux')
    else:
        pr3('I\'m not sure what operating system you are running on.')
        pr3('Please write the author at jackdesert@gmail.com to report possible bug')
    # GNU/Linux, Mac, and unidentified OS's call rxvt
    return('rxvt -T "LyXBlogger" -fg gold -bg black -fn 10x20 -e python %s %s %s ')


def term_open(in_input_file):

    CALLED_FROM_XTERM = '--run-here'
    CALL_MODULE = '-m lyxblogger'
    # If already called from xterm, run the program as normal.
    # Otherwise, call the program from xterm so it's visible
    if (len(sys.argv) >= 3) and (sys.argv[2] == CALLED_FROM_XTERM):
        pass    # Called correctly, so code will execute
    else:
        # Spawn a new xterm window to run this program in
        # -hold means leave window open after process completes
        # -fg is foreground color
        # -bg is background color
        # -fn is font (size)
        # -e means call a program
        command = new_shell() % (CALL_MODULE, in_input_file, CALLED_FROM_XTERM)
        pr3('command is ' + command)
        os.system(command)
        sys.exit(0)     # Exit so program is not repeated.
        # Anything below this will not be executed



import sys, time
import wordpresslib

def get_post_id(wp_obj, history = 9):
    DATE_FLAG = "DATE"
    pr3 ('\nUPDATE A PREVIOUS POST')
    pr3 ('Retrieving Previous Posts From Server')
    #~ post_list = wp_obj.getpostegoryList()
    post_counter = 1
    post_list = []
    posts = wp_obj.getRecentPosts(history)
    dict = {}   # This dictionary matches display number with post_id
    try:
        while True:
            a = posts.next()
            # Make note in the dictionary which post id (a.id) each displayed title represents
            date_string = ''
            if a.date:
                mon = str(a.date[1])
                day = str(a.date[2])
                if len(day) == 1:   # Formatting
                    day = '0' + day
                yr = str(a.date[0])
                date_string = '    ' + mon  + '/' + day + '/' + yr
            key = str(post_counter)
            dict[key] = MiniPost(in_post_id = a.id, in_title = a.title, in_date = date_string)
            display = key + '.  ' + dict[key].title + DATE_FLAG + dict[key].date
            post_list.append(display)
            post_counter += 1
    except StopIteration:
        # The StopIteration exception is called once all the function generator entries have passed
        formatted_list = same_length(post_list, DATE_FLAG)
        if history != 0:
            formatted_list.append('A.    --  Show All Entries  --  ')
        for item in formatted_list:
            try:
                print(item)
            except UnicodeEncodeError:
                print("This line skipped because the Unicode would not display properly")

    while (1):
        pr3 ('\nPlease enter the NUMBER next to the post to overwrite')
        if (len(formatted_list) > 12 and sys.platform != 'win32'):
            pr3('Hint: SHIFT + PageUp scrolls screen')
        response = sys.stdin.readline().replace('\n', '')
        if (response == 'a' or response == 'A'):
            pr3('\nPlease allow up to a minute to download all post headers')
            post_id = get_post_id(wp_obj, 0)  # List all entries
            break
        else:
            try:
                post_id = dict[response].post_id
                # Print used on this instead of pr3 to prevent erros with Unicode titles
                print ('Selected: ' + dict[response].title + dict[response].date)
                break
            except KeyError:
                pr3 ("Post Selection Not Understood.\n")
    return post_id

def same_length(in_list,date_flag):
    TRUNCATE_LENGTH = 50    # The longest
    # Find max length of the items in the list
    max_length = 0
    for item in in_list:
        a = len(item)
        if a > max_length:
            max_length = a
    # Now we know the max_length
    out_list = []
    for item in in_list:
        a = len(item)
        spaces_to_add = max_length - a
        assert(spaces_to_add >= 0)
        assert(date_flag in item)
        pieces = item.rpartition(date_flag)   # Looks for last 'Date:'space in item
        # Limit the length of the title
        title_w_spaces = pieces[0] + (spaces_to_add)*' '
        title_w_spaces = title_w_spaces[0:TRUNCATE_LENGTH]
        # Add space in the middle
        new_item = title_w_spaces + pieces[2]
        out_list.append(new_item)
    return out_list


def get_cat_id(wp_obj):
    pr3 ('\nCATEGORY')
    pr3 ('Retrieving Categories From Server')
    cat_list = wp_obj.getCategoryList()
    cat_counter = 1
    dict = {}
    for cat in cat_list:
        print (str(cat_counter) + '.  ' + cat.name)
        dict[cat_counter] = cat.id
        cat_counter += 1
    output_list = []
    while (1):
        try:
            pr3 ('Please enter the NUMBER next to the category for this post')
            pr3 ('To select multiple categories, separate with commas')
            cat_response = sys.stdin.readline().replace('\n', '')
            cat_response_list = cat_response.split(',')
            for cat in cat_response_list:
                cat_int = int(cat)
                cat_id = cat_list[cat_int-1].id
                output_list.append(cat_id)
                print ('Category Selected: ' + cat_list[cat_int-1].name + '\n')
            break
        except ValueError:
            pr3 ("Category Response Not Understood.\n")
    assert(len(output_list) > 0)
    return output_list

class MiniPost:
    "A minipost contains just the title, numerical selector, and post_id"
    def __init__(self, in_post_id, in_title, in_date):
        self.post_id = in_post_id
        self.title = in_title
        self.date = in_date

import os, sys
import re
import wordpresslib

def get_html(input_file, CUT_FLAG):

    # Read data from file
    f = open(input_file, 'r')
    html = f.read()
    f.close()

    pr3 ("FORMAT")
    ELYXER_ENGINE = get_format(html)

    # Trim designated cut material from bottom of post
    html = trim_cut_material(html, CUT_FLAG, ELYXER_ENGINE)

    # RECORD TITLE FROM HEADER TO USE AS POST
    tit_exp = re.compile('''
        <title>         # Start of the <title> tag
        ..{1,}?         # Anything in the middle (non-greedy)
        </title>        # Closing </title> tag
        ''', re.VERBOSE)    # VERBOSE allows ''' '''
    tit_obj = tit_exp.search(html)
    # eLyXer uses 'Converted document' as the default title in the head
    # and body. LyXHTML uses 'LyX Document' as the default, but only
    # puts it in the head. The following code detects these default
    # titles and asks for a real title
    TITLE_EXPECTED_IN_BODY, TITLE_PROMPT = False, True
    pr3 ("\nTITLE")
    if(tit_obj):
        TITLE_EXPECTED_IN_BODY = True
        TITLE_PROMPT = False
        full_title_tag = tit_obj.group()
        blog_title = full_title_tag[7:-8]   # Strip tags off
        if (blog_title == 'Converted document'):    # eLyXer's default (head and body)
            TITLE_PROMPT = True
        if (blog_title == 'LyX Document'):  # LyXHTML's default (only in head)
            TITLE_PROMPT = True
            TITLE_EXPECTED_IN_BODY = False
    if(TITLE_PROMPT):
        pr3 ('No title found in document.')
        pr3 ('Please enter a title now')
        blog_title = sys.stdin.readline().replace('\n', '')
    pr3 ('Using title: ' + blog_title)

    # REMOVING TITLE FROM BODY
    # Typical body title using ENGINE_INTERNAL:
    #   <h1 class="title"><a id='magicparlabel-309' />
    #   Example Article Title</h1>
    #   <h1 class="title">
    # Typical body title using ELYXER_ENGINE using optional sizing:
    #   <h1 class="title">
    #   <span class="footnotesize">Hi Brian</span>
    #
    #   </h1>
    exp = re.compile('''
        <h1\                   # Beginning of tag with space
        class="title">         # The rest of the tag
        ..{1,}?                # Anything (non-greedy)
        </h1>                  # Closing tag
        ''', re.VERBOSE | re.DOTALL)                 # .. can include linebreaks
    bt_obj = exp.search(html)
    if(bt_obj):
        entire_bt_tag = bt_obj.group()
        html = html.replace(entire_bt_tag, '')
    elif (TITLE_EXPECTED_IN_BODY):
        pass
        #~ pr3 ('\nWARNING! The title of your entry may appear twice.')
        #~ pr3 ('Please notify the author at jackdesert@gmail.com to')
        #~ pr3 ('have this bug squashed.\n\n Press Enter to continue uploading.')
        #~ sys.stdin.readline()
        # What this really means is an opening title tag was found, but
        # no title tag was found in the body.

    # Eliminate everything outside the <body></body> tags
    START_TAG = '<body>'
    END_TAG = '</body>'
    if (START_TAG in html):
        html = html.partition(START_TAG)[2]
    html = html.partition(END_TAG)[0]

    # Reinvoke <code> and </code> tags from their escape sequence counterparts
    html = html.replace('&lt;code&gt;', '<code>')
    html = html.replace('&lt;/code&gt;', '</code>')

    # Remove Arrows from footnotes and margin notes
    html = html.replace('[→', '[')
    html = html.replace('→]', ']')

    # Change the elyxer-generated id to a class, since wordpresslib appears to
    # strip out all ids upon upload
    html = html.replace("<div class=\"footer\" id=\"generated-by\">", "<div class=\"footer generated-by-elyxer\">")

    return html, blog_title, ELYXER_ENGINE


import sys, os, time, ConfigParser, xmlrpclib
import getpass
from socket import gaierror
from xmlrpclib import Fault as xmlFault
from xmlrpclib import ProtocolError as xmlrpcProtocolError

def get_configpath():
    # Determine which operating system is in use
    system = sys.platform
    if (system == 'win32'):
        pr3('Running on Windows')
        return("~\\lyxblogger\\config.cfg")
    elif (system == 'darwin'):
        # pr3('Running on OSX')
        return "~/.lyxblogger/config.cfg"
    elif (system == 'linux2'):
        # pr3('Running on GNU/Linux')
        return "~/.lyxblogger/config.cfg"
    else:
        pr3('I\'m not sure what operating system you are running on.')
        pr3('Please write the author at jackdesert@gmail.com to report possible bug')
        wait_for_consumer()
    # GNU/Linux, Mac, and unidentified OS's call xterm




def run_init_config():
    rel_file = get_configpath()
    abs_file = os.path.expanduser(rel_file)
    configdir = os.path.dirname(abs_file)
    if not os.path.exists(configdir): os.makedirs(configdir)
    config = init_config(abs_file)
    return config

def init_config(in_config_file):
    config = ConfigParser.ConfigParser()
    if not os.path.exists(in_config_file):
        # Set up initial config file
        config.set('DEFAULT', 'delay', '1.0') # wait while showing author info
        config.set('DEFAULT', 'cut_flag', '#! CUT MATERIAL') # we remove anything after this in the html
        config.set('DEFAULT', 'last_profile', '0') # use as default input option
        config.set('DEFAULT', 'next_section_n', '1') # next usable profile section number
        with open(in_config_file, 'wb') as configfile: config.write(configfile)
        pr3 ("Default config file created in " + in_config_file + '\n' )

    config.read(in_config_file)
    return config

def display_profiles(config):
    last_serial = config.get('DEFAULT', 'last_profile')

    disp_0 = '0. ' + str(Credentials.defaults())
    if last_serial == '0':
        disp_0 += "  **"
    pr3(disp_0)
    config_ctr = 1  # Zero is reserved for the test site, so we start one higher
    cfg_dict = {'0':'0'}  # This is to make sure the test site is reachable
    for section in config.sections():
        cfg_dict[str(config_ctr)] = section
        disp = str(config_ctr) + '. ' + str(Credentials.fromconfig(config,section))
        if section == last_serial:
            disp += "  **"
        pr3(disp)
        config_ctr += 1
    return cfg_dict

def get_serial(key, dict):
    if key.isdigit():
        try:
            return dict[key]
        except KeyError:
            # pr3("No such profile")
            # pr3("you entered: " + key)
            # pr3(dict)
            return None
    else:
        return None

def get_credentials(config):
    configpath = os.path.expanduser(get_configpath())

    # Select existing profile (and setting last_profile to that)
    # or create a new profile in the config file
    while (1):
        pr3 ('\nSELECT BLOG')
        cfg_dict = display_profiles(config)

        last_serial = config.get('DEFAULT', 'last_profile')
        pr3 ('\nEnter the number next to the desired profile.')
        pr3 ('(**latest) N = New, D = Delete')
        cat_response = sys.stdin.readline().replace('\n', '')

        if cat_response == 'D' or cat_response == 'd':
            cfg_dict = display_profiles(config)
            pr3 ('Enter a number to delete that profile, N to cancel')
            del_response = sys.stdin.readline().replace('\n', '')
            d_serial = get_serial(del_response, cfg_dict)
            if del_response == '0':
                pr3 ('Default section 0 cannot be deleted\n')
                pr3("Keyboard control will resume in 5 seconds")
                time.sleep(3)
            elif d_serial:
                config.remove_section(d_serial)
                if d_serial == config.get('DEFAULT', 'last_profile'):
                    config.set('DEFAULT', 'last_profile', '0')
                with open(configpath, 'wb') as configfile: config.write(configfile)
                pr3 ('Profile ' + del_response + ' removed!\n')
            else:
                pr3 (del_response + " Is Not A Profile Number.\n")

        elif cat_response == 'N' or cat_response == 'n':
            section = config.get('DEFAULT', 'next_section_n')
            new = Credentials.ask()
            pr3("Your password is: " + len(new.password)*"*")
            if url_passes(new, new.password):
                config.set('DEFAULT', 'last_profile', section)
                config.add_section(section)
                config.set(section, 'url',      new.url)
                config.set(section, 'user',     new.user)
                config.set(section, 'password', new.password)                # make a previously unused number to be used by the next section created:
                config.set('DEFAULT', 'next_section_n', str(int(section)+1))
                with open(configpath, 'wb') as configfile: config.write(configfile)
                pr3 ("Profile created, config file saved to " + configpath + '\n')
            else:
                time.sleep(3)
        # USE THIS PROFILE
        elif get_serial(cat_response, cfg_dict) or cat_response == '':
            if cat_response == '':
                u_serial = config.get('DEFAULT', 'last_profile')
            else:
                u_serial = get_serial(cat_response, cfg_dict)
            selected = Credentials.fromconfig(config, u_serial)
            config.set('DEFAULT', 'last_profile', u_serial)
            with open(configpath, 'wb') as configfile: config.write(configfile)
            break

        else:
            pr3 ("Response " + cat_response + " Not Understood.\n")
            time.sleep(1)

    pr3 ('Profile selected:  ' + str(selected))
    if selected.password == '':
            pr3 ("Profile has no password set. Please enter your WordPress password")
            selected.password = getpass.getpass()
    # Repeat process until credentials pass
    while not url_passes(selected, CHECK_PASSWORD = True):
        selected = get_credentials(config)

    pr3("Credentials Passed")
    return selected

def url_passes(selected, CHECK_PASSWORD = False):
    # prepare client object
    # verify that credentials work by getting info
    if CHECK_PASSWORD == False or CHECK_PASSWORD == '':
        pr3("Making sure " + selected.url + " exists and is reachable.")
    else:
        pr3("Verifying host, username, and password.")
    rpc_server = xmlrpclib.ServerProxy(selected.url)
    try:
        userinfo = rpc_server.blogger.getUserInfo('', selected.user, selected.password)
        return True
    except gaierror:    # gaierror caught if no connection to host
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # print(exc_type, exc_value, exc_traceback)   # Use print intead of pr3 because print can take three args
        pr3("\n" + selected.url + " is unreachable.")
        pr3("Please check the spelling and make sure your Internet is working.")
        pr3("Working example: http://cool_url.com/xmlrpc.php")
        pr3("You may try again in just a moment.")
        time.sleep(3)
        return False
    except xmlFault:    # xmlFault caught if host found but user/pass mismatch
        if CHECK_PASSWORD == False or CHECK_PASSWORD == '':
            # Don't bother checking if password is correct
            return True
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_value)    # Using PRINT on purpose
            pr3("\nIncorrect Password. Please try again in just a moment.")
            time.sleep(3)
            return False
    except xmlrpcProtocolError:
            pr3("\nHTTP Protocol Error. Probably not your fault. Please try again in just a moment.")
            time.sleep(3)
            return False

def delete_config_file():
    rel_path = get_configpath()
    abs_path = os.path.expanduser(rel_path)
    pr3("abs_path is " + abs_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)

class Credentials:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password

    @classmethod
    def ask(cls):
        "Initialize Credentials with values given by user"
        pr3 ('\nCREATING NEW PROFILE.')
        pr3 ("\nUSERNAME")
        while (1):
            pr3 ("Please enter your WordPress username")
            user = sys.stdin.readline().replace('\n', '')
            if user != '': break
        pr3 ("Username is " + user + '.')
        pr3 ("\nURL")
        while (1):
            pr3 ("Please enter your WordPress URL")
            pr3 ("Example: cool_site.wordpress.com")
            url = sys.stdin.readline().replace('\n', '')
            if url != '': break
        url = url.replace('http://', '')
        url = url.replace('www.', '')
        if url.endswith('/'):
            url = 'http://' + url + 'xmlrpc.php'
        else:
            url = 'http://' + url + '/xmlrpc.php'
        pr3 ("The PhP page we'll be talking to is " + url)
        pr3 ("\nPROMPT for PASSWORD?")
        pr3 ("Press ENTER now to be prompted each time (recommended).")
        pr3 ("Or type your precious password here, to be saved as plain text on you computer.")
        password = getpass.getpass()
        return cls(url, user, password)

    @classmethod
    def defaults(cls):
        "Initialize Credentials with default values"
        return cls('http://blogtest.twomorelines.com/xmlrpc.php',
                   'test',
                   'test')

    @classmethod
    def fromconfig(cls, config, section):
        "Initialize Credentials with values from config; use defaults if section is '0'"
        if section == '0': return cls.defaults()
        else:
            return cls(config.get(section, 'url'),
                       config.get(section, 'user'),
                       config.get(section, 'password'))

    def __str__(self):
        return self.user + "@" + self.url[7:-11]

def main():
    error_msg = ''
    input_file = sys.argv[1]    # Incoming file name
    # DIR_OFFSET is where the file being called is relative to where your shell is open to
    DIR_OFFSET = ''            # Empty until defined otherwise

    # Open LyXBlogger in a separate terminal
    term_open(input_file)

    pr3 ('LYXBLOGGER')
    pr3('Copyright 2010 - 2012 Jack Desert')
    pr3('Please send any comments, suggestions, or bug reports')
    pr3('to jackdesert@gmail.com')
    pr3 ('License: GNU GPL3. See <http://www.gnu.org/licenses>')
    pr3('Documentation at http://lyxblogger.nongnu.org\n')
    config = run_init_config()
    time.sleep(config.getfloat('DEFAULT', 'delay'))

    DIR_OFFSET = get_dir_offset(input_file)

    html, blog_title, ELYXER_ENGINE = get_html(input_file, config.get('DEFAULT', 'cut_flag'))

    keys = get_credentials(config)

    wordpress_url = keys.url
    user = keys.user
    password = keys.password

    # prepare client object
    wp = wordpresslib.WordPressClient(wordpress_url, user, password)

    # select blog id
    pr3('\nNEW OR EXISTING')
    while (1):
        pr3('Create New post or overwrite Existing? (N) E')
        cat_response = sys.stdin.readline().replace('\n', '')
        if cat_response == 'E' or cat_response == 'e':
            post_id = get_post_id(wp)
            break
        elif cat_response == 'N' or cat_response == 'n' or cat_response == '':
            post_id = 0
            pr3('Publishing new post')
            break
        else:
            pr3 ("Response Not Understood.\n")
    try:
        wp.selectBlog(post_id)
    except (gaierror, WordPressException):
        handle_gaierror()

    # create post object
    post = wordpresslib.WordPressPost()
    post.title = blog_title

    cat_id = get_cat_id(wp)
    # I have no idea why this takes a tuple (something, )
    post.categories = cat_id #(cat_id,)
    # publish images
    html = up_images(html, wp, ELYXER_ENGINE, DIR_OFFSET)
    post.description = html
    # publish post
    pr3 ("\nWORDS\nLet's upload your thoughts")

    filesize = str(os.path.getsize(input_file) / 1024) + ' kB'
    pr3("Uploading xhtml: " + input_file + '.  Size: ' + filesize )
    try:
        if(post_id == 0):
            wp.newPost(post, True)
        else:
            wp.editPost(post_id, post, True)
    except (gaierror, WordPressException):
        handle_gaierror()

    pr3 ('\nSUCCESS!')
    pr3 ('You just published your document to ' + wordpress_url[7:-11])
    pr3 ('Thank you for using LyXBlogger.\n\n')
    wait_for_consumer()


if __name__ == '__main__':
    try:
        main()
    except IndexError:
        handle_input_error()
    except SystemExit:
        pass    # Let this exception pass through so sys.exit() calls will work
    except:
        handle_general_error()


