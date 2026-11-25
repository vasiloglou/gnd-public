#!/usr/bin/env bash
# Rehearse probe 3: PyRel exports, new tree vs 0.4.0. Usage: p3.sh WORK NEWPY OLDPY
set -u
work=$1; new=$2; old=$3
rm -rf "$work"; mkdir -p "$work"; cd "$work"
"$new" -I -c 'import shutil,sys; from importlib.resources import files; shutil.copytree(str(files("gnd")/"examples"/"literature"), sys.argv[1])' lit
"$new" -I -m gnd.examples.literature.interop run --out "$work/interop" >/dev/null
models=(lit/assertions/model.orm.yaml lit/model.orm.yaml lit/depth_fixture/decimal.orm.json lit/quantity_fixture/time.orm.yaml lit/lineage/model.orm.yaml interop/checking.orm.json interop/extraction.orm.json)
for m in "${models[@]}"; do
  for mode in default duckdb lqp; do
    for who in new old; do
      py=$new; [ $who = old ] && py=$old
      out="out-$who-$(echo "$m" | tr '/.' '__')-$mode.py"
      if [ $mode = default ]; then args=(export pyrel "$m" --out "$out"); else args=(export pyrel "$m" --rules $mode --out "$out"); fi
      msg=$("$py" -I -m gnd "${args[@]}" 2>&1 >/dev/null | tail -1 | cut -c1-230); code=$?
      "$py" -I -m gnd "${args[@]/$out/$out.2}" >/dev/null 2>&1; code=$?
      printf '%-38s %-7s %-3s exit %s  %s\n' "$m" "$mode" "$who" "$code" "$msg"
    done
  done
done
