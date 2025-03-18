#!/bin/bash

# Run pylint and save the score
pylint --output-format=text *.py > pylint_output.txt
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

# Generate badge markdown
badge="[![Pylint Score](https://img.shields.io/badge/pylint-$score-yellow)](PYLINT_SCORE.md)"
echo "$badge" > PYLINT_BADGE.md

# Update README.md with the new badge
sed -i "s|!\[Pylint Score\](https://img.shields.io/badge/pylint-[0-9\.]*-yellow)|$badge|" README.md

# Clean up
rm pylint_output.txt