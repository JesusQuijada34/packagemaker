# Emulación visual

Se generaron capturas locales en 375x812 (iPhone SE), 768x1024 (tablet) y 1440x900 (desktop).

La versión móvil pequeña no muestra overflow horizontal y el encabezado queda compacto con logo, selector de idioma y botón de menú. El hero cabe en el viewport y los botones mantienen buen tamaño táctil.

La versión de escritorio presenta el mismo patrón compacto con menú visible como botón, evitando la fila saturada de enlaces. La revisión del menú mediante DOM confirmó `aria-expanded=true`, etiqueta `Cerrar menú`, visibilidad del panel y nueve enlaces.

La descarga protegida sin sesión devuelve 302 hacia `/login?next=%2Fdownload`. La revisión inicial mostró que el sitio público podía estar retrasado respecto al commit local; la comprobación final debe hacerse después del deploy de la rama `render`.
