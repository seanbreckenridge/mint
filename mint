#!/bin/bash
# setup/interact with accounts, fetch data and keep it tracked in git

THIS_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
readonly CONFIG_FILE="${THIS_DIR}/mintable.jsonc" # config file is kept in this dir
readonly DATA_DIR="${THIS_DIR}/data"              # where transactions/balances are kept

[[ ! -d "$DATA_DIR" ]] && mkdir "$DATA_DIR"

# mint with config
mintc() {
	mintable "$@" --config-file "$CONFIG_FILE"
}

prompt() {
	echo -en "${1} (N/y) > "
	read -r
	case "$REPLY" in
	y | Y)
		return 0
		;;
	*)
		return 1
		;;
	esac
}

setup_data_version_control() {
	if [[ ! -r "${DATA_DIR}/transactions.csv" ]]; then
		echo "Can't read transactions.csv file!"
		return 1
	fi
	if [[ ! -d "${DATA_DIR}/.git" ]]; then
		cd "${DATA_DIR}" || {
			echo "Could not cd into the data directory..." 1>&2
			return 1
		}
		echo "Creating git repo for transactions..."
		git init || return $?
	fi
}

commit_data_changes() {
	if cd "$DATA_DIR"; then
		# add any changes to a local git repo
		git add ./*.csv
		git commit -m "transaction updates" || echo "No changes detected in data directory..."
	else
		echo "Couldn't move into ${DATA_DIR}!" 1>&2 || return $?
	fi
}

CMD="${1:?No command provided! Provide either setup or fetch, or some other undlerying 'mintable' command}"
case "$CMD" in
setup)
	command -v mintable >/dev/null 2>&1 || npm install -g mintable
	prompt "Setup plaid authentication tokens?" && mintc plaid-setup
	prompt "Setup CSV export?" && mintc csv-export-setup
	prompt "Setup bank/investment accounts?" && mintc account-setup
	echo "Done with setup!"
	;;

fetch)
	shift
	mintc fetch "$@" &&
		setup_data_version_control &&
		commit_data_changes
	;;
*)
	printf "Couldn't find a command named '%s'\n" "$1" 1>&2
	echo "Trying to run it with mintable..."
	mintc "$@"
	;;
esac
