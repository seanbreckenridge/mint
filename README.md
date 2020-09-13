## mint

Wrapper script/code to interact with [`mintable`](https://github.com/kevinschaich/mintable/)

Requires:
 - `mintable` (`npm install -g mintable`)
 - `whiptail` (typically installable as `newt` or `libnewt`)
 - `figlet`

I use [plaid](http://plaid.com/) to get the account information, and export those to local CSV files.

`./mint setup` prompts me to setup any accounts, and sets up a git-tracked `./data` directory for my account balances/transactions.

For the `csv-export-setup` step of `./mint setup`, where `<THIS_DIR>` is the absolute path to this repo on my file system; I enter: `<THIS_DIR>/data/transactions.csv` and `<THIS_DIR>/balances.csv`

After `./mint fetch`, if the `./data` directory has untracked changes, it adds it to the local git repo, so that I never lose any of the data.

`./mint fetch` is run in the background once every few hours, using [`bgproc`](https://github.com/seanbreckenridge/bgproc/blob/master/personal_jobs/mint.job)

---

`budget` contains python to read/process the transactions. It uses the `git` history to create snapshots of the account data so all changes to any of my accounts are timestamped.

Currently, all it does is parse the balance/transaction CSV files into ADTs and drops me into an `IPython` shell.

Plan is to do some more data cleaning/jupyter visualization and make some graphs.

To install as an editable package (so changes to the code immediately update):

```
git clone https://github.com/seanbreckenridge/mint && cd ./mint
cd ./budget
pip install -e .
budget ../data
```
