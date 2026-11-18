# NEXUS ARES
## Examen del Segundo Parcial — Arquitectura de Computadoras

**Universidad:** UTH  
**Asignatura:** Arquitectura de Computadoras  
**Docente:** Ricardo Enrique Lagos Mendoza  
**Grupo:** 01

### Descripción del proyecto

NEXUS ARES es un sistema de gestión de órdenes de venta desarrollado utilizando una arquitectura de tres servicios mediante Docker Compose.

El proyecto integra:

- **Django:** interfaz web para gestionar órdenes.
- **Flask:** API REST para consultar y administrar información.
- **SQL Server 2022:** almacenamiento persistente de datos.
- **Docker Compose:** administración de los tres servicios.

### Funcionalidades

- Consultar órdenes registradas.
- Crear nuevas órdenes.
- Editar y eliminar órdenes.
- Agregar productos a las órdenes.
- Calcular los totales de venta.
- Consultar el estado de la API.

### Ejecución del proyecto

Desde la carpeta principal, ejecutar:

```bash
docker compose up -d --build
```

Acceder a:

- Aplicación web: http://localhost:8000
- API: http://localhost:5000/api/ordenes
- Estado de la API: http://localhost:5000/health

Antes de iniciar, configurar el archivo `.env` con las variables requeridas. No publicar contraseñas ni credenciales.

### Repositorio GitHub

https://github.com/johnnyCage098/nexus-ares

### Imágenes Docker Hub

**API Flask:**  
https://hub.docker.com/r/johnnycage098/nexus-ares-api

**Web Django:**  
https://hub.docker.com/r/johnnycage098/nexus-ares-web

### Integrantes del grupo

| Nombre completo | Número de cuenta |
|---|---|
| José Alfredo Mejía Granados | 202510060768 |
| Raúl Andrés Raudales García | 202510010696 |
| Stanley Lemuel Goff Sterbroock | 202410060287 |
| Nelson Javier Guerra Nolasco | 202320020194 |
| Astrid Lizbeth Castellanos Pineda | 202410010300 |
| Ruth Nohemí Sánchez García | 202010060043 |
| Lester Antonio Alvarado Arita | 202210010652 |