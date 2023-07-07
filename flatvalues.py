#!/bin/python

import csv

def flatten(fname):
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
    flatten("values-edited.txt")