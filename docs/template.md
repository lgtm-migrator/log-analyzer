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
JSON, sino que viene en crudo o en formato semiestructurado. En el primer caso
es más difícil procesar los logs, mientras que en el segundo,
podemos emplear expresiones regulares para estructurar los datos y prepararlos
para guardarlos en una base de datos por ejemplo. 

# Importancia

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

Utilizaremos este punto para introducir nuestra solución. Antes de continuar,
vamos a explicar las tres etapas que nosotros consideramos fundamentales
en el flujo de información para el análisis de logs. Estás
etapas también son comunes a otros desarrollos basados en IoT o 
donde se requiera analizar un flujo continuo de información.
Las partes son las siguientes:

- **Ingestión**: La ingestión es el momento en el que cogemos los datos (logs) 
y los movemos al servidor donde se procesarán.
Para esto utilizaremos [Apache Flume](https://flume.apache.org/) y 
[Apache Kafka](https://kafka.apache.org/). (No, Apache no patrocina esta memoria)

- **Procesamiento:**
El procesamiento es el momento en el que tomamos los logs en crudo, tal y como
los produce nuestro servidor web, y obtenemos la información que nos interesa de
los eventos. Para esto utilizaremos [Apache Spark](https://spark.apache.org/),
[Apache Cassandra](https://cassandra.apache.org/) y [Apache
Hadoop](https://hadoop.apache.org/) (HDFS).

- **Presentación de la información:**
El visionado es el momento en el que se muestra la distinta información, ya
digerida, en un panel para que puedan consultarse. Aquí pueden consultarse
diferentes relaciones entre los eventos como el número total de visitantes, los
diferentes códigos de error devueltos... Para esto utilizaremos 
[Dash (by Plotly)](https://plot.ly/products/dash/).

Vamos a comentar un poco por qué hemos usado este software y no otro:

En el caso de Kafka, cuenta con una interfaz genérica con todas las fuentes de
información. Spark tiene una integración perfecta con Kafka y soporta HDFS como
sistema de almacenamiento principal HDFS. 
Además la paralelización es la base de su desarrollo. En
cuanto a Flume, se conecta bien con Kafka y además permite muchas fuentes
distintas (más adelante veremos esto).

Todas estas herramientas están pensadas para el Big Data, por lo que escala tan
bien como una granja web. Además todo es de Apache, por lo que el hecho de que
se integre bien no es ninguna sorpresa.

El motivo de la escalabilidad de estos sistemas es porque están diseñados para ejecutarse
en clusters. Tanto Kafka, como Spark y Cassandra se pueden ejecutar en un cluster
de manera prácticamente automática. Esto permite que el sistema de análisis de logs
y la granja web escalen de manera similar.

Aunque estamos siendo específicos en software ha utilizar en cada etapa, cabe
mencionar que todos los componentes son reemplazables. Nos debemos ajustar a los
recursos disponibles y a las necesidades de la empresa. Por ejemplo, Apache Spark
permite un gran cauce a cambio de alta latencia. Para obtener un sistema con baja
latencia, prácticamente en tiempo real, podríamos usar Apache Storm. Por otra parte,
Kafka puede ser reemplazado por RabbitMQ o cualquier sistema de mensajería o cola
de datos. Al igual que Flume y Cassandra. Este último se podría remplazar por HBase
para muchos otros casos.

Además, si lo que necesitamos es una solución rápida de desarrollar y no nos importa
perder flexibilidad podemos optar por usar una solución integrada como la siguiente:
[InfluxDB](https://www.influxdata.com/products/influxdb-overview/),
que a pesar de perder flexibilidad tiene un buen rendimiento por defecto.


## Arquitectura y diseño

Una vez que tenemos una idea aproximada de cual será el flujo de datos, lo
aclararemos con una imagen. Como vemos en la Figura 1, en pocas palabras nuestro
diseño hará lo siguiente: 

![Diseño que implementaremos](img/design.jpg)

-   Un agente de Flume (instalado en cada uno de los servidores finales) enviará
    los logs a Kafka.

-   Spark tomará la información que recibe Kafka y la irá almacenando en crudo
    en HDFS. También procesará esta información, estructurándola y almacenándola
    en una base de datos Cassandra.

-   El Dashboard recibe los datos de Cassandra para análisis por lotes y de Kafka
    para mostrar los datos en tiempo real.

Ahora veremos qué hace exactamente cada programa y como nos permite realizar
esto.

-   **Apache Flume:** Servicio que nos permite coger, agregar y mover grandes
    cantidades de logs de manera eficiente. Tiene una arquitectura simple basada
    flujo de datos. En la Figura 2 podemos ver como funciona:
    Un agente toma la información de una fuente (por ejemplo leer un archivo), la
    mueve mediante un canal (por ejemplo la memoria principal) y lo deposita en una
    pila (por ejemplo otro servicio como Kafka).

-   **Apache Kafka:** Plataforma de streaming distribuido. La idea básica es que
    tenemos canales, llamados "topics", por donde fluirá la información. Hay dos
    tipos de usuarios, los productores (en nuestro caso los agentes Flume) que
    enviarán la información y los consumidores que serán los que tomarán esa
    información. Además tiene particiones, lo cual da paralelismo tanto a los
    consumidores como a los productores sobre el mismo topic.

-   **Apache Spark:** Framework open-source que permite hacer cómputo en clusters,
    en nuestro caso para procesar logs de manera rápida y eficiente. Utilizamos 
    este sistema para convertir los logs de un formato semiestructurado
    (Apache Log Access) a un formato estructurado.

-   **Apache Cassandra:** Sistema de almacenamiento de bases de datos NoSQL. Permite
    manejar grandes cantidades de datos de manera eficiente y escalable. Lo
    utilizaremos para almacenar la información ya procesada, para luego ser
    mostrada a nuestra voluntad en el panel.

-   **Apache Hadoop:** Colección de herramientas que facilita el manejo de grandes
    cantidades de datos. Nosotros más concretamente proponemos HDFS, que es un
    sistema de ficheros distribuidos basado en Java para almacenar grandes
    cantidades de datos. Esto es esencial en entornos de producción donde es
    necesario almacenar los logs en crudo, sin procesar.

-   **Dash by Plotly:** Framework escrito en Python que nos permite de manera
    sencilla desarrollar aplicación web para el análisis. Es así como
    presentamos los datos una vez han sido procesados.

## Implementación

Para implementar esta arquitectura y el diseño que mostramos en la Figura 1, lo
primero que hemos hecho es aprovisionarnos de servidores. Hemos utilizado los
VPS (Virtual Private Server) de [DigitalOcean](https://www.digitalocean.com/).
Hemos elegido este proveedor porque cuenta con un plan de referidos en el que a
nuevos clientes les dan 100 euros para gastar en servidores, por lo que podremos
hacernos con un buen arsenal:

-   4 x Servidores web básicos finales. Aquí tendremos corriendo el agente de
    Flume y [un generador de
    logs](https://github.com/kiritbasu/Fake-Apache-Log-Generator) que simulará gran
    cantidad de tráfico.

-   1 x Servidor para procesar toda la información. Se trata de un servidor más
    potente (4 núcleos). Es por eso que hemos escogido usar 4 servidores web
    finales, para aprovechar al máximo el paralelismo. Aquí estará Kafka, Spark,
    Cassandra y el Dashboard. En nuestro ejemplo no instalaremos HDFS por
    motivos de espacio. En un entorno de real cada uno de estos servicios
    correría en servidores diferentes y sería obligatorio, como ya comentamos
    anteriormente, el uso de HDFS para almacenar los logs en crudo. Esto es así
    por motivos de seguridad y redundancia de datos. HDFS es un sistema de ficheros
    distribuido bastante seguro.

Para llevar a cabo la instalación, comenzaremos por configurar los servidores
web (aquí lo explicaremos de manera muy general, cada uno luego podrá consultar
de manera más específica lo que tenga dudas viendo [el
repositorio](https://github.com/antoniomdk/log-analyzer/)). Para ello
pondremos primero a generar los logs de manera automática. Una vez que se están
generando, debemos instalar Apache Flume (que lamentablemente no está en los
repositorios, tendremos que descargar el código fuente e instalarlo nosotros
mismos). Una vez instalado y configurado para que envíe los logs a nuestro
servidor de procesamiento, lo dejaremos a la espera de ejecutar (primero debemos
instalar y configurar Kafka).

Cuando ya tenemos todos los servidores web preparados, nos vamos al servidor de
procesamiento. Aquí en primer lugar instalaremos Apache ZooKeeper para
facilitarnos la instalación. Una vez hecho esto, simplemente iniciaremos el
servicio. Es turno de instalar Apache Kafka. Todos estos servicios, al igual que
Flume, no están en el repositorio sino que debemos descargarlo de la web de
Apache. Tras instalarlo, debemos crear los topics por donde fluirá la
información (en nuestro caso dos, uno para Flume y otro para el Dashboard).

Una vez hecho esto, ya podemos iniciar Flume en los servidores web y veremos
como empiezan a llegar los logs (se crea un archivo en /tmp). Como dato curioso,
habia que añadir el hostname del servidor de procesamiento en el */etc/hosts* de
cada uno de los servidores web, aún no sabemos muy bien por qué.

Ha llegado el momento de procesar la información. Para ello en primer lugar
instalaremos Cassandra, ya que será en una de sus bases de datos donde iremos
guardando esta información. Para ello primero añadiremos el repositorio donde se
encuentra para poder instalarlo con APT. Ejecutamos el servicio y ya podemos
crear nuestra tabla. Para ello debemos crear un *key space* que será nuestro
espacio de trabajo para cada tabla.

Cuando ya tenemos listo nuestro almacenamiento, debemos procesar la información.
Para ello usaremos Spark, que se conectará a Kafka para recibir los batches
(entradas de log) y procesarlos de forma paralela. Cada CPU tiene su conexión a
la base de datos Cassandra para poder ir añadiendo entradas a la tabla de forma
paralela. En la Figura 3 podemos ver un ejemplo de como se nos queda la tabla.
En la Figura 4, podemos ver en tiempo real como Spark va recibiendo y procesando
los diferentes batches.


![Tabla de la BD Cassandra](img/cassandra.jpg)


![Streaming de Apache Spark](img/spark.png)


Llegó el momento de presentar la información. Para ello implementaremos un panel
sobre Dash. Cuando se genera una acción sobre el Dashboard, se
genera la petición sobre la base de datos para obtener la información que se ha
pedido. Tiene una parte de tiempo real en la que el panel obtiene los datos
directamente de Spark que están en cola en Kafka, lo que nos permite ver todo en
tiempo real en un intervalo de 5 a 10 segundos. En la Figura 5 podemos ver como
nos ha quedado nuestro panel.

![Dashboard](img/dashboard.jpg)
