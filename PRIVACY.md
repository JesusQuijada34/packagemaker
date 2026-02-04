# Política de Privacidad | Package Maker (IPM)

**Última actualización:** 25 de enero de 2026

La presente Política de Privacidad describe el compromiso de **Package Maker (IPM)** y su desarrollador, **Jesús Quijada**, con la protección de la privacidad y la transparencia en el manejo de la información técnica y del usuario.

---

## Índice
1. [Información General](#1-información-general)
2. [Recopilación y Procesamiento de Datos](#2-recopilación-y-procesamiento-de-datos)
3. [Almacenamiento y Localización](#3-almacenamiento-y-localización)
4. [Seguridad de la Información](#4-seguridad-de-la-información)
5. [Servicios de Terceros](#5-servicios-de-terceros)
6. [Contacto](#6-contacto)

---

## 1. Información General
Package Maker (IPM) es una herramienta de escritorio diseñada para la creación y gestión de paquetes de software. Al ser una aplicación de ejecución local, el control de la información reside exclusivamente en el usuario final.

## 2. Recopilación y Procesamiento de Datos
La aplicación opera bajo el principio de **minimización de datos**. No se recolectan datos personales de forma automática ni se envían a servidores externos, salvo en las siguientes interacciones técnicas:

*   **Integración con GitHub API:** El programa realiza consultas públicas a la API de GitHub para validar la existencia de nombres de usuario o repositorios proporcionados por el desarrollador durante la configuración del proyecto.
*   **Gestión de Recursos Externos:** Si el usuario define una URL para el icono del paquete, la aplicación realizará una petición de red para descargar y procesar dicho archivo localmente.

## 3. Almacenamiento y Localización
Toda la información del proyecto (nombre de la empresa, identificadores de aplicación, versiones, metadatos y scripts) se almacena **únicamente de forma local** en el directorio de trabajo seleccionado por el usuario.
*   **Archivos generados:** `details.xml`, `README.md`, y estructuras de carpetas del proyecto.
*   **Persistencia:** No existe una base de datos en la nube que sincronice estos datos sin la intervención manual del usuario (ej. mediante Git).

## 4. Seguridad de la Información
Para garantizar la fiabilidad del software y la integridad de los paquetes generados, se implementan las siguientes medidas:
*   **Verificación de Integridad:** Uso de algoritmos de suma de comprobación **SHA-256** para asegurar que los archivos del paquete no hayan sido alterados o corrompidos.
*   **Permisos de Sistema:** La aplicación requiere permisos de lectura y escritura limitados exclusivamente a las rutas de proyecto definidas por el usuario.

## 5. Servicios de Terceros
El uso de Package Maker puede implicar la interacción con plataformas externas bajo la responsabilidad del usuario:
*   **GitHub:** Al cargar proyectos a repositorios remotos, el usuario se sujeta a los [Términos de Servicio](https://docs.github.com/es/site-policy/github-terms/github-terms-of-service) y la [Política de Privacidad](https://docs.github.com/es/site-policy/privacy-policies/github-privacy-statement) de GitHub.
*   **Ecosistema Fluthin Store:** Los paquetes con extensión `.iflapp` están optimizados para este entorno, el cual posee sus propios estándares de validación y seguridad.

## 6. Contacto
Para cualquier consulta técnica o duda relacionada con la privacidad y el manejo de datos en Package Maker, puede contactar directamente con el desarrollador:

*   **Repositorio Oficial:** [GitHub Issues](https://github.com/jesusquijada/package-maker)
*   **Comunidad:** Telegram
