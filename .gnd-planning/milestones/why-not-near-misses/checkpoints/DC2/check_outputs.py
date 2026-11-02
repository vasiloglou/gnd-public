"""Re-run every gnd-run block of a checkpoint page and compare each shown output, as the tutorial runner does."""
import re, sys, tempfile, subprocess
from pathlib import Path
page = Path(sys.argv[1]); text = page.read_text()
blank = re.sub(r"(<!-- gnd-run[^>]*output=\w+ -->\n```\w+\n.*?\n```\n\n```text\n)(.*?)(\n```)", r"\1@OUT@\3", text, flags=re.S)
tmp = Path(tempfile.mkdtemp()) / page.name; tmp.write_text(blank)
subprocess.run([sys.executable, str(Path(__file__).with_name("fill_outputs.py")), str(tmp)], check=True)
print(page, "outputs match" if tmp.read_text() == text else "OUTPUTS DIFFER")
sys.exit(tmp.read_text() != text)
