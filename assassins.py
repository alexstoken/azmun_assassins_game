#!/Users/alexstoken/anaconda/bin/python
"""
This program is meant to take in a list of participants and then use some python libraries to run the assassins game for AZMUN

Created by: Alex Stoken 4 Nov 2017
Made Great Again By: Chris Mason
Modified: 1 Nov 2017
"""
import sys, os, re
import numpy as np
import smtplib
import datetime
import email
import imaplib
import mailbox
import random
import csv
import argparse
import time
import pandas as pd

"""
Design outline:
- Start with list of tuples with everyones name, email address, and a link to their picture
- Shuffle the list when given command line argument
- Take this list and send an email to everyone with the name below them on the list and the picture, use full path
- When recieving an email back with a specific name, then remove that persons email from the list and send them the next name on the list
"""

#global variables
#ia_email = "internalaffairs@arizonamun.org"
#ia_password = "makeMUNgreatagain2016"

ia_email = "azmunassassins@gmail.com"
ia_password = "arizonamun"

#function from the internet to just send an email from smtp
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems


#sends initial email out to all participants
def initial_email(ass_list):

    for i in xrange(len(ass_list)):

        #set variables to the tuple element
        name, email, pic_link = ass_list[i]

        #set target name to the next name element
        if i< (len(ass_list) - 1):
            target_name, next_email, next_pic = ass_list[i+1]
        else:
            target_name, next_email, next_pic = ass_list[0]


        addr_to_list = [email]
        initial_email_body ="""
        Hello %s,

        Welcome to the AZMUN Spring 2k18 edition of Assassins!

        Your target is %s.

        Please consult Facebook or email azmunassassins@gmail.com if you need help identifying your ta

        When you get a kill, you MUST email azmunassassins@gmail.org (NOTE, new email!!) with the following message:

        Subject: Assassins kill
        Body: Killed: _______<-----put the name of the person you assassinated here!

        As a reminder, the rules are as follows:
        1. You MUST use a plastic spoon (supply your own)
        2. The game begins IMMEADIETLY
        3. The game is single elimination
        4. NOBODY can see the assassination (I mean like don't be creepy about it but be stealthy)
        5. If you have a questionable assassination, text me BEFORE sending an email.

        Contact Alex Stoken (480-528-5633, internalaffairs@arizonamun.org) if you have any questions.

        May the odds be EVER in your favor.

        BQ-BA-BD,

        Alex "Assassin Master" Stoken
        """ %(name, target_name, next_pic) #target name is just the next name so maybe just d0 [i+1 element]
        sendemail(ia_email, addr_to_list, [],"Welcome to AZMUN Assassins", initial_email_body, ia_email , ia_password )

#emails everyone who has been killed
def been_killed(ass_list):

    for i, name, email, pic in enumerate(ass_list):
        if email == assassination_response:

    #set variables to the tuple element
            name, email, pic_link = ass_list[i]

    #set target name to the next name element
            if i< (len(ass_list) - 1):
                target_name, next_email, next_pic = ass_list[i+1]
            else:
                target_name, next_email, next_pic = ass_list[0]


                addr_to_list = [email]

                been_killed_email_body = """Hello %s,
            You have been... assassinated.

            I'm sorry for your loss. Better luck next year. Note that you may
            still participate in the game by helping others to eliminate their targets.


            Contact Alex Stoken (480-528-5633, internalaffairs@email.arizona.edu) if you think you have been assassinated in error.

            """ %(name)

            sendemail(ia_email, addr_to_list, [],"You have been assassinated in AZMUN Assassins", been_killed_email_body,ia_email ,ia_password )

#gives players their next target
def respond_to_kill(ass_list):

    for i, name, email, pic in enumerate(ass_list):
        if email == assassination_response:
        #set variables to the tuple element
            name, email, pic_link = ass_list[i]

        #set target name to the next name element
            if i< (len(ass_list) - 1):
                target_name, next_email, next_pic = ass_list[i+1]
            else:
                target_name, next_email, next_pic = ass_list[0]


                addr_to_list = [email]
                respond_to_kill_email_body = """
    Hello %s,
    Congratulations on your kill!

    Your next target is %s. You can see a picture of them here: %s
    Contact Alex Stoken (480-528-5633, internalaffairs@email.arizona.edu) if you have any questions.

    """ %(name, target_name, next_pic)

        sendemail(ia_email, addr_to_list, [],"Your next AZMUN Assassins target", respond_to_kill_email_body, ia_email ,ia_password )


