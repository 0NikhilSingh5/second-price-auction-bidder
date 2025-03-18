#!/bin/bash

# Run pylint and save the score
pylint --output-format=text *.py > pylint_output.txt
score=$(grep "Your code has been rated at" pylint_output.txt | grep -o '[0-9]\+\.[0-9]\+')

# Ensure score is not empty
if [[ -z "$score" ]]; then
    score="0.0"
fi

# Create temporary file
temp_file=$(mktemp)

# Read README.md line by line
in_score_section=false
while IFS= read -r line; do
    # Check if we're at the score section header
    if [[ "$line" == "## Code Quality score" ]]; then
        echo "$line" >> "$temp_file"
        echo "Pylint Score: $score/10.0" >> "$temp_file"
        in_score_section=true
        continue
    fi
    
    # If we're in the score section and find the next section or empty line, exit the section
    if $in_score_section && [[ "$line" =~ ^## || "$line" == "" ]]; then
        in_score_section=false
        echo "$line" >> "$temp_file"
        continue
    fi
    
    # Skip lines in the score section
    if $in_score_section; then
        continue
    fi
    
    # Copy all other lines
    echo "$line" >> "$temp_file"
done < README.md

# Replace the original README.md with our edited version
mv "$temp_file" README.md

# Clean up
rm pylint_output.txt