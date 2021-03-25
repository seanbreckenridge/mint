## mint

Wrapper script/code to interact with [`mintable`](https://github.com/kevinschaich/mintable/). Used as part of [HPI](https://github.com/seanbreckenridge/HPI)

Requires:

- `mintable` (`npm install -g mintable`)
- `whiptail` (typically installable as `newt` or `libnewt`)
- `figlet`
- `bash` 4.0+
- `python` 3.7+

I use [`plaid`](http://plaid.com/) to get the account information, and export those to local CSV files.

`./mint setup` prompts me to setup any accounts, and sets up a git-tracked `./data` directory for my account balances/transactions.

For the `csv-export-setup` step of `./mint setup`, where `<THIS_DIR>` is the absolute path to this repo on my file system; I enter: `<THIS_DIR>/data/transactions.csv` and `<THIS_DIR>/data/balances.csv`

After `./mint fetch`, if the `./data` directory has untracked changes, it adds a commit to the local git repo, so that I never lose any of the data, when `plaid` stops returning old transactions.

I run `./mint fetch` is run in the background once [every few hours](https://github.com/seanbreckenridge/dotfiles/blob/master/.local/scripts/supervisor/jobs/linux/mint.job)

---

`budget` contains python to read/process the transactions. It uses the `git` history to create snapshots of the account balances, so all changes to any of my accounts are timestamped and I can look at and graph my assets over time.

This isn't a drop-in replacement for some general budgeting system, it has the features that I want. I split private/public parts into optional importable modules, but, If anyone wants to use this, would probably require you to edit the python to fit your needs.

---

This:

- parses all of the data from mintable
- can parse the additional, manually edited transactions/balances files; includes TUIs to edit manually tracked balances
- loads all the balance snapshots/transactions into memory (using git history to find possibly overwritten ones) and drops you into `IPython`
- cleans up transaction data; has patterns to fix transaction names/sort into meta-categories

[`budget.analyze`](./budget/budget/analyze):

- has a account/transaction summary, summarizes spending categories over a couple time periods
- uses the git history to create a graph of account balances over time, removing outliers that might have occurred because of account transfers.

---

To install as an editable package (so changes to the code immediately update):

```
git clone https://github.com/seanbreckenridge/mint && cd ./mint/budget
pip install -e .
python3 -m budget
```

```
Usage: budget [OPTIONS] COMMAND [ARGS]...

  Interact with my budget!

Options:
  --help  Show this message and exit.

Commands:
  accounts     Show a summary/graph of the current/past accounts balances
  edit-manual  Edit the manual balances file
  summary      Prints a summary of current accounts/recent transactions
```

Shorthands I add to my shell config:

```shell
# (~/Repos/mint is where I keep the cloned dir)
export MINT_DATA="${HOME}/Repos/mint/data"
alias budget-history='python3 -m budget accounts --graph'
# to edit the account/transaction map information
alias 'budget-config=fd -IH conf.py --full-path $REPOS/mint | fzf | xargs -r -I {} editor {}'
```

`budget summary` emits markdown tables/formatting, so it can be used nicely with a terminal markdown viewer like [`glow`](https://github.com/charmbracelet/glow):

```shell
# ( defined in my aliases/functions file )
budget-summary() {
  if [[ -z "$1" ]]; then
    python3 -m budget summary | glow -
  else
    python3 -m budget summary "$@"
  fi
}
```
