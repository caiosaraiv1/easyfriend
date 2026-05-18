for Kaique

man o banco e back estão ligadas 

Como verifiquei depois de subir os docker e povoar o banco de dados, localhost:8000/docs no navegador, vai ver post matches, get matches



povoar banco

docker-compose exec db psql -U easyfriend -d easyfriend_db -f /docker-entrypoint-initdb.d/02_seed.sql



No post matches 

1.aperta no botão Try it out

2.entrada
{
  "usuario_a_id": 1,
  "usuario_b_id": 2,
  "criterio": "idioma"
}

3. aperta no botão execute
saida exemplo:
{
  "match_id": 4,
  "usuario_a": "Carlos Silva",
  "usuario_b": "Ana Souza",
  "criterio": "idioma"
}

No Get matches 
mesma coisa

entrada: já existe padrão
saida exemplo:
[
  {
    "id": 1,
    "nome": "Carlos Silva",
    "idioma": "pt",
    "pais_origem": "Brasil"
  },
  {
    "id": 2,
    "nome": "Ana Souza",
    "idioma": "pt",
    "pais_origem": "Brasil"
  },
  {
    "id": 9,
    "nome": "Diogo Ferreira",
    "idioma": "pt",
    "pais_origem": "Angola"
  }
]