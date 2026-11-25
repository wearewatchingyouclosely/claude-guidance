# -*- coding: utf-8 -*-
# CODESYS scripting (IronPython 2.7). Dumps a .project to text without saving it. Run on a COPY.
# Env: CDS_SRC = project copy, CDS_OUT = output folder (no spaces in either; see run_codesys.ps1).
# Writes: _export_log.txt, _tree.txt, src\*.st (textual objects), project_plcopen.xml (everything,
# including LD/FBD POUs, device configuration, I/O mappings and task calls).
import os, codecs, traceback

src, out = os.environ["CDS_SRC"], os.environ["CDS_OUT"]
if not os.path.isdir(out):
    os.makedirs(out)
log = codecs.open(os.path.join(out, "_export_log.txt"), "w", "utf-8")
def L(s):
    log.write(s + u"\n"); log.flush()

def safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default

def clean(name):
    return "".join(c if c.isalnum() or c in "-_. " else "_" for c in name)

ok = True
try:
    proj = projects.open(src, primary=True)
    L(u"opened: " + src)
    tree = codecs.open(os.path.join(out, "_tree.txt"), "w", "utf-8")
    src_dir = os.path.join(out, "src")
    if not os.path.isdir(src_dir):
        os.makedirs(src_dir)

    def walk(obj, depth, path):
        name = obj.get_name()
        tags = []
        if safe(lambda: obj.is_folder): tags.append("folder")
        if safe(lambda: obj.is_device):
            tags.append("device")
            di = safe(lambda: obj.get_device_identification())
            if di is not None:
                tags.append(u"type=%s id=%s ver=%s" % (di.type, di.id, di.version))
            mi = safe(lambda: obj.get_module_identification())
            if mi:
                tags.append(u"module=%s" % mi)
        hd = safe(lambda: obj.has_textual_declaration, False)
        hi = safe(lambda: obj.has_textual_implementation, False)
        if hd: tags.append("decl")
        if hi: tags.append("impl")
        tree.write(u"%s%s  [%s]\n" % (u"  " * depth, name, u", ".join(tags)))
        if hd or hi:
            parts = []
            if hd:
                parts.append(obj.textual_declaration.text)
            if hi:
                parts.append(u"\n(* ---------- IMPLEMENTATION ---------- *)\n")
                parts.append(obj.textual_implementation.text)
            f = codecs.open(os.path.join(src_dir, clean(u"__".join(path + [name])) + u".st"), "w", "utf-8")
            f.write(u"".join(parts)); f.close()
        for c in obj.get_children(False):
            walk(c, depth + 1, path + [name])

    for top in proj.get_children(False):
        walk(top, 0, [])
    tree.close()
    L(u"tree + text done (note: child order after a reopen may not be the insert order; trust the XML)")
    try:
        proj.export_xml(proj.get_children(False), os.path.join(out, "project_plcopen.xml"), True)
        L(u"plcopen export done")
    except Exception:
        ok = False
        L(u"plcopen export failed:\n" + traceback.format_exc())
    proj.close()
    L(u"closed without saving")
except Exception:
    ok = False
    L(u"FATAL:\n" + traceback.format_exc())
L(u"RESULT: " + (u"OK" if ok else u"CHECK LOG"))
log.close()
