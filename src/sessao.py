class Sessao:
    _usuario = None

    @classmethod
    def iniciar(cls, usuario):
        cls._usuario = dict(usuario)

    @classmethod
    def encerrar(cls):
        cls._usuario = None

    @classmethod
    def usuario(cls):
        return cls._usuario

    @classmethod
    def e_admin(cls):
        return bool(cls._usuario and cls._usuario.get("perfil") == "admin")
