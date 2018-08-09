#!/usr/bin/python

import subprocess
import argparse
import re

def set_pids(pname, tmapping):
    proc = subprocess.Popen(['pidof',pname],stdout=subprocess.PIPE)
    lines = (str(proc.stdout.readlines())).rstrip()
    #print (lines)
    split = lines.split()

    for l in split:
        pid = int(re.sub('[^0-9]','', l))
        set_thread_cpu(str(pid), tmapping)


def get_tid_to_cpu(mapfile):
    dict = {}
    with open(mapfile) as f:
        for line in f:
            split = line.split();
            dict[split[0]] = split[1]
    return dict

def set_thread_cpu(pid, tmapping):
#    top -H -p 10135 -n1 -b
    tid_to_cpu = get_tid_to_cpu(tmapping)
    dict = {} # thread id to cpu id
    proc = subprocess.Popen(['top','-H', '-n', '1', '-b', '-p', pid ],stdout=subprocess.PIPE)
    count = 0
    for line in proc.stdout.readlines():
        if count < 7: 
            count = count + 1
            continue

        threads = line.decode('utf-8').lstrip()
        split = threads.split()
        #print("thr=> " + split[0] + " " + split[11])
        thread_name = split[11]
        threadid = split[0]
        if None != tid_to_cpu.get(thread_name):
            cpulist = tid_to_cpu[thread_name]
            if None == dict.get(cpulist):
                dict[cpulist] = [];
            dict.get(cpulist).append(threadid)

    #print(dict)
    assign_cpuid_to_thread(dict)

def assign_cpuid_to_thread(dictionary):
    for cpulist, value in dictionary.items():
        for tid in value:
#            print ("cpulist" + " => " + tid)
            proc = subprocess.Popen(['taskset', '-pc', cpulist, tid], stdout=subprocess.PIPE)
            print(proc.stdout.readlines())

if __name__== "__main__":
    parser = argparse.ArgumentParser("")
    parser.add_argument("-n", "--pname", help="process name")
    parser.add_argument("-m", "--tmapping", help="thread mapping file")
    args = parser.parse_args()
    set_pids(args.pname, args.tmapping)
    get_tid_to_cpu(args.tmapping)

