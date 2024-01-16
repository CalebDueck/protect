#!/bin/bash


file_to_remove="./pygame_output.txt"

if [ -e "$file_to_remove" ]; then
	rm "$file_to_remove"
	echo "File deleted"
else
	echo "File does not exist"
fi

pygame_script="./IRFrame.py"

log_file="./pygame_output.txt"

lxterminal_process="lxterminal"

is_lxterminal_running() {
	pgrep -x "$lxterminal_process" > /dev/null
}

kill_lxterminal() {
	pkill -x "$lxterminal_process"
}



check_for_string() {
	grep -q "$search_string" "$log_file" 2>/dev/null
}

search_string="Server listening on"

if is_lxterminal_running; then
	echo "Killing previous lxterminal"
	kill_lxterminal
	sleep 1

fi

lxterminal -e sh -c "export DISPLAY=:0; . venv/bin/activate; python3 $pygame_script > $log_file 2>&1" &

timeout=10

start_time=$(date +%s)

current_time=$(date +%s)


while [ $((current_time - start_time)) -lt $timeout ]; do 
	if check_for_string; then
		echo "Success"
		break

	else
		current_time=$(date +%s)
	fi
done

if [ $((current_time - start_time)) -ge $timeout ]; then
	echo "Timeout"

fi