#email watcher looking for a certain subject, then analyzes the text with regex, compares it to the name they expect, and modifies the list
def monitor(login, password, ass_list):
    #this function reads emails to internalaffairs and finds unread kill emails,
    #reads in the content, eliminates the person from the player list,
    #and then triggers respond_to_kill function

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(login, password)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "UNSEEN") # (ALL/UNSEEN)
    i = len(data[0].split())

    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # result, email_data = conn.store(num,'-FLAGS','\\Seen')
        # this might work to set flag to seen, if it doesn't already

        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # Header Details
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                message_content = (email_from, subject, body.decode('utf-8'))
                #message_content = subject # testing here


    try:
        message_content
    except NameError:
        # no new messages
        return False
    else:
        return message_content



def make_list(csv_path):
    csv_tuple_list = []
    with open(csv_path, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            #csv_tuple_list.append((row[0], row[1], row[2]))
            csv_tuple_list.append((row[0], row[1]))
    return csv_tuple_list

def message_parser(message, ass_list):
    #use regex to figure out who was killed, and who killed them
    #might be enough to just use email??
    email_sender, email_subject, email_content = message
    if "kill" in email_content:
        return email_sender
    else:
        return False

def return_list(origin_list, mode):
    """
    this function writes the original shuffled assassins order, as well
    as the updated list of current participants, to a csv and returns
    the path of the file
    """
    if mode == 'original': filename = 'original_ass_list'
    if mode == 'current': filename = 'latest_ass_list'
    df = pd.DataFrame(origin_list)
    #df.to_csv("latest_assassins_list.csv", sep=",", na_rep='', header=False, index=False, index_label=None, mode='w', encoding=None, compression=None, quoting=None, quotechar='"', line_terminator='n', chunksize=None, tupleize_cols=None, date_format=None, doublequote=True, escapechar=None, decimal='.')
    df.to_excel(filename+ '.xlsx', sheet_name='latest_list', header=['Name', 'Email', 'Photo'], index=False, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, encoding=None, inf_rep='inf', verbose=True, freeze_panes=None)



#make list of tuples with Name, Email address
def main():
    #start off by figuring out which situation the program is being run in

    #assassin_list_test = [('Alex Stoken', 'astoken@email.arizona.edu','https://drive.google.com/file/d/1aX2DzfLG0TEBadx3VvdwGUzafYbKPdrk/view?usp=sharing'),
    #            ('Alex Stoken 2', 'alex.stoken@gmail.com', 'https://drive.google.com/file/d/12ws2m03tiK50zHi1rkgvNRlkWMeiotQy/view?usp=sharing')]

    #assassins_list = make_list("/Users/alexstoken/projects/AZMUN/assassins_list.csv")
    assassins_list = make_list("./small_list.csv");

    original_list = assassins_list[:]


    mode = input("""Enter Game Mode:
    Options - 1. start (new game, resends initial email)
              2. original (returns the original list)
              3. current (returns list of current participants)
              4. monitor (just begin monitoring email)

    """)
    if mode == 'start':
        random.shuffle(assassins_list)
        initial_email(assassins_list)

    if mode == 'original': return_list(original_list,mode)
    if mode == 'current': return_list(assassins_list,mode)


    if mode == 'monitor':
        while assassins_list:
            assassination_response = monitor(ia_email, ia_password, assassins_list)
            from_name, subject, body = assassination_response
            if(assassination_response == False):
                print("No new messages")
            else:
                for i, name, email, pic in enumerate(assassins_list):

                    if email == assassination_response: eliminate = i


                been_killed(assassination_response, assassins_list,)
                respond_to_kill(assassination_response, assassins_list)
                assassins_list.pop(i)
                assassins_list

            time.sleep(5)


try:
    main()
except KeyboardInterrupt:
    print("Process Interrupted by User")
