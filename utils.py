import os
import shutil
import secrets
import requests
import tempfile
from datetime import timedelta
from html2image import Html2Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def __perfect(s):
	s = s.replace("à", "&agrave")
	s = s.replace("è", "&egrave")
	s = s.replace("é", "&eacute")
	s = s.replace("ì", "&igrave")
	s = s.replace("ò", "&ograve")
	s = s.replace("ù", "&ugrave")
	return s

def next_weekday(date, weekday):
    day_gap = weekday - date.weekday()
    if day_gap <= 0:
        day_gap += 7
    return date + timedelta(days=day_gap)

def csvToIMG(fin, fout, delimiter, lineterminator, temp_dir, size=(1000, 500)):
    hti = Html2Image(output_path=temp_dir)

    file = open(f"{temp_dir}/{fin}.csv", 'r', encoding="UTF8") 
    file = __perfect(file.read()).split(lineterminator)

    data = []
    for line in file:
        for x in line.split(delimiter):
            data.append(x)

    data = list(filter(None,data))

    materie = [v for i, v in enumerate(data) if i % 2 == 0]
    compiti = [v for i, v in enumerate(data) if i % 2 != 0]
    
    th = "<th>%s</th>"
    tr = "<tr>%s</tr>"
    td = "<td>%s</td>"
    HTML_table = ""

    for x in range(len(materie)):
        tmp = ""
        tmp += th % materie[x].replace("'", "").replace('"', "")
        tmp += td % compiti[x]

        HTML_table += tr % tmp

    with open(f"{CURRENT_DIR}/table_layout.html", "r") as f:
        HTML_layout = f.read()

    with open(f"{temp_dir}/{fout}.html", "w") as f:
        f.write(HTML_layout.replace("%insert%", HTML_table))

    hti.screenshot(url=f"file://{temp_dir}/{fout}.html", save_as=f"{fout}.png", size=size)

def compiti2IMG(file_in, fout, compiti, temp_dir):
    with open(f"{temp_dir}/{file_in}.csv", "w", encoding="UTF8") as f:
        delimiter = f"%!{secrets.token_hex(16)}!%"
        lineterminator = f"%_{secrets.token_hex(16)}_%"
        countCompiti = 0
        for c in compiti:
            row = [c["desMateria"], c["desCompiti"]]
            fin = f"{delimiter}".join(row)
            f.write(fin + lineterminator)
            countCompiti += 1
        f.close()

    if countCompiti == 1:
        size = (500, 250)
    else:
        size = (countCompiti*255, countCompiti*135)
    csvToIMG(file_in, fout, delimiter, lineterminator, temp_dir, size=size)
    return True

def clearDir():
    folder = tempfile.gettempdir()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception:
            pass

def url2File(url, filename, path=CURRENT_DIR):
    r = requests.get(url)
    with open(f"{path}/{filename}", "wb") as f:
        f.write(r.content)
    return f"{path}/{filename}"
