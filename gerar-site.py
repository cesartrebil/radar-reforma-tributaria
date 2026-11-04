"""Gera docs/index.html: a versão pública do Radar, com os dados dentro do arquivo.

Uso: python -I gerar-site.py
Entradas: radar-reforma-tributaria.html e os JSON em dados/ (edicoes, agenda, painel).
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados"
DESCRICAO = "Novidades semanais e agenda de prazos da reforma tributária: CBS, IBS, split payment, Simples Nacional e Imposto Seletivo."

HEAD = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="%s">
<style>
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:light}
body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%%}[hidden]{display:none!important}
</style>
<script>
/* Dados embutidos: a página lê daqui em vez do banco de dados do Claude. */
window.RADAR_DADOS = %s;
window.claude = { use: function () {
  var D = window.RADAR_DADOS;
  function query(rows) {
    var q = {
      orderBy: function () { return q; },
      limit: function () { return q; },
      onSnapshot: function (next) {
        next({ docs: rows.map(function (r) { return { data: function () { return r; } }; }), metadata: { fromCache: false } });
        return function () {};
      }
    };
    return q;
  }
  return Promise.resolve({
    collection: function (nome) { return query(D[nome] || []); },
    doc: function () {
      return { onSnapshot: function (next) {
        next({ exists: !!D.painel, data: function () { return D.painel; } });
        return function () {};
      } };
    }
  });
} };
</script>
</head>
<body>
"""


def ler(colecao):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((DADOS / colecao).glob("*.json"))]


def main():
    dados = {
        "edicoes": sorted(ler("edicoes"), key=lambda d: d["data"], reverse=True),
        "agenda": sorted(ler("agenda"), key=lambda d: d["data"]),
        "painel": json.loads((DADOS / "painel" / "atual.json").read_text(encoding="utf-8")),
    }
    embutido = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    pagina = (RAIZ / "radar-reforma-tributaria.html").read_text(encoding="utf-8")
    saida = RAIZ / "docs" / "index.html"
    saida.parent.mkdir(exist_ok=True)
    (saida.parent / ".nojekyll").touch()
    saida.write_text(HEAD % (DESCRICAO, embutido) + pagina + "\n</body>\n</html>\n", encoding="utf-8")
    print(f"{saida}: {len(dados['edicoes'])} edição(ões), {len(dados['agenda'])} prazos, {saida.stat().st_size} bytes")


if __name__ == "__main__":
    main()
