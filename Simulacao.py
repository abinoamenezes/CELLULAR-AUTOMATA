"""
Simulação da propagação de Fake News em Redes Sociais
usando Autômatos Celulares.

Estados das células:
0 - Não informado
1 - Informado, mas não compartilha
2 - Compartilhando fake news
3 - Verificando a informação
4 - Resistente à fake news
5 - Corrigido após verificação

Dependências:
    pip install numpy matplotlib

Execução:
    python simulacao_fake_news.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import BoundaryNorm


# Estados possíveis
NAO_INFORMADO = 0
INFORMADO = 1
COMPARTILHANDO = 2
VERIFICANDO = 3
RESISTENTE = 4
CORRIGIDO = 5

NOMES_ESTADOS = {
    NAO_INFORMADO: "Não informado",
    INFORMADO: "Informado",
    COMPARTILHANDO: "Compartilhando",
    VERIFICANDO: "Verificando",
    RESISTENTE: "Resistente",
    CORRIGIDO: "Corrigido",
}


@dataclass
class Parametros:
    """Parâmetros principais da simulação."""

    tamanho_grade: int = 60
    iteracoes: int = 150

    # Probabilidade de uma pessoa não informada receber a fake news
    prob_exposicao: float = 0.40

    # Probabilidade de uma pessoa exposta começar a compartilhar
    prob_compartilhar: float = 0.45

    # Probabilidade de uma pessoa informada verificar a notícia
    prob_verificar: float = 0.20

    # Probabilidade de a verificação corrigir a pessoa
    prob_correcao: float = 0.80

    # Probabilidade de um compartilhador parar espontaneamente
    prob_parar_compartilhar: float = 0.08

    # Probabilidade de um compartilhador iniciar verificação
    prob_compartilhador_verificar: float = 0.10

    # Fração inicial de pessoas resistentes
    fracao_resistentes: float = 0.08

    # Quantidade inicial de focos compartilhando fake news
    focos_iniciais: int = 8

    # Tipo de vizinhança: "moore" = 8 vizinhos; "von_neumann" = 4 vizinhos
    vizinhanca: str = "moore"

    # Semente para tornar os resultados reproduzíveis
    semente: int = 42


class SimulacaoFakeNews:
    def __init__(self, parametros: Parametros) -> None:
        self.p = parametros

        if self.p.vizinhanca not in {"moore", "von_neumann"}:
            raise ValueError(
                "A vizinhança deve ser 'moore' ou 'von_neumann'."
            )

        random.seed(self.p.semente)
        np.random.seed(self.p.semente)

        self.grade = np.full(
            (self.p.tamanho_grade, self.p.tamanho_grade),
            NAO_INFORMADO,
            dtype=np.int8,
        )

        self.historico = {
            estado: [] for estado in NOMES_ESTADOS
        }

        self._inicializar_populacao()
        self._registrar_estado()

    def _inicializar_populacao(self) -> None:
        """Cria resistentes e focos iniciais de compartilhamento."""

        total_celulas = self.p.tamanho_grade ** 2

        qtd_resistentes = int(total_celulas * self.p.fracao_resistentes)
        indices = np.arange(total_celulas)
        np.random.shuffle(indices)

        resistentes = indices[:qtd_resistentes]
        self.grade.flat[resistentes] = RESISTENTE

        candidatos = indices[qtd_resistentes:]
        focos = candidatos[: self.p.focos_iniciais]
        self.grade.flat[focos] = COMPARTILHANDO

    def _vizinhos(self, linha: int, coluna: int) -> list[tuple[int, int]]:
        """Retorna os vizinhos usando bordas periódicas."""

        if self.p.vizinhanca == "moore":
            deslocamentos = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1),
            ]
        else:
            deslocamentos = [
                (-1, 0),
                (0, -1), (0, 1),
                (1, 0),
            ]

        n = self.p.tamanho_grade

        return [
            ((linha + dl) % n, (coluna + dc) % n)
            for dl, dc in deslocamentos
        ]

    def _quantidade_vizinhos_compartilhando(
        self, linha: int, coluna: int
    ) -> int:
        return sum(
            self.grade[l, c] == COMPARTILHANDO
            for l, c in self._vizinhos(linha, coluna)
        )

    def _probabilidade_exposicao(
        self, quantidade_compartilhando: int
    ) -> float:
        """
        Quanto mais vizinhos compartilham, maior é a chance de exposição.

        Fórmula:
            1 - (1 - p)^n
        """
        if quantidade_compartilhando <= 0:
            return 0.0

        return 1 - (
            1 - self.p.prob_exposicao
        ) ** quantidade_compartilhando

    def passo(self) -> None:
        """Executa uma geração do autômato celular."""

        nova_grade = self.grade.copy()

        for linha in range(self.p.tamanho_grade):
            for coluna in range(self.p.tamanho_grade):
                estado = self.grade[linha, coluna]
                r = random.random()

                if estado == NAO_INFORMADO:
                    qtd_compartilhando = (
                        self._quantidade_vizinhos_compartilhando(
                            linha, coluna
                        )
                    )

                    prob_receber = self._probabilidade_exposicao(
                        qtd_compartilhando
                    )

                    if random.random() < prob_receber:
                        if random.random() < self.p.prob_compartilhar:
                            nova_grade[linha, coluna] = COMPARTILHANDO
                        else:
                            nova_grade[linha, coluna] = INFORMADO

                elif estado == INFORMADO:
                    if r < self.p.prob_verificar:
                        nova_grade[linha, coluna] = VERIFICANDO
                    elif r < (
                        self.p.prob_verificar
                        + self.p.prob_compartilhar * 0.25
                    ):
                        nova_grade[linha, coluna] = COMPARTILHANDO

                elif estado == COMPARTILHANDO:
                    if r < self.p.prob_compartilhador_verificar:
                        nova_grade[linha, coluna] = VERIFICANDO
                    elif r < (
                        self.p.prob_compartilhador_verificar
                        + self.p.prob_parar_compartilhar
                    ):
                        nova_grade[linha, coluna] = INFORMADO

                elif estado == VERIFICANDO:
                    if r < self.p.prob_correcao:
                        nova_grade[linha, coluna] = CORRIGIDO
                    else:
                        nova_grade[linha, coluna] = INFORMADO

                elif estado == CORRIGIDO:
                    # Pessoas corrigidas tornam-se resistentes após aprenderem
                    if r < 0.15:
                        nova_grade[linha, coluna] = RESISTENTE

                elif estado == RESISTENTE:
                    # Estado absorvente: permanece resistente
                    nova_grade[linha, coluna] = RESISTENTE

        self.grade = nova_grade
        self._registrar_estado()

    def _registrar_estado(self) -> None:
        for estado in NOMES_ESTADOS:
            self.historico[estado].append(
                int(np.sum(self.grade == estado))
            )

    def executar(self) -> None:
        for _ in range(self.p.iteracoes):
            self.passo()

    def percentual_alcancado(self) -> float:
        """
        Percentual da população que teve contato com a fake news,
        excluindo resistentes que nunca foram expostos.
        """
        total = self.p.tamanho_grade ** 2
        nao_alcancados = int(np.sum(self.grade == NAO_INFORMADO))
        return 100 * (total - nao_alcancados) / total

    def exibir_animacao(self) -> None:
        """Executa e exibe a simulação animada."""

        cmap = plt.get_cmap("tab10", len(NOMES_ESTADOS))
        norm = BoundaryNorm(
            np.arange(-0.5, len(NOMES_ESTADOS) + 0.5, 1),
            cmap.N,
        )

        fig, ax = plt.subplots(figsize=(8, 7))
        imagem = ax.imshow(
            self.grade,
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
        )

        ax.set_title("Propagação de Fake News — geração 0")
        ax.set_xlabel("Indivíduos na rede")
        ax.set_ylabel("Indivíduos na rede")

        barra = fig.colorbar(
            imagem,
            ax=ax,
            ticks=list(NOMES_ESTADOS.keys()),
        )
        barra.ax.set_yticklabels(list(NOMES_ESTADOS.values()))

        texto = ax.text(
            0.02,
            1.02,
            "",
            transform=ax.transAxes,
        )

        def atualizar(frame: int):
            self.passo()
            imagem.set_data(self.grade)

            compartilhando = int(
                np.sum(self.grade == COMPARTILHANDO)
            )
            corrigidos = int(
                np.sum(self.grade == CORRIGIDO)
            )
            resistentes = int(
                np.sum(self.grade == RESISTENTE)
            )

            ax.set_title(
                f"Propagação de Fake News — geração {frame + 1}"
            )
            texto.set_text(
                f"Compartilhando: {compartilhando} | "
                f"Corrigidos: {corrigidos} | "
                f"Resistentes: {resistentes}"
            )

            return imagem, texto

        self.animacao = FuncAnimation(
            fig,
            atualizar,
            frames=self.p.iteracoes,
            interval=120,
            repeat=False,
        )

        plt.tight_layout()
        plt.show()

        self.exibir_grafico_historico()
        self.exibir_resumo()

    def exibir_grafico_historico(self) -> None:
        """Exibe a evolução da quantidade de indivíduos por estado."""

        plt.figure(figsize=(10, 6))

        for estado, nome in NOMES_ESTADOS.items():
            plt.plot(self.historico[estado], label=nome)

        plt.title("Evolução dos estados ao longo da simulação")
        plt.xlabel("Geração")
        plt.ylabel("Quantidade de indivíduos")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def exibir_resumo(self) -> None:
        print("\n=== RESULTADO FINAL ===")
        print(
            f"Percentual da população alcançada: "
            f"{self.percentual_alcancado():.2f}%"
        )

        for estado, nome in NOMES_ESTADOS.items():
            quantidade = int(np.sum(self.grade == estado))
            print(f"{nome}: {quantidade}")


def main() -> None:
    parametros = Parametros(
        tamanho_grade=60,
        iteracoes=150,
        prob_exposicao=0.40,
        prob_compartilhar=0.45,
        prob_verificar=0.20,
        prob_correcao=0.80,
        prob_parar_compartilhar=0.08,
        prob_compartilhador_verificar=0.10,
        fracao_resistentes=0.08,
        focos_iniciais=8,
        vizinhanca="moore",
        semente=42,
    )

    simulacao = SimulacaoFakeNews(parametros)
    simulacao.exibir_animacao()


if __name__ == "__main__":
    main()