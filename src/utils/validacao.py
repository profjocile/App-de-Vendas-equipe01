from datetime import datetime

CONECTIVOS_NOME = {
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "di",
    "du",
    "del",
    "van",
    "von",
}


def somente_digitos(texto):
    return "".join(caractere for caractere in str(texto) if caractere.isdigit())


def formatar_nome(texto):
    texto = " ".join(str(texto or "").split())
    if not texto:
        return ""
    todo_maiusculo = texto.isupper()
    partes = []
    for indice, palavra in enumerate(texto.split(" ")):
        if indice > 0 and palavra.lower() in CONECTIVOS_NOME:
            partes.append(palavra.lower())
            continue
        if not todo_maiusculo and palavra.isupper() and len(palavra) > 1:
            partes.append(palavra)
            continue
        partes.append(
            "-".join(segmento.capitalize() for segmento in palavra.split("-"))
        )
    return " ".join(partes)


def formatar_titulo(texto):
    texto = " ".join(str(texto or "").split())
    if not texto:
        return ""
    if texto.isupper():
        return texto.capitalize()
    return texto[0].upper() + texto[1:]


def formatar_email(texto):
    return str(texto or "").strip().lower()


def formatar_cpf(cpf):
    digitos = somente_digitos(cpf)
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return str(cpf or "").strip()


def formatar_telefone(texto):
    if texto is None:
        return ""
    digitos = somente_digitos(texto)
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return str(texto).strip()


def normalizar_telefone(texto):
    if not str(texto or "").strip():
        return ""
    digitos = somente_digitos(texto)
    if len(digitos) not in (10, 11):
        raise ValueError("O telefone deve conter DDD + 8 ou 9 dígitos.")
    return formatar_telefone(digitos)


def formatar_moeda(valor):
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        valor = 0.0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_moeda(texto):
    limpo = str(texto).replace("R$", "").replace(" ", "").strip()
    if not limpo:
        raise ValueError("Informe um valor.")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    return float(limpo)


def parse_inteiro(texto, campo="quantidade"):
    try:
        return int(str(texto).strip())
    except (TypeError, ValueError):
        raise ValueError(f"O campo {campo} deve ser um número inteiro.")


def parse_data(texto):
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        raise ValueError("Data inválida. Use o formato DD/MM/AAAA.")


def formatar_data_hora(texto):
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            data = datetime.strptime(texto, formato)
            if formato == "%Y-%m-%d":
                return data.strftime("%d/%m/%Y")
            return data.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            continue
    return texto
