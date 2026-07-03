"""
Análisis y recomendación de inversión en Plazos Fijos
Banco Provincia, Banco Nación y Banco Hipotecario.

Trabajo Práctico - Parcial 2

Este script aplica el ciclo de vida del dato (Captura -> Pre-procesamiento ->
Análisis -> Visualización) para comparar modalidades de inversión de un
capital de $850.000 y recomendar la opción más rentable.
"""

from dataclasses import dataclass, field

CAPITAL_INICIAL = 850000.0
ANIOS_HISTORICOS = 3
BANCOS = ["Banco Provincia", "Banco Nación", "Banco Hipotecario"]


# ---------------------------------------------------------------------------
# Fase 1: Captura de Datos
# Se solicitan al usuario las tasas anuales históricas de cada banco.
# Esta es la entrada cruda del sistema: sin captura confiable, ninguna etapa
# posterior (descriptiva, predictiva, prescriptiva) tiene valor.
# ---------------------------------------------------------------------------

def leer_tasa(banco: str, anio: int) -> float:
    """Pide una tasa anual (%) con validación estricta de formato y rango.

    La validación es la herramienta concreta contra la problemática de
    "Calidad de los Datos": un dato incompleto, mal tipeado o fuera de rango
    razonable contamina el promedio y, en cascada, toda recomendación
    prescriptiva basada en él.
    """
    while True:
        entrada = input(
            f"  Tasa anual {banco} - Año {anio} (en %, ej: 110.5): "
        ).strip().replace(",", ".")
        try:
            tasa = float(entrada)
        except ValueError:
            print("    -> Error: ingresá un número válido (use punto decimal).")
            continue

        if tasa < 0:
            print("    -> Error: la tasa no puede ser negativa.")
            continue
        if tasa > 500:
            print("    -> Advertencia: tasa fuera de rango histórico plausible (>500%).")
            continue

        return tasa


def capturar_tasas_historicas() -> dict:
    """Recorre los bancos y años pidiendo las tasas anuales históricas."""
    print("\n=== Fase 1: Captura de Datos ===")
    print(f"Ingrese las tasas anuales de los últimos {ANIOS_HISTORICOS} años.\n")

    historico = {}
    for banco in BANCOS:
        print(f"-- {banco} --")
        tasas = [leer_tasa(banco, anio) for anio in range(1, ANIOS_HISTORICOS + 1)]
        historico[banco] = tasas
    return historico


# ---------------------------------------------------------------------------
# Fase 2: Pre-procesamiento
# Limpieza y validación de formatos ya ocurrió en la captura (leer_tasa).
# Acá se normalizan los datos a una estructura analizable.
# ---------------------------------------------------------------------------

def preprocesar(historico: dict) -> dict:
    """Normaliza tasas de porcentaje a proporción decimal (ej: 110% -> 1.10)."""
    print("\n=== Fase 2: Pre-procesamiento ===")
    normalizado = {
        banco: [t / 100 for t in tasas] for banco, tasas in historico.items()
    }
    print("Datos normalizados a formato decimal para cálculo financiero.")
    return normalizado


# ---------------------------------------------------------------------------
# Fase 3: Análisis
# 3.a) Analítica Descriptiva: ¿Qué pasó? -> promedio de tasas históricas.
# 3.b) Analítica Predictiva/Prescriptiva: ¿Qué pasará? / ¿Qué conviene? ->
#      simulación de las 3 modalidades de inversión y comparación.
# ---------------------------------------------------------------------------

def calcular_promedio(tasas: list) -> float:
    """Analítica Descriptiva: resume el comportamiento histórico (BI)."""
    return sum(tasas) / len(tasas)


@dataclass
class ResultadoBanco:
    banco: str
    tasa_promedio: float
    rendimiento_anual: float = 0.0
    rendimiento_trimestral: float = 0.0
    rendimiento_mensual: float = 0.0


