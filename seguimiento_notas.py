#!/usr/bin/env python3
"""Programa simple para seguimiento de notas y evaluaciones en 5 skills."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import Dict, List

ARCHIVO_DATOS = Path("datos_alumnos.json")
SKILLS = ["Listening", "Speaking", "Reading", "Writing", "Use of English"]


@dataclass
class Evaluacion:
    fecha: str
    skill: str
    nota: float
    observacion: str = ""


@dataclass
class Alumno:
    nombre: str
    curso: str
    evaluaciones: List[Evaluacion]


def cargar_datos() -> Dict[str, Alumno]:
    if not ARCHIVO_DATOS.exists():
        return {}

    with ARCHIVO_DATOS.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    alumnos: Dict[str, Alumno] = {}
    for key, value in raw.items():
        evaluaciones = [Evaluacion(**ev) for ev in value.get("evaluaciones", [])]
        alumnos[key] = Alumno(
            nombre=value["nombre"],
            curso=value["curso"],
            evaluaciones=evaluaciones,
        )
    return alumnos


def guardar_datos(alumnos: Dict[str, Alumno]) -> None:
    serializable = {}
    for key, alumno in alumnos.items():
        serializable[key] = {
            "nombre": alumno.nombre,
            "curso": alumno.curso,
            "evaluaciones": [asdict(ev) for ev in alumno.evaluaciones],
        }

    with ARCHIVO_DATOS.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)


def crear_id(nombre: str, curso: str) -> str:
    return f"{nombre.strip().lower()}::{curso.strip().lower()}"


def registrar_alumno(alumnos: Dict[str, Alumno]) -> None:
    print("\n== Registrar alumno ==")
    nombre = input("Nombre del alumno: ").strip()
    curso = input("Curso (ej. 5A): ").strip()

    if not nombre or not curso:
        print("Nombre y curso son obligatorios.")
        return

    alumno_id = crear_id(nombre, curso)
    if alumno_id in alumnos:
        print("Ese alumno ya existe.")
        return

    alumnos[alumno_id] = Alumno(nombre=nombre, curso=curso, evaluaciones=[])
    guardar_datos(alumnos)
    print("Alumno registrado correctamente.")


def seleccionar_alumno(alumnos: Dict[str, Alumno]) -> str | None:
    if not alumnos:
        print("No hay alumnos registrados todavía.")
        return None

    print("\nAlumnos disponibles:")
    ids = list(alumnos.keys())
    for i, alumno_id in enumerate(ids, start=1):
        alumno = alumnos[alumno_id]
        print(f"{i}. {alumno.nombre} ({alumno.curso})")

    opcion = input("Selecciona número de alumno: ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= len(ids)):
        print("Selección inválida.")
        return None

    return ids[int(opcion) - 1]


def registrar_evaluacion(alumnos: Dict[str, Alumno]) -> None:
    print("\n== Registrar evaluación ==")
    alumno_id = seleccionar_alumno(alumnos)
    if not alumno_id:
        return

    print("\nSkills disponibles:")
    for i, skill in enumerate(SKILLS, start=1):
        print(f"{i}. {skill}")

    opcion_skill = input("Selecciona skill: ").strip()
    if not opcion_skill.isdigit() or not (1 <= int(opcion_skill) <= len(SKILLS)):
        print("Skill inválida.")
        return

    skill = SKILLS[int(opcion_skill) - 1]
    fecha = input("Fecha (YYYY-MM-DD): ").strip()

    try:
        nota = float(input("Nota (0 a 10): ").strip())
    except ValueError:
        print("La nota debe ser un número.")
        return

    if nota < 0 or nota > 10:
        print("La nota debe estar entre 0 y 10.")
        return

    observacion = input("Observación (opcional): ").strip()

    alumnos[alumno_id].evaluaciones.append(
        Evaluacion(fecha=fecha, skill=skill, nota=nota, observacion=observacion)
    )
    guardar_datos(alumnos)
    print("Evaluación registrada correctamente.")


def promedios_por_skill(evaluaciones: List[Evaluacion]) -> Dict[str, float]:
    resumen: Dict[str, List[float]] = {skill: [] for skill in SKILLS}
    for ev in evaluaciones:
        resumen.setdefault(ev.skill, []).append(ev.nota)

    return {
        skill: round(mean(notas), 2) if notas else 0.0
        for skill, notas in resumen.items()
    }


def reporte_alumno(alumnos: Dict[str, Alumno]) -> None:
    print("\n== Reporte por alumno ==")
    alumno_id = seleccionar_alumno(alumnos)
    if not alumno_id:
        return

    alumno = alumnos[alumno_id]
    print(f"\nReporte de {alumno.nombre} - {alumno.curso}")

    if not alumno.evaluaciones:
        print("Sin evaluaciones registradas.")
        return

    for ev in alumno.evaluaciones:
        obs = f" | Obs: {ev.observacion}" if ev.observacion else ""
        print(f"- {ev.fecha} | {ev.skill}: {ev.nota}{obs}")

    promedios = promedios_por_skill(alumno.evaluaciones)
    print("\nPromedios por skill:")
    for skill in SKILLS:
        print(f"  {skill}: {promedios[skill]}")

    promedio_global = round(mean([ev.nota for ev in alumno.evaluaciones]), 2)
    print(f"Promedio global: {promedio_global}")


def reporte_curso(alumnos: Dict[str, Alumno]) -> None:
    print("\n== Reporte por curso ==")
    curso = input("Curso a consultar (ej. 5A): ").strip().lower()

    alumnos_curso = [a for a in alumnos.values() if a.curso.lower() == curso]
    if not alumnos_curso:
        print("No se encontraron alumnos para ese curso.")
        return

    print(f"\nCurso {curso.upper()} - {len(alumnos_curso)} alumno(s)")
    for alumno in alumnos_curso:
        if alumno.evaluaciones:
            prom = round(mean([ev.nota for ev in alumno.evaluaciones]), 2)
        else:
            prom = 0.0
        print(f"- {alumno.nombre}: promedio {prom}")


def menu() -> None:
    alumnos = cargar_datos()

    while True:
        print(
            """
===== SEGUIMIENTO DE NOTAS (INGLÉS PRIMARIA) =====
1. Registrar alumno
2. Registrar evaluación
3. Ver reporte de un alumno
4. Ver reporte por curso
5. Salir
"""
        )

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            registrar_alumno(alumnos)
        elif opcion == "2":
            registrar_evaluacion(alumnos)
        elif opcion == "3":
            reporte_alumno(alumnos)
        elif opcion == "4":
            reporte_curso(alumnos)
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()
