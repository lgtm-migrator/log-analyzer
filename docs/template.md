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

# Un problema a solucionar...

A lo largo de esta asignatura hemos visto como desplegar servidores web de altas
prestaciones. El concepto que hace eco en nuestra cabeza seguramente sea "granja
web". Tras usar esta técnica, una de las cuestiones a solucionar es: ¿cómo
recopilo información de mi granja? A estas alturas es muy probable que todos
tengamos claro que es un log y la importancia que tiene (si no es así, tranquilo,
en el siguiente punto daremos un repaso para los más rezagados). Cuando tenemos
un solo servidor, simplemente consultamos un único archivo que genera Apache
HTTP, Nginx, [inserte aquí su servidor web]... para ver los logs pero, ¿y si
nuestra granja web esta compuesta por 10 servidores finales?¿Y si son 100? Esto
rápidamente se nos va de las manos...

En esta memoria os presentaremos la solución que hemos dado nosotros y cómo lo
hemos implementado. Obviamente hay muchas otras maneras de hacerlo y os
invitamos a que investigueis al respecto.


# ¿Que es Log Analysis?

- Que es un log
- Que información aporta
- Son datos semiestructurados (necesitan parsearse con Regex por ejemplo)

Cuando un programa está ejecutándose (este puede ser un servidor web, el propio
sistema operativo...) pasan cosas constantemente (clientes abriendo la página
web, inicios de sesión, crear un nuevo archivo...). Llamaremos a esto eventos.
Estos eventos se almacenan en unos archivos que reciben el nombre de "archivos de
log".

En los archivos de log, como ya hemos dicho, podemos encontrar un registro de
los eventos que han sucedido en ciertos programas (obviamente cada programa
tiene su propio archivo, si no esto sería un caos, aunque hay maneras de
consultar todos los logs del sistema de manera simultanea). En el caso que nos
interesa a nosotros, los servidores web, veremos información de las peticiones
HTTP que han realizado los diferentes clientes. Obtendremos información como la
IP desde la que el cliente se conecta, qué parte de la web ha solicitado, el
código de error que ha devuelto nuestro servidor (2xx, 3xx, 5xx...), a qué hora
realizó la petición, el protocolo usado...

Toda esta información no viene dada en un formato estructurado como por ejemplo
JSON, sino que es una línea de información que siempre muestra los mismo campos
en el mismo órden y que nosotros deberemos ir extrayendo mediante parsing (Regex
por ejemplo).

# ¿Importancia?

Cosas que podemos hacer con los logs:

- Monitorizacion

- Alertas

- Obtener insights (esto es lo que nosotros hacemos con el Dashboard)

Analizar los logs es súmamente importante. En la informática, como su propio
nombre indica, la información es lo más importante. Cuando más información
tengamos de cómo está funcionando nuestro servidor web, más podremos prevenir
los futuros problemas. Por ejemplo, si vamos analizando los logs de nuestro
servidor en tiempo real, al fin y al cabo estamos monitorizándolo. Podemos poner
diferentes alertas, por ejemplo si un mismo cliente (misma IP) está intentando
entrar a ciertas rutas que no paran de devolver un código 4xx (aquí se incluyen
peticiones que resultan páginas prohibidas, que requieren autenticación...) y
actuar al respecto, por ejemplo baneando dicha IP (prohibiendo que vuelva a
conectarse más a nuestro servidor) o seguirle de cerca para tratar de averiguar
quién es o qué quiere.


# Problemas con el análisis en tiempo real

Lo que buscamos entonces es poder analizar estos logs en tiempo real para poder
monitorizar bien nuestra granja. Para explicar bien esto introduciremos dos
términos: cauce y latencia. Cauce es la cantidad de datos que procesas por
unidad de tiempo. Latencia es el tiempo que tardas en procesar un log. Debemos
de mantener un equilibrio entre estos términos a la hora de analizar nuestros
datos. No tiene sentido ir procesando los logs cada segundo, ya que si no hay
muchos clientes, iremos procesando los logs de uno en uno o ninguno; tampoco
tiene sentido esperar a tener en cola 100 logs para entonces procesarlos, ya que
quizás esperaremos demasiado y perderemos el "tiempo real".

# Nuestra solución

Utilizaremos este punto para introducir nuestra solución. En primer lugar,
dividiremos este problema en varias partes:
- Ingestión
La ingestión es el momento en el que cogemos los datos, los logs, y los movemos
al servidor donde se procesarán. Para esto utilizaremos Apache Flume, Apache
Kafka y Apache Kafka. (No, Apache no patrocina esta memoria)
- Procesamiento
El procesamiento es el momento en el que tomamos los logs en crudo, tal y como
los produce nuestro servidor web, y obtenemos la información que nos interesa de
los eventos. Para esto utilizaremos Apache Spark, Apache Cassandra y Apache
Hadoop (HDFS).
- Visionado de la información
El visionado es el momento en el que se muestra la distinta información, ya
digerida, en un panel para que puedan consultarse. Aquí pueden consultarse
diferentes relaciones entre los eventos como el número total de visitantes, los
diferentes códigos de error devueltos... Para esto utilizaremos Apache Kafka y
Dash (by Plotly).

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
