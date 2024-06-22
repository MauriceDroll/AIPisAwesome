import os
import subprocess
from datetime import datetime

def create_timestamped_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timestamp_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"Timestamp file created at {timestamp}")
    return filename

def run_command(command,commit_message):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
               
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")


def run_git_commands(commit_message):
    try:
        # Änderungen zu Git hinzufügen
        git_add_command = "git add ."
        execute_command(git_add_command)
        
        # Änderungen committen
        git_commit_command = f"git commit -m '{commit_message}'"
        execute_command(git_commit_command)
        
        # Änderungen pushen
        # Hole den Token aus den Umgebungsvariablen
        username = os.getenv('GIT_USERNAME')
        token = os.getenv('GIT_TOKEN')
        
        git_push_command = f"git push https://{token}:@github.com/MauriceDroll/AIPisAwesome main"
        execute_command(git_push_command)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")

timestamped_file = create_timestamped_file()
# Liste der Python-Befehle
python_commands = [
    f"python3 -c \"with open('{timestamped_file}', 'w') as f: f.write('This file was created by a Python command.')\"",    # Weitere Befehle können hier hinzugefügt werden
    # "python another_script.py --option value"
]

commit_messages = [
    "11 commit",
    # Weitere Commit-Nachrichten können hier hinzugefügt werden
    # "Automated commit: another_script"

]

# Iteriere durch die Liste der Python-Befehle und führe jeden aus
for python_command in python_commands:
    for commit_message in commit_messages:
        execute_command(python_command)
        run_git_commands(commit_message)
    


