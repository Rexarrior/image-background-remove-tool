from functools import wraps

from carvekit.web.database.models.base import Base

def managed_session(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        session = kwargs.get('session')
        if session:
            is_session_managed = False
        else:
            session = self.get_session()
            is_session_managed = True
            kwargs['session'] = session

        try:
            result = method(self, *args, **kwargs)
            session.commit()
            if isinstance(result, Base):
                session.refresh(result)
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    return wrapper