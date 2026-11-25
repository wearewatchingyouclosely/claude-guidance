# -*- coding: utf-8 -*-
# CODESYS scripting (IronPython 2.7). Applies a make_io.py build folder to a project COPY and saves it.
# Env (no spaces): CDS_SRC = project copy to change, CDS_BUILD = build folder (build_config.json etc.),
#                  CDS_OUT = folder for apply_log.txt
# Steps: delete old objects -> (re)create I/O modules in table order -> map channels + comments
#        -> create the GVL -> import the LD POUs -> add task calls -> build -> save.
# API notes are in rules/21_CODESYS_PROJECTS.md §4.
import os, codecs, json, traceback

src, bld, out = os.environ["CDS_SRC"], os.environ["CDS_BUILD"], os.environ["CDS_OUT"]
if not os.path.isdir(out):
    os.makedirs(out)
log = codecs.open(os.path.join(out, "apply_log.txt"), "w", "utf-8")
def L(s):
    log.write(unicode(s) + u"\n"); log.flush()

def rd(name):
    f = codecs.open(os.path.join(bld, name), "r", "utf-8"); t = f.read(); f.close(); return t

ok = True
try:
    cfg = json.loads(rd("build_config.json"))
    proj = projects.open(src, primary=True)
    L(u"opened " + src)
    apps = proj.find("Application", True)
    if len(apps) != 1:
        raise Exception("expected one object named Application, found %d" % len(apps))
    app = apps[0]

    # 1. delete objects that are replaced
    for n in cfg["remove_objects"] + [cfg["gvl"]["name"]] + [p["name"] for p in cfg["pous"]]:
        for o in app.find(n, False):
            o.remove(); L(u"removed " + n)

    # 2. I/O modules
    parents = proj.find(cfg["io_parent"], True)
    if len(parents) != 1:
        raise Exception("expected one I/O parent named %s, found %d" % (cfg["io_parent"], len(parents)))
    io = parents[0]
    if cfg["rebuild_modules"]:
        for m in list(io.get_children(False)):
            L(u"removing module %s (%s)" % (m.get_name(), m.get_module_identification()))
            m.remove()
    for mod in cfg["modules"]:
        name = mod["name"]
        if cfg["rebuild_modules"]:
            # insert() at the end keeps table order; add() puts the module at the top.
            io.insert(name, len(io.get_children(False)), mod["dev_type"], mod["dev_id"], mod["dev_version"], mod["module_id"])
        found = io.find(name, False)
        if not found:
            ok = False; L(u"!! module %s not found" % name); continue
        dev = found[0]
        got = dev.get_module_identification()
        if unicode(got) != unicode(mod["module_id"]):
            ok = False; L(u"!! %s module id %s, expected %s" % (name, got, mod["module_id"]))
        params = {}
        for con in dev.connectors:
            for p in con.host_parameters:
                params[unicode(p.visible_name)] = p
        for ch in mod["channels"]:
            p = params.get(ch["param"])
            if p is None:
                ok = False; L(u"!! %s: no parameter '%s'" % (name, ch["param"])); continue
            p.io_mapping.variable = ch["var"]
            if ch["comment"]:
                p.user_comment = ch["comment"]   # Description column; p.description is read-only
            L(u"  %s.%s -> %s" % (name, ch["param"], p.io_mapping.variable))
    L(u"module order in session: " + u", ".join(c.get_name() for c in io.get_children(False)))

    # 3. GVL
    gvl = app.create_gvl(cfg["gvl"]["name"])
    gvl.textual_declaration.replace(rd(cfg["gvl"]["file"]))
    L(u"created GVL " + cfg["gvl"]["name"])

    # 4. POUs (PLCopen XML) and task calls
    tasks = proj.find(cfg["task"], True)
    if len(tasks) != 1:
        raise Exception("expected one task named %s, found %d" % (cfg["task"], len(tasks)))
    for p in cfg["pous"]:
        app.import_xml(os.path.join(bld, p["file"]))
        if not app.find(p["name"], False):
            ok = False; L(u"!! %s not found after import" % p["name"]); continue
        tasks[0].pous.add(p["name"])   # an uncalled POU is not compiled, so the build would not check it
        L(u"imported %s (%d networks) and added to %s" % (p["name"], len(p["networks"]), cfg["task"]))

    # 5. build
    app.build()
    errors = 0
    for cat in system.get_message_categories(True):
        for msg in system.get_message_objects(cat):
            sev = unicode(msg.severity)
            L(u"  MSG [%s] %s" % (sev, msg.text))
            if sev.lower().startswith(u"error") or sev.lower().startswith(u"fatal"):
                errors += 1
    if errors:
        ok = False; L(u"!! %d build error(s)" % errors)

    proj.save()
    L(u"saved")
    proj.close()
except Exception:
    ok = False
    L(u"FATAL:\n" + traceback.format_exc())
L(u"RESULT: " + (u"OK" if ok else u"CHECK LOG"))
log.close()
