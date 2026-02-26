# SOFTWARE-DEVELOPMENT-TOOLS-AND-ENVIRONMENTS

## เนื้อหาตามหลักสูตร :

หลักการเพื่อเป็นผู้เชี่ยวชาญด้านซอฟต์แวร์ บทบาทของแอพพลิเคชันในงานด้านวิศวกรรมซอฟต์แวร์ เครื่องมือการพัฒนาซอฟต์แวร์แบบอไจล์ การติดตามความคืบหน้าของการพัฒนาผลิตภัณฑ์ การจัดการเวอร์ชั่นและการกำหนดค่า เครื่องสำหรับสร้างและการบูรณาการอย่างต่อเนื่อง เครื่องสำหรับแก้จุดบกพร่องและการรวบรวมข้อมูลเชิงประสิทธิภาพชองโปรแกรม สภาพแวดล้อมแบบร่วมมือพัฒนา เครื่องมือสำหรับการควบรวบรวมและติดตั้ง

------------------------------------------------------------------------------------------------------------------------


Principles to Software Professionals, Roles of Applications in Software Engineering Tasks, Agile Software Development Tools, Product Development Tracking, Version and Configuration Management, Build and Continuous Integration Tools, Program Debugging and Profiling Tools, Collaborative Development Environments, Packaging and Deployment


## Course Learning Outcomes (CLOs)

| CLO ID | CLO Description |
|--------|----------------|
| CLO-1 | เข้าใจสภาพแวดล้อมและเครื่องมือที่ใช้ในการพัฒนาซอฟต์แวร์ในภาคอุตสาหกรรม |
| CLO-2 | เข้าใจแนวคิดของการจัดเก็บเวอร์ชั่นและสามารถใช้ Git Workflow เช่น Git Push, Git Fetch, Git Pull และการแตก Git Branch และเข้าใจการรวม Git Merges และ Merge Conflicts ในการทำงานพัฒนาซอฟต์แวร์ |
| CLO-3 | เข้าใจระบบ Undo Changes โดยใช้ `git restore`, `git revert` และ `git reset` พร้อมทั้งเข้าใจระบบ Git Collaboration Workflow |
| CLO-4 | เข้าใจระบบคอนเทนเนอร์ Docker ได้แก่ Docker Images, Docker Engine, Docker Storage, Docker Networking และการใช้งาน Docker Compose และ Docker Swarm รวมถึงการออกแบบ CI/CD |
| CLO-5 | เข้าใจการจัดการควบคุมปฏิบัติงานของคอนเทนเนอร์โดยใช้ Kubernetes การกำหนดค่า Kubernetes Configuration Files ใน YAML และสามารถเข้าใจการสร้าง Kubernetes Cluster ได้ |
| CLO-6 | เข้าใจการ Deploy Applications บน Kubernetes และการตั้งค่า ReplicaSets, Services และ Deployments รวมถึงสามารถเข้าใจการสร้าง Microservices Application บน Kubernetes และ CI/CD |


# 📋 ตารางแผนการสอน — SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS

