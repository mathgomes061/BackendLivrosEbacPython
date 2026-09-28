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
import secrets

from sqlalchemy import (
    create_engine,
    select,
    func,
    UniqueConstraint
)
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Session,
    Mapped,
    mapped_column
)

DATABASE_URL = "sqlite:///./books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


class Base(DeclarativeBase):
    pass


class BookDB(Base):
    __tablename__ = "Books"

    __table_args__ = (
        UniqueConstraint(
            "book_title",
            "book_author",
            name="uq_book_title_author"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_title: Mapped[str] = mapped_column(index=True)
    book_author: Mapped[str] = mapped_column(index=True)
    book_release: Mapped[int] = mapped_column()


class Book(BaseModel):
    book_title: str
    book_author: str
    book_release: int


Base.metadata.create_all(bind=engine)


def get_session_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Page ou limit estão com valores inválidos"
        )

    stmt = (
        select(BookDB)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    books = db.scalars(stmt).all()

    if not books:
        return {"message": "Não existe nenhum livro!"}

    total_books = db.scalar(
        select(func.count()).select_from(BookDB)
    )

    return {
        "page": page,
        "limit": limit,
        "total": total_books,
        "books": [
            {
                "id": book.id,
                "book_title": book.book_title,
                "book_author": book.book_author,
                "book_release": book.book_release
            }
            for book in books
        ]
    }


@app.post("/add")
def post_books(
    book: Book,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    stmt = select(BookDB).where(
        BookDB.book_title == book.book_title,
        BookDB.book_author == book.book_author
    )

    db_book = db.scalars(stmt).first()

    if db_book:
        raise HTTPException(
            status_code=400,
            detail="Esse livro já existe!"
        )

    new_book = BookDB(
        book_title=book.book_title,
        book_author=book.book_author,
        book_release=book.book_release
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return {"message": "O livro foi criado com sucesso!"}


@app.put("/update/{book_id}")
def put_books(
    book_id: int,
    book: Book,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    stmt = select(BookDB).where(BookDB.id == book_id)

    db_book = db.scalars(stmt).first()

    if not db_book:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado"
        )

    stmt_duplicate = select(BookDB).where(
        BookDB.book_title == book.book_title,
        BookDB.book_author == book.book_author,
        BookDB.id != book_id
    )

    existing_book = db.scalars(stmt_duplicate).first()

    if existing_book:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro livro com esse título e autor!"
        )

    db_book.book_title = book.book_title
    db_book.book_author = book.book_author
    db_book.book_release = book.book_release
    db.commit()
    db.refresh(db_book)

    return {
        "message": "As informações do livro foram atualizadas com sucesso!"
    }


@app.delete("/delete/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    stmt = select(BookDB).where(BookDB.id == book_id)

    db_book = db.scalars(stmt).first()

    if not db_book:
        raise HTTPException(
            status_code=404,
            detail="Esse livro não foi encontrado"
        )

    db.delete(db_book)
    db.commit()

    return {"message": "Seu livro foi deletado com sucesso!"}
