# general imports to every file in this directory
from fastapi import APIRouter
from fastapi import status, APIRouter, Depends, Response, Request
from src.aspects.decorators import public
# imports to append APIRouters of dynamic way in the list routers
import importlib
from pathlib import Path
from typing import List

routers:List[APIRouter] = []

current_dir = Path(__file__).parent

for file in current_dir.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"src.routers.{file.stem}"

    try:
        module = importlib.import_module(module_name)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, APIRouter):
                routers.append(attr)
    except ImportError as e:
        print(f"Error while importing module {file.name}: {e}")
