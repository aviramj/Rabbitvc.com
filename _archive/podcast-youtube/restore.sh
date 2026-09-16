#!/bin/sh
# Put the YouTube version of /podcast/ back. Run it from anywhere; paths are
# resolved against the script. It only copies files, so the result can be read
# with git diff before it is committed.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../.." && pwd)

rm -rf "$root/podcast"
cp -R "$here/podcast" "$root/podcast"

# These pages were archived with the stylesheet cache-buster of their day.
# Carry over whatever the rest of the site is on now, so a restored page does
# not ask browsers for a stale rv.css.
v=$(sed -n 's/.*rv\.css?v=\([a-z0-9]*\).*/\1/p' "$root/index.html" | head -1)
if [ -n "$v" ]; then
  find "$root/podcast" -name '*.html' -exec \
    sed -i.bak "s/rv\.css?v=[a-z0-9]*/rv.css?v=$v/g" {} +
  find "$root/podcast" -name '*.html.bak' -delete
fi

echo "Restored the YouTube version of /podcast/ from $here/podcast."
echo "Review with: git -C \"$root\" diff -- podcast"
