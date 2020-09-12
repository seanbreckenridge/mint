import csv
disc = []
with open("/home/sean/Repos/mint/data/raw/credit_history.csv") as f:
    cf = csv.reader(f)
    for line in cf:
        disc.append(line)
disc = [d[1:] for d in disc]
disc = disc[1:]
account_name = "Credit Card"
def fix_date(dstr):
    items = reversed(list(map(str, dstr.split("/"))))
    return "-".join(items)
fixed = [[fix_date(d[0]), d[2], d[1], account_name, d[3]] for d in disc]
with open("/home/sean/Repos/mint/data/old_transactions.csv", 'a') as f:
    cs = csv.writer(f)
    for l in fixed:
        cs.writerow(l)
