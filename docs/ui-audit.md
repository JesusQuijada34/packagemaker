# Auditoría visual del sitio público

La portada pública actual funciona, pero se percibe como una página larga de bloques: barra superior, hero con degradado y muchas tarjetas bento. Tiene buen contraste general y ya incluye `prefers-reduced-motion`, pero el hero no explica una historia ni muestra una interacción central del producto. El movimiento visible se concentra en orbes, entrada de elementos y degradados; falta un momento memorable que comunique el ciclo escribir → construir → distribuir.

La jerarquía está dispersa: hay muchas secciones con el mismo peso visual, varias capturas grandes y demasiados iconos de Font Awesome. La interfaz se acerca a dark glassmorphism/cinema más que a iOS; faltan controles tipo sistema, superficies con profundidad más contenida, un CTA primario inequívoco y una navegación adaptativa que conecte la identidad de usuario con las acciones protegidas.

La ruta pública `/download` actualmente renderiza directamente la página de descargas y no tiene una barrera `/login`. La ruta `/linkdevice` todavía devolvía 404 en la instancia pública observada, aunque la rama remota `render` contiene la implementación. La nueva arquitectura debe hacer que `/download` y `/linkdevice` redirijan a `/login?next=...`, y que `/login` preserve una sesión web mínima en una cookie segura y redirija al destino original después del callback de GitHub.

Dirección recomendada: una portada más breve y narrativa, con un hero de producto tipo “command center”, un SVG central que anime el flujo de empaquetado, capítulos de scroll con una sola animación dominante por sección, CTA único por pantalla y una vista móvil equivalente sin depender de hover.
