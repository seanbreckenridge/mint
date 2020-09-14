import csv

disc = []
with open("/home/sean/Repos/mint/data/raw/bank_history.csv") as f:
    cf = csv.reader(f)
    for line in cf:
        disc.append(line)
acc_name = "Checking"
disc = disc[1:]
fixed = [[d[0], -1 * float(d[-2]), d[1], acc_name, d[3]] for d in disc]
with open("/home/sean/Repos/mint/data/old_transactions.csv", "a") as f:
    cs = csv.writer(f)
    for l in fixed:
        cs.writerow(l)
