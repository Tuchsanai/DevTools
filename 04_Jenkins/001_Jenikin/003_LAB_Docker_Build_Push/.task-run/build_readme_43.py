#!/usr/bin/env python3
"""Replace README section 4.3 with template + the whole Jenkinsfile verbatim."""
import os
LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jf = open(os.path.join(LAB, "Jenkinsfile"), encoding="utf-8").read()
tpl = open(os.path.join(LAB, ".task-run", "readme_43_template.md"), encoding="utf-8").read()
new = tpl.replace("@@JENKINSFILE@@", "```groovy\n" + jf.rstrip("\n") + "\n```")
p = os.path.join(LAB, "README.md")
s = open(p, encoding="utf-8").read()
a = s.index("**4.3) ")
b = s.index("> 📌 **ทางเลือก ข")
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
