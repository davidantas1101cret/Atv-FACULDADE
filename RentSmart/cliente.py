"""Classe Cliente: dados e validação do cliente."""
import re


class ValidacaoErro(ValueError):
    """Erro de validação de regra de negócio ou de entrada."""


class Cliente:
    def __init__(self, nome, email, telefone):
        nome, email, telefone = (nome or "").strip(), (email or "").strip(), (telefone or "").strip()
        if len(nome.split()) < 2:
            raise ValidacaoErro("Informe o nome completo (nome e sobrenome).")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValidacaoErro("Informe um e-mail válido, como nome@dominio.com.")
        if len(re.sub(r"\D", "", telefone)) not in (10, 11):
            raise ValidacaoErro("Informe o telefone com DDD (10 ou 11 dígitos).")
        self._nome, self._email, self._telefone = nome, email, telefone

    @property
    def nome(self): return self._nome
    @property
    def email(self): return self._email
    @property
    def telefone(self): return self._telefone

    def para_dict(self):
        return {"nome": self._nome, "email": self._email, "telefone": self._telefone}
