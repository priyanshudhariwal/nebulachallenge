#!/bin/bash
export LC_NUMERIC="C"

if [ -z "$1" ]; then
    echo "usage: ./execution.sh <filename.yaml>"
    exit 1
fi

NOXIM_BINARY_PATH="../noxim/noxim/bin/noxim"

YAML_CONFIG_FILE=$1

FILENAME=$(basename "$YAML_CONFIG_FILE" .yaml)
OUTPUT_FILE="results_${FILENAME}.txt"

PIR_START=0.01
PIR_STEP=0.01
PIR_END=0.20

rm -f "$OUTPUT_FILE"
touch "$OUTPUT_FILE"

for pir in $(seq $PIR_START $PIR_STEP $PIR_END)
do
    echo "--------------------------------------------------" | tee -a "$OUTPUT_FILE"
    printf "\n------------RUNNING FOR PIR = %.2f--------------\n" "$pir" | tee -a "$OUTPUT_FILE"
    echo "--------------------------------------------------" | tee -a "$OUTPUT_FILE"

    "$NOXIM_BINARY_PATH" -config "$YAML_CONFIG_FILE" -pir "$pir" "poisson" >> "$OUTPUT_FILE"

    #debugging statement
    printf "$NOXIM_BINARY_PATH" -config "$YAML_CONFIG_FILE" -pir "$pir" "poisson" >> "$OUTPUT_FILE"

    printf "finished for PIR = %0.2f. \n \n" "$pir"
done

echo "execution complete\n"