#!/bin/bash
# setup/interact with accounts, fetch data and keep it tracked in git

# get the name of this script
readonly script_name='mint'

# function to verify an external command is installed
havecmd() {
	local BINARY ERRMSG
	# error if first argument isn't provided
	BINARY="${1:?Must provide command to check}"
	# the commend exists, exit with 0 (success!)
	if command -v "${BINARY}" >/dev/null 2>&1; then
		return 0
	else
		# construct error message
		ERRMSG="'${script_name}' requires '${BINARY}', could not find that on your \$PATH"
		if [[ -n "$2" ]]; then
			ERRMSG="${ERRMSG}. $2"
		fi
		printf '%s\n' "${ERRMSG}" 1>&2
		return 1
	fi
}

# check commands
set -e
havecmd tput
havecmd figlet
havecmd whiptail "This is typically installable as 'newt' or 'libnewt'"
havecmd mintable "Install by running: 'npm install -g mintable'"
set +e

THIS_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
readonly CONFIG_FILE="${THIS_DIR}/mintable.jsonc" # config file is kept in this dir
declare DATA_DIR DEFUALT_DATA_DIR
DEFAULT_DATA_DIR="${THIS_DIR}/data" # where transactions/balances are kept
DATA_DIR="${MINT_DATA:-${DEFAULT_DATA_DIR}}"
readonly DATA_DIR

[[ ! -d "${DATA_DIR}" ]] && mkdir "${DATA_DIR}"

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

# mint with config
mintc() {
	mintable "$@" --config-file "${CONFIG_FILE}"
	return $?
}

prompt() {
	local width
	# use width of message
	width="$(wc -c <<<"$1")"
	# or default to 1/3rd of the terminal width
	((width < TERMINAL_COLUMNS / 3)) && width="$((TERMINAL_COLUMNS / 3))"
	whiptail --yesno --defaultno "$1" 8 "${width}"
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
	if cd "${DATA_DIR}"; then
		# add any changes to a local git repo
		git add ./*.csv
		if git commit -m "transaction updates"; then
			:
		else
			echo "No changes detected in data directory..."
		fi
	else
		echo "Couldn't move into ${DATA_DIR}!" 1>&2
		return 1
	fi
}

CMD="${1:?No command provided! Provide either \'setup\' or \'fetch\', or some other undlerying \'mintable\' command}"
case "${CMD}" in
setup)
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
