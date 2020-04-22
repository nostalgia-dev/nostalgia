from nostalgia.src.common.meta.category.services import Service
from nostalgia.src.common.infrastructure.sdf import join_time
from nostalgia.src.common.infrastructure.sdf import get_type_from_registry


class Web(Service):
    ##filter sdf when I was browsing
    def browsing(self, other, **window_kwargs):
        if isinstance(other, str):
            other = get_type_from_registry("browser").containing(other)
        return self.__class__(join_time(other, self, **window_kwargs))
