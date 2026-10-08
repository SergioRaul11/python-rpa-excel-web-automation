import pandas as pd


df = pd.DataFrame(
    [
        {
            "nombre": "Juan",
            "apellido": "Perez",
            "correo": "juan.prueba@example.com",
            "tipo_de_acceso": "Acceso total",
        }
    ]
)

df.to_excel("estudiantes.xlsx", index=False)
print("Archivo estudiantes.xlsx creado correctamente.")
