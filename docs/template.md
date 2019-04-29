---
title: Análisis de logs escalable.
author:
  - Álvaro García Jaén
  - Antonio Molner Domenech
lang: es
geometry: margin=3cm
toc: True
toc-own-page: True
linkcolor: blue
titlepage: True
listings-no-page-break: True
---

# ¿Que es Log Analysis?

- Que es un log
- Que información aporta
- Son datos semiestructurados (necesitan parsearse con Regex por ejemplo)

# ¿Importancia?

Cosas que podemos hacer con los logs:

- Monitorizacion

- Alertas

- Obtener insights (esto es lo que nosotros hacemos con el Dashboard)


# Problemas con el análisis en tiempo real

# Nuestra solución

## Arquitectura y diseño

Hablar sobre la arquitectura en general y cada parte en específico.

- Ingestion (Flume's -> Kafka -> Spark)
- Processing (Spark + Cassandra + HDFS)
- Serving layer (Kafka -> Dashboard)

Y porque hemos diseñado la arquitectura así. Beneficios de usar Flume, Kafka
, Spark y Cassandra.

Otras posibles configuraciones:

Cassandra -> Hbase
Spark -> Storm


Hablar de que es un arquitectura genérica que se puede adaptar a Monitorización y
alertas también.

## Implementación

Hablar sobre la configuración de los clusters, agentes, y base de datos.
Hablar del consumo de datos por parte del Dashboard (peticiones a cassandra
y consumo de Kafka).

# Demo

Hablar sobre la construcción del dashboard

# Métricas (opcional)

Hablar sobre la cantidad de peticiones que podemos procesar,
latencia, o cauce (throughput)
