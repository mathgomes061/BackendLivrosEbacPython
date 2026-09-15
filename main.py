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

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os

app = FastAPI(
    title="API de livros",
    description="API para gerenciar catálogo de livros",
    version="1.0.0",
    contact={
        "name": "Matheus Gomes",
        "email": "mathgomes061@gmail.com"
    }
)

MY_USER = "admin"
MY_PASSWORD = 'admin'

security = HTTPBasic()

my_books: dict = {}


class Book(BaseModel):
    book_title: str
    book_author: str
    book_release: int


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(
        credentials.username, MY_USER
    )
    is_password_correct = secrets.compare_digest(
        credentials.password, MY_PASSWORD
    )

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.get("/books")
def get_books(
    page: int = 1,
    limit: int = 10,
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Page ou limit estão com valores inválidos"
        )

    if not my_books:
        return {"message": "Não existe nenhum livro!"}

    sorted_books = sorted(my_books.items(), key=lambda x: x[0])

    start = (page - 1) * limit
    end = start + limit

    paged_books = [
        {
            "id": book_id,
            "book_title": book_data["book_title"],
            "book_author": book_data["book_author"],
            "book_release": book_data["book_release"]
        }
        for book_id, book_data in sorted_books[start:end]
    ]

    return {
        "page": page,
        "limit": limit,
        "total": len(my_books),
        "books": paged_books
    }


@app.post("/add")
def post_books(
    book_id: int,
    book: Book,
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if book_id in my_books:
        raise HTTPException(status_code=400, detail="Esse livro já existe!")
    else:
        my_books[book_id] = book.model_dump()
        return {"message": "O livro foi criado com sucesso!"}


@app.put("/update/{book_id}")
def put_books(
    book_id: int,
    book: Book,
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    check_book = my_books.get(book_id)

    if check_book is None:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado"
        )

    my_books[book_id] = book.model_dump()

    return {
        "message": "As informações do livro foram atualizadas com sucesso!"
    }


@app.delete("/delete/{book_id}")
def delete_book(
    book_id: int,
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if book_id not in my_books:
        raise HTTPException(
            status_code=404, detail="Esse livro não foi encontrado!"
        )

    del my_books[book_id]

    return {"message": "Seu livro foi deletado com sucesso!"}
