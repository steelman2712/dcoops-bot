from dcoopsdb.models import Bind


class Soundboard:
    def load_bind_names(self, server):
        binds = Bind().load_all(server=server)
        output = [bind.alias for bind in binds]
        return output
