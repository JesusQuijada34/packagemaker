# Runtime Python de PackageMaker en Android

La rama `android` integra **Chaquopy 14.0.2** con Android Gradle Plugin 7.4. El APK contiene un intérprete Python 3.8 y el núcleo adaptado de PackageMaker en `android/app/src/main/python`.

## Operaciones locales

El módulo `packagemaker_android.py` expone la creación de proyectos con las plantillas originales, reparación de estructuras, validación de `details.xml` y carpetas requeridas y generación de paquetes `.iflapp` mediante ZIP. La actividad Kotlin inicia Python con `Python.start(AndroidPlatform(context))`, invoca `packagemaker_android.main(...)` y copia el proyecto generado al árbol persistente `Documentos/PackageMaker Projects`.

## Compilación

La creación y validación del proyecto y el empaquetado `.iflapp` se ejecutan localmente en Android. La generación de binarios de escritorio mediante PyInstaller o toolchains externos no se incluye dentro del runtime Android, porque esos componentes dependen de APIs y ejecutables de escritorio. La aplicación conserva el panel SSH para transferir el proyecto y ejecutar en la máquina remota el comando configurado por el usuario.

## ABI y tamaño

El APK se compila para `armeabi-v7a`, `arm64-v8a`, `x86` y `x86_64`. Incluir el intérprete Python para las cuatro arquitecturas incrementa legítimamente el tamaño del APK. Para reducirlo a producción, se pueden dejar únicamente `arm64-v8a` y `armeabi-v7a`.

## Compilación local

Desde `android/`, configurar `local.properties` con `sdk.dir` y ejecutar:

```bash
gradle --no-daemon assembleDebug
```

Para una compilación release firmada, proporcionar `PACKAGEMAKER_KEYSTORE`, `PACKAGEMAKER_KEY_PASSWORD` y opcionalmente `PACKAGEMAKER_KEY_ALIAS` sin guardarlos en Git.

## Limitación conocida

El entorno de compilación disponible usa Python 3.12 como intérprete del host, mientras que el runtime embebido Chaquopy es Python 3.8. La compilación continúa correctamente, pero para generar bytecode `.pyc` reproducible se recomienda compilar con un Python 3.8 en la máquina de build. El APK conserva el código fuente Python durante esta fase para facilitar el diagnóstico.

## Referencias

- [Chaquopy 14.0 Android documentation](https://chaquo.com/chaquopy/doc/14.0/android.html)
- [Chaquopy 14.0.2 release notes](https://chaquo.com/chaquopy/chaquopy-version-14-0-2/)
- [Python on Android](https://docs.python.org/3/using/android.html)
