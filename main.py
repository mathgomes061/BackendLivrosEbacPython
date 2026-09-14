# API de Livros

# GET, POST, PUT, DELETE

# POST - Adicionar novos livros (Create)
# GET - Buscar os dados dos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - Deletar informações dos livros (Delete)

# CRUD
# Create
# Read
# Update
# Delete

# Para acessar um ENDPOINT (local): fastapi dev caminho_do_arquivo
# Acessar os PATH's desse endpoint

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

my_books: dict = {}


class Book(BaseModel):
    book_title: str
    book_author: str
    book_release: int


@app.get("/books")
def get_books():
    if not my_books:
        return {"message:": "Não existe nenhum livro!"}

    return {"books": my_books}


# id do livro
# titulo do livro
# autor do livro
# ano de lançamento do livro

@app.post("/add")
def post_books(book_id: int, book: Book):
    if book_id in my_books:
        raise HTTPException(status_code=400, detail="Esse livro já existe!")
    else:
        my_books[book_id] = book.dict()
        return {"message": "O livro foi criado com sucesso!"}


@app.put("/update/{book_id}")
def put_books(book_id: int, book: Book):
    book_update = my_books.get(book_id)

    if book_update is None:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado"
        )

    my_books[book_id] = book.dict()

    return {
        "message": "As informações do livro foram atualizadas com sucesso!"
    }


@app.delete("/delete/{book_id}")
def delete_book(book_id: int):
    if book_id not in my_books:
        raise HTTPException(
            status_code=404, detail="Esse livro não foi encontrado!"
        )

    del my_books[book_id]

    return {"message": "Seu livro foi deletado com sucesso!"}
