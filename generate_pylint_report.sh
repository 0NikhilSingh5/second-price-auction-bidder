#!/bin/bash
# Run pylint and save the score
pylint --output-format=text your_module_directory > pylint_output.txt
score=$(grep "Your code has been rated at" pylint_output.txt | grep -o '[0-9]\+\.[0-9]\+')

# Generate a simple markdown report
echo "# Pylint Score" > PYLINT_SCORE.md
echo "" >> PYLINT_SCORE.md
echo "Current score: $score/10.0" >> PYLINT_SCORE.md
echo "" >> PYLINT_SCORE.md
echo "Last updated: $(date)" >> PYLINT_SCORE.md
echo "" >> PYLINT_SCORE.md
echo "## Details" >> PYLINT_SCORE.md
echo '```' >> PYLINT_SCORE.md
cat pylint_output.txt >> PYLINT_SCORE.md
echo '```' >> PYLINT_SCORE.md

# Optional: generate
echo "[![Pylint Score](https://img.shields.io/badge/pylint-$score-yellow)](PYLINT_SCORE.md)" > PYLINT_BADGE.md

# Clean up
rm pylint_output.txt