## my-mintable

Wrapper script/code to interact with [`mintable`](https://github.com/kevinschaich/mintable/)

I use [plaid](http://plaid.com/) to get the account information, and export those to local CSV files.

`./mint setup` prompts me to setup any accounts, and sets up a git-tracked `./data` directory for my account balances/transactions.

For the `csv-export-setup` step of `./mint setup`, where `<THIS_DIR>` is the absolute path to this repo on my file system; I enter: `<THIS_DIR>/data/transactions.csv` and `<THIS_DIR>/balances.csv`

After `./mint fetch`, if the `./data` directory has untracked changes, it adds it to the local git repo, so that I never lose any of the data.

`./mint fetch` is run in the background once every few hours, using [`bgproc`](https://github.com/seanbreckenridge/bgproc)

---

TODO: add code to analyze/read in the data.
