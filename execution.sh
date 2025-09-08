#!/bin/bash

NOXIM_BINARY_PATH = "../noxim/noxim/bin/noxim"

YAML_CONFIG_FILE = $1

FILENAME = $(basename "$YAML_CONFIG_FILE" .yaml)
OUTPUT_FILE = "results_${FILENAME}.txt"

rm -f "$OUTPUT_FILE"
touch "$OUTPUT_FILE"

PIR_START = 0.01
PIR_STEP = 0.01
PIR_END = 0.2

for pir in $(seq $PIR_START $PIR_STEP $PIR_END)
do
    echo "--------------------------------------------------" tee -a "$OUTPUT_FILE"
    echo "------------RUNNING FOR PIR = %.2f\n--------------" "$pir" | tee -a "$OUTPUT_FILE"
    echo "--------------------------------------------------" tee -a "$OUTPUT_FILE"

    "$NOXIM_BINARY_PATH" - config "$YAML_CONFIG_FILE" -pir "$pir" >> "$OUTPUT_FILE"

    printf "finished for PIR = %0.2f. \n \n" "$pir"
done

echo "execution complete\n"