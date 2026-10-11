
import re
from app.models.rule import AnalysisResult


RESERVED = {
    "REGLA": "TK_REGLA",
    "SI": "TK_SI",
    "Y": "TK_Y",
    "O": "TK_O",
    "ENTONCES": "TK_ENTONCES",
    "SINO": "TK_SINO",
    "FIN_REGLA": "TK_FIN_REGLA"
}

TOKEN_PATTERN = re.compile(
    r'"[^"]*"|>=|<=|==|!=|[><=()+*/-]|'
    r'[A-Za-z_][A-Za-z0-9_]*|'
    r'[0-9]+(?:\.[0-9]+)?|\S'
)


def classify_lexeme(lexeme):
    if lexeme in RESERVED:
        return RESERVED[lexeme]

    if re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', lexeme):
        return "TK_NUMERO"

    if re.fullmatch(r'"[^"]*"', lexeme):
        return "TK_CADENA"

    operators = {
        ">=": "TK_MAYOR_IGUAL",
        "<=": "TK_MENOR_IGUAL",
        "==": "TK_IGUAL",
        "!=": "TK_DIFERENTE",
        ">": "TK_MAYOR",
        "<": "TK_MENOR",
        "=": "TK_ASIGNACION",
        "(": "TK_PARENTESIS_ABRE",
        ")": "TK_PARENTESIS_CIERRA",
        "+": "TK_SUMA",
        "-": "TK_RESTA",
        "*": "TK_MULTIPLICACION",
        "/": "TK_DIVISION"
    }

    if lexeme in operators:
        return operators[lexeme]

    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', lexeme):
        return "TK_IDENTIFICADOR"

    return "TK_DESCONOCIDO"


def tokenize(source):
    tokens = []

    for number, line in enumerate(source.splitlines(), start=1):
        for match in TOKEN_PATTERN.finditer(line):
            lexeme = match.group(0)

            tokens.append({
                "line": number,
                "lexeme": lexeme,
                "token": classify_lexeme(lexeme)
            })

    return tokens


def validate_syntax(source):
    errors = []

    lines = [
        (number, line.strip())
        for number, line in enumerate(source.splitlines(), start=1)
        if line.strip()
    ]

    if not lines:
        return [{
            "line": 1,
            "message": "Escribe una regla antes de analizar."
        }]

    first_number, first_line = lines[0]

    if not re.fullmatch(
        r'REGLA\s+[A-Za-z_][A-Za-z0-9_]*',
        first_line
    ):
        errors.append({
            "line": first_number,
            "message": "La primera línea debe ser REGLA nombre."
        })

    if not any(re.match(r'^SI\s+', line) for _, line in lines):
        errors.append({
            "line": 0,
            "message": "Falta una condición SI."
        })

    if not any(
        re.match(r'^ENTONCES\s+', line)
        for _, line in lines
    ):
        errors.append({
            "line": 0,
            "message": "Falta una acción ENTONCES."
        })

    if lines[-1][1] != "FIN_REGLA":
        errors.append({
            "line": lines[-1][0],
            "message": "La regla debe terminar con FIN_REGLA."
        })

    condition_pattern = re.compile(
        r'^(SI|Y|O)\s+'
        r'[A-Za-z_][A-Za-z0-9_]*\s*'
        r'(>=|<=|==|!=|>|<)\s*'
        r'([A-Za-z_][A-Za-z0-9_]*|[0-9]+(?:\.[0-9]+)?)$'
    )

    action_pattern = re.compile(
        r'^(ENTONCES|SINO)\s+[A-Za-z_][A-Za-z0-9_]*$'
    )

    valid_start = re.compile(
        r'^(REGLA\s+|SI\s+|Y\s+|O\s+|'
        r'ENTONCES\s+|SINO\s+|FIN_REGLA$)'
    )

    for number, line in lines:
        if re.match(r'^(SI|Y|O)\s+', line):
            if not condition_pattern.fullmatch(line):
                errors.append({
                    "line": number,
                    "message": f"Condición incorrecta: {line}"
                })

        if re.match(r'^(ENTONCES|SINO)\s+', line):
            if not action_pattern.fullmatch(line):
                errors.append({
                    "line": number,
                    "message": f"Acción incorrecta: {line}"
                })

        if not valid_start.match(line):
            errors.append({
                "line": number,
                "message": f"Instrucción no reconocida: {line}"
            })

    return errors


def analyze_rule(source):
    tokens = tokenize(source)
    errors = validate_syntax(source)

    for token in tokens:
        if token["token"] == "TK_DESCONOCIDO":
            errors.append({
                "line": token["line"],
                "message": (
                    f"Lexema no reconocido: {token['lexeme']}"
                )
            })

    return AnalysisResult(
        tokens=tokens,
        errors=errors,
        line_count=len(source.splitlines()) if source.strip() else 0
    )
