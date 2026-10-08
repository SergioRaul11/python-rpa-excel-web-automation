from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable
import sys
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


# ============================================================
# CONFIGURACION
# ============================================================
URL = "https://systeme.io/es/login"
EXCEL_FILE = "estudiantes.xlsx"
WAIT_TIMEOUT = 20
HEADLESS = False
AUTO_CONTINUE_AFTER_SECONDS = 0
COMBOBOX_POLL_FREQUENCY = 0.2

# Si deseas usar un chromedriver especifico, indica la ruta aqui.
# Si lo dejas en None, Selenium intentara resolverlo automaticamente.
CHROMEDRIVER_PATH = None

# Localizadores: reemplaza estos valores por los correctos segun tu pagina.
# Recomendacion: empieza probando con XPATH o CSS.
LOCATORS: Dict[str, tuple[str, str]] = {
    "student_modal": (
        By.XPATH,
        "//*[self::div or self::section][.//*[contains(normalize-space(.), 'Crear estudiante')]][last()]",
    ),
    "add_student_button": (
        By.XPATH,
        "//button[contains(., 'Agregar estudiante')] | //a[contains(., 'Agregar estudiante')]",
    ),
    "first_name_input": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//input[not(@type='hidden')])[1]",
    ),
    "last_name_input": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//input[not(@type='hidden')])[2]",
    ),
    "email_input": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//input[not(@type='hidden')])[3]",
    ),
    "access_type_select": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//label[contains(normalize-space(.), 'Tipo de acceso')]/following::select[1])[last()]",
    ),
    "access_type_combobox": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//label[contains(normalize-space(.), 'Tipo de acceso')]/following::*[@role='combobox' or @aria-haspopup='listbox' or self::button][1])[last()]",
    ),
    "access_type_options": (
        By.XPATH,
        "//*[@role='option' or @role='listbox']//div | //*[@role='option'] | //li[@role='option'] | //ul[@role='listbox']//li | //div[contains(@class, 'option')]",
    ),
    "save_button": (
        By.XPATH,
        "(.//*[contains(normalize-space(.), 'Crear estudiante')]/ancestor::*[self::div or self::section][1]//button[contains(normalize-space(.), 'Guardar') or contains(normalize-space(.), 'Save')])[last()]",
    ),
}

# Columnas obligatorias del Excel.
REQUIRED_COLUMNS = {
    "nombre": ["nombre"],
    "apellido": ["apellido"],
    "correo": ["correo", "email"],
    "tipo_de_acceso": ["tipo_de_acceso", "tipo de acceso"],
}


# ============================================================
# UTILIDADES
# ============================================================
def get_runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent



def get_excel_path() -> Path:
    excel_path = Path(EXCEL_FILE)
    if excel_path.is_absolute():
        return excel_path
    return get_runtime_base_dir() / excel_path



def normalize_header(value: str) -> str:
    return str(value).strip().lower()


def find_matching_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalized = {normalize_header(col): col for col in columns}
    for candidate in candidates:
        match = normalized.get(normalize_header(candidate))
        if match:
            return match
    return None


def load_students(excel_path: Path) -> pd.DataFrame:
    if not excel_path.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo Excel: {excel_path.resolve()}"
        )

    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
    except Exception as exc:
        raise RuntimeError(f"No se pudo leer el archivo Excel: {exc}") from exc

    if df.empty:
        raise ValueError("El archivo Excel no contiene filas para procesar.")

    column_mapping: dict[str, str] = {}
    missing_fields: list[str] = []

    for internal_name, candidates in REQUIRED_COLUMNS.items():
        matched = find_matching_column(df.columns, candidates)
        if matched is None:
            missing_fields.append(internal_name)
        else:
            column_mapping[matched] = internal_name

    if missing_fields:
        expected = ", ".join(REQUIRED_COLUMNS.keys())
        missing = ", ".join(missing_fields)
        raise ValueError(
            "Faltan columnas obligatorias en el Excel. "
            f"Esperadas: {expected}. No encontradas: {missing}."
        )

    df = df.rename(columns=column_mapping)
    df = df[list(REQUIRED_COLUMNS.keys())].copy()
    df = df.fillna("")

    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()

    return df


