import polib


count = 0

for pofile in [
    "udata_gouvfr/theme/gouvfr/translations/gouvfr.pot",
    "udata_gouvfr/translations/udata-gouvfr.pot"
]:
    po = polib.pofile(pofile)
    newpo = polib.POFile()
    newpo.metadata = po.metadata
    for entry in po:
        if entry.msgid.find("@@") == 0:
            newpo.append(
                polib.POEntry(
                    msgid=entry.msgid[2:],
                    msgstr=entry.msgstr,
                    occurrences=entry.occurrences
                )
            )

    newpo.save(".".join(pofile.split(".")[:-1]) + "@@.pot")
