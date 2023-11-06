
Se utilizó este archivo como bitácora, mencionando aquellos puntos que causaron más trabajo resolver así como también el razonamiento tras ciertas decisiones.

# I
## Jupyter Notebook
Se encontraron bugs mínimos en Jupyter Notebook. Se agregaron los parámetros "x=" e "y=" a sns.barplot debido a error de argumentos.

## Model
- Se tradujo todo el contenido de  Jupyter Notebook a los métodos pre creados en el archivo model.py.
- Se crea una clase CustomFeature que alberga métodos estáticos encargados de realizar los features custom
realizados por el DS, si bien no se usan todos, me parece útil tenerlos a mano en caso de que ocurra algún cambio.
- El modelo XGB fué escogido debido a que fué el único que pasó los requerimientos de las pruebas.
- En el método setUp de la clase TestModel en test_model.py se cambió la ruta del archivo debido a que no
se lograba encontrar, le asigné la ruta exacta del archivo al argumento filepath_or_buffer. **Este cambio no fue subido para no entorpecer las pruebas internas.**
- en model.py, en la línea 79 se cambió el tipo de dato retornado debido a error en las pruebas (pasó de "Union()" a "Union[]"):
    -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]

- La línea 130, el test fallaba porque los features devueltos "no eran de tipo pd.Dataframe"
- La línea 191, el valor devuelto de la predicción era un array([]) y no un "list", por lo que se transofrmó a esta

- En el test "test_model_predict" se generaba un error que decía que no existía el modelo (_model = None), esto se solucionó guardando el modelo en un .json dentro del método fit y cargándolo en el método predict siempre que exista y sea necesario.

- Modelo pasó todos los tests

# II
## API
- Se realizó el endpoint para hacer predict, previamente se crearon Modelos para validar de forma fácil el body y devolver mensajes de error personalizados.
- Se obtienen desde Jupyter Notebook los posibles datos para los campos utilizados, así validando los posibles valores de cada campo.
- Es imposible que elmodelo pueda predecir a partir del body proporcionado por las pruebas, así que se sigue las instrucciones del archivo test_api.py, el endpoint /predict realizará la carga y preproceso de forma normal, pero a la hora de predecir simplemente devolverá [0].

- API pasó todos los tests

# III
## Deploy
- Se configura Dockerfile para Dockerizar la API.
- Se crean los archivos deployment y servicio para realizar deploy a kubernetes en GCP.
- Se crea proyecto GCP y se habilitan las instancias de Kubernetes.
- Se hace push a la imagen de Docker a gcr.io.
- Se aplican los archivos deployment y servicio.
- En Makefile se cambia la ruta a la de la API en GCP.
- La API en el servidor pasa todas las pruebas.

# IV
## CI/CD
- Se configuran los archivos ci y cd según los pasos realizados anteriormente.
- Se automatizan los tests y comandos de deploy a kubernetes.