# ============================================================
# SELENIUM
# ============================================================
def build_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if CHROMEDRIVER_PATH:
        service = Service(CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)

    return webdriver.Chrome(options=options)


def wait_for_clickable(driver: webdriver.Chrome, locator: tuple[str, str]):
    return WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable(locator)
    )


def wait_for_visible(driver: webdriver.Chrome, locator: tuple[str, str]):
    return WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located(locator)
    )


def get_modal_inputs(driver: webdriver.Chrome):
    modal = wait_for_visible(driver, LOCATORS["student_modal"])
    inputs = modal.find_elements(By.XPATH, ".//input[not(@type='hidden')]")
    visible_inputs = [element for element in inputs if element.is_displayed()]
    return visible_inputs



def get_student_form_fields(driver: webdriver.Chrome):
    visible_inputs = get_modal_inputs(driver)
    if len(visible_inputs) < 3:
        raise RuntimeError(
            "No se encontraron suficientes inputs visibles dentro del modal. "
            f"Cantidad detectada: {len(visible_inputs)}."
        )

    print(
        "[DEBUG] Inputs visibles del modal detectados: "
        f"{len(visible_inputs)}. Se usaran las posiciones 1, 2 y 3."
    )
    return visible_inputs[0], visible_inputs[1], visible_inputs[2]


def clear_and_type(driver: webdriver.Chrome, element, value: str) -> None:
    text = value or ""

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].focus();", element)

    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)

    try:
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)
        if element.get_attribute("value") == text:
            return
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].value = '';", element)
        driver.execute_script("arguments[0].value = arguments[1];", element, text)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            element,
        )
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            element,
        )
    except Exception:
        pass

    final_value = element.get_attribute("value") or ""
    if final_value != text:
        raise RuntimeError(
            f"No se pudo escribir correctamente el valor '{text}' en el campo. "
            f"Valor detectado despues del intento: '{final_value}'."
        )


def click_element(driver: webdriver.Chrome, element) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].focus();", element)

    try:
        element.click()
        return
    except ElementClickInterceptedException:
        pass
    except Exception:
        pass

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: element.is_enabled() and element.is_displayed()
        )
    except Exception:
        pass

    driver.execute_script("arguments[0].click();", element)



def normalize_option_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())



def get_visible_access_options(search_context):
    candidates = search_context.find_elements(*LOCATORS["access_type_options"])
    visible = []

    for element in candidates:
        try:
            text = element.text.strip()
            if element.is_displayed() and text:
                visible.append((text, element))
        except Exception:
            continue

    unique_options = []
    seen = set()
    for text, element in visible:
        normalized = normalize_option_text(text)
        if normalized not in seen:
            seen.add(normalized)
            unique_options.append((text, element))

    return unique_options



def wait_for_combobox_options(driver: webdriver.Chrome, modal, combo):
    def _resolve_options(_driver):
        for context in (modal, combo, driver):
            try:
                options = get_visible_access_options(context)
                if options:
                    return options
            except Exception:
                continue
        return False

    return WebDriverWait(
        driver,
        WAIT_TIMEOUT,
        poll_frequency=COMBOBOX_POLL_FREQUENCY,
    ).until(_resolve_options)



