# -*- coding: utf-8 -*-
"""
Created on Tue May 15 14:02:04 2018

@author: rpriem
"""
from __future__ import absolute_import, division, print_function
from builtins import (
    ascii,
    bytes,
    chr,
    dict,
    filter,
    hex,
    input,
    int,
    map,
    next,
    oct,
    open,
    pow,
    range,
    round,
    str,
    super,
    zip,
)


import os
import subprocess
import shlex
import sys
import time
from argparse import ArgumentParser


def main(
    DOE_path="./", Output_path="./", budget=10, max_simu=1, n_eval_sub=35, n_init=5, n_comp=2
):
    cases = os.listdir(DOE_path)
    print(cases)

    p = []
    p_count = 0
    delete = 0

    for case in cases:
        path_doe_dir = DOE_path + "/" + case
        path_all_doe = os.listdir(path_doe_dir)
        print(path_all_doe)
        path_res = Output_path + "/" + case
        os.mkdir(path_res)
        log_dir = os.path.join(path_res, "main")
        os.mkdir(log_dir)

        for i in range(len(path_all_doe)):

            path_doe_i = path_doe_dir + "/" + path_all_doe[i]
            output_dir = path_res + "/res_" + str(i)
            os.mkdir(output_dir)

            output_filename = os.path.join(log_dir, "main_%d.log" % (i))
            output_file = open(output_filename, "w")

            # Launch String max_eval res_path case n_init n_reg
            exp = (
                "python -u run_REMBO.py --n_iter=%s --res_path=%s --case=%s --doe_size=%s --budget=%s --doe_path=%s --n_comp=%d"
                % (budget, output_dir, case, n_init, n_eval_sub, path_doe_i,n_comp)
            )

            p_i = subprocess.Popen(
                shlex.split(exp), stdout=output_file, stderr=output_file
            )

            print("Running experiment %s. PID = %d" % (exp, p_i.pid))
            sys.stdout.flush()
            p.append(p_i)
            p_count += 1
            delete += 1

            # Check if process is finished to run another one
            while p_count >= max_simu:
                for p_i in p:
                    if p_i.poll() is not None:
                        sys.stdout.write("\n")
                        print("Experiment with PID = %d finished" % (p_i.pid))
                        p_count -= 1
                        p.remove(p_i)
                if p_count != 0:
                    time.sleep(10)
                    sys.stdout.write(".")
                    sys.stdout.flush()
            sys.stdout.flush()

    running = True
    while running:
        for p_i in p:
            if p_i.poll() is not None:
                sys.stdout.write("\n")
                print("Experiment with PID = %d finished" % (p_i.pid))
                p.remove(p_i)
            else:
                running = True
        if not p:
            running = False
        time.sleep(30)
        sys.stdout.write(".")
        sys.stdout.flush()
    print("FINISHED !!!")


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "--doe_path", dest="doe_path", help="paht to does", type=str, default="./"
    )
    parser.add_argument(
        "--budget",
        dest="budget",
        help="maximum number of evaluations",
        type=int,
        default=20,
    )
    parser.add_argument(
        "--max_simu",
        dest="max_simu",
        help="Maximum of simulation to run in parallel",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--res_path", dest="res_path", help="path to res folder", type=str, default="./"
    )
    parser.add_argument(
        "--n_eval", dest="n_eval", help="number of eval in sub opt", type=int, default=5
    )
    parser.add_argument(
        "--n_init",
        dest="n_init",
        help="number of points in initial doe in sub opt",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--n_comp",
        dest="n_comp",
        help="number of component",
        type=int,
        default=2,
    )

    # test to save
    kwargs = parser.parse_args()

    main(
        DOE_path=kwargs.doe_path,
        Output_path=kwargs.res_path,
        budget=kwargs.budget,
        max_simu=kwargs.max_simu,
        n_eval_sub=kwargs.n_eval,
        n_init=kwargs.n_init,
        n_comp=kwargs.n_comp,
    )
