#!/usr/bin/python3
from KeyReleaseAgent import KeyReleaseAgent
from DataCollector import DataCollector
import time
import threading
import argparse
import logging
import logging.handlers
from os import path
from datetime import datetime

logger = logging.getLogger(__name__)
log_file = "satellite_sim.log"
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10**9)
logger.addHandler(handler)

class IsolatedReleaseSim:
    # -------- PARAMETERS --------
    #Number of bits of key required to release the keys into the system
    key_bits_release_threshold = 10000 # TODO verify this number

    #Number of bits per key taken by OpenQKDNetwork
    key_bit_size = 256;

    #Number of bits to create a bit for a key
    bit_to_key_ineffiency = 1;

    #Number of keys per key file taken by OpenQKDNetwork 
    keys_per_file = 4096;

    #Amount of virtual time seconds that pass every real second
    virtual_seconds_per_real_second = 100000;

    #Time before the first satellite pass
    pre_first_pass_delay = 10000;

    #Toggles whether a report is generated and output to console
    generate_report = True;

    #Number of virtual seconds between console reports are given
    report_frequency = 100;

    # -------- INIT VALUES --------
    current_bits_a = 0;
    current_index_a = 0;

    current_bits_b = 0;
    current_index_b = 0;

    current_time = 0;

    report_counter = 0;

    def __init__(self, sim_data_a_file, sim_data_b_file, qkd_dir, site):

        dc = DataCollector();

        self.kra = KeyReleaseAgent(
            qkd_dir,
            site,
            list(),
            self.key_bit_size,
            self.bit_to_key_ineffiency,
            self.keys_per_file
        );

        if sim_data_a_file is not None:
            self.sim_data_a = dc.get_named_sim_release_data(sim_data_a_file)
        else:
            self.sim_data_a = dc.get_bristol_sim_release_data()
        self.sim_data_a.sort(key=lambda x: x[0] + x[1])

        if sim_data_a_file is not None:
            self.sim_data_b = dc.get_named_sim_release_data(sim_data_b_file)
        else:
            self.sim_data_b = dc.get_ottawa_sim_release_data()
        self.sim_data_b.sort(key=lambda x: x[0] + x[1])

        min_pass_time = int(self.sim_data_a[0][0])

        if(self.sim_data_b[0][0] < self.sim_data_a[0][0]):
            min_pass_time = self.sim_data_b[0][0]
        
        self.current_time = int(min_pass_time)-self.pre_first_pass_delay;

        threading.Thread(target=lambda: self.exe_loop(1/self.virtual_seconds_per_real_second, self.control_at_time, self.kra, self.sim_data_a, self.sim_data_b)).start()

    # -------- EXECUTION THREAD LOOP --------
    def exe_loop(self, loop_time_delay, per_loop_function, kra, sim_data_a, sim_data_b):
        next_time = time.time() + loop_time_delay
        while True:
            time.sleep(max(0, next_time - time.time()))

            if(self.generate_report):
                if(self.report_counter >= self.report_frequency):
                    logger.info("\n\n\n-------- TIME REPORT A --------")
                    logger.info("Current Time: " + datetime.utcfromtimestamp(self.current_time).strftime('%Y-%m-%d %H:%M:%S'))
                    logger.info("Number of simulated passes: " + str(self.current_index_a))
                    
                    seconds_to_next_pass = int(sim_data_a[self.current_index_a][0])-self.current_time;
                    
                    days = seconds_to_next_pass//(60*60*24);
                    hours = seconds_to_next_pass//(60*60) - days *24;
                    minutes = seconds_to_next_pass//(60) - hours*60 - days*24*60;
                    seconds = seconds_to_next_pass - minutes* 60- hours*60*60 - days*24*60*60;

                    logger.info("Time to next pass:")
                    logger.info("\tDays: " + str(days))
                    logger.info("\tHours: " + str(hours))
                    logger.info("\tMinutes: " + str(minutes))
                    logger.info("\tSeconds: " + str(seconds))

                    logger.info("\n-------- STATUS REPORT A --------")
                    logger.info("Remaining bits: " + str(self.current_bits_a))

                    logger.info("\n-------- TIME REPORT B --------")
                    logger.info("Current Time: " + datetime.utcfromtimestamp(self.current_time).strftime('%Y-%m-%d %H:%M:%S'))
                    logger.info("Number of simulated passes: " + str(self.current_index_b))
                    
                    seconds_to_next_pass = int(sim_data_b[self.current_index_b][0])-self.current_time;
                    days = seconds_to_next_pass//(60*60*24);
                    hours = seconds_to_next_pass//(60*60) - days *24;
                    minutes = seconds_to_next_pass//(60) - hours*60 - days*24*60;
                    seconds = seconds_to_next_pass - minutes* 60 - hours*60*60 - days*24*60*60;

                    logger.info("Time to next pass:")
                    logger.info("\tDays: " + str(days))
                    logger.info("\tHours: " + str(hours))
                    logger.info("\tMinutes: " + str(minutes))
                    logger.info("\tSeconds: " + str(seconds))

                    logger.info("\n-------- STATUS REPORT B --------")
                    logger.info("Remaining bits: " + str(self.current_bits_b))

                    self.report_counter =0;

            next_time += loop_time_delay
            self.current_time += 1;
            
            if(self.generate_report):
                self.report_counter +=1;

            per_loop_function()

    # -------- PER LOOP FUNCTION --------
    def control_at_time(self):
        data_a = self.sim_data_a[self.current_index_a];
        if(self.current_time >= int(data_a[0])):
            self.current_bits_a += int(data_a[2]);
            self.current_index_a = (self.current_index_a + 1) % len(self.sim_data_a);

        data_b = self.sim_data_b[self.current_index_b];
        if(self.current_time >= int(data_b[0])):
            self.current_bits_b += int(data_b[2]);
            self.current_index_b = (self.current_index_b + 1) % len(self.sim_data_b);

        if(self.current_bits_a >= self.key_bits_release_threshold and self.current_bits_b >= self.key_bits_release_threshold):
            multiplier_a = self.current_bits_a//self.key_bits_release_threshold;
            multiplier_b = self.current_bits_b//self.key_bits_release_threshold;
            key_release_size = self.key_bits_release_threshold*multiplier_a;

            if(self.key_bits_release_threshold*multiplier_b < self.key_bits_release_threshold*multiplier_a):
                key_release_size = self.key_bits_release_threshold*multiplier_b;

            release_return = self.kra.releaseKeys(key_release_size) - key_release_size;
            
            self.current_bits_a += release_return;
            self.current_bits_b += release_return;
            #logger.info("\tPASSING " + str(multiplier*self.key_bits_release_threshold) + " BITS")


def main():
    parser = argparse.ArgumentParser(
        description="""
        Start satellite driver between local and remote node.
        """)
    parser.add_argument(
        'site',
        metavar='S',
        type=str,
        nargs=1,
        help='Remote site to send keys to.'
    )
    parser.add_argument(
        '-d','--qkd_dir',
        default=f"{path.expanduser('~/.qkd')}",
        dest='qkd_dir',
        help='.qkd directory to use.'
    )
    parser.add_argument(
        '-a','--a_data',
        dest='site_a_data',
        help='The location of the local site\'s simulation data.'
    )
    parser.add_argument(
        '-b','--b_data',
        dest='site_b_data',
        help='The location of the remote site\'s simulation data.'
    )
    args = parser.parse_args()

    IsolatedReleaseSim(args.site_a_data, args.site_b_data, args.qkd_dir, args.site[0])

if __name__ == "__main__":
    main()
