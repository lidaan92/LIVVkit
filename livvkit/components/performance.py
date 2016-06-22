# Copyright (c) 2015, UT-BATTELLE, LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Performance Test Base Module.  
"""
import os
import glob
import json
import pprint
import numpy as np
import matplotlib.pyplot as plt


from livvkit.util import functions
from livvkit.util import variables
from livvkit.util import colormaps
from livvkit.util.datastructures import LIVVDict
from livvkit.util.datastructures import ElementHelper
from livvkit.util.functions import sort_processor_counts
from livvkit.util.functions import sort_scale

def _run_suite(case, config, summary):
    """ Run the full suite of performance tests """
    config["name"] = case
    result = LIVVDict() 
    timing_data = dict()
    bundle = variables.performance_model_module
    model_dir = os.path.join(variables.model_dir, config['data_dir'], case)
    bench_dir = os.path.join(variables.bench_dir, config['data_dir'], case)
    plot_dir = os.path.join(variables.output_dir, "performance", "imgs")
    plot_relpath = os.path.relpath(plot_dir, os.path.dirname(plot_dir))
    model_cases = functions.collect_cases(model_dir)
    bench_cases = functions.collect_cases(bench_dir)
    functions.mkdir_p(plot_dir)

    for subcase in sorted(model_cases):
        bench_subcases = bench_cases[subcase] if subcase in bench_cases else []
        timing_data[subcase] = dict()
        for mcase in model_cases[subcase]:
            config["case"] = "-".join([subcase, mcase])
            bpath = (os.path.join(bench_dir, subcase, mcase.replace("-", os.sep))
                            if mcase in bench_subcases else None)
            mpath = os.path.join(model_dir, subcase, mcase.replace("-", os.sep))
            timing_data[subcase][mcase] = _analyze_case(mpath, bpath, config)
   
    timing_plots = []
    timing_plots.append(generate_scaling_plot(
            bundle.weak_scaling(timing_data, config['scaling_var']),
            "Weak Scaling for " + case.capitalize(), "", 
            os.path.join(plot_dir, case + "_weak_scaling.png")
        ))
    timing_plots.append(generate_scaling_plot(
                bundle.strong_scaling(timing_data, config['scaling_var']),
                "Strong Scaling for " + case.capitalize(), "",
                os.path.join(plot_dir, case + "_strong_scaling.png")
        ))
    timing_plots = timing_plots + [generate_timing_breakdown_plot(timing_data[s], config['scaling_var'],
            "Timing Breakdown for " + case.capitalize()+" "+s, "",
            os.path.join(plot_dir, case+"_"+s+"_timing_breakdown.png")
        ) for s in sorted(timing_data.keys(), key=sort_scale)]
  
    el = [
            ElementHelper.gallery("Performance Plots", timing_plots)
         ]

    result = ElementHelper.section(case, config["description"], el)
    summary[case] = _summarize_result(timing_data, config)
    _print_result(case, summary) 
    functions.create_page_from_template("performance.html",
            os.path.join(variables.index_dir, "performance", case+".html"))
    functions.write_json(result, os.path.join(variables.output_dir, "performance"), case+".json")


def _analyze_case(model_dir, bench_dir, config):
    """ Run all of the performance checks on a particular case """
    model_timings = set(glob.glob(os.path.join(model_dir, "*" + config["timing_ext"])))
    if bench_dir is not None:
        bench_timings = set(glob.glob(os.path.join(bench_dir, "*" + config["timing_ext"])))
    else:
        bench_timings = set()
    if not len(model_timings):
        return LIVVDict(model=LIVVDict(), bench=LIVVDict()) 
    model_stats = generate_timing_stats(model_timings, config['timing_vars'])
    bench_stats = generate_timing_stats(bench_timings, config['timing_vars'])
    return dict(model=model_stats, bench=bench_stats) 


def _print_result(case, summary):
    """ Show some statistics from the run """
    for case, case_data in summary.items():
        for dof, data in case_data.items():
            print("    " + case + " " + dof)
            print("    -------------------")
            for header, val in data.items():
                print("    " + header + " : " + str(val))
            print("")


def _write_result(case,result):
    """ Take the result and write out a JSON file """
    outpath = os.path.join(variables.output_dir, "Performance", case)
    util.functions.mkdir_p(outpath)
    with open(os.path.join(outpath, case+".json"), 'w') as f:
        json.dump(result, f, indent=4)


def _summarize_result(result, config):
    """ Trim out some data to return for the index page """
    timing_var = config['scaling_var']
    summary = LIVVDict()
    for size, res in result.items():
        proc_counts = []
        bench_times = []
        model_times = []
        for proc, data in res.items():
            proc_counts.append(int(proc[1:]))
            try:
                bench_times.append(data['bench'][timing_var]['mean'])
            except KeyError: 
                pass
            try:
                model_times.append(data['model'][timing_var]['mean'])
            except KeyError:
                pass
        if model_times != [] and bench_times != []:
            time_diff = np.mean(model_times)/np.mean(bench_times)
        else: time_diff = 'NA'
        summary[size]['Proc. Counts'] = ", ".join([str(x) for x in sorted(proc_counts)])
        summary[size]['Mean Time Diff (% of benchmark)'] = time_diff
    return summary


def _populate_metadata():
    """ Provide some top level information for the summary """
    return {"Type"    : "Summary",
            "Title"   : "Performance",
            "Headers" : ["Proc. Counts", "Mean Time Diff (% of benchmark)"]}


def generate_timing_stats(file_list, var_list):
    """
    Parse all of the timing files, and generate some statistics
    about the run.

    Args:
        model_dir: Path to the model output
        bench_dir: Path to the benchmark data
        config: A dictionary containing option specifications

    Returns:
        A LIVVDict containing values that have the form: 
            [mean, min, max, mean, diff. from bench mean]
    """
    timing_result = LIVVDict()
    timing_summary = dict()
    for file in file_list:
        timing_result[file] = parse_gptl(file, var_list)
    for var in var_list:
        var_time = []
        for f, data in timing_result.items():
            if var in data: 
                var_time.append(data[var])
        if len(var_time):
            var_mean = np.mean(var_time)
            var_max  = np.max(var_time)
            var_min  = np.min(var_time)
            var_std  = np.std(var_time)
            timing_summary[var] = {'mean':var_mean, 'max':var_max, 'min':var_min, 'std':var_std}
    return timing_summary


def generate_scaling_plot(timing_data, title, description, plot_file):
    """ 
    Generate a scaling plot.  

    Args:
        timing_data: data returned from a bundle's *_scaling method
        tite: the title of the plot
        description: a description of the plot
        plot_file: the file to write out to

    Returns:
        an image element containing the plot file and metadata
    """
    proc_counts = timing_data['proc_counts']
    if len(proc_counts) > 2:
        plt.figure(figsize=(10,8), dpi=150)
        plt.title(title)
        plt.xlabel("Number of processors")
        plt.ylabel("Runtime (s)")
        
        for case, case_color in zip(['bench','model'], ['#91bfdb','#fc8d59']):
            case_data = timing_data[case]
            means = case_data['means']
            mins = case_data['mins']
            maxs = case_data['maxs']

            plt.fill_between(proc_counts, mins, maxs, facecolor=case_color, alpha=0.5)
            plt.plot(proc_counts, means, 'o-', color=case_color, label=case)

        plt.legend(loc='best')
        plt.savefig(plot_file)
        plt.close()
    return ElementHelper.image_element(title, description, os.path.basename(plot_file))


def generate_timing_breakdown_plot(timing_stats, scaling_var, title, description, plot_file):
    """ 
    Description

    Args:
        timing_stats: a dictionary of the form 
            {proc_count : {model/bench : { var : { stat : val }}}}
        scaling_var: the variable that accounts for the total runtime
        title: the title of the plot
        description: the description of the plot
        plot_file: the file to write the plot out to
    Returns:
        an image element containing the plot file and metadata
    """
    cmap_data = colormaps._viridis_data
    n_subplots = len(timing_stats.keys())
    left_bounds = [i+1 for i in range(n_subplots)]
    fig, ax = plt.subplots(1, n_subplots+1, figsize=(3*(n_subplots+2), 5))
    for plot_num, p_count in enumerate(sorted(timing_stats.keys(), key=sort_processor_counts)):
        case_data = timing_stats[p_count]
        sub_ax = plt.subplot(1, n_subplots+1, plot_num+1)
        sub_ax.set_title(p_count)
        sub_ax.set_ylabel('Runtime (s)') 
        for case, var_data in case_data.items():
            if case == 'bench':
                bar_num = 2
            else: 
                bar_num = 1

            var_datum = sorted(var_data.keys(), reverse=True)
            
            cmap_stride = int(len(cmap_data)/(len(var_datum)+1))
            colors = [cmap_data[i*cmap_stride] for i in range(len(var_datum))]
            
            offset = 0
            if var_data != {}:
                for idx, var in enumerate(var_datum):
                    if var != scaling_var:
                        plt.bar(bar_num, var_data[var]['mean'], 0.8, bottom=offset, 
                                color=colors[idx], label=(var if bar_num == 1 else '_none') )
                        offset+=var_data[var]['mean']
                    else: 
                        s_idx = idx
                
                plt.bar(bar_num, var_data[scaling_var]['mean']-offset, 0.8, bottom=offset, 
                        color=colors[s_idx], label=(scaling_var if bar_num == 1 else '_none') )
                
                sub_ax.set_xticks([1.4, 2.4])
                sub_ax.set_xticklabels(('test', 'bench'))
    
    plt.legend(loc=6, bbox_to_anchor=(1.05,0.5))
    plt.tight_layout()

    sub_ax = plt.subplot(1, n_subplots+1, n_subplots+1)
    hid_bar = plt.bar(1, 100)
    for group in hid_bar:
            group.set_visible(False)
    sub_ax.set_visible(False)
    
    plt.savefig(plot_file)
    plt.close()
    return ElementHelper.image_element(title, description, os.path.basename(plot_file))


def parse_gptl(file_path, var_list):
    """
    Read a GPTL timing file and extract some data.

    Args:
        file_path: the path to the GPTL timing file
        var_list: a list of strings to look for in the file

    Returns:
        A LIVVDict containing key-value pairs of the variables
        and the times associated with them
    """
    timing_result = LIVVDict()
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            for var in var_list:
                for line in f:
                    if var in line:
                        timing_result[var] = float(line.split()[4])/int(line.split()[2])
                        break
    return timing_result

