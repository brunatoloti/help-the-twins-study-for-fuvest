# Ajudar minhas primas gêmeas a estudar para a Fuvest

## Descrição do projeto

Este projeto é uma plataforma web criada para ajudar minhas primas gêmas a estudar para a Fuvest. Elas farão o vestibular esse ano e decidi criar essa plataforma para facilitar os estudos delas.

## Funcionalidades

**Dashboard de acompanhamento de provas e questões feitas:** gráficos e cards que fornecem informações e métricas das provas e questões que elas fizerem na plataforma.

**Página de primeira fase:** página com o quiz de questões de primeira fase, com filtros de opções de questões. Ao finalizar a prova, a página retorna as questões feitas, mas com as resoluções, a alternativa correta e a indicação se o usuário acertou ou não a questão.

**Página de segunda fase:** página que, no futuro, terá o quiz de questões de segunda fase. (Em construção)

## Tecnologias utilizadas

* **Linguagem:** Python
* **Principais bibliotecas:** streamlit, pandas, openai, requests
* **"Banco de dados":** GoogleSheets

## Questões

No momento, só foram coletadas, mapeadas e processadas questões de primeira fase da Fuvest dos anos 2020 a 2025. Essas questões foram extraídas dos arquivos de PDF das provas pegas do site da Fuvest.
Após a coleta das questões, elas passaram por um script criado que se usa de um prompt e da API da OpenAI para tirar algumas informações delas, como:
 - enunciado
 - texto de apoio, se houver
 - alternativas

Além disso, foi possível também:
 - gerar uma resolução detalhada
 - identificar a alternativa correta
 - inferir a disciplina (Biologia, Inglês, Física, Matemática, Geografia, Português, Química, História, Artes, Educação Física, Filosofia, Sociologia, Literatura)
 - inferir o assunto dentro da disciplina (ex: Interseccionalidade, Revolução Industrial, etc)

As imagens das questões foram extraídas manualmente. Além disso, foram criados scripts de apoio, como o que compara o gabarito oficial com o gabarito gerado pela OpenAI, de forma que tenhamos alternativas corretas e resolução na plataforma de acordo com o que é de fato correto.

## Observações

- Neste repositório, não se encontram os scripts de processamento de questões mencionados na seção anterior.

- A página de quiz foi inspirada na criada em https://medium.com/@fesomade.alli/building-a-quiz-app-in-python-using-streamlit-d7c1aab4d690