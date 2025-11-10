# general imports to every file in this directory
from fastapi import APIRouter
from fastapi import status, APIRouter, Depends, Response, Request
from src.aspects.decorators import public
# imports to append APIRouters of dynamic way in the list routers
import importlib
from pathlib import Path
from typing import Iterator, List

routers: List[APIRouter] = []
current_dir = Path(__file__).parent
initial_folder_name: str = "src.routers"

def add_to_routers(iterator_path: Iterator[Path], folder_name: str = ""):
    for file_or_folder in iterator_path:
        if file_or_folder.name == "__init__.py":
            continue
        
        if file_or_folder.is_dir():
            add_to_routers(file_or_folder.glob("*.py"), file_or_folder.name)
            continue
        
        module_name = f"{initial_folder_name}.{folder_name}.{file_or_folder.stem}" if folder_name else f"{initial_folder_name}.{file_or_folder.stem}"

        try:
            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, APIRouter):
                    routers.append(attr)
        except ImportError as e:
            print(f"Error while importing module {file_or_folder.name}: {e}")

def main():
    for folder in current_dir.glob("*"):
        if folder.is_dir():
            add_to_routers(folder.glob("*.py"), folder.name)
    
    add_to_routers(current_dir.glob("*.py"))
    
main()