#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fachada de compatibilidad de la ley de nombres canónicos.

La autoridad vive en ``lib/makeselfEngine/naming.py``. Este módulo se conserva
para no romper a los módulos históricos que importan ``ProjectNameFormatter``
desde aquí; simplemente reexporta la clase.
"""
from __future__ import annotations

from lib.makeselfEngine.naming import ProjectNameFormatter

__all__ = ["ProjectNameFormatter"]
