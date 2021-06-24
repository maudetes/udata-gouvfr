import json
import glob

import polib

with open("/home/estelle/Téléchargements/en.json", "r") as f:
    translations = json.load(f)

files = glob.glob("../**/*.vue", recursive=True)
for vue_file in files:
    with open(vue_file, "r") as f:
        content = f.read()

    for key in translations:
        if translations[key].find("@@") != 0:
            content = content.replace("@@" + key, translations[key])
    
    with open(vue_file, "w") as f:
        f.write(content)

fr_en_translations = {}
for key in translations:
    if translations[key].find("@@") != 0:
        fr_en_translations[translations[key]] = key
    else:
        fr_en_translations[key] = translations[key].replace("@@", "")

with open("theme/js/locales/fr.json", "w") as f:
    f.write(json.dumps(fr_en_translations, indent=2, ensure_ascii=False))

en_translations = {key: key for key in fr_en_translations}
with open("theme/js/locales/en.json", "w") as f:
    f.write(json.dumps(en_translations, indent=2, ensure_ascii=False))

## .po files

def escape_quote(text):
    return text.replace("'", "\\'")

for pofile, prefix in [
    ("/home/estelle/Téléchargements/gouvfr@@-en.po", "udata_gouvfr/theme/gouvfr/"),
    ("/home/estelle/Téléchargements/udata-gouvfr@@-en.po", "")
]:
    po = polib.pofile(pofile)
    for entry in po:
        for occur_file, _ in entry.occurrences:

            with open(prefix + occur_file, "r") as f:
                content = f.read()

            if entry.msgstr.find("@@") == 0:
                content = content.replace("'@@" + escape_quote(entry.msgid) + "'", 
                                          "'" + escape_quote(entry.msgid) + "'")
                content = content.replace('"@@' + entry.msgid + '"',
                                          '"' + entry.msgid + '"')
            else:
                content = content.replace("'@@" + escape_quote(entry.msgid) + "'", 
                                          "'" + escape_quote(entry.msgstr) + "'")
                content = content.replace('"@@' + entry.msgid + '"',
                                          '"' + entry.msgstr + '"')

            with open(prefix + occur_file, "w") as f:
                f.write(content)

for pofile_src, pofile_tgt in [
    (
        "/home/estelle/Téléchargements/gouvfr@@-en.po", 
        "udata_gouvfr/theme/gouvfr/translations/fr/LC_MESSAGES/gouvfr.po"
    ),
    (
        "/home/estelle/Téléchargements/udata-gouvfr@@-en.po",
        "udata_gouvfr/translations/fr/LC_MESSAGES/udata-gouvfr.po"
    )
]:
    po = polib.pofile(pofile_src)
    newpo = polib.pofile(pofile_tgt)
    for entry in po:
        if entry.msgstr.find("@@") == 0:
            newpo.append(
                polib.POEntry(
                    msgid=entry.msgid,
                    msgstr=entry.msgstr[2:],
                    occurrences=entry.occurrences
                )
            )
        else:            
            newpo.append(
                polib.POEntry(
                    msgid=entry.msgstr,
                    msgstr=entry.msgid,
                    occurrences=entry.occurrences
                )
            )
        newpo.save(pofile_tgt)
