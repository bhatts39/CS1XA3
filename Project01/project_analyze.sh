#!/bin/bash
cd ~/CS1XA3/Project01
printf "PROJECT01\n"
while true
do
	#read command from user
	read -p ">>" command
	
	if [ $command == "filetypecount" ]; then
		echo -e "File types:"
		#create array of file types to keep track of
		declare -a types=( "html" "js" "css" "py" "hs" "sh" )
		for type in "${types[@]}"
		do
			#count number of lines outputted by find command
			count=$(find ~/CS1XA3/ -name "*.$type" | wc -l)
			printf "%s\n" "$type: $count" 
		done
		
	elif [ $command == "compilefaillog" ]; then
		echo -e "Python and Haskell files that fail to compile:"
		#create empty log file
		> compile_fail.log
		find ~/CS1XA3/ -name "*.hs" | while read -r line ; do
			if  ! ghc -c $line &> /dev/null; then
				echo $line >> compile_fail.log
			fi
			#remove extra files generated
			rm -f "${line%??}hi" "${line%??}o"
		done
		find ~/CS1XA3/ -name "*.py" | while read -r line ; do
			#B flag stops python from creating additional files
			if ! python -Bm py_compile $line &> /dev/null; then
				echo $line >> compile_fail.log
			fi
			#remove pyc file which is generated on succesful compile
			rm -f "${line%??}pyc"
		done
		#show results to user
		cat compile_fail.log
		printf "Compile fail log outputted to compile_fail.log\n"
		
	elif [ $command == "commitstats" ]; then
		echo -e "Total commits to repos by all users in the /home directory sorted by weekday:"
		#find all .git files, which indicate a git repo
		find /home -name ".git" 2>/dev/null | while read -r line ; do
			#go to the directory containing the .git file
			cd $(dirname $line)
			#output the git log, formatted to only show the weekday, and append each line to a temporary file
			git log --pretty=format:"%ad" --date=format:"%A" >> /tmp/statistics.tmp 2>/dev/null
		done
		# create an array of days to keep track of commits per day
		declare -A days=( ["Monday"]=0 ["Tuesday"]=0 ["Sunday"]=0 ["Wednesday"]=0 ["Thursday"]=0 ["Friday"]=0 ["Saturday"]=0 )
		#start counter at 0
		echo 0 > temp
		for day in "${!days[@]}"
		do
			#count up total number of times each day appears in the temporary file
			count=$(grep $day /tmp/statistics.tmp | wc -l) 
			echo $(($(cat temp) + $count)) > temp
			echo -e "$day:" $count 
		done |
		sort -rn -k2
		echo -e "Total number of commits: " $(($(cat temp)))
		#delete temp files
		unlink temp
		unlink /tmp/statistics.tmp
		
	elif [ $command == "help" ]; then
		echo -e "filetypecount: Counts number of html, js, css, py, hs, and sh files"
		echo -e "compilefaillog: Creates a log of python and haskell files that fail to compile"
		echo -e "commitstats: Outputs number of commits by all users sorted by weekday" 
		
	else 
		printf "$command: command not found. Enter 'help' for a list of commmands\n"
		
	fi
done
