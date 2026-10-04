#!/usr/bin/env python3
"""export_inspect.py — แกะไฟล์ zip ที่ Plane export มา (CSV / XLSX / JSON) แล้วสรุปว่าแต่ละไฟล์มีกี่แถว คอลัมน์อะไรบ้าง

ใช้:  python export_inspect.py out.zip            # สรุปทุกไฟล์ใน zip
      python export_inspect.py out.zip --compare PLAB   # เทียบจำนวนแถวกับ total_results จาก API v1 (ต้องมี ~/.plane_token)
ไม่ต้องติดตั้งไลบรารีเพิ่ม: xlsx คือ zip ของ XML → นับ <row> และอ่าน sharedStrings เอง
"""
import argparse
import csv
import io
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

ap = argparse.ArgumentParser()
ap.add_argument("zip")
ap.add_argument("--compare", metavar="PROJECT", help="เทียบจำนวนแถวกับ GET /work-items/ ของโปรเจกต์นี้")
a = ap.parse_args()

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def inspect_csv(data: bytes):
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    return len(rows) - 1, rows[0] if rows else []


def inspect_json(data: bytes):
    d = json.loads(data.decode("utf-8"))
    if isinstance(d, dict):            # บางรูปแบบห่อเป็น {results: [...]}
        d = d.get("results", d.get("issues", []))
    return len(d), list(d[0].keys()) if d else []


def inspect_xlsx(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data)) as x:
        shared = []
        if "xl/sharedStrings.xml" in x.namelist():
            root = ET.fromstring(x.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")) for si in root.findall("m:si", NS)]
        sheet = ET.fromstring(x.read("xl/worksheets/sheet1.xml"))
        rows = sheet.findall(".//m:sheetData/m:row", NS)
        header = []
        if rows:
            for c in rows[0].findall("m:c", NS):
                if c.get("t") == "inlineStr":            # openpyxl/xlsxwriter บางรุ่นเขียน string ฝังในเซลล์
                    header.append("".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t")))
                    continue
                v = c.find("m:v", NS)
                if v is None:
                    continue
                header.append(shared[int(v.text)] if c.get("t") == "s" else v.text)
        return len(rows) - 1, header


results = {}
with zipfile.ZipFile(a.zip) as z:
    for info in z.infolist():
        data = z.read(info.filename)
        ext = info.filename.rsplit(".", 1)[-1].lower()
        fn = {"csv": inspect_csv, "json": inspect_json, "xlsx": inspect_xlsx}.get(ext)
        if not fn:
            print(f"  (ข้าม {info.filename})")
            continue
        n, header = fn(data)
        results[info.filename] = n
        print(f"== {info.filename}  ({info.file_size:,} bytes)")
        print(f"   rows    : {n}")
        print(f"   columns : {len(header)} → {', '.join(header)}")

if a.compare:
    from planeapi import Plane
    p = Plane()
    proj = p.project(a.compare)
    r = p.get(f"projects/{proj['id']}/work-items/", per_page=1)
    total = r.json().get("total_results")
    print(f"== API  GET /work-items/ ของ {a.compare} → total_results = {total}")
    for fname, n in results.items():
        mark = "✔ เท่ากัน" if n == total else "✘ ไม่เท่ากัน (export นับ archived/draft ต่างจาก API?)"
        print(f"   {fname}: {n} แถว {mark}")
    if any(n != total for n in results.values()):
        sys.exit(1)
