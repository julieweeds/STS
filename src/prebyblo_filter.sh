# Usage: input_file threshold

TEMP_FILE=filtered
awk '{print $1}' $1 | sort | uniq -c | awk -v thresh=$2 '$1 < thresh {print $2}' > $TEMP_FILE
python prebyblo_filter.py $1 $TEMP_FILE 
