## mint

Wrapper script/code to interact with [`mintable`](https://github.com/kevinschaich/mintable/)

Requires:
 - `mintable` (`npm install -g mintable`)
 - `whiptail` (typically installable as `newt` or `libnewt`)
 - `figlet`
 - `bash` 4.0+
 - `python` 3.7+

I use [plaid](http://plaid.com/) to get the account information, and export those to local CSV files.

`./mint setup` prompts me to setup any accounts, and sets up a git-tracked `./data` directory for my account balances/transactions.

For the `csv-export-setup` step of `./mint setup`, where `<THIS_DIR>` is the absolute path to this repo on my file system; I enter: `<THIS_DIR>/data/transactions.csv` and `<THIS_DIR>/balances.csv`

After `./mint fetch`, if the `./data` directory has untracked changes, it adds it to the local git repo, so that I never lose any of the data.

`./mint fetch` is run in the background once every few hours, using [`bgproc`](https://github.com/seanbreckenridge/bgproc/blob/master/personal_jobs/mint.job)

---

`budget` contains python to read/process the transactions. It uses the `git` history to create snapshots of the account balances, so all changes to any of my accounts are timestamped and I can look at balance over time.

This isn't a drop-in replacement for some general budgeting system, it has the features that I want. I split private/public parts into optional importable modules, but, If anyone wants to use this, would probably require you to edit the python to fit your needs.

---

### Status

Currently this:

- parses all of the data from mintable
- can parse the additional, manually edited transactions/balances files; includes TUIs to edit manually tracked balances
- loads all the balance snapshots/transactions into memory and drops you into IPython
- cleans up transaction data; has patterns to fix transaction names/sort into meta-categories
- has a basic account summary

Need to:

- create code to track budget
- see if transactions get overwritten? it seems that `mintable` just saves the transactions it gets to the file, so may have to use the `git` repo to get transactions from the past

---

To install as an editable package (so changes to the code immediately update):

```
git clone https://github.com/seanbreckenridge/mint && cd ./mint
cd ./budget
pip install -e .
python3 -m budget --repl
```

To my aliases file, I add:

```shell
export MINT_DATA="${HOME}/Repos/mint/data"
alias budget='python3 -m budget'
```

