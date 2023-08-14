from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.openapi.utils import get_openapi
from models import Curso, Aluno
from database import engine, Base, get_db
from repositories import CursoRepository, AlunoRepository
from schemas import CursoRequest, CursoResponse, AlunoRequest, AlunoResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def create(request: CursoRequest, db: Session = Depends(get_db)):
    curso = CursoRepository.save(db, Curso(**request.dict()))
    return CursoResponse.from_orm(curso)

@app.get("/api/cursos", response_model=list[CursoResponse])
def find_all(db: Session = Depends(get_db)):
    cursos = CursoRepository.find_all(db)
    return [CursoResponse.from_orm(curso) for curso in cursos]

@app.get("/api/cursos/{id_curso}")
def find_id(response: Response, db: Session = Depends(get_db), id_curso = int):
    curso = CursoRepository.find_by_id(db, id_curso)
    if curso:
        return CursoResponse.from_orm(curso)
    else:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message" : "Curso não encontrado"}
    
@app.delete("/api/cursos/{id_curso}")
def delete_id(response: Response, db: Session = Depends(get_db), id_curso = int):
    curso = CursoRepository.find_by_id(db, id_curso)
    if curso:
        CursoRepository.delete_by_id(db, id_curso)
        return {"message": f"Curso de ID {id_curso} deletado com sucesso"}
    else:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message" : "Curso não encontrado"}
    
@app.patch("/api/cursos/{id_curso}")
def update_id(response: Response, request: CursoRequest, db: Session = Depends(get_db),  id_curso = int):
    curso = CursoRepository.find_by_id(db, id_curso)
    if curso:
        curso.titulo = request.titulo
        curso.descricao = request.descricao
        curso.carga_horaria = request.carga_horaria
        curso.qtd_exercicios = request.qtd_exercicios
        Session.commit(db)
        return {"message": f"Curso de ID {id_curso} modificado com sucesso"}
    else:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message" : "Curso não encontrado"}
    
# -----------=-=-=-=-=-=-=-=-=-= ALUNOS -=-=--==-=-=-=-=-=-=-=

@app.post("/api/alunos", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def create(request: AlunoRequest, db: Session = Depends(get_db)):
    aluno = AlunoRepository.save(db, Aluno(**request.dict()))
    return AlunoResponse.from_orm(aluno)

@app.get("/api/alunos", response_model=list[AlunoResponse])
def find_all(db: Session = Depends(get_db)):
    alunos = AlunoRepository.find_all(db)
    return [AlunoResponse.from_orm(aluno) for aluno in alunos]

@app.get("/api/alunos/{id_aluno}")
def find_id(response: Response, db: Session = Depends(get_db), id_aluno = int):
    aluno = AlunoRepository.find_by_id(db, id_aluno)
    if aluno:
        return AlunoResponse.from_orm(aluno)
    else:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message" : "Aluno não encontrado"}
    
@app.delete("/api/alunos/{id_aluno}")
def delete_id(response: Response, db: Session = Depends(get_db), id_aluno = int):
    aluno = AlunoRepository.find_by_id(db, id_aluno)
    if aluno:
        curso = CursoRepository.find_by_id(db, aluno.id_curso)
        try:
            if curso.active:
                response.status_code=status.HTTP_409_CONFLICT
                return {"message" : "o curso do aluno está ativo, impossível remover"}
            else:
                AlunoRepository.delete_by_id(db, id_aluno)
                return {"message": f"Aluno de ID {id_aluno} deletado com sucesso"}
        except Exception:    
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"message" : "Aluno não encontrado"}
    
@app.patch("/api/alunos/{id_aluno}")
def update_id(response: Response,request: AlunoRequest, db: Session = Depends(get_db),  id_aluno = int):
    aluno = AlunoRepository.find_by_id(db, id_aluno)
    if aluno:
        aluno.nome = request.nome
        aluno.sobrenome = request.sobrenome
        aluno.cpf = request.cpf
        aluno.idade = request.idade
        aluno.email = request.email
        aluno.id_curso = request.id_curso
        Session.commit(db)
        return {"message": f"Dados do aluno de ID {id_aluno} modificado com sucesso"}
    else:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message" : "Aluno não encontrado"}

    
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Ambiente Virtual de Aprendizagem",
        version="1.0.0",
        summary="Alunos EAD",
        description="Sistema de Ambiente Virtual de Aprendizagem para auxiliar alunos 100% EAD",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
