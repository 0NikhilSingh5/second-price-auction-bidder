#!/bin/bash

# Run pylint and save the score
pylint --output-format=text *.py > pylint_output.txt
score=$(grep "Your code has been rated at" pylint_output.txt | grep -o '[0-9]\+\.[0-9]\+')

# Ensure score is not empty
if [[ -z "$score" ]]; then
    score="0.0"
fi

# Update README.md with the new score text
# Look for a line that contains "Code Quality score" and update the next line
sed -i '/## Code Quality score/!b;n;c\\nPylint Score: '"$score"'/10.0\n' README.md

# Clean up
rm pylint_output.txt