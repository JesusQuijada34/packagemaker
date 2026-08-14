# Compilación Android mediante SSH

Esta guía permite usar una máquina Linux dedicada como **servidor de compilación** para `Package Maker Mobile`. El flujo conserva el código fuente en la máquina local, transfiere una copia al servidor mediante SSH y devuelve el APK generado. Los comandos están escritos para Ubuntu 22.04 o 24.04.

> **Principio de seguridad:** SSH debe usar una clave pública, un usuario sin privilegios y, cuando sea posible, una regla de firewall que permita el puerto 22 únicamente desde la IP del equipo desarrollador.

## 1. Preparar la máquina de compilación

En la máquina remota, inicia sesión por consola o mediante el proveedor de la máquina y ejecuta:

```bash
sudo apt update
sudo apt install -y openssh-server unzip rsync curl git openjdk-17-jdk
sudo systemctl enable --now ssh
sudo adduser --disabled-password --gecos "" androidbuilder
sudo usermod -aG sudo androidbuilder
```

No es necesario que `androidbuilder` use privilegios durante la compilación. Si la cuenta solo se utilizará para compilar, puede retirarse del grupo `sudo` después de completar la instalación:

```bash
sudo deluser androidbuilder sudo
```

Comprueba la dirección de la máquina:

```bash
hostname -I
sudo systemctl status ssh --no-pager
```

## 2. Instalar Android SDK y Gradle

Como `androidbuilder`, instala el SDK en el directorio personal. El siguiente bloque descarga las command-line tools oficiales y acepta las licencias necesarias:

```bash
sudo -iu androidbuilder
mkdir -p "$HOME/android-sdk/cmdline-tools"
cd /tmp
curl -fL -o commandlinetools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q commandlinetools.zip -d "$HOME/android-sdk/cmdline-tools"
mv "$HOME/android-sdk/cmdline-tools/cmdline-tools" "$HOME/android-sdk/cmdline-tools/latest"
cat >> "$HOME/.bashrc" <<'EOF'
export ANDROID_SDK_ROOT="$HOME/android-sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export PATH="$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools"
EOF
source "$HOME/.bashrc"
yes | sdkmanager --licenses >/dev/null
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
```

El proyecto usa Android Gradle Plugin 7.4.0, por lo que instala Gradle 7.5.1 en el perfil del usuario:

```bash
cd "$HOME"
curl -fL -o gradle.zip https://services.gradle.org/distributions/gradle-7.5.1-bin.zip
unzip -q gradle.zip
echo 'export PATH="$HOME/gradle-7.5.1/bin:$PATH"' >> "$HOME/.bashrc"
source "$HOME/.bashrc"
gradle --version
```

## 3. Configurar la autenticación por clave

En el equipo local, genera una clave separada para este servidor si todavía no existe:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/package-maker-builder -C "package-maker-builder"
ssh-copy-id -i ~/.ssh/package-maker-builder.pub androidbuilder@IP_DEL_SERVIDOR
ssh -i ~/.ssh/package-maker-builder androidbuilder@IP_DEL_SERVIDOR 'echo SSH correcto'
```

Después de verificar que la clave funciona, endurece la configuración del servidor. Hazlo desde una segunda sesión abierta para no perder el acceso:

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sshd -t
sudo systemctl reload ssh
```

Si el servidor tiene UFW activo, limita SSH a la IP de confianza:

```bash
sudo ufw allow from IP_DEL_EQUIPO_LOCAL to any port 22 proto tcp
sudo ufw enable
sudo ufw status verbose
```

## 4. Enviar el proyecto para compilar

Desde la raíz del repositorio local (`packagemaker`), ejecuta:

```bash
export BUILDER="androidbuilder@IP_DEL_SERVIDOR"
export SSH_KEY="$HOME/.ssh/package-maker-builder"
ssh -i "$SSH_KEY" "$BUILDER" 'rm -rf ~/packagemaker-build && mkdir -p ~/packagemaker-build'
rsync -az --delete \
  --exclude '.git' \
  --exclude 'android/.gradle' \
  --exclude 'android/build' \
  --exclude 'android/app/build' \
  -e "ssh -i $SSH_KEY" \
  ./ "$BUILDER":~/packagemaker-build/
```

La copia se realiza con `rsync` para que los siguientes envíos solo transfieran cambios. No incluyas claves privadas, archivos `.env` ni credenciales en el repositorio.

## 5. Compilar en la máquina remota

```bash
ssh -i "$SSH_KEY" "$BUILDER" 'bash -lc '\''
  cd ~/packagemaker-build/android
  export ANDROID_SDK_ROOT="$HOME/android-sdk"
  export ANDROID_HOME="$ANDROID_SDK_ROOT"
  export PATH="$HOME/gradle-7.5.1/bin:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH"
  printf "sdk.dir=%s\\n" "$ANDROID_SDK_ROOT" > local.properties
  gradle --no-daemon --stacktrace assembleDebug
'\'''
```

El resultado esperado es `android/app/build/outputs/apk/debug/app-debug.apk`. Para una compilación de distribución, configura una firma propia y ejecuta `assembleRelease`; no uses una contraseña escrita directamente en el repositorio.

## 6. Recuperar y verificar el APK

```bash
mkdir -p ./artifacts
scp -i "$SSH_KEY" \
  "$BUILDER":~/packagemaker-build/android/app/build/outputs/apk/debug/app-debug.apk \
  ./artifacts/package-maker-mobile-debug.apk
sha256sum ./artifacts/package-maker-mobile-debug.apk
```

Para instalarlo en un dispositivo conectado al equipo local:

```bash
adb install -r ./artifacts/package-maker-mobile-debug.apk
```

## Diagnóstico rápido

| Síntoma | Comprobación | Corrección habitual |
|---|---|---|
| `Permission denied (publickey)` | `ssh -vv -i "$SSH_KEY" "$BUILDER"` | Revisar `authorized_keys`, permisos de `~/.ssh` y usuario destino. |
| `SDK location not found` | `cat android/local.properties` | Escribir `sdk.dir` con la ruta absoluta del SDK remoto. |
| `Could not resolve dependencies` | `curl -I https://repo.maven.apache.org` | Permitir salida HTTPS y repetir Gradle. |
| `Manifest merger failed` | `gradle --stacktrace assembleDebug` | Revisar el primer error del log, no solo la última línea. |
| APK no aparece | `find android/app/build -name '*.apk'` | Confirmar que se ejecutó `assembleDebug` dentro de `android`. |

## Limpieza del servidor

Cuando la copia ya no sea necesaria, elimina solo el directorio de trabajo del usuario de compilación:

```bash
ssh -i "$SSH_KEY" "$BUILDER" 'rm -rf ~/packagemaker-build'
```

Conserva los logs y el hash del APK si necesitas trazabilidad de una compilación concreta.
