for i in `find . -type f -name "*.po"`; do \
	msgmerge "$i" "../messages.pot" --output-file="$i"; \
done
