# Cellular Automata — Propagação de Fake News

Simulação da propagação de notícias falsas em uma rede social utilizando **Autômatos Celulares**. Cada célula da grade representa um indivíduo, cujo comportamento evolui de acordo com seu estado, seus vizinhos e probabilidades configuráveis.

## Objetivo

O projeto busca representar, de forma simplificada, como uma fake news pode se espalhar por uma população e como a verificação da informação e a resistência dos indivíduos influenciam essa dinâmica.

Durante a execução, a simulação apresenta:

- a evolução espacial dos indivíduos em uma grade;
- uma animação da propagação da fake news;
- o histórico da quantidade de indivíduos em cada estado;
- o percentual da população alcançada ao final da simulação.

## Estados dos indivíduos

| Código | Estado | Descrição |
| --- | --- | --- |
| `0` | Não informado | Ainda não teve contato com a fake news |
| `1` | Informado | Recebeu a informação, mas não está compartilhando |
| `2` | Compartilhando | Está propagando a fake news para seus vizinhos |
| `3` | Verificando | Está verificando a veracidade da informação |
| `4` | Resistente | Não compartilha a fake news e permanece resistente |
| `5` | Corrigido | Foi corrigido após verificar a informação |

## Funcionamento do modelo

A população é organizada em uma grade bidimensional com bordas periódicas. Isso significa que as extremidades da grade são conectadas, formando uma superfície contínua.

A cada geração, todos os indivíduos são atualizados com base em regras probabilísticas:

1. indivíduos não informados podem ser expostos por vizinhos que estão compartilhando;
2. indivíduos expostos podem apenas ficar informados ou começar a compartilhar;
3. indivíduos informados ou compartilhadores podem verificar a notícia;
4. a verificação pode corrigir o indivíduo;
5. indivíduos corrigidos podem se tornar resistentes;
6. indivíduos resistentes permanecem nesse estado.

A probabilidade de exposição cresce conforme aumenta o número de vizinhos compartilhando, segundo a expressão:

```text
P(exposição) = 1 - (1 - p)ⁿ
```

em que `p` é a probabilidade básica de exposição e `n` é a quantidade de vizinhos compartilhando.

O modelo permite utilizar a vizinhança de **Moore**, com oito vizinhos, ou a vizinhança de **von Neumann**, com quatro vizinhos.

## Tecnologias utilizadas

- Python 3
- NumPy
- Matplotlib

## Instalação

Clone o repositório:

```bash
git clone https://github.com/abinoamenezes/CELLULAR-AUTOMATA.git
cd CELLULAR-AUTOMATA
```

Instale as dependências:

```bash
pip install numpy matplotlib
```

## Execução

Execute o arquivo principal:

```bash
python Simulacao.py
```

Uma janela será aberta com a animação da grade. Ao final, será exibido um gráfico com o histórico dos estados e um resumo dos resultados no terminal.

## Parâmetros da simulação

Os parâmetros podem ser alterados na função `main`, no arquivo `Simulacao.py`:

| Parâmetro | Descrição | Valor padrão |
| --- | --- | ---: |
| `tamanho_grade` | Largura e altura da população | `60` |
| `iteracoes` | Número de gerações | `150` |
| `prob_exposicao` | Probabilidade básica de exposição | `0.40` |
| `prob_compartilhar` | Probabilidade de compartilhar | `0.45` |
| `prob_verificar` | Probabilidade de verificar a notícia | `0.20` |
| `prob_correcao` | Probabilidade de correção após verificar | `0.80` |
| `prob_parar_compartilhar` | Probabilidade de parar espontaneamente | `0.08` |
| `prob_compartilhador_verificar` | Probabilidade de um compartilhador verificar | `0.10` |
| `fracao_resistentes` | Fração inicial de resistentes | `0.08` |
| `focos_iniciais` | Número inicial de compartilhadores | `8` |
| `vizinhanca` | Tipo de vizinhança utilizada | `moore` |
| `semente` | Semente para resultados reproduzíveis | `42` |

## Estrutura do projeto

```text
CELLULAR-AUTOMATA/
├── README.md
└── Simulacao.py
```

## Autor

Desenvolvido por [Abinoã Menezes](https://github.com/abinoamenezes).
