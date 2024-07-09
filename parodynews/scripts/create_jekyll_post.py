import os
from datetime import datetime
import dotenv

# Load the environment variables from the .env file
dotenv.load_dotenv()

githome=os.getenv('GITHOME')
git_repo=os.getenv('GIT_REPO')
posts_dir=os.getenv('POSTS_DIR')

zrepo = os.path.join(githome, git_repo, posts_dir)

def create_jekyll_post(title, content):
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_str}-{title.replace(' ', '-')}.md"
    filepath = os.path.join(zrepo, filename)
    filepath = os.path.expanduser(filepath)  # This expands the '~' to the full home directory path

    with open(filepath, 'w') as file:
        file.write(f"---\ntitle: {title}\ndate: {date_str}\n---\n\n{content}")
    return filepath