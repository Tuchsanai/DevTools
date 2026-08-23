#!/usr/bin/env python3
"""Replace only the frozen LAB 4 slide window while preserving all page numbers."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "slides_src.html"
START = '<script id="slideData" type="text/plain">'
END = "</script>"
US = "␟"


def normal(eyebrow: str, title: str, body: str) -> str:
    # One physical line is one slide record. Keep code line breaks as HTML
    # entities and strip the visual '+' introduced by Python continuation text.
    body = body.replace("\n+", "&#10;").replace("\n", "&#10;")
    return US.join(("ตอน 5.2 · LAB 4", "normal", eyebrow, title, body))


slides = [
    normal("LAB 4 • ภาพรวม", "7 การทดลองเชื่อม source revision ถึง immutable image", '<div class="grid3"><div class="card g"><h3>GitHub</h3><p>ownership marker · anonymous checkout · Pipeline as Code</p></div><div class="card"><h3>Jenkins</h3><p>deterministic test · SHA tags · credential binding · Poll SCM</p></div><div class="card a"><h3>Docker Hub</h3><p>full/short SHA · OCI revision · digest · pull-run</p></div></div><div class="chips"><span class="chip">1 marker</span><span class="chip">2 test</span><span class="chip">3 push source</span><span class="chip">4 SCM + credential</span><span class="chip">5 build/push</span><span class="chip">6 Poll SCM</span><span class="chip g">7 check.sh</span></div><div class="callout good" style="margin-top:18px"><strong>เป้าหมาย:</strong> หลักฐานทุกจุดต้องย้อนกลับไปยัง Git commit เดียวกันและไม่มี secret ใน repository, log หรือภาพ</div>'),
    normal("DIAGRAM D18", "สายหลักฐาน GitHub → Jenkins → Docker Hub → pull by digest", '<div class="diagram" data-inline-svg="slides_assets/d18_lab4_sha_digest.svg"></div>'),
    normal("SHA → DIGEST", "Tag ใช้ค้นหา · digest ใช้ยืนยัน content แบบ immutable", '<video class="hero-video" data-asset="slides_assets/motion/mo_lab4_sha_digest.mp4" data-composition="mo-lab4-sha-digest" autoplay muted loop playsinline preload="auto"></video><div class="caption">วิดีโอ Remotion: revision เดียวเดินทางผ่าน test, build, push และ pull-run</div>'),
    normal("LAB 4 • การทดลองที่ 1", "Repository นี้เป็นของแล็บและอ่านแบบ anonymous ได้หรือไม่?", '<pre class="code sm" data-lang="bash">git clone https://github.com/&lt;GITHUB_USER&gt;/hello-ci.git "$HOME/hello-ci" &amp;&amp; \\\n+test "$(cat "$HOME/hello-ci/.course-cicd2569")" = \'course fixture — safe to delete\'</pre><div class="callout good" style="margin-top:18px"><strong>✅ สังเกต:</strong> clone ไม่ถาม credential และ marker ตรง canonical ก่อนแก้ repository</div>'),
    normal("LAB 4 • การทดลองที่ 1 • หลักฐาน UI", "ตรวจ branch main และ ownership marker บน GitHub", '<div class="shotwrap"><div class="shot" style="height:448px"><img data-asset="slides_assets/lab4_s03_github_repo_files.png" data-max-width="1360" alt="GitHub repository จริงหลัง push source ของ LAB 4"></div><div><ol class="steps"><li><b>เปิด repository</b><br>ใช้ public URL</li><li><b>ตรวจ branch</b><br>ต้องเป็น main</li><li><b>ตรวจไฟล์</b><br>marker + Pipeline source</li></ol><div class="callout good"><strong>✅</strong> ชื่อบัญชีในภาพถูกแทนด้วย &lt;GITHUB_USER&gt;</div></div></div><div class="caption">ภาพจริงจาก GitHub · กรอบแดงและหมายเลขชี้จุดตรวจ</div>'),
    normal("LAB 4 • การทดลองที่ 2", "ผลทดสอบซ้ำได้โดยไม่ขึ้นกับ Jenkins หรือไม่?", '<pre class="code" data-lang="bash">cd "$HOME/hello-ci" &amp;&amp; ./hello.sh &gt; actual.txt &amp;&amp; \\\n+diff -u expected.txt actual.txt</pre><div class="callout good" style="margin-top:18px"><strong>✅ สังเกต:</strong> diff ไม่แสดงความแตกต่างและคืน exit code 0 จึงนำ test เดิมไปรันใน Jenkins ได้</div>'),
    normal("LAB 4 • การทดลองที่ 3", "Push Pipeline-as-Code โดยไม่ฝัง PAT", '<pre class="code sm" data-lang="bash">cd "$HOME/hello-ci" &amp;&amp; git add .course-cicd2569 .dockerignore Dockerfile Jenkinsfile app expected.txt hello.sh &amp;&amp; \\\n+git -c user.name=Student -c user.email=student@example.invalid commit -m \'Build immutable image from Git SHA\'</pre><pre class="code sm" data-lang="bash" style="margin-top:12px">git push origin main</pre><div class="callout warn" style="margin-top:12px"><strong>Credential prompt:</strong> Username = &lt;GITHUB_USER&gt; · Password = &lt;GITHUB_TOKEN&gt; และห้ามเก็บ token ใน URL/history</div><div class="callout good" style="margin-top:10px"><strong>✅ สังเกต:</strong> main มี Dockerfile, Jenkinsfile และ app จาก commit เดียวกัน</div>'),
    normal("LAB 4 • การทดลองที่ 3 • Pipeline as Code", "หนึ่ง commit ระบุทั้งสิ่งที่จะ build และวิธี build", '<div class="split"><div><pre class="code sm" data-lang="text">hello-ci/\n├── .course-cicd2569\n├── Dockerfile\n├── Jenkinsfile\n├── app/index.html\n├── expected.txt\n└── hello.sh</pre></div><div><div class="card g"><h3>review ได้</h3><p>ขั้น test/build/push เปลี่ยนพร้อม source และเห็น diff ใน GitHub</p></div><div class="card a" style="margin-top:14px"><h3>ย้อนกลับได้</h3><p>SHA เลือก Pipeline และ image revision ที่สอดคล้องกัน</p></div></div></div><div class="callout good" style="margin-top:16px"><strong>✅ สังเกต:</strong> remote URL ไม่มี token และ history ไม่มี secret literal</div>'),
    normal("LAB 4 • การทดลองที่ 4", "แยก anonymous GitHub read ออกจาก Docker credential", '<ol class="steps"><li><b>New Item → Pipeline</b> ตั้งชื่อ hello-ci-pipeline</li><li><b>Pipeline script from SCM → Git</b> URL public · Credentials - none - · */main · Jenkinsfile</li><li><b>Manage Jenkins → Credentials</b> สร้าง Username with password ID dockerhub</li></ol><pre class="code sm" data-lang="bash" style="margin-top:12px">curl -fsS -u \'&lt;JENKINS_USER&gt;:&lt;JENKINS_API_TOKEN&gt;\' \\\n+  http://localhost:8080/job/hello-ci-pipeline/config.xml | grep -E \'github.com|credentialsId|scriptPath\'</pre><div class="callout good" style="margin-top:12px"><strong>✅ สังเกต:</strong> SCM XML ไม่มี credentialsId; dockerhub ถูกเรียกเฉพาะ stage push</div>'),
    normal("LAB 4 • การทดลองที่ 4 • หลักฐาน UI", "Pipeline from SCM แบบ anonymous", '<div class="shotwrap"><div class="shot" style="height:455px"><img data-asset="slides_assets/lab4_s05_jenkins_scm_config.png" data-max-width="1360" alt="Jenkins Pipeline from SCM จริง"></div><div><ol class="steps"><li>Definition</li><li>Git</li><li>Public URL</li><li>Credentials: none</li><li>Branch */main</li></ol></div></div><div class="caption">ภาพจริงจาก Jenkins · marker ครบลำดับกรอกก่อน Save</div>'),
    normal("LAB 4 • การทดลองที่ 5", "Credential มีชีวิตเฉพาะ Publish image", '<pre class="code sm" data-lang="groovy">stage(\'Build OCI image\') {\n  steps { sh \'docker build -t hello-ci-local:$FULL_SHA .\' }\n}\nstage(\'Publish image\') {\n  steps {\n    withCredentials([usernamePassword(credentialsId: \'dockerhub\', usernameVariable: \'DOCKER_USER\', passwordVariable: \'DOCKER_TOKEN\')]) {\n      sh \'printf %s "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin\'\n      sh \'docker tag hello-ci-local:$FULL_SHA $DOCKER_USER/hello-ci:$FULL_SHA &amp;&amp; docker push $DOCKER_USER/hello-ci:$FULL_SHA\'\n    }\n  }\n}</pre><div class="callout good" style="margin-top:12px"><strong>✅ สังเกต:</strong> Build และ Verify ไม่มี withCredentials; Publish เป็น stage เดียวที่ bind credential</div>'),
    normal("LAB 4 • การทดลองที่ 5 • Console", "Build local → Publish with credential → Verify public digest", '<div class="shotwrap"><div class="shot" style="height:455px"><img data-asset="slides_assets/lab4_s06_manual_build_console.png" data-max-width="1360" alt="Console Output จริงของ LAB 4"></div><div><ol class="steps"><li>Build local tag</li><li>Bind เฉพาะ Publish</li><li>Public pull ไม่ bind</li><li>Finished: SUCCESS</li></ol></div></div><div class="caption">ภาพจริงจาก Jenkins build ที่แยก credential boundary สำเร็จ</div>'),
    normal("LAB 4 • การทดลองที่ 5 • Docker Hub", "Full SHA tag และ short SHA tag ชี้ digest เดียวกัน", '<div class="shotwrap"><div class="shot" style="height:455px"><img data-asset="slides_assets/lab4_s10_dockerhub_sha_tags.png" data-max-width="1360" alt="Docker Hub จริงแสดง SHA tags และ digest"></div><div><ol class="steps"><li>full SHA tag</li><li>short SHA tag</li><li>immutable digest</li></ol><div class="callout good"><strong>✅</strong> ชื่อบัญชีถูกแทนด้วย &lt;DOCKER_USER&gt;</div></div></div><div class="caption">ภาพจริงจาก Docker Hub หลัง Jenkins push</div>'),
    normal("LAB 4 • การทดลองที่ 6", "Poll SCM จะสร้าง build เมื่อ revision เปลี่ยนหรือไม่?", '<ol class="steps"><li><b>hello-ci-pipeline → Configure → Triggers</b></li><li><b>Poll SCM</b> แล้วกรอก <span class="inline">* * * * *</span></li><li>อ่านคำเตือน every minute แล้วกด <b>Save</b></li></ol><pre class="code sm" data-lang="bash" style="margin-top:12px">cd "$HOME/hello-ci" &amp;&amp; printf \'\\n# Poll SCM probe\\n\' &gt;&gt; hello.sh &amp;&amp; \\\n+git add hello.sh &amp;&amp; git commit -m \'Observe Poll SCM\' &amp;&amp; git push origin main</pre><div class="callout warn" style="margin-top:12px"><strong>ห้ามกด Build Now:</strong> ต้องให้ scheduler เป็นผู้เริ่ม build เพื่อพิสูจน์ cause</div>'),
    normal("LAB 4 • การทดลองที่ 6 • Trigger UI", "ตั้ง schedule เป็นดาวห้าช่อง", '<div class="shotwrap"><div class="shot" style="height:455px"><img data-asset="slides_assets/lab4_s07_poll_scm_trigger.png" data-max-width="1360" alt="Jenkins Poll SCM trigger จริง"></div><div><ol class="steps"><li>เลือก Poll SCM</li><li>กรอก * * * * *</li><li>อ่านคำเตือน</li><li>Save</li></ol></div></div><div class="caption">ภาพจริงจาก Jenkins Configure · <b>H/1</b> ไม่ใช่ทุกนาที แต่คือหนึ่งครั้งต่อชั่วโมง</div>'),
    normal("LAB 4 • การทดลองที่ 6 • ผลจริง", "Polling log และ build cause ยืนยัน revision เดียวกัน", '<div class="grid2"><div class="shot" style="height:430px"><img data-asset="slides_assets/lab4_s08_git_polling_log.png" data-max-width="1360" alt="Git Polling Log จริงแสดง Changes found"></div><div class="shot" style="height:430px"><img data-asset="slides_assets/lab4_s09_scm_build_cause.png" data-max-width="1360" alt="Jenkins build cause จาก SCM change จริง"></div></div><div class="caption">ซ้าย: Changes found จาก Poll SCM จริง · ขวา: Started by an SCM change ของ build ที่เกิดตามมา</div>'),
    normal("LAB 4 • การทดลองที่ 7", "ตรวจ contract ทั้งชุดซ้ำด้วย check.sh", '<pre class="code" data-lang="bash">cd "$COURSE_ROOT/004_LAB_Pipeline_From_Git" &amp;&amp; bash check.sh</pre><div class="grid3" style="margin-top:18px"><div class="card g metric"><strong>SHA</strong><span>GitHub = build = OCI revision</span></div><div class="card g metric"><strong>digest</strong><span>รูปแบบ sha256:64 hex</span></div><div class="card g metric"><strong>run</strong><span>Hello from GitHub</span></div></div><div class="callout good" style="margin-top:16px"><strong>✅ สังเกต:</strong> ผลรวม: PASS พร้อม exit code 0 และ pull-run by digest สำเร็จ</div>'),
    normal("LAB 4 • แก้ปัญหาที่พบบ่อย", "อ่านอาการจากหลักฐานก่อนแก้ configuration", '<table class="table"><tr><th>อาการ</th><th>จุดตรวจ</th><th>แนวแก้</th></tr><tr><td>checkout ล้มเหลว</td><td>*/main · Jenkinsfile</td><td>แก้ branch/script path โดยไม่เพิ่ม SCM credential</td></tr><tr><td>unauthorized ตอน push</td><td>credential ID dockerhub</td><td>แก้ Jenkins credential; ห้ามวาง token ในไฟล์</td></tr><tr><td>digest ว่าง</td><td>docker push exit code</td><td>inspect RepoDigests หลัง push สำเร็จ</td></tr><tr><td>Poll ไม่เกิด build</td><td>* * * * * · Polling Log</td><td>push revision ใหม่แล้วรอ scheduler</td></tr><tr><td>Invalid option timestamps</td><td>plugin ที่ติดตั้ง</td><td>ตัด option ที่ไม่จำเป็นหรือเพิ่ม plugin</td></tr></table>'),
    normal("LAB 4 • สรุป", "หลักฐานที่ตรวจย้อนกลับได้สำคัญกว่า tag ที่อ่านง่ายเพียงอย่างเดียว", '<div class="grid2"><div class="card g"><h3>Tag จาก SHA</h3><p>ค้นหา image ตาม source revision ได้ และ full/short tag ช่วยคนอ่าน</p></div><div class="card"><h3>Digest</h3><p>ยืนยัน content แบบ immutable และใช้ pull-run เพื่อพิสูจน์ artifact ที่เผยแพร่จริง</p></div></div><div class="callout" style="margin-top:18px"><strong>ขอบเขต credential:</strong> public checkout ไม่ใช้ credential; Docker Hub credential มีชีวิตเฉพาะ stage ที่ต้อง push</div><div class="callout warn" style="margin-top:14px"><strong>ข้อจำกัด:</strong> Poll SCM มีความหน่วงและถาม Git แม้ไม่มี commit — LAB 5 จะเปลี่ยนเป็น webhook</div>'),
    US.join(("ตอน 5.2 · LAB 4", "labgo", "LAB 4", "GitHub → Jenkins → Docker Hub ด้วย SHA + digest", "004_LAB_Pipeline_From_Git", "anonymous checkout • deterministic test • SHA tags • OCI labels • pull-run by digest", "50′")),
]


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    prefix, tail = text.split(START, 1)
    block, suffix = tail.split(END, 1)
    records = block.strip().splitlines()
    if len(slides) != 20:
        raise SystemExit(f"LAB 4 replacement must remain 20 slides, got {len(slides)}")
    opener = next(
        (i for i, record in enumerate(records) if record.split(US)[1:3] == ["labopen", "4"]),
        None,
    )
    if opener is None:
        raise SystemExit("LAB 4 opener missing; refusing rewrite")
    next_section = next(
        (i for i in range(opener + 1, len(records)) if records[i].split(US)[1:2] == ["subsection"]),
        None,
    )
    if next_section is None:
        raise SystemExit("LAB 5 subsection missing; refusing rewrite")
    records[opener + 1 : next_section] = slides
    if len(records) != 198:
        raise SystemExit(f"replacement did not restore frozen page count: {len(records)}")
    SOURCE.write_text(prefix + START + "\n" + "\n".join(records) + "\n" + END + suffix, encoding="utf-8")
    print("updated LAB 4 slides 103-122; total pages unchanged at 198")


if __name__ == "__main__":
    main()
