# Import all the models, so that metadata has them before being
# imported by Alembic

from app.db import models  # noqa
from app.db.base_class import Base  # noqa
