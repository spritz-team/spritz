import concurrent.futures
import glob
import hashlib
import os
from math import ceil
from typing import NewType

from spritz.framework.framework import (  # noqa: F401
    add_dict_iterable,
    read_chunks,
    write_chunks,
)

MERGE_RESULT_FNAME = "tmp_special_"

"""
# Result is something like:
{
    "dataset1": {
        # result of single dataset
    }
}
"""
Result = NewType("Result", dict[str, dict])
# from typing import TypedDict

# class ChunkResult(TypedDict):


# class Result(TypedDict):
#     results: list[ChunkResult]
#     errors: list[ChunkErred]


def read_inputs(inputs: list[str]) -> list[Result]:
    inputs_obj = []
    for input in inputs:
        job_result = read_chunks(input)
        #print("JOB RESULT")
        #print(job_result, job_result == -99999, inputs)
        new_job_result = []
        if isinstance(job_result, list):
            for job_result_single in job_result:
                if job_result_single["result"] != {}:
                    new_job_result.append(job_result_single["result"]["real_results"])
            # job_result = new_job_result
            # if check_input(job_result):
            #     inputs_obj.append(job_result["real_results"])
            inputs_obj.extend(new_job_result)
        else:
            # job_result = {k: v for k, v in job_result.items() if k in ["result", "error"]}
            # del job_result["result"]["performance"]
            # if check_input(job_result):
            #     inputs_obj.append(job_result["real_results"])
            inputs_obj.append(job_result)
    # print(inputs_obj)
    return inputs_obj


def check_input(input: Result) -> bool:
    # Returns true if input is ok
    for chunk in input:
        if input["result"] == {} or input["error"] != "":
            return False
    return True


def postprocess_inputs(inputs):
    for input in inputs:
        if MERGE_RESULT_FNAME in input.split("/")[-1]:
            print("removing", input)
            os.remove(input)


def reduction(inputs, reduce_function, output):
    inputs_obj = read_inputs(inputs)
    result = reduce_function(inputs_obj)
    postprocess_inputs(inputs)
    print("writing to", output)
    write_chunks(result, output)


def split_inputs(inputs, elements_for_task):
    ntasks = ceil(len(inputs) / elements_for_task)
    splits = []
    for i in range(ntasks):
        start = min(i * elements_for_task, len(inputs) - 1)
        stop = min((i + 1) * elements_for_task, len(inputs))
        if start == stop:
            break
        splits.append(slice(start, stop))

    return splits


def create_tree(inputs, reduce_function, output, executor, elements_for_task=10):
    if len(inputs) <= elements_for_task:
        reduction(inputs, reduce_function, output)

    else:
        output_dir = "/".join(output.split("/")[:-1])
        output_format = output.split(".")[-1]
        splits = split_inputs(inputs, elements_for_task)
        tasks = []
        new_inputs = []

        for itask, split in enumerate(splits):
            h = hashlib.new("sha256")
            h.update(str(itask).encode("utf-8"))
            for input in inputs[split]:
                h.update(input.encode("utf-8"))
            h = h.hexdigest()[:10]
            output_tmp = f"{output_dir}/{MERGE_RESULT_FNAME}_{h}.{output_format}"
            tasks.append(
                executor.submit(reduction, inputs[split], reduce_function, output_tmp)
            )
            new_inputs.append(output_tmp)
        concurrent.futures.wait(tasks)
        for task in tasks:
            task.result()

        create_tree(new_inputs, reduce_function, output, executor, elements_for_task)


def main():
    # basepath = "/gwdata/users/gpizzati/condor_processor/results"
    # inputs = glob.glob(f"{basepath}/results_job_*.pkl")
    basepath = os.path.abspath("condor")
    inputs = glob.glob(f"{basepath}/job_*/chunks_job.pkl")[:]
    output = f"{basepath}/results_merged_new.pkl"
    reduce_function = sum
    reduce_function = add_dict_iterable
    elements_for_task = 10
    cpus = 10
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpus) as executor:
        create_tree(
            inputs,
            reduce_function,
            output,
            executor,
            elements_for_task=elements_for_task,
        )

    results = read_chunks(output)
    # datasets = list(filter(lambda k: "root:" not in k, results.keys()))
    datasets = results.keys()


if __name__ == "__main__":
    main()
