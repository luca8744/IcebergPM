import PyInstaller.__main__
import os
import shutil

def build():
    print("Inizio procedura di build per IcebergPM...")
    
    # Nome dell'eseguibile
    name = "IcebergPM"
    
    # Percorsi
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(current_dir, "frontend")
    
    # Pulizia cartelle precedenti
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Rossa cartella vecchia: {d}")

    # Configurazione PyInstaller
    # --onefile: Crea un unico file eseguibile
    # --add-data: Include la cartella frontend
    # --name: Nome del file exe
    # --clean: Pulisce la cache
    
    params = [
        'run.py',
        '--name', name,
        '--onefile',
        '--add-data', f'{frontend_dir};frontend',
        '--clean',
        '--noconfirm',
        # Includiamo esplicitamente alcuni moduli che a volte sfuggono
        '--hidden-import', 'uvicorn.logging',
        '--hidden-import', 'uvicorn.loops',
        '--hidden-import', 'uvicorn.loops.auto',
        '--hidden-import', 'uvicorn.protocols',
        '--hidden-import', 'uvicorn.protocols.http',
        '--hidden-import', 'uvicorn.protocols.http.auto',
        '--hidden-import', 'uvicorn.protocols.websockets',
        '--hidden-import', 'uvicorn.protocols.websockets.auto',
        '--hidden-import', 'uvicorn.lifespan',
        '--hidden-import', 'uvicorn.lifespan.on',
        '--hidden-import', 'passlib.handlers.bcrypt',
    ]

    print(f"Esecuzione PyInstaller con parametri: {params}")
    PyInstaller.__main__.run(params)
    
    print("\n" + "="*50)
    print("BUILD COMPLETATA CON SUCCESSO!")
    print(f"Trovi il pacchetto portable in: {os.path.join(current_dir, 'dist', name)}")
    print("="*50)
    print("\nNOTA: Ricordati di copiare il file .env nella cartella dist/IcebergPM")
    print("se vuoi che l'eseguibile usi una configurazione specifica.")

if __name__ == "__main__":
    build()
