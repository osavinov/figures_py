import logging
import os
import datetime
from game_level import GameLevel
from settings import LOG_LEVEL

logger = logging.getLogger(__name__)


def main():
    root_dir: str = os.path.split(os.path.abspath(__file__))[0]
    logs_dir: str = os.path.join(root_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename: str = datetime.datetime.utcnow().isoformat().replace('-', '').replace(':', '')[:15]
    logging.basicConfig(
        filename=os.path.join(logs_dir, f'{log_filename}.log'),
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s: %(message)s',
    )
    game: GameLevel = GameLevel()
    while game.update_field():
        pass


if __name__ == '__main__':
    main()
