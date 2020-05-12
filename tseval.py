#!/bin/python
# compare a knows good troubleshooting script to the recorded script
# output a quantified score of the ts steps

import getopt  # options for cli arguments
import sys  # 

# function: parse all the user inputs from the tslog => user_target_log[list]
# ignore automated inputs, non related lines
# open path, read-only, and put user lines into an variable list
def parse_user_data(tglog_file_path, user_name):#good //crr
    with open(tglog_file_path, "r") as file:  
        user_target_log = [] 
        # for each line in the file, copy the lines that have the user name into list
        for line in file:    # overly simplistic? need to seperate all the user commands from the system generated entries
            if user_name in line: 
                line = line.rstrip()
                line = line.strip("*")
                user_target_log.append(line)
    file.close()
    return(user_target_log)
# function: parse the trobleshooting steps and resolution from known good log
#open path, read-only, and put known good text into an variable 
def parse_known_good(kglog_file_path):
    with open(kglog_file_path, "r") as file:  
        known_good_log = [] 
        # for each line in the file, put steps in list
        for line in file:  
            if "resolution" not in line:
                line = line.rstrip() 
                known_good_log.append(line)
    file.close()
    return(known_good_log)
# function: parse the resolution commands from the known good
def parse_res_cmds(kglog_file_path):
    with open(kglog_file_path, "r") as file:  
        resolution_cmds = []
        # for each line in the file, put resolution in list
        for line in file:  
            if "resolution" in line: 
                line = line.rstrip()
                line = line.split(":", 2)
                resolution_cmds.append(line)
    file.close()
    return(resolution_cmds)
# function: count number of good troubleshooting steps are in the target log
# returns a dict of commands that are in the kglog and count of extra commands
def good_ts_count(kg_list, u_tg_log): #good//crr
    goodline_count = 0
    extra_cmd_count = 0
    eval_dict = {"extra": 0}
    for goodline in kg_list: 
        for tgline in u_tg_log:
            if goodline in tgline: 
                goodline_count += 1
        eval_dict.update({goodline:goodline_count}) 
        goodline_count = 0     
    return(eval_dict) 
# get a timesequense list of admin executed events => 
# evaluate time to ts and time between commands
def dtg_to_seconds(line):
    cardinal_mon_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,"Nov": 11, "Dec": 12}
    date = []
    #line:  May  4 01:43:24: %PARSER-5-CFGLOG_LOGGEDCMD: User:parsonsmi.ga  logged command:command
    logentry = line.split()
    logentry[0] = cardinal_mon_dict[logentry[0]]  # turn *May into 5
    dtg = logentry[2]  #['01:37:57:']
    dtg = dtg.split(":")[0:3]  # split h, m, s
    dtg[-1] = round(float(dtg[-1])) # round the seconds to nearest second if decimanl seonds
    date.append(logentry[0])
    date.append(logentry[1])
    epoch = date + dtg
    #print(epoch," epoch")
    #start_epoch_int_list = list(map(int, start_epoch))
    epoch_ints = [int(i) for i in epoch]
    dtg_list = epoch_ints
    months = (dtg_list[0]-1)*30*24*60*60
    days = (dtg_list[1]-1)*24*60*60
    hours = dtg_list[2]*60*60
    minutes = dtg_list[3]*60
    seconds = dtg_list[4]
    dtg_sum = (months + days + hours + minutes + seconds)
    return(dtg_sum)
# count number of duplicate commands => 
# what good is duplicate efforts 
def dup_count(u_tg_log):
    cmd_count = 0
    cmd_count_dict = {}
    s, a = [], []
    for line in u_tg_log:
        s = line.split("%",2)
        a.append(s[1])
        x = list(set(a))
    for i in x:
        for j in a:
            if i in j: 
                cmd_count += 1
                cmd_count_dict.update({i:cmd_count})
        cmd_count = 0
    return(cmd_count_dict)
# function: help options of cli arguments
def usage():
    print (' -------------------------------------------------------------------------')
    print ('NOSS May 2020')
    print (' ')
    print ('Evaluate the quality of a troublshooting effort')
    print (' ')
    print (' example:')
    print (' tseval.py -g C:\knowngoodlog.txt -t C:\\targetlog.txt')
    print (' -g Known good log file prepared by NOSS')
    print (' -t Target log file to evaluate')
    print (' -------------------------------------------------------------------------')
    sys.exit(' ')
def main(argv):
    #tglog_file_path = 'ios.txt'
    #kglog_file_path = 'kgscript.txt'
    #user_name = 'console'
    tglog_file_path = ''
    kglog_file_path = ''
    user_name = ''
    try:
        opts, args = getopt.getopt(argv,"h:g:t:u:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-g"):
            kglog_file_path = arg
        elif opt in ("-t"):
            tglog_file_path = arg
        elif opt in ("-u"):
            user_name = arg
    #make function calls and set to variables
    u_tg_log = parse_user_data(tglog_file_path, user_name)
    kg_list = parse_known_good(kglog_file_path)
    resolution_cmds = parse_res_cmds(kglog_file_path)
    eval_dict = good_ts_count(kg_list, u_tg_log)
    cmd_count_dict = dup_count(u_tg_log)
    first_line = u_tg_log[0]
    last_line = u_tg_log[-1]
    #do the math
    start_seconds = (dtg_to_seconds(first_line))
    end_seconds = (dtg_to_seconds(last_line))
    elapsed_seconds = end_seconds - start_seconds
    elapsed_hh = elapsed_seconds // 60
    elaped_ss = elapsed_seconds % 60
    # average time between good commands
    # elaped time / good cmds = average time to get to each good cmd
    good_cmd_count = sum(eval_dict.values()) # sum all the values in the dictionary
    avg_secs_per_good_cmd = elapsed_seconds // len(kg_list)
    # Efficiency: ratio of good/extra commands
    # number of commands issued / number of good commands
    extraneous_cmds = len(u_tg_log) - len(kg_list)
    efficiency = round((len(kg_list) / extraneous_cmds) * 100)

    #outputs
    #print(eval_dict)
    print("----------------------------------------------")
    print("tg =",tglog_file_path)
    print("kg =",kglog_file_path)
    print("un =",user_name)
    print("----------------------------------------------")
    print(elapsed_hh,"hrs",elaped_ss,"secs elapsed time")
    print(len(u_tg_log), " commands issued by user")
    print(len(kg_list)," expected commands")
    print(extraneous_cmds," ineffective or extra user commands")
    print(len(cmd_count_dict) ," commands were reptead")
    print("----------------------------------------------")
    print(avg_secs_per_good_cmd, "secs: average time between expected commands")
    print(efficiency, "% trouble shooting efficiency") 
    print("----------------------------------------------")

    #-------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])