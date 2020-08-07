# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 13:03:13 2020

@author: rpriem
"""

import numpy as np
import scipy as scp
import time
import os
import pickle as pkl
from argparse import ArgumentParser

from REMBO import RunRembo
from sego.cases.case_generator import _import_case


def main(
    func_name="MB_10",
    n_comp=2,
    init_doe=5,
    budget=35,
    n_iter=10,
    dir_out=None,
    doe_path=None,
):

    func_name_in = "SEGO-" + func_name

    case = _import_case(func_name)()

    high_dim = len(case["vars"])

    if doe_path is not None:
        x_all = np.load(os.path.join(doe_path, "doe.npy"))
        y_all = np.load(os.path.join(doe_path, "doe_response.npy"))
    else:
        x_all = []

    time_0 = time.process_time()

    case_conf = {}
    case_conf["doe"] = len(x_all)
    case_conf["vars"] = case["vars"]
    case_conf["analytical_diff"] = False
    case_conf["con_sig"] = 0
    case_conf["con_tol"] = []
    case_conf["criterion"] = "REMBO"
    case_conf["con_type"] = []
    case_conf["cst_criterion"] = []
    case_conf["mode"] = "Minimization"
    case_conf["funs"] = func_name
    case_conf["optimizer"] = "snopt"
    case_conf["reclust_rate"] = 10
    case_conf["n_multistart"] = 1
    case_conf["smooth_recombination"] = False

    for i in range(n_iter):
        _, _, _, _, fs_true, high_s = RunRembo(
            low_dim=n_comp,
            high_dim=high_dim,
            func_type=func_name_in,
            initial_n=init_doe,
            total_itr=budget,
            kern_inp_type="psi",
            ARD=True,
            noise_var=0,
            matrix_type="normal",
        )
        time_i = time.process_time() - time_0

        if i == 0 and doe_path is None:
            x_all = high_s
            y_all = fs_true
        else:
            x_all = np.concatenate((x_all, high_s))
            y_all = np.concatenate((y_all, fs_true))

        if dir_out is not None:

            np.save(os.path.join(dir_out, "doe.npy"), x_all)
            np.save(os.path.join(dir_out, "doe_response.npy"), -y_all)
            np.save(os.path.join(dir_out, "time.npy"), time_i)

            case_file = open(os.path.join(dir_out, "case.pkl"), "wb+")
            pkl.dump(case_conf, case_file)
            case_file.close()

    return x_all, y_all


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "--doe_path", dest="doe_path", help="paht to does", type=str, default=None
    )
    parser.add_argument(
        "--budget",
        dest="budget",
        help="budget of the inner optimization",
        type=int,
        default=35,
    )
    parser.add_argument(
        "--res_path", dest="res_path", help="path to res folder", type=str, default="./"
    )
    parser.add_argument(
        "--case", dest="case", help="name of the case pb", type=str, default="MB_10"
    )
    parser.add_argument(
        "--n_comp", dest="n_comp", help="number of component", type=int, default=2
    )
    parser.add_argument(
        "--doe_size",
        dest="doe_size",
        help="number of point in the doe",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--n_iter", dest="n_iter", help="number of bo optim", type=int, default=10
    )

    # test to save
    kwargs = parser.parse_args()

    main(
        func_name=kwargs.case,
        n_comp=kwargs.n_comp,
        init_doe=kwargs.doe_size,
        budget=kwargs.budget,
        n_iter=kwargs.n_iter,
        dir_out=kwargs.res_path,
        doe_path=kwargs.doe_path,
    )