| Session | Topics | Teaching Methods | CLOs |
|:---:|------|:---:|:---:|
| 1 | **Introduction to Software Development Tools and Environments** | บรรยาย | CLO-1 |
| | **• Principles to Software Professionals** | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Software Professional vs Programmer | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ SOLID & Design Principles (DRY, KISS, YAGNI) | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Clean Code & Professional Ethics (ACM/IEEE) | | |
| | **• Roles of Applications in Software Engineering Tasks** | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Planning & Development Tools (Jira, Trello, VS Code) | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Version Control, CI/CD & Monitoring | | |
| | **• Agile Software Development Tools (Scrum & Kanban)** | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Scrum Framework (3 Roles, 5 Events, 3 Artifacts) | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Kanban (Board, WIP Limit) & Agile Metrics | | |
| | **• Product Development Tracking (Jira & Trello)** | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Jira (Epic/Story/Task/Bug, Sprint Board, JQL) | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Trello (Board-List-Card, Automation) | | |
| | **• Overview of Development Workflow & Toolchain** | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ Plan & Code → Test & Deploy → Monitor & Feedback | | |
| | &nbsp;&nbsp;&nbsp;&nbsp;◦ CI/CD Pipeline Overview | | |
| 2 | **Git and GitHub Fundamentals** | บรรยาย + LAB | CLO-1, CLO-2 |
| | • Configure Git | | |
| | • Creating & Cloning Repositories | | |
| | • Private Repositories & Token | | |
| | • Add & Commit | | |
| | • Git Log | | |
| | • Git Remote & Git Push | | |
| | • Fetch & Pull | | |
| 3 | **Understanding Branches** | บรรยาย + LAB | CLO-2 |
| | • Understanding HEAD | | |
| | • Git Branch Commands | | |
| | • Delete & Rename Branches | | |
| | • Merging Branches (Theory & Practice) | | |
| | • Git Diff | | |
| 4 | **Git with Going Back and Undoing Changes** | บรรยาย + LAB | CLO-1, CLO-3 |
| | • Git Checkout & Detached HEAD | | |
| | • Git Restore / Git Reset / Git Revert | | |
| | • Undoing Changes Exercise | | |
| | • Git Collaboration Workflow (Forking, Pull Requests) | | |
| 5 | **Google Cloud** | บรรยาย + LAB | CLO-4 |
| | • Create a Project on GCP | | |
| | • Create a Virtual Machine (VM Instance) | | |
| | • Create an SSH Key | | |
| | • Google Cloud Storage Bucket | | |
| | • Open Port / Firewall Rules | | |
| 6 | **Docker Overview** | บรรยาย + LAB | CLO-4 |
| | • Basic Docker Commands | | |
| | • Docker Run | | |
| | • Docker Images | | |
| | • Environment Variables | | |
| | • Command vs Entrypoint | | |
| 7 | **Docker Compose & Registry** | บรรยาย + LAB | CLO-4 |
| | • Docker Compose | | |
| | • Docker Registry | | |
| 8 | **Docker Engine, Storage & Networking** | บรรยาย + LAB | CLO-4 |
| | • Docker Engine | | |
| | • Docker Storage | | |
| | • Docker Networking | | |
| 9 | **Docker Applications & CI/CD** | บรรยาย + LAB | CLO-4 |
| | • Docker Applications | | |
| | • CI/CD — Docker Integration | | |
| 10 | **Jenkins CI/CD — Fundamentals** | บรรยาย + LAB | CLO-4 |
| | • Installing Jenkins on Ubuntu | | |
| | • Adding Credentials in Jenkins | | |
| | • Creating Your First Pipeline | | |
| | • Multi-Stage Pipeline and Environment Variables | | |
| 11 | **Jenkins CI/CD — GitHub Integration & Deployment** | บรรยาย + LAB | CLO-4 |
| | • CI/CD Pipeline Concepts (Continuous Integration / Continuous Deployment) | | |
| | • Workflow: Code Push → GitHub → Webhook → Jenkins → Build → Test → Deploy | | |
| | • Running Jenkinsfile from GitHub with SCM | | |
| | • Running Jenkinsfile from GitHub without SCM | | |
| | • GitHub Webhook + Build & Deploy Docker | | |
| | • Deploying to Remote Server via SSH | | |
| 12 | **Kubernetes 1** | บรรยาย + LAB | CLO-5 |
| | • Container Orchestration | | |
| | • Kubernetes Architecture | | |
| | • PODs | | |
| | • Services | | |
| 13 | **Kubernetes 2** | บรรยาย + LAB | CLO-5 |
| | • Basics of Networking in Kubernetes | | |
| | • ReplicaSets & Deployments | | |
| 14 | **Application Docker and Kubernetes 1** | บรรยาย + LAB | CLO-5, CLO-6 |
| | • Deploy Applications บน Kubernetes | | |
| | • ตั้งค่า ReplicaSets / Services / Deployments | | |
| 15 | **Application Docker and Kubernetes 2** | บรรยาย + LAB | CLO-5, CLO-6 |
| | • สร้าง Microservices Application บน Kubernetes | | |
| 16 | **Mini Project** | Mini Project + Pitch | - |
| | • นำเสนอ Mini Project ที่รวม Git, Docker, Kubernetes และ CI/CD | | |