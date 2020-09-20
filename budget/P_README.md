## budget

Some configuration is split into private configuration files (to hide my own account details), tried to defined `NamedTuple` interfaces/describe what I was doing there.

In addition to the `transactions.csv`/`balances.csv` file, this maintains `old_transactions.csv`, which are exported/wrangled data from other sources. Also maintains `manual_balances.csv`, which is in the same format as `balances.csv`, and is manually edited `python3 -m budget --edit-manual`.

My data dir looks like:

```
>>>PMARK
#!/bin/sh
perl -E 'print "`"x3, "\n"'
cd ../data
tree -I 'tags*' .
perl -E 'print "`"x3, "\n"'
```