def select_access_type(driver: webdriver.Chrome, value: str) -> None:
    normalized_value = normalize_option_text(value)
    modal = wait_for_visible(driver, LOCATORS["student_modal"])

    try:
        select_element = modal.find_element(*LOCATORS["access_type_select"])
        if select_element.is_displayed():
            Select(select_element).select_by_visible_text(value.strip())
            return
    except Exception:
        pass

    combo = modal.find_element(*LOCATORS["access_type_combobox"])
    click_element(driver, combo)

    options = wait_for_combobox_options(driver, modal, combo)

    detected_options = [text for text, _ in options]
    print(f"[DEBUG] Opciones detectadas en Tipo de acceso: {detected_options}")

    for text, element in options:
        if normalize_option_text(text) == normalized_value:
            click_element(driver, element)
            return

    print(
        "[DEBUG] No se encontro coincidencia exacta para Tipo de acceso. "
        f"Se conservara la opcion por defecto del formulario. Valor buscado: '{value}'."
    )

    try:
        combo.send_keys(Keys.ESCAPE)
    except Exception:
        try:
            click_element(driver, combo)
        except Exception:
            pass


def add_student(driver: webdriver.Chrome, student: pd.Series) -> None:
    add_button = wait_for_clickable(driver, LOCATORS["add_student_button"])
    click_element(driver, add_button)

    wait_for_visible(driver, LOCATORS["student_modal"])

    first_name_input, last_name_input, email_input = get_student_form_fields(driver)

    clear_and_type(driver, first_name_input, student["nombre"])
    clear_and_type(driver, last_name_input, student["apellido"])
    clear_and_type(driver, email_input, student["correo"])
    select_access_type(driver, student["tipo_de_acceso"])

    save_button = wait_for_visible(driver, LOCATORS["save_button"])
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: save_button.is_enabled()
    )
    click_element(driver, save_button)

    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.invisibility_of_element_located(LOCATORS["student_modal"])
    )

    # Pequena pausa para permitir que la interfaz se estabilice.
    time.sleep(1)


# ============================================================
# FLUJO PRINCIPAL
# ============================================================
def wait_for_user_confirmation() -> None:
    if AUTO_CONTINUE_AFTER_SECONDS and AUTO_CONTINUE_AFTER_SECONDS > 0:
        print(
            "Modo prueba activo. Esperando "
            f"{AUTO_CONTINUE_AFTER_SECONDS} segundos antes de continuar..."
        )
        time.sleep(AUTO_CONTINUE_AFTER_SECONDS)
        return

    input("Cuando estes listo para comenzar la automatizacion, presiona Enter...")



def main() -> int:
    excel_path = get_excel_path()

    try:
        students_df = load_students(excel_path)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(f"Se cargaron {len(students_df)} estudiantes desde '{excel_path.name}'.")

    driver = None
    try:
        driver = build_driver()
        driver.get(URL)

        print("\nSe abrio Systeme.io en el navegador.")
        print("Inicia sesion manualmente si es necesario.")
        wait_for_user_confirmation()

        total = len(students_df)
        for index, student in students_df.iterrows():
            current = index + 1
            full_name = f"{student['nombre']} {student['apellido']}".strip()
            email = student["correo"]
            access = student["tipo_de_acceso"]
            print(
                f"[{current}/{total}] Procesando: {full_name} - {email} - Acceso: {access}"
            )

            try:
                add_student(driver, student)
                print(f"[{current}/{total}] Exito\n")
            except TimeoutException as exc:
                print(f"[{current}/{total}] Error por tiempo de espera: {exc}\n")
            except Exception as exc:
                print(f"[{current}/{total}] Error: {exc}\n")

        print("Proceso finalizado.")
        return 0

    except WebDriverException as exc:
        print(f"[ERROR] Fallo general del navegador/Selenium: {exc}")
        return 1
    except EOFError:
        print(
            "[ERROR] No se pudo leer la confirmacion del usuario en consola. "
            "Si estas probando en un entorno no interactivo, configura "
            "AUTO_CONTINUE_AFTER_SECONDS con un valor mayor a 0."
        )
        return 1
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        return 1
    except Exception as exc:
        print(f"[ERROR] Fallo general e irrecuperable: {exc}")
        return 1
    finally:
        if driver is not None:
            driver.quit()
            print("Navegador cerrado correctamente.")


if __name__ == "__main__":
    sys.exit(main())
