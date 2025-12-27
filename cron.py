from crontab import CronTab
import os

current_dir = os.getcwd()
python_path = os.path.join(current_dir, "venv/bin/python")
script_path = os.path.join(current_dir, "scripts/daily_report.py")
log_path = os.path.join(current_dir, "cron_log.txt")

cron = CronTab(user=True)

job_comment = "Finance Dashboard Daily Report"
existing_jobs = list(cron.find_comment(job_comment))

if existing_jobs:
    print("Le Cron Job existe déjà. Mise à jour...")
    cron.remove_all(comment=job_comment)

command = f"{python_path} {script_path} >> {log_path} 2>&1"
job = cron.new(command=command, comment=job_comment)

job.setall("0 20 * * *")

cron.write()

print("✅ Cron Job configuré avec succès :")
print(f"Commande : {command}")
print("Horaire : 20h00 tous les jours")