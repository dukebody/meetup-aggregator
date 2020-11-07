Meetup Aggregator
=================

Herramienta para recoger y publicar en un único lugar todos los eventos de una serie de meetups de Meetup.com.

Hace scraping de la web de Meetup.com en lugar de usar la API, ya que para usar la API se necesita una cuenta Pro. 

El código de scraping está casi íntegramente sacado de `https://github.com/python-chile/pythonchile_v2/blob/master/events/tasks.py`, bajo licencia Apache 2.0.

Instrucciones:

1. Crear y activar entorno virtual.
2. Instalar dependencias:
```
pip install -r requirements.txt
```
3. Correr el scraping. La lista de meetups está en el propio archivo.
```
python main.py
```
4. Servir los resultados:
```
FLASK_APP=app.py FLASK_ENV=development flask run
```
5. Están disponibles en `http://localhost:5000/`.


Consideraciones:
- Ahora mismo la "base de datos" es un archivo json, que no es ni ACID ni escalable ni nada, pero para un volumen pequeño y filtrado sencillo ya vale.
- La idea es que el script de crawling se ejecute periódicamente (¿cada hora?) mediante un cron.


Futuro/ideas:
- Scrapear eventos próximos además de (o quizá en vez de) los pasados :D
- Mejorar el diseño de la página que es cutrísimo. Para variar, podríamos reutilizar el de Python Chile ;) `https://pythonchile.cl/eventos/`.
- Construir resiliencia respecto a fallos al crawlear un grupo de meetup. Si uno falla, no deberían fallar todos.
- No reescribir toda la base de datos en cada crawling, sino solamente actualizar los datos necesarios (quizá solamente actualizar próximos eventos y dejar los pasados).
- Proporcionar una vista "calendario" que la gente pueda añadir a su propio calendario como remoto.
- Proporcionar una vista RSS. Esto probablemente después permitiría automatizaciones del rollo enviar mails, mensajes, etc. cuando haya nuevos meetups.
- Permitir filtros/búsquedas en los eventos. Por ejemplo, permitir buscar por ciudad, o por temática. Lo más sencillo sería quizá simplemente dejar una búsqueda de texto que buscase en todos los campos (tipo freetext search).
  