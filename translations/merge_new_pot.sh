# May be reduncant: Extacting to pot seems to automatically update the .po files
for i in `find . -type f -name "*.po"`; do \
	msgmerge "$i" "../messages.pot" --output-file="$i"; \
done
