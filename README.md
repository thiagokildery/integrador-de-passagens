# Integração de Passagens Rodoviárias

Plataforma centralizada que integra payloads JSON de diferentes empresas de ônibus, cada uma com formato próprio, em um modelo padronizado único (`Passagem`).

---

## Decisões de Arquitetura

### Strategy Pattern + Registry Pattern

Cada empresa tem seu próprio conversor (Strategy) que herda de `BasePassagemConverter`. O `ConverterRegistry` guarda esses conversores e entrega o certo para cada empresa. Assim, adicionar uma empresa nova é só criar uma classe — sem if/else e sem mexer em código existente.

### Auto-Descoberta (Open/Closed Principle)

O sistema escaneia automaticamente a pasta `converters/` em busca de classes e a pasta `data/` em busca de JSONs. Para adicionar uma empresa, basta criar dois arquivos — nenhuma linha de código existente precisa ser alterada.

### SOLID

- **SRP**: Cada classe faz uma coisa só — converter, orquestrar, exportar, representar dados.
- **OCP**: O sistema está aberto para extensão (nova empresa) e fechado para modificação (sem editar código existente).
- **DIP**: O integrador depende da abstração (`BasePassagemConverter`), não de conversores concretos.

### Dados separados do código

Os JSONs de entrada ficam na pasta `data/`, separados do Python. Dados podem ser editados sem risco de quebrar a lógica.

### Padronização centralizada

`date_utils.py` converte 9 formatos de data diferentes para `datetime`. `money_utils.py` converte float, dict com moeda e centavos para BRL. Os conversores não repetem lógica de conversão — chamam as funções de utilidade.

### Erros sem interromper

O integrador captura erros por payload e continua processando os demais. Os erros só são exportados para `payloads_invalidos.json` se existirem.

---

## Como Adicionar uma Empresa

1. Criar `converters/empresa_x.py` com a classe do conversor
2. Criar `data/empresa_x.json` com os payloads

## Como Executar

```bash
python app.py                    # Executa a aplicação
python -m pytest tests/ -v       # Rodar os testes
```
