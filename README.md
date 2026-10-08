# 🤖 Python RPA — Excel to Web Automation

RPA desarrollado en **Python** para automatizar el registro de información almacenada en archivos Excel dentro de una plataforma web, reduciendo tareas manuales y mejorando la eficiencia del proceso.

## 🚀 ¿Qué hace?

El robot automatiza el flujo de trabajo:

**Excel → Procesamiento de datos → Plataforma Web → Registro automático**

El proceso utiliza archivos Excel como fuente de información, procesa los datos y posteriormente interactúa automáticamente con el sitio web para realizar los registros correspondientes.

## 🛠️ Tecnologías utilizadas

* 🐍 Python
* 🐼 Pandas
* 📊 OpenPyXL
* 🌐 Selenium

## ✨ Características

* Lectura y procesamiento de archivos Excel.
* Manipulación y validación de datos.
* Automatización de navegación web.
* Registro automático de información.
* Reducción de tareas repetitivas.
* Automatización de un proceso manual mediante RPA.

## 🏗️ Flujo del proceso

```text
Archivo Excel
     ↓
Lectura y procesamiento
     ↓
Validación de datos
     ↓
Selenium inicia el navegador
     ↓
Acceso a la plataforma web
     ↓
Registro automático
     ↓
Proceso finalizado
```

## 📂 Estructura del proyecto

```text
python-rpa-excel-web-automation/
│
├── src/
│   ├── main.py
│   ├── excel_handler.py
│   └── web_automation.py
│
├── data/
│   └── example.xlsx
│
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Instalación

Clona el repositorio e instala las dependencias:

```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

```bash
python main.py
```

> **Nota:** Para utilizar el proyecto es necesario configurar previamente los parámetros de acceso y los elementos correspondientes de la plataforma web.

## 🔐 Seguridad

Por motivos de seguridad, este repositorio **no contiene credenciales, datos reales ni información sensible** utilizada durante la automatización.

## 📚 Aprendizajes

Este proyecto permitió trabajar con:

* Automatización de procesos mediante RPA.
* Manipulación de información con Pandas y OpenPyXL.
* Automatización de navegadores utilizando Selenium.
* Manejo de procesos repetitivos.
* Integración entre archivos Excel y aplicaciones web.

## 🔮 Posibles mejoras

* Implementar logging del proceso.
* Agregar manejo avanzado de errores.
* Crear reportes de ejecución.
* Incorporar configuración mediante archivos `.env`.
* Añadir pruebas automatizadas.
* Mejorar la recuperación ante errores.

---

### 👨‍💻 Autor

**Sergio Orozco**
Software Developer
