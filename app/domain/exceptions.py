"""Excepciones de dominio: la capa Domain las lanza y la capa API las convierte en JSON."""


class ErrorDominio(Exception):
    codigo = 400

    def __init__(self, mensaje: str, regla: str | None = None, campo: str | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.regla = regla
        self.campo = campo


class NoEncontrado(ErrorDominio):
    codigo = 404


class Conflicto(ErrorDominio):
    codigo = 409


class ReglaNegocio(ErrorDominio):
    codigo = 422
