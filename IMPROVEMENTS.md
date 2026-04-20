# Miglioramenti Futuri - IcebergPM

Questo documento elenca le funzionalità e le ottimizzazioni pianificate per le prossime versioni di IcebergPM.

## 📊 Funzionalità Core (In Programma)
- **[I-10] Import/Export Excel/JSON**: Caricamento di massa di task e costi per accelerare il setup dei progetti.
- **[I-11] Gestione Allegati**: Upload di documenti (PDF, immagini) direttamente negli item.
- **[I-12] Notifiche Email**: Invio automatico di alert al cliente quando un task viene completato o aggiornato.

## 🎨 Interfaccia & UX
- **[I-20] Dark Mode**: Supporto nativo per tema scuro/chiaro in base alle preferenze di sistema.
- **[I-21] Reportistica Grafica**: Dashboard con grafici (Chart.js) per l'andamento dei costi e avanzamento task.
- **[I-22] Micro-interazioni**: Animazioni fluide per transizioni tra dashboard e modali.

## 🔒 Sicurezza & Infrastruttura
- **[I-30] MFA (Multi-Factor Authentication)**: Secondo fattore (OTP) per login Amministratori.
- **[I-31] Rate Limiting**: Limitazione tentativi di login per prevenire attacchi brute-force.
- **[I-32] Dockerization**: Dockerfile e docker-compose per semplificare il deployment su server Linux.
- **[I-33] Backup Schedulati**: Snapshot automatici del DB ogni 24 ore verso cartelle configurate.

