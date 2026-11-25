"""Dump Logix L5X programs to readable text for review.

Usage: python -I _tools/extract.py <ProgramExports dir> <out dir> PROGRAM [PROGRAM ...]
Writes <out>/<PROGRAM>.txt (RLL rungs with numbers, SFC steps/actions/transitions/links)
and <out>/<PROGRAM>_rungs.tsv (program, routine, rung, text) used by build.py.
"""
import html, re, sys
from pathlib import Path


def program_xml(src: Path, prog: str) -> str:
    t = (src / f"{prog}.L5X").read_text(encoding="utf-8-sig")
    m = re.search(r'<Program Use="Target" Name="%s".*?</Program>' % re.escape(prog), t, re.S)
    if not m:
        sys.exit(f"{prog}: target program not found")
    return m.group(0)


def cdata(s: str) -> list[str]:
    return [html.unescape(x) for x in re.findall(r"<!\[CDATA\[(.*?)\]\]>", s, re.S)]


def dump_sfc(body: str, out: list[str]) -> None:
    items = []  # (y, x, text)
    for m in re.finditer(r'<Step ID="(\d+)" X="(\d+)" Y="(\d+)" Operand="([^"]+)"(.*?)</Step>', body, re.S):
        sid, x, y, op, inner = m.groups()
        lines = [f"STEP id={sid} {op}" + ("  (initial)" if 'InitialStep="true"' in m.group(0) else "")]
        for am in re.finditer(r'<Action ID="(\d+)" Operand="([^"]+)" Qualifier="([^"]+)"(.*?)</Action>', inner, re.S):
            lines.append(f"    action {am.group(2)} [{am.group(3)}]")
            lines += [f"      {l}" for l in cdata(am.group(4))]
        items.append((int(y), int(x), "\n".join(lines)))
    for m in re.finditer(r'<Transition ID="(\d+)" X="(\d+)" Y="(\d+)" Operand="([^"]+)"(.*?)</Transition>', body, re.S):
        tid, x, y, op, inner = m.groups()
        items.append((int(y), int(x), f"TRAN id={tid} {op}: " + " ".join(l.strip() for l in cdata(inner))))
    for m in re.finditer(r'<Branch ID="(\d+)" Y="(\d+)" BranchType="(\w+)" BranchFlow="(\w+)"(.*?)</Branch>', body, re.S):
        bid, y, bt, bf, inner = m.groups()
        legs = re.findall(r'<Leg ID="(\d+)"', inner)
        items.append((int(y), 0, f"BRANCH id={bid} {bt}/{bf} legs={legs}"))
    for m in re.finditer(r'<TextBox ID="(\d+)" X="(\d+)" Y="(\d+)"(.*?)</TextBox>', body, re.S):
        items.append((int(m.group(3)), int(m.group(2)), "TEXTBOX: " + " | ".join(cdata(m.group(4)))))
    for y, x, txt in sorted(items):
        out.append(f"  @y={y:5} x={x:5}  {txt}")
    links = re.findall(r'<DirectedLink FromID="(\d+)" ToID="(\d+)"', body)
    out.append("  LINKS: " + " ".join(f"{a}->{b}" for a, b in links))


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for prog in sys.argv[3:]:
        p = program_xml(src, prog)
        out, rows = [f"PROGRAM {prog}"], []
        tags = re.search(r"<Tags>(.*?)</Tags>", p, re.S)
        if tags:
            out.append("TAGS:")
            for tm in re.finditer(r'<Tag Name="([^"]+)" TagType="(\w+)"(?: DataType="([^"]+)")?(?: Dimensions="([^"]+)")?', tags.group(1)):
                out.append(f"  {tm.group(1)} : {tm.group(3) or tm.group(2)}" + (f"[{tm.group(4)}]" if tm.group(4) else ""))
        for rm in re.finditer(r'<Routine Name="([^"]+)" Type="([^"]+)"(.*?)</Routine>', p, re.S):
            name, typ, body = rm.groups()
            out.append(f"\n=== ROUTINE {name} ({typ})")
            if typ == "RLL":
                for g in re.finditer(r'<Rung Number="(\d+)"[^>]*>(.*?)</Rung>', body, re.S):
                    txt = re.search(r"<Text>\s*<!\[CDATA\[(.*?)\]\]>", g.group(2), re.S)
                    txt = html.unescape(txt.group(1)) if txt else ""
                    out.append(f"  R{g.group(1):>3}: {txt}")
                    rows.append((prog, name, g.group(1), txt))
            elif typ == "SFC":
                dump_sfc(body, out)
            else:
                out.append("  (not dumped)")
        (dst / f"{prog}.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
        with open(dst / f"{prog}_rungs.tsv", "w", encoding="utf-8", newline="") as f:
            f.write("program\troutine\trung\ttext\n")
            for r in rows:
                f.write("\t".join(r) + "\n")
        print(f"{prog}: {len(rows)} rungs")


if __name__ == "__main__":
    main()
