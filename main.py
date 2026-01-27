import sys
import requests 
import time

from compiler.lexer.lexer import Lexer
from compiler.parser import Parser
from compiler.ast.node import Event, Definition
from compiler.codegen.json_generator import generate_event, generate_definition
from compiler.utils.colors import minecraft_color

from compiler.utils.continue_line import continue_handler

def compile_source(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer, source)
    starts = parser.parse() 

    result = []
    for st in starts:

        if isinstance(st, Event): start_json = generate_event(st)
        if isinstance(st, Definition): start_json = generate_definition(st)
        
        result.extend(continue_handler(start_json))
        
    for index, st in enumerate(result):
        st["position"] = index

    return {"handlers": result }


def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py <файл_скрипта>")
        sys.exit(1)

    script_path = sys.argv[1]

    with open(script_path, "r", encoding="utf-8") as f:
        source = f.read()

    start_compile = time.time()
    print(minecraft_color(f"\n&#8EFF9B   ===== Начинаем создавать код ====="))

    try:
        result_json = compile_source(source)
    except Exception as e:
        print("Ошибка компиляции:")
        print(e)
        sys.exit(1)

    
    print(minecraft_color(f"&#FFE5B2       ● Компиляция » &6{time.time()-start_compile:.3f} сек."))

    start_url = time.time()
    url = "https://m.justmc.ru/api/" + try_upload(result_json)

    print(minecraft_color(f"&#F9BCFF         ● Модуль » &6{time.time()-start_url:.3f} сек."))    
    print(minecraft_color(f"\n&#8EFF9B      ===== Ссылка на модуль ====="))
    print(minecraft_color(f"&e/module loadUrl {url}"))
    print(minecraft_color(f"&e/module loadUrl force {url}\n"))



def try_upload(code):
    response = requests.post('https://m.justmc.ru/api/upload', json=code)
    response = response.json()
    return response['id']



if __name__ == "__main__":
    main()