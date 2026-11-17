"""
Cria gabarito_final2_humano.csv a partir das notas do autor (avaliar_final2.xlsx, notas 0 a 2).
Nota 1 ou 2 = boa resposta; nota 2 = excelente. Em branco = não conhece (não entra).

Uso:
    python -I criar_gabarito_humano.py
"""
import re
import sys

import pandas as pd


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    av = pd.read_excel("avaliar_final2.xlsx", sheet_name="Avaliar")
    av.columns = ["numero", "pedido", "titulo", "ano", "generos", "nota"]
    av["numero"] = av.numero.astype(int)
    av["titulo"] = av.titulo.astype(str).str.strip()
    pedidos = pd.read_csv("pedidos_final2.csv", dtype=str, keep_default_na=False)
    pedidos["numero"] = pedidos.numero.astype(int)
    v2 = pd.read_csv("filmes_v2.csv", usecols=["titulo", "ano"])
    no_catalogo = set(zip(v2.titulo.str.strip(), pd.to_numeric(v2.ano, errors="coerce")))

    fora = av[[(t, a) not in no_catalogo for t, a in zip(av.titulo, pd.to_numeric(av.ano, errors="coerce"))]]
    print(f"Filmes avaliados: {len(av)} em {av.numero.nunique()} pedidos; com nota: {av.nota.notna().sum()}; "
          f"em branco (não conhece): {av.nota.isna().sum()}")
    print(f"Avaliados que não estão no filmes_v2.csv (título + ano): {len(fora)}"
          + ("" if fora.empty else " -> " + "; ".join(f"{r.titulo} ({r.ano})" for r in fora.itertuples())))

    linhas = []
    for p in pedidos.itertuples():
        g = av[av.numero == p.numero]
        boas = g[g.nota >= 1].sort_values("nota", ascending=False)
        exc = g[g.nota == 2]
        linhas.append({
            "numero": p.numero, "estilo": p.estilo, "pedido": p.pedido,
            "boas_respostas": "|".join(boas.titulo),
            "excelentes": "|".join(exc.titulo),
            "observacoes": "Gabarito humano: filmes que o autor avaliou com nota 1 ou 2 (só entre os sugeridos por A e T).",
            "n_avaliados": int(g.nota.notna().sum()), "n_sem_nota": int(g.nota.isna().sum()),
            "n_boas": len(boas), "n_excelentes": len(exc),
        })
    gab = pd.DataFrame(linhas)
    gab.to_csv("gabarito_final2_humano.csv", index=False, encoding="utf-8")
    print("\nPor pedido (boas = nota 1 ou 2; excelentes = nota 2):")
    print(f"{'nº':>4} {'estilo':<11}{'avaliados':>10}{'em branco':>10}{'boas':>6}{'excel.':>7}  pedido")
    for r in gab.itertuples():
        print(f"{r.numero:>4} {r.estilo:<11}{r.n_avaliados:>10}{r.n_sem_nota:>10}{r.n_boas:>6}{r.n_excelentes:>7}  {r.pedido[:52]}")
    print(f"Total: {gab.n_boas.sum()} boas respostas ({gab.n_excelentes.sum()} excelentes); "
          f"média de {gab.n_boas.mean():.1f} por pedido; pedidos sem nenhuma boa: {(gab.n_boas == 0).sum()}")

    # Conferência das contas do autor: em quantos pedidos A e T tiveram algum filme com nota 1 ou 2
    nota = {(r.numero, r.titulo): r.nota for r in av.itertuples()}
    for motor in ("A", "T"):
        res = pd.read_csv(f"resultados_{motor}_final2.csv", keep_default_na=False)
        ok = 0
        for r in res.itertuples():
            titulos = [re.sub(r" \(\d{4}\)$", "", str(getattr(r, f"top{i}"))) for i in range(1, 6) if getattr(r, f"top{i}", "")]
            if any((nota.get((r.numero, t)) or 0) >= 1 for t in titulos):
                ok += 1
        print(f"Conferência: {motor} teve algum filme com nota 1 ou 2 em {ok} de {len(res)} pedidos")
    print("\nSalvo em gabarito_final2_humano.csv")


if __name__ == "__main__":
    main()
