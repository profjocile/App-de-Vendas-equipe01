import zipfile
from xml.sax.saxutils import escape, quoteattr

ESTILO_PADRAO = 0
ESTILO_TITULO = 1
ESTILO_ROTULO = 2
ESTILO_VALOR = 3
ESTILO_SECAO = 4
ESTILO_CABECALHO = 5
ESTILO_TEXTO = 6
ESTILO_TEXTO_ALT = 7
ESTILO_INTEIRO = 8
ESTILO_INTEIRO_ALT = 9
ESTILO_MOEDA = 10
ESTILO_MOEDA_ALT = 11
ESTILO_DESTAQUE = 12
ESTILO_MOEDA_DESTAQUE = 13
ESTILO_CONCLUIDA = 14
ESTILO_CANCELADA = 15

_FONTES = """<fonts count="8">
<font><sz val="11"/><name val="Calibri"/><color rgb="FF1F2937"/></font>
<font><b/><sz val="16"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font>
<font><b/><sz val="10"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font>
<font><b/><sz val="11"/><name val="Calibri"/><color rgb="FF1F2937"/></font>
<font><sz val="10"/><name val="Calibri"/><color rgb="FF4B5563"/></font>
<font><b/><sz val="11"/><name val="Calibri"/><color rgb="FF1F2937"/></font>
<font><b/><sz val="11"/><name val="Calibri"/><color rgb="FF15803D"/></font>
<font><b/><sz val="11"/><name val="Calibri"/><color rgb="FFB91C1C"/></font>
</fonts>"""

_FILLS = """<fills count="9">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1D4ED8"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1E3A8A"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF2563EB"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFEFF6FF"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFDBEAFE"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFDCFCE7"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFFEE2E2"/><bgColor indexed="64"/></patternFill></fill>
</fills>"""

_BORDAS = """<borders count="2">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border><left style="thin"><color rgb="FFD1D5DB"/></left><right style="thin"><color rgb="FFD1D5DB"/></right><top style="thin"><color rgb="FFD1D5DB"/></top><bottom style="thin"><color rgb="FFD1D5DB"/></bottom><diagonal/></border>
</borders>"""

_ESTILOS = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="1"><numFmt numFmtId="164" formatCode="[$R$-416] #,##0.00"/></numFmts>
{_FONTES}
{_FILLS}
{_BORDAS}
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="16">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="left" vertical="center" indent="1"/></xf>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="center"/></xf>
<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="center"/></xf>
<xf numFmtId="0" fontId="2" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="left" vertical="center" indent="1"/></xf>
<xf numFmtId="0" fontId="2" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
<xf numFmtId="164" fontId="0" fillId="5" borderId="1" xfId="0" applyNumberFormat="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
<xf numFmtId="0" fontId="5" fillId="6" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
<xf numFmtId="164" fontId="5" fillId="6" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
<xf numFmtId="0" fontId="6" fillId="7" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="7" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
<dxfs count="0"/>
<tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>"""


def _coluna(indice):
    letras = ""
    while indice > 0:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _numero(valor):
    if isinstance(valor, int):
        return str(valor)
    return format(float(valor), ".15g")


def _celula(referencia, valor, estilo):
    atributos = f'r="{referencia}" s="{estilo}"'
    if valor is None or valor == "":
        return f"<c {atributos}/>"
    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(valor, (int, float)):
        return f"<c {atributos}><v>{_numero(valor)}</v></c>"
    texto = escape(str(valor))
    return (
        f'<c {atributos} t="inlineStr"><is><t xml:space="preserve">'
        f"{texto}</t></is></c>"
    )


class Planilha:
    def __init__(self, nome="Planilha"):
        self.nome = nome
        self.larguras = []
        self._linhas = []
        self._mesclagens = []

    def definir_larguras(self, larguras):
        self.larguras = list(larguras)

    def adicionar(self, valores, estilos=None, altura=None):
        total = len(valores)
        if estilos is None:
            estilos = [ESTILO_PADRAO] * total
        self._linhas.append((list(valores), list(estilos), altura))
        return len(self._linhas)

    def mesclar(self, linha, coluna_ini, coluna_fim):
        referencia = (
            f"{_coluna(coluna_ini)}{linha}:{_coluna(coluna_fim)}{linha}"
        )
        self._mesclagens.append(referencia)

    def _sheet_data(self):
        partes = []
        for indice, (valores, estilos, altura) in enumerate(self._linhas, start=1):
            atributos = f'r="{indice}"'
            if altura:
                atributos += f' ht="{altura}" customHeight="1"'
            celulas = "".join(
                _celula(f"{_coluna(coluna)}{indice}", valor, estilos[coluna - 1])
                for coluna, valor in enumerate(valores, start=1)
            )
            if celulas:
                partes.append(f"<row {atributos}>{celulas}</row>")
            else:
                partes.append(f"<row {atributos}/>")
        return "".join(partes)

    def _cols(self):
        if not self.larguras:
            return ""
        colunas = "".join(
            f'<col min="{indice}" max="{indice}" width="{largura}" '
            'customWidth="1"/>'
            for indice, largura in enumerate(self.larguras, start=1)
        )
        return f"<cols>{colunas}</cols>"

    def _merges(self):
        if not self._mesclagens:
            return ""
        itens = "".join(
            f'<mergeCell ref="{referencia}"/>' for referencia in self._mesclagens
        )
        return f'<mergeCells count="{len(self._mesclagens)}">{itens}</mergeCells>'

    def salvar(self, caminho):
        total_linhas = max(len(self._linhas), 1)
        total_colunas = max(
            (len(valores) for valores, _, _ in self._linhas), default=1
        )
        dimensao = f"A1:{_coluna(total_colunas)}{total_linhas}"
        sheet = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<dimension ref="{dimensao}"/>'
            '<sheetViews><sheetView showGridLines="0" workbookViewId="0"/></sheetViews>'
            '<sheetFormatPr defaultRowHeight="18"/>'
            f"{self._cols()}"
            f"<sheetData>{self._sheet_data()}</sheetData>"
            f"{self._merges()}"
            '<pageMargins left="0.5" right="0.5" top="0.75" bottom="0.75" '
            'header="0.3" footer="0.3"/>'
            '<pageSetup orientation="landscape" fitToWidth="1" fitToHeight="0" '
            'paperSize="9"/>'
            "</worksheet>"
        )
        workbook = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name={quoteattr(self.nome[:31])} sheetId="1" '
            'r:id="rId1"/></sheets>'
            "</workbook>"
        )
        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            'Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
            'Target="styles.xml"/>'
            "</Relationships>"
        )
        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            "</Relationships>"
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            "</Types>"
        )
        with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as arquivo:
            arquivo.writestr("[Content_Types].xml", content_types)
            arquivo.writestr("_rels/.rels", rels)
            arquivo.writestr("xl/workbook.xml", workbook)
            arquivo.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            arquivo.writestr("xl/styles.xml", _ESTILOS)
            arquivo.writestr("xl/worksheets/sheet1.xml", sheet)
