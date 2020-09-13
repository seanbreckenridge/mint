#!/bin/bash
# setup/interact with accounts, fetch data and keep it tracked in git

# Function to test if a command is on the users $PATH
# i.e. if they have a binary/script installed
havecmd() {
	if command -v "$1" >/dev/null 2>&1; then
		return 0
	else
		printf "Requires '%s', could not find that on your \$PATH\n" "$1" >&2
		return 1
	fi
}

# check commands
set -e
havecmd whiptail
havecmd figlet
havecmd tput
set +e

# get columns
declare TERMINAL_COLUMNS
TERMINAL_COLUMNS="${COLUMNS:-$(tput cols)}"

# setup whiptail colors; dark mode
declare -rx NEWT_COLORS='
root=black,black
window=,black
border=white,black
textbox=white,black
button=black,brightred
'

THIS_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
readonly CONFIG_FILE="${THIS_DIR}/mintable.jsonc" # config file is kept in this dir
readonly DATA_DIR="${THIS_DIR}/data"              # where transactions/balances are kept

[[ ! -d "$DATA_DIR" ]] && mkdir "$DATA_DIR"

# mint with config
mintc() {
	mintable "$@" --config-file "$CONFIG_FILE"
	return $?
}

prompt() {
	local width
	# use width of message
	width="$(wc -c <<<"$1")"
	# or default to 1/3rd of the terminal width
	((width < TERMINAL_COLUMNS / 3)) && width="$((TERMINAL_COLUMNS / 3))"
	whiptail --yesno --defaultno "$1" 8 "$width"
	return $?
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
		git commit -m "transaction updates" || {
			echo "No changes detected in data directory..."
			return $?
		}
	else
		echo "Couldn't move into ${DATA_DIR}!" 1>&2
		return 1
	fi
}

CMD="${1:?No command provided! Provide either \'setup\' or \'fetch\', or some other undlerying \'mintable\' command}"
case "$CMD" in
setup)
	command -v mintable >/dev/null 2>&1 || npm install -g mintable
	prompt "Setup plaid authentication tokens?" && {
		mintc plaid-setup || exit $?
	}
	prompt "Setup CSV export?" && {
		mintc csv-export-setup || exit $?
	}
	prompt "Setup bank accounts?" && {
		mintc account-setup || exit $?
	}
	figlet -f script 'done!'
	;;

fetch)
	shift
	mintc fetch "$@" &&
		setup_data_version_control &&
		commit_data_changes || exit $?
	;;
*)
	printf "Couldn't find a command named '%s'\n" "$1" 1>&2
	echo "Trying to run it with mintable..."
	mintc "$@" || exit $?
	;;
esac
