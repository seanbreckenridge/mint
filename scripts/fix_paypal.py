import csv

disc = []
with open("/home/sean/Repos/mint/data/raw/paypal.csv") as f:
    cf = csv.reader(f)
    header = next(cf)
    for line in cf:
        disc.append(line)
acc_name = "PayPal"
fixed_disc = []
for ds in disc:
    month, day, year = list(map(int, ds[0].split("/")))
    fixed_date = f"{year}-{month}-{day}"
    # ignore other currencies that
    # get converted to USD as separate
    # transactions
    if ds[6].lower() not in ["usd", ""]:
        print("ignoring {}".format(ds))
        continue

    col = [fixed_date, -1 * float(ds[7]), ds[3], acc_name, ds[4]]
    fixed_disc.append(col)

with open("/home/sean/Repos/mint/data/old_transactions.csv", "a") as f:
    cs = csv.writer(f)
    for l in fixed_disc:
        cs.writerow(l)