def simular_anual(capital: float, tasa_anual: float) -> float:
    """Modalidad anual: interés simple sobre la tasa anual promedio.

    Monto final = capital * (1 + tasa_anual)
    """
    return capital * (1 + tasa_anual)


def simular_compuesto(capital: float, tasa_anual: float, periodos: int) -> float:
    """Modalidades trimestral/mensual: interés compuesto con reinversión.

    Se reparte la tasa anual proporcionalmente entre los períodos y se
    reinvierte el capital + interés ganado al cierre de cada período.

    Monto final = capital * (1 + tasa_anual / periodos) ** periodos
    """
    tasa_periodo = tasa_anual / periodos
    return capital * (1 + tasa_periodo) ** periodos


def analizar_banco(banco: str, tasas: list, capital: float) -> ResultadoBanco:
    promedio = calcular_promedio(tasas)
    resultado = ResultadoBanco(banco=banco, tasa_promedio=promedio)
    resultado.rendimiento_anual = simular_anual(capital, promedio)
    resultado.rendimiento_trimestral = simular_compuesto(capital, promedio, 4)
    resultado.rendimiento_mensual = simular_compuesto(capital, promedio, 12)
    return resultado


def analizar(historico_normalizado: dict, capital: float) -> list:
    print("\n=== Fase 3: Análisis (Descriptivo, Predictivo y Prescriptivo) ===")
    resultados = [
        analizar_banco(banco, tasas, capital)
        for banco, tasas in historico_normalizado.items()
    ]
    return resultados


def determinar_mejor_opcion(resultados: list):
    """Analítica Prescriptiva: ¿qué conviene hacer? Elige la mejor combinación
    banco/modalidad comparando los tres rendimientos simulados de cada banco."""
    mejor = None
    for r in resultados:
        opciones = [
            (r.banco, "Anual", r.rendimiento_anual),
            (r.banco, "Trimestral", r.rendimiento_trimestral),
            (r.banco, "Mensual", r.rendimiento_mensual),
        ]
        for banco, modalidad, monto in opciones:
            if mejor is None or monto > mejor[2]:
                mejor = (banco, modalidad, monto)
    return mejor


# ---------------------------------------------------------------------------
# Fase 4: Visualización
# Reporte final en consola: comparación tipo BI (tasas históricas) y
# resultado del modelado predictivo/prescriptivo (mejor decisión).
# ---------------------------------------------------------------------------

def mostrar_resultados(resultados: list, mejor: tuple, capital: float):
    print("\n=== Fase 4: Visualización de Resultados ===")
    print(f"Capital invertido: ${capital:,.2f}\n")

    for r in resultados:
        print(f"-- {r.banco} --")
        print(f"  Tasa anual promedio (Descriptiva): {r.tasa_promedio * 100:.2f}%")
        print(f"  Modalidad Anual       -> ${r.rendimiento_anual:,.2f}")
        print(f"  Modalidad Trimestral  -> ${r.rendimiento_trimestral:,.2f}")
        print(f"  Modalidad Mensual     -> ${r.rendimiento_mensual:,.2f}")
        print()

    banco, modalidad, monto = mejor
    ganancia = monto - capital
    print("=== Recomendación (Analítica Prescriptiva) ===")
    print(f"Opción más rentable: {banco} - Modalidad {modalidad}")
    print(f"Monto final estimado: ${monto:,.2f}")
    print(f"Ganancia estimada: ${ganancia:,.2f}")


def main():
    print("ANÁLISIS DE INVERSIÓN EN PLAZOS FIJOS")
    print("=" * 45)

    historico = capturar_tasas_historicas()
    historico_normalizado = preprocesar(historico)
    resultados = analizar(historico_normalizado, CAPITAL_INICIAL)
    mejor = determinar_mejor_opcion(resultados)
    mostrar_resultados(resultados, mejor, CAPITAL_INICIAL)


if __name__ == "__main__":
    main()
