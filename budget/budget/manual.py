# manually log current for some account
# edits manual_balances.csv
# this would require a file that looks like balances.csv
# at manual_balances.csv, which has data that either
# cant be accessed from an API or cash I have on-hand
# this writes back to the file, but *doesnt commit*,
# that'll get done if you run ./mint fetch
# or just let the task in background auto-commit

import sys
import csv
from pathlib import Path
from typing import List

import pick  # type: ignore[import]
import vimbuffer  # type: ignore[import]

# main entrypoint
#
# pick one of the balances
# edit the line in vim
# checks to make sure the ints are still ints
# write back
def edit_manual_balances(bfile: Path) -> None:
    before_data: List[str] = []
    with bfile.open(newline="") as bf:
        bf_reader = csv.reader(bf)
        header: List[str] = next(bf_reader)
        for line in bf_reader:
            before_data.append(line)  # type: ignore

    # ask user for input
    try:
        _, idx = pick.pick([",".join(bf) for bf in before_data], "edit which balance?")
    except KeyboardInterrupt:
        return

    # edit in vim
    edit_balance: List[str] = before_data[idx]
    edited_balance: str = vimbuffer.buffer(
        string="# edit the line and then save and quit!\n" + ",".join(before_data[idx])
    )

    # remove extra lines, get the line with the data
    edited_data: List[str] = list(filter(str.strip, edited_balance.splitlines()))[
        -1
    ].split(",")

    # validate
    assert len(edited_data) == len(
        edit_balance
    ), "Number of columns has changed since before!"
    try:
        float(edited_data[3])
        float(edited_data[4])
        float(edited_data[5])
    except ValueError as ve:
        print("Error converting the values to floats!", file=sys.stderr)
        print(str(ve), file=sys.stderr)
        return

    # replace data
    before_data[idx] = edited_data

    # writeback to file
    with bfile.open("w", newline="") as bf:
        bf_writer = csv.writer(bf)
        bf_writer.writerow(header)
        bf_writer.writerows(before_data)
