
import pandas as pd
import io
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

'''
@mcp.tool()
def to_uppercase(text: str) -> str:
    """Converte tutte le lettere del testo in maiuscolo"""
    return text.upper()
# Test di tool MCP
# Questo è un esempio di come definire un tool MCP per convertire un testo in maiuscolo.
'''

@mcp.tool()
def analyze_dataset(csv_data: str) -> str:
    """
    Analizza un dataset CSV fornito come stringa.
    Include:
    - Info generali
    - Statistiche descrittive
    - Valori nulli
    - Anteprima
    - Analisi outlier (IQR)
    con gestione delle eccezioni.
    """
   
    try:
        # Tentativo di lettura del CSV
        df = pd.read_csv(io.StringIO(csv_data))
    except pd.errors.EmptyDataError:
        return "Il dataset fornito è vuoto o non contiene dati validi."
    except pd.errors.ParserError as e:
        return f"Errore di parsing del CSV: {str(e)}"
    except Exception as e:
        return f"Errore imprevisto durante il caricamento del dataset: {str(e)}"

    try:
        # INFO GENERALI
        info_buf = io.StringIO()
        df.info(buf=info_buf)
        info = info_buf.getvalue()

        # STATISTICHE DESCRITTIVE
        try:
            description = df.describe(include='all').to_string()
        except ValueError as e:
            description = f"Impossibile calcolare statistiche descrittive: {str(e)}"

        # VALORI NULLI
        try:
            missing = df.isnull().sum().to_string()
        except Exception as e:
            missing = f"Errore durante il calcolo dei valori nulli: {str(e)}"

        # PREVIEW
        try:
            preview = df.head().to_string()
        except Exception as e:
            preview = f"Errore durante l'anteprima del dataset: {str(e)}"

        # OUTLIER ANALYSIS (IQR)
        outlier_report = ""
        try:
            numeric_cols = df.select_dtypes(include='number').columns

            if len(numeric_cols) == 0:
                outlier_report = "\nNessuna colonna numerica trovata per analisi IQR."
            else:
                for col in numeric_cols:
                    series = df[col].dropna()
                    if series.empty:
                        outlier_report += f"\nColonna '{col}': contiene solo valori nulli.\n"
                        continue

                    q1 = series.quantile(0.25)
                    q3 = series.quantile(0.75)
                    iqr = q3 - q1
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    outliers = df[(df[col] < lower) | (df[col] > upper)]
                    count = len(outliers)

                    if count > 0:
                        outlier_report += f"\nColonna '{col}': {count} outlier trovati (IQR)"
                    else:
                        outlier_report += f"\nColonna '{col}': nessun outlier rilevato (IQR)"

        except Exception as e:
            outlier_report += f"\nErrore durante l'analisi degli outlier: {str(e)}"

        # RISULTATO FINALE
        result = (
            "INFORMAZIONI GENERALI:\n" + info +
            "\n\nSTATISTICHE DESCRITTIVE:\n" + description +
            "\n\nVALORI NULLI PER COLONNA:\n" + missing +
            "\n\nANTEPRIMA (prime 5 righe):\n" + preview +
            "\n\nANALISI OUTLIER (IQR):" + outlier_report
        )
        return result

    except Exception as e:
        return f"Errore imprevisto durante l'analisi del dataset: {str(e)}"


# Esempio di chiamata diretta nel main
if __name__ == "__main__":
    with open("/workspaces/mcp-example-main/Dataset/Housing.csv", "r", encoding="utf-8") as f:
        csv_data = f.read()
    result = analyze_dataset(csv_data)
    print(result)
