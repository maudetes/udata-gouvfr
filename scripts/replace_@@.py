import json
import glob

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