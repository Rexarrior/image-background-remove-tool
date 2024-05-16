from carvekit.web.schemas.config import WebAPIConfig
from carvekit.web.utils.init_utils import init_config
from carvekit.web.utils.task_queue import MLProcessor
from carvekit.web.database.managers import DBSingleton
from carvekit.web.database.engines import PgEngine, SqlliteDbEngine

config: WebAPIConfig = init_config()
DBSingleton().init_db(config)
ml_processor = MLProcessor(api_config=config)
