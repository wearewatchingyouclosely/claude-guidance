"""Build Studio 5000 'Import Tags and Logic Comments' CSVs from comment tables.

Usage:
    python -I build.py <exports dir> <config.json>

<exports dir>  one <Program>.L5X per program, plus the tag export CSV named in the config.
<config.json>  which programs get which comments (see README). The comment tables are read from
               <config folder>/comments/ and the import files written to <config folder>/import/.

For each comment set (comments/<SET>_rungs.tsv, optional comments/<SET>_steps.tsv) and each program:
  - every rung must still start with the 'expect' text, or the build fails (shifted rung numbers);
  - every SFC step element must still set the expected step number (NewStepNr:= or StepIndex:=);
  - RCOMMENT rows (rung comments) and COMMENT rows (SFC step descriptions) are written.
Placeholders like {L} in 'expect' and 'comment' are filled per program from the config.
An optional 'note' column is appended only for the programs listed in 'note_for' (comma separated).
Import with Match by Rung Number = Yes and Tags = Discard (rules/20 §7).
"""
import csv, html, io, json, re, sys
from pathlib import Path

TAG_HEADER = "TYPE,SCOPE,NAME,DESCRIPTION,DATATYPE,SPECIFIER,ATTRIBUTES"
RC_HEADER = "TYPE,SCOPE,ROUTINE,COMMENT,OWNING_ELEMENT,LOCATION"


def program_xml(src, prog):
    t = (src / f"{prog}.L5X").read_text(encoding="utf-8-sig")
    m = re.search(r'<Program Use="Target" Name="%s".*?</Program>' % re.escape(prog), t, re.S)
    if not m:
        sys.exit(f"{prog}.L5X: no target program named {prog}")
    return m.group(0)


def rungs(p):
    out = {}
    for rm in re.finditer(r'<Routine Name="([^"]+)" Type="RLL"(.*?)</Routine>', p, re.S):
        for g in re.finditer(r'<Rung Number="(\d+)"[^>]*>(.*?)</Rung>', rm.group(2), re.S):
            txt = re.search(r"<Text>\s*<!\[CDATA\[(.*?)\]\]>", g.group(2), re.S)
            out[(rm.group(1), int(g.group(1)))] = html.unescape(txt.group(1)).strip() if txt else ""
    return out


def step_numbers(p):
    out = {}
    for m in re.finditer(r'<Step ID="\d+"[^>]*Operand="(\w+)\[(\d+)\]"(.*?)</Step>', p, re.S):
        nr = re.search(r"(?:NewStepNr|StepIndex):=(\d+)", m.group(3))
        out[(m.group(1), int(m.group(2)))] = int(nr.group(1)) if nr else None
    return out


def first_instruction(rung):
    """First instruction on the rung. Informative only: the import matches by rung number."""
    s = rung.lstrip("[ ,")
    m = re.match(r"[A-Za-z_][\w:]*\(", s)
    if not m:
        return ""
    depth = 0
    for j in range(m.end() - 1, len(s)):
        depth += s[j] == "("
        depth -= s[j] == ")"
        if depth == 0:
            return s[: j + 1]
    return s


def read_tsv(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build_set(src, here, tag_rows, cset, progs, log, errors):
    tag_lines, rc_rows = [], []
    rc = read_tsv(here / "comments" / f"{cset}_rungs.tsv")
    st = read_tsv(here / "comments" / f"{cset}_steps.tsv")
    for prog, subs in progs.items():
        fill = lambda s: re.sub(r"\{(\w+)\}", lambda m: subs.get(m.group(1), m.group(0)), s)
        p = program_xml(src, prog)
        r, steps = rungs(p), step_numbers(p)
        for row in rc:
            key = (row["routine"], int(row["rung"]))
            if key not in r:
                errors.append(f"{prog} {key}: rung not found")
                continue
            if not r[key].startswith(fill(row["expect"])):
                errors.append(f"{prog} {key}: expected '{fill(row['expect'])}', found '{r[key][:60]}'")
                continue
            text = fill(row["comment"])
            if row.get("note") and prog in [x.strip() for x in (row.get("note_for") or "").split(",")]:
                text += " " + fill(row["note"])
            rc_rows.append([prog, key[0], text, first_instruction(r[key]).rstrip(";"), str(key[1])])
            log.append([prog, key[0], str(key[1]), "rung comment", text])
        for tag in sorted({row["tag"] for row in st}):
            if (prog, tag) not in tag_rows:
                errors.append(f"{prog}: tag {tag} not in the tag export")
                continue
            tag_lines.append(tag_rows[(prog, tag)])
            for row in [x for x in st if x["tag"] == tag]:
                key = (tag, int(row["index"]))
                if steps.get(key) != int(row["expect_stepnr"]):
                    errors.append(f"{prog} {key}: expected step {row['expect_stepnr']}, found {steps.get(key)}")
                    continue
                text = fill(row["comment"]).replace('"', '""')
                tag_lines.append(f'COMMENT,{prog},{tag},"{text}",,"{tag}[{key[1]}]"')
                log.append([prog, tag, str(key[1]), "step description", text])
    return tag_lines, rc_rows


def write_csv(out, header, tag_lines, rc_rows):
    buf = io.StringIO()
    buf.write("\r\n".join(header + tag_lines) + "\r\n")
    buf.write(RC_HEADER + "\r\n")
    for row in rc_rows:
        line = io.StringIO()
        csv.writer(line, quoting=csv.QUOTE_ALL, lineterminator="").writerow(row)
        buf.write("RCOMMENT," + line.getvalue() + "\r\n")
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(buf.getvalue().encode("ascii"))  # non-ASCII text fails here on purpose
    n_desc = sum(1 for l in tag_lines if l.startswith("COMMENT"))
    print(f"OK: {len(rc_rows)} rung comments, {n_desc} step descriptions -> {out}")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, cfg_path = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    here = cfg_path.parent
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    tag_csv = (src / cfg["tag_csv"]).read_text(encoding="ascii").splitlines()
    header = tag_csv[: tag_csv.index(TAG_HEADER) + 1]
    tag_rows = {}
    for line in tag_csv:
        if line.startswith("TAG,"):
            f = next(csv.reader([line]))
            tag_rows[(f[1], f[2])] = line

    log, errors, outputs = [], [], []
    for cset, spec in cfg["sets"].items():
        tag_lines, rc_rows = build_set(src, here, tag_rows, cset, spec["programs"], log, errors)
        outputs.append((here / "import" / spec["output"], tag_lines, rc_rows))
    if errors:
        print("BUILD FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)
    for out, tag_lines, rc_rows in outputs:
        write_csv(out, header, tag_lines, rc_rows)
    (here / "data").mkdir(exist_ok=True)
    with open(here / "data" / "changelog.tsv", "w", encoding="utf-8", newline="") as f:
        f.write("program\troutine_or_tag\trung_or_index\tkind\ttext\n")
        for row in log:
            f.write("\t".join(row) + "\n")


if __name__ == "__main__":
    main()
