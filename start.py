#!/usr/bin/env python3
"""
Script para inicializar o projeto chatbot-llm
"""
import os
import sys
from pathlib import Path

def check_requirements():
    """Verifica se os requisitos básicos estão instalados"""
    try:
        import fastapi
        import langchain
        import openai
        print("Dependencias principais encontradas")
        return True
    except ImportError as e:
        print(f"Dependencia faltando: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    dirs = ['dados', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Diretorio {dir_name}/ criado")

def check_env_file():
    """Verifica se arquivo .env existe"""
    if not Path('.env').exists():
        print("Arquivo .env nao encontrado")
        print("Copie .env.example para .env e configure suas chaves:")
        print("   cp .env.example .env")
        return False
    print("Arquivo .env encontrado")
    return True

def main():
    print("Iniciando configuracao do Chatbot-LLM\n")
    
    # Verificações
    if not check_requirements():
        print("\nInstale as dependencias:")
        print("   pip install -r requirements.txt")
        return
    
    create_directories()
    
    if not check_env_file():
        return
    
    print("\nProjeto configurado com sucesso!")
    print("\nPara iniciar o servidor:")
    print("   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI docs disponivel em: http://localhost:8000/docs")

if __name__ == "__main__":
    main()