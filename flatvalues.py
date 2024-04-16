#!/bin/python
"""From a values file, get a flattened version,
which can be fed into the same algorithms to work with labels as if they are unrelated.
"""
import csv


def flatten(fname):
    assert fname.startswith("vocab/") and fname.endswith(
        ".csv"
    ), "Only values files in the corresponding folder can be flattened"
    if fname.endswith(".flat.csv"):
        return
    result = []
    with open(fname) as fin:
        for row in csv.reader(fin):
            for v in row:
                c = v.strip().lower()
                if c:
                    result += [c]

    lastdot = fname.rfind(".")
    fout = f"{fname[:lastdot]}.flat.{fname[lastdot+1:]}"
    with open(fout, "w") as fout:
        fout.write("\n".join(result))


if __name__ == "__main__":
    flatten("vocab/values.csv")
