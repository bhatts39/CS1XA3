#!/bin/bash
printf "PROJECT01\n"
while true
do
	read -p ">>" command
	if [ $command == "filetypecount" ]; then
		declare -a types=( "html" "js" "css" "py" "hs" "sh" )
		for type in "${types[@]}"
		do
			count=$(find ~/CS1XA3/ -name "*.$type" | wc -l)
			printf "%s\n" "$type: $count" 
		done
	elif [ $command == "compilefaillog" ]; then
		> compile_fail.log
		find ~/CS1XA3/ -name "*.hs" | while read -r line ; do
			if  ! ghc -c $line &> /dev/null; then
				echo $line >> compile_fail.log
			fi
			rm -f "${line%??}hi" "${line%??}o"
		done
		find ~/CS1XA3/ -name "*.py" | while read -r line ; do
			if ! python -Bm py_compile $line &> /dev/null; then
				echo $line >> compile_fail.log
			fi
		done
		printf "Compile fail log outputted to compile_fail.log\n"
	else 
		printf "Error: command not found\n"
	fi
done