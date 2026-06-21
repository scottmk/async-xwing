import logging
import os
import subprocess
import sys


logger = logging.getLogger()


LOGO = r"""
     ___           _______.____    ____ .__   __.   ______
    /   \         /       |\   \  /   / |  \ |  |  /      |
   /  ^  \       |   (----` \   \/   /  |   \|  | |  ,----'
  /  /_\  \       \   \      \_    _/   |  . `  | |  |
 /  _____  \  .----)   |       |  |     |  |\   | |  `----.
/__/     \__\ |_______/        |__|     |__| \__|  \______|

___   ___      ____    __    ____  __  .__   __.   _______
\  \ /  /      \   \  /  \  /   / |  | |  \ |  |  /  _____|
 \  V  /   _____\   \/    \/   /  |  | |   \|  | |  |  __
  >   <   |______\            /   |  | |  . `  | |  | |_ |
 /  .  \          \    /\    /    |  | |  |\   | |  |__| |
/__/ \__\          \__/  \__/     |__| |__| \__|  \______|
"""


def main():
    print(LOGO)
    print()
    if not os.path.exists('../.env'):
        logger.info('📝 Creating .env from template...')
        subprocess.run(['cp', '.env.example', '.env'])
        logger.warning(
            '⚠️ Template .env copied; please add your bot token to TOKEN and execute the setup script again'
        )
        return

    subprocess.run([sys.executable, '-m', 'scripts.upload_emoji'])

    logger.info('✅ Setup complete! You are ready to develop.')


if __name__ == '__main__':
    main()
