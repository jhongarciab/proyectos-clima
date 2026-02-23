# Capa Silver — Decisiones de limpieza de datos

## Contexto del proyecto

Análisis climático para **Pereira, Risaralda, Colombia** usando datos diarios de dos fuentes:
IDEAM (estaciones observacionales) y NASA POWER (datos grillados de reanálisis). El objetivo
es producir una serie de tiempo diaria limpia y lista para el análisis de temperatura,
precipitación y humedad, cubriendo un período consistente de 10 años.

---

## 1. Período de análisis: 2015–2025

Ambas fuentes (IDEAM y NASA POWER) fueron descargadas con datos diarios desde el 1 de enero de 2015 hasta el 31 de diciembre de 2025, cubriendo 11 años completos.

---

## 2. Selección de estaciones

De las diez entradas de estación encontradas en las tablas bronze, solo **tres estaciones**
se incluyen en la capa silver:

| Código     | Nombre                | Justificación                                              |
|------------|-----------------------|------------------------------------------------------------|
| 0026125710 | Aeropuerto Matecaña   | Mejor referencia urbana de largo plazo; ubicación aeropuerto |
| 0026125508 | LaCatalina            | Buena cobertura; temperatura coherente con Pereira urbana  |
| 0026135501 | El Pilamo             | Cobertura adecuada; valores climáticamente consistentes    |

### Estaciones excluidas y razones

**LA LAGUNA DEL OTUN (0026135330)** — Temperatura media de ~6.75 °C. Esta estación está
ubicada en el páramo del Otún, por encima de los 3.500 m.s.n.m., una zona climática
completamente diferente a la de Pereira urbana (~1.400 m.s.n.m.). Incluirla en el promedio
de estaciones introduciría un sesgo frío sistemático de aproximadamente 15 °C respecto
al clima de la ciudad.

**PNN QUIMBAYA (0026135300)** — Temperatura media de ~17 °C, lo que también indica una
ubicación más alta y fría que Pereira urbana. Adicionalmente, esta estación presenta 26
registros de temperatura igual a cero y, en su entrada de 2025, una humedad relativa media
de 2.93 % con valores mínimos de 0.05 %, lo cual es físicamente imposible para cualquier
punto de Colombia. Estas anomalías indican errores sistemáticos del sensor o del reporte
que comprometen la confiabilidad de la estación.

**CARTAGO (0026127040), PUERTO CALDAS (2613700156), EL RETEN (0026137220)** — Estas
estaciones están ubicadas en otro municipio o departamento, tienen cobertura temporal muy
limitada (menos de ~100 registros o cubriendo un solo año), o ambas cosas. No aportan
datos relevantes para un análisis específico de Pereira.

### Manejo de estaciones renombradas

Cuatro códigos de estación aparecen bajo dos nombres distintos en la API, con rangos de
fechas no solapados (confirmado por la consulta de fechas duplicadas: cero solapamientos
en ninguna variable). Estas entradas representan la misma estación física, reconectada o
reetiquetada en el sistema de IDEAM. En la capa silver se tratan como una sola estación
continua, unidas por `codigoestacion`:

- `0026125710`: "APTO MATECAÑA TX GPS/GOES" (2015–2022) + "AEROPUERTO MATECANA" (2023–2025)
- `0026125508`: "LACATALINA - AUT" (2016–2023) + "LACATALINA" (pocos días en sep 2023)
- `0026135501`: "EL PILAMO - AUT" (2016–2023) + "EL PILAMO" (pocos días en sep 2023)
- `0026135330`: excluida por otras razones, pero presenta el mismo patrón

---

## 3. Valores centinela: ceros en temperatura y humedad

### Ceros en temperatura
Los cuatro registros de temperatura igual a cero en `APTO MATECAÑA TX GPS/GOES` se tratan
como `NULL`. Una temperatura diaria promedio de 0 °C es físicamente inconsistente con el
clima de Pereira (el promedio general de la estación es ~22 °C). Se trata de errores de
sensor o de transmisión, no de observaciones reales. Las demás estaciones seleccionadas
no presentan ningún cero.

### Ceros en humedad
`APTO MATECAÑA TX GPS/GOES` tiene 4 registros con humedad igual a cero. Una humedad
relativa de 0 % es físicamente imposible en una ciudad andina tropical. Todos los registros
con humedad igual a cero se convierten a `NULL` antes de calcular el promedio.

---

## 4. Valor centinela en precipitación: 288 mm en Matecaña (2022)

La estación `APTO MATECAÑA TX GPS/GOES` contiene múltiples registros con exactamente
288.0 mm en febrero y marzo de 2022 (al menos 9 ocurrencias del mismo valor redondo).
Este valor se identifica como un **desbordamiento del sensor o centinela de error**,
no como lluvia real, por las siguientes razones:

- El valor 288 es sospechosamente redondo y se repite de forma idéntica en días no consecutivos.
- Supera ampliamente el p99 de todas las demás estaciones seleccionadas (LaCatalina: 46 mm,
  El Pilamo: 51 mm).
- Ninguna otra estación registró precipitación extraordinaria en esas mismas fechas.
- La mediana diaria de precipitación de la misma estación para todo el período es de 1.24 mm,
  lo que hace de 288 mm una desviación de más de 230 veces sobre la mediana.

Todos los registros donde `codigoestacion = '0026125710'` y `valor_diario = 288` en la
tabla de precipitación se convierten a `NULL` en la capa silver.

---

## 5. Promedio entre estaciones

Los valores diarios se promedian entre las estaciones seleccionadas para producir un
único valor diario representativo de Pereira. Esta consolidación es espacial: reduce
el ruido de mediciones puntuales y produce una serie más representativa de la ciudad.
El promedio se calcula como `AVG(valor_diario)`, que ignora automáticamente los valores
`NULL`. Los días faltantes que resulten de este proceso se identifican y cuantifican
según lo indicado en la sección 6, pero no se imputan.

---

## 6. Cuantificación de datos faltantes

El enunciado del Mini Proyecto 1 establece explícitamente que los datos faltantes deben
identificarse y cuantificarse, y que un dato faltante es diferente de un dato de valor
cero. En consecuencia, la capa silver no imputa ningún valor faltante. Para cada variable
y cada estación se registra el conteo y el porcentaje de días sin dato respecto al
calendario completo 2015–2025 (4.018 días). Esta métrica se lleva hasta la serie agregada
final para que el análisis posterior pueda identificar períodos con baja cobertura.

---

## Tabla resumen de decisiones

| Decisión | Criterio | Acción en silver |
|---|---|---|
| Estaciones | Representativas de Pereira urbana | Conservar 0026125710, 0026125508, 0026135501 |
| Estaciones renombradas | Mismo código, sin solapamiento de fechas | Unir transparentemente por `codigoestacion` |
| Temperatura = 0 | Físicamente imposible en Pereira | Convertir a NULL |
| Humedad = 0 | Físicamente imposible | Convertir a NULL |
| Precipitación = 288 en Matecaña | Valor centinela o desbordamiento del sensor | Convertir a NULL |
| Promedio entre estaciones | Consolidar representación espacial de Pereira | AVG ignorando NULLs |
| Días faltantes | Requerimiento del enunciado | Cuantificar y reportar, no imputar |
