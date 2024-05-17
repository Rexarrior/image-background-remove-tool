from carvekit.web.schemas.config import WebAPIConfig
from carvekit.web.utils.init_utils import init_config
from carvekit.web.utils.task_queue import MLProcessor
from carvekit.web.database.managers import DbFacade

config: WebAPIConfig = init_config()
db = DbFacade.make_db_facade(config)
ml_processor = MLProcessor(api_config=config)
