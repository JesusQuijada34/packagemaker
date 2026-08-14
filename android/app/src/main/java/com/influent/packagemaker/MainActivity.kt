package com.influent.packagemaker

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.util.Base64
import android.webkit.WebResourceRequest
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec
import javax.net.ssl.HttpsURLConnection
import java.net.URL
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.documentfile.provider.DocumentFile
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import java.util.zip.ZipInputStream
import java.util.regex.Pattern
import java.io.ByteArrayOutputStream
import com.jcraft.jsch.ChannelSftp
import com.jcraft.jsch.JSch
import com.jcraft.jsch.Session

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private lateinit var bridge: AndroidBridge
    private val prefs by lazy { getSharedPreferences("packagemaker", Context.MODE_PRIVATE) }
    private val packagePicker = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) bridge.importPackageFromUri(uri)
    }
    private val folderPicker = registerForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri != null) {
            contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            prefs.edit().putString("projects_tree_uri", uri.toString()).apply()
            toast("Carpeta de proyectos configurada en Documentos")
            webView.reload()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        bridge = AndroidBridge(this)
        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            webViewClient = WebViewClient()
            addJavascriptInterface(bridge, "AndroidBridge")
        }
        setContentView(webView)
        webView.loadUrl("file:///android_asset/index.html")
        if (projectsRoot() == null) webView.postDelayed({ chooseProjectsFolder() }, 650)
    }

    private fun chooseProjectsFolder() {
        folderPicker.launch(null)
    }

    private fun choosePackageFile() {
        packagePicker.launch(arrayOf("application/octet-stream", "application/zip", "*/*"))
    }

    private fun projectsRoot(): DocumentFile? {
        val raw = prefs.getString("projects_tree_uri", null) ?: return null
        return try { DocumentFile.fromTreeUri(this, Uri.parse(raw)) } catch (_: Exception) { null }
    }

    private fun projectsFolder(): DocumentFile? {
        val selected = projectsRoot() ?: return null
        return selected.findFile("PackageMaker Projects") ?: selected.createDirectory("PackageMaker Projects")
    }

    private fun toast(message: String) = runOnUiThread { Toast.makeText(this, message, Toast.LENGTH_LONG).show() }

    private data class ApiResponse(val code: Int, val body: String)

    inner class AndroidBridge(private val context: Context) {
        private val buildsDir: File by lazy { File(context.cacheDir, "builds").apply { mkdirs() } }
        private val safeSegment = Pattern.compile("[A-Za-z0-9_-]{1,64}")

        @JavascriptInterface
        fun hasProjectsFolder(): Boolean = projectsFolder() != null

        @JavascriptInterface
        fun openGithubTokenPage() = startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/settings/personal-access-tokens/new")))

        @JavascriptInterface
        fun openProjectPage() = startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/JesusQuijada34/packagemaker")))

        @JavascriptInterface
        fun githubState(): String {
            val token = readGithubToken() ?: return JSONObject().put("connected", false).toString()
            return try {
                val response = githubRequest("/user", "GET", null, token)
                if (response.code in 200..299) JSONObject(response.body).let { JSONObject().put("connected", true).put("login", it.optString("login")).put("avatar", it.optString("avatar_url")) }.toString()
                else JSONObject().put("connected", false).toString()
            } catch (_: Exception) { JSONObject().put("connected", false).toString() }
        }

        @JavascriptInterface
        fun connectGithub(token: String): String {
            val clean = token.trim()
            if (clean.length < 20) return JSONObject().put("ok", false).put("error", "El token parece incompleto").toString()
            return try {
                val response = githubRequest("/user", "GET", null, clean)
                if (response.code !in 200..299) JSONObject().put("ok", false).put("error", "GitHub rechazó el token (${response.code})").toString()
                else { saveGithubToken(clean); val user = JSONObject(response.body); JSONObject().put("ok", true).put("login", user.optString("login")).put("avatar", user.optString("avatar_url")).toString() }
            } catch (e: Exception) { JSONObject().put("ok", false).put("error", e.message ?: "No se pudo conectar con GitHub").toString() }
        }

        @JavascriptInterface
        fun disconnectGithub() { prefs.edit().remove("github_token_enc").remove("github_token_iv").apply() }

        @JavascriptInterface
        fun listGithubRepos(): String {
            val token = readGithubToken() ?: return JSONObject().put("ok", false).put("error", "Conecta GitHub primero").toString()
            return try { val r = githubRequest("/user/repos?per_page=100&sort=updated", "GET", null, token); JSONObject().put("ok", r.code in 200..299).put("repos", if (r.body.startsWith("[")) org.json.JSONArray(r.body) else org.json.JSONArray()).put("error", if (r.code in 200..299) "" else r.body).toString() } catch (e: Exception) { JSONObject().put("ok", false).put("error", e.message ?: "Error de red").toString() }
        }

        @JavascriptInterface
        fun uploadProjectToGithub(folderName: String, ownerRepo: String, branch: String, message: String) {
            runAsync {
                val token = readGithubToken() ?: error("Conecta GitHub primero")
                val folder = projectsFolder()?.findFile(folderName) ?: error("Proyecto no encontrado")
                val repo = ownerRepo.trim().removePrefix("https://github.com/").removeSuffix("/")
                require(repo.matches(Regex("[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"))) { "Repositorio inválido: usa propietario/repositorio" }
                var uploaded = 0
                fun visit(dir: DocumentFile, prefix: String) {
                    dir.listFiles().forEach { child ->
                        val name = child.name ?: return@forEach
                        val path = if (prefix.isEmpty()) name else "$prefix/$name"
                        if (child.isDirectory) visit(child, path) else {
                            val bytes = contentResolver.openInputStream(child.uri)?.use { it.readBytes() } ?: ByteArray(0)
                            val existing = githubRequest("/repos/$repo/contents/${encodePath(path)}?ref=${encodePath(branch)}", "GET", null, token)
                            val payload = JSONObject().put("message", message.ifBlank { "Upload project $folderName" }).put("content", Base64.encodeToString(bytes, Base64.NO_WRAP)).put("branch", branch)
                            if (existing.code in 200..299) payload.put("sha", JSONObject(existing.body).optString("sha"))
                            val response = githubRequest("/repos/$repo/contents/${encodePath(path)}", "PUT", payload.toString(), token)
                            require(response.code in 200..299) { "GitHub rechazó $path (${response.code})" }
                            uploaded++
                        }
                    }
                }
                visit(folder, "")
                notifyAndReload("Proyecto subido a $repo: $uploaded archivos")
            }
        }

        @JavascriptInterface
        fun chooseProjectsFolder() = runOnUiThread { this@MainActivity.chooseProjectsFolder() }

        @JavascriptInterface
        fun importPackage() = runOnUiThread { this@MainActivity.choosePackageFile() }

        fun importPackageFromUri(uri: Uri) {
            runAsync {
                val root = projectsFolder() ?: error("Selecciona primero la carpeta Documentos")
                val input = contentResolver.openInputStream(uri) ?: error("No se pudo abrir el paquete")
                ZipInputStream(input).use { zip ->
                    var entry = zip.nextEntry
                    var project: DocumentFile? = null
                    while (entry != null) {
                        val clean = entry.name.replace('\\', '/')
                        require(!clean.startsWith("/") && !clean.split('/').contains("..")) { "Paquete rechazado por ruta insegura" }
                        val parts = clean.split('/').filter { it.isNotBlank() }
                        if (parts.isNotEmpty()) {
                            if (project == null) project = root.findFile(parts.first()) ?: root.createDirectory(parts.first())
                            var parent = project!!
                            parts.drop(1).dropLast(if (entry.isDirectory) 0 else 1).forEach { part -> parent = parent.findFile(part) ?: parent.createDirectory(part)!! }
                            if (!entry.isDirectory) {
                                val fileName = parts.last()
                                val file = parent.findFile(fileName) ?: parent.createFile("application/octet-stream", fileName)!!
                                contentResolver.openOutputStream(file.uri, "wt")!!.use { out -> zip.copyTo(out) }
                            }
                        }
                        zip.closeEntry(); entry = zip.nextEntry
                    }
                }
                notifyAndReload("Paquete importado en Documentos/PackageMaker Projects")
            }
        }

        @JavascriptInterface
        fun getProjectsLocation(): String = projectsFolder()?.uri?.toString() ?: "No configurada"

        @JavascriptInterface
        fun getProjectsJson(): String {
            val projects = JSONArray()
            projectsFolder()?.listFiles()?.filter { it.isDirectory && it.findFile("details.xml") != null }?.sortedBy { it.name?.lowercase() }?.forEach { dir ->
                projects.put(JSONObject().apply {
                    put("name", dir.name ?: "Proyecto")
                    put("path", dir.uri.toString())
                })
            }
            return JSONObject().put("projects", projects).toString()
        }

        @JavascriptInterface
        fun createProject(publisher: String, appName: String, version: String, author: String, displayName: String, description: String) {
            runAsync {
                val root = projectsFolder() ?: error("Selecciona primero la carpeta Documentos")
                val pub = validateSegment(publisher, "Publisher")
                val app = validateSegment(appName, "ID de aplicación")
                val ver = validateVersion(version)
                val auth = author.trim().ifEmpty { "Usuario" }.take(80)
                val name = displayName.trim().ifEmpty { app.replaceFirstChar { it.uppercase() } }.take(100)
                val folderName = "$pub.$app.v$ver-AlphaCube"
                require(root.findFile(folderName) == null) { "Ya existe el proyecto $folderName" }
                val folder = root.createDirectory(folderName) ?: error("No se pudo crear la carpeta")
                createStructure(folder, pub, app, ver, auth, name, description)
                notifyAndReload("Proyecto creado en Documentos/PackageMaker Projects/$folderName")
            }
        }

        @JavascriptInterface
        fun buildPackage(folderName: String) {
            runAsync {
                val folder = projectsFolder()?.findFile(folderName) ?: error("Proyecto no encontrado")
                val output = File(buildsDir, "${folder.name}.iflapp")
                zipDocumentTree(folder, output)
                val compiled = projectsFolder()?.findFile("Compiled") ?: projectsFolder()?.createDirectory("Compiled")
                val stored = compiled?.findFile(output.name) ?: compiled?.createFile("application/octet-stream", output.name)
                if (stored != null) contentResolver.openOutputStream(stored.uri, "wt")!!.use { FileInputStream(output).use { input -> input.copyTo(it) } }
                notifyAndReload("Paquete generado en Documentos/PackageMaker Projects/Compiled/${output.name}")
            }
        }

        @JavascriptInterface
        fun deleteProject(folderName: String): Boolean {
            val folder = projectsFolder()?.findFile(folderName) ?: return false
            return folder.delete()
        }

        @JavascriptInterface
        fun getProjectFilesJson(folderName: String): String {
            val folder = projectsFolder()?.findFile(folderName) ?: return JSONObject().put("files", JSONArray()).toString()
            val files = JSONArray()
            fun visit(dir: DocumentFile, prefix: String) {
                dir.listFiles().forEach { child ->
                    val name = child.name ?: return@forEach
                    val relative = if (prefix.isEmpty()) name else "$prefix/$name"
                    if (child.isDirectory) visit(child, relative) else files.put(relative)
                }
            }
            visit(folder, "")
            return JSONObject().put("files", files).toString()
        }

        @JavascriptInterface
        fun readProjectFile(folderName: String, relativePath: String): String {
            val file = resolveProjectFile(folderName, relativePath) ?: return ""
            return try { contentResolver.openInputStream(file.uri)?.bufferedReader()?.use { it.readText() } ?: "" } catch (_: Exception) { "" }
        }

        @JavascriptInterface
        fun writeProjectFile(folderName: String, relativePath: String, content: String): Boolean {
            val file = resolveProjectFile(folderName, relativePath) ?: return false
            return try { contentResolver.openOutputStream(file.uri, "wt")!!.use { it.write(content.toByteArray(Charsets.UTF_8)) }; true } catch (_: Exception) { false }
        }

        @JavascriptInterface
        fun remoteBuild(host: String, portText: String, user: String, password: String, remoteDir: String, remoteCommand: String, folderName: String) {
            runAsync {
                val localZip = File(buildsDir, "${File(folderName).name}.iflapp")
                val folder = projectsFolder()?.findFile(folderName) ?: error("Proyecto no encontrado")
                zipDocumentTree(folder, localZip)
                val session = JSch().getSession(user.trim(), host.trim(), portText.toIntOrNull() ?: 22).apply {
                    setPassword(password)
                    setConfig("StrictHostKeyChecking", "no")
                    connect(20_000)
                }
                try {
                    val setup = session.openChannel("exec") as com.jcraft.jsch.ChannelExec
                    setup.setCommand("mkdir -p '$remoteDir'")
                    setup.connect(20_000)
                    while (!setup.isClosed) Thread.sleep(80)
                    require(setup.exitStatus == 0) { "No se pudo crear el directorio remoto" }
                    setup.disconnect()
                    val sftp = session.openChannel("sftp") as ChannelSftp
                    sftp.connect(20_000)
                    try { sftp.put(localZip.absolutePath, "$remoteDir/${localZip.name}") } finally { sftp.disconnect() }
                    val exec = session.openChannel("exec") as com.jcraft.jsch.ChannelExec
                    val command = remoteCommand.trim().ifEmpty { "python3 /opt/packagemaker/packagemaker.py --buildthis source" }
                    exec.setCommand("cd $remoteDir && rm -rf source && mkdir -p source && unzip -o '${localZip.name}' -d source >/dev/null && $command && echo PACKAGE_MAKER_BUILD_OK")
                    exec.connect(20_000)
                    val result = exec.inputStream.bufferedReader().readText()
                    exec.disconnect()
                    require(result.contains("PACKAGE_MAKER_BUILD_OK")) { "La compilación remota no terminó correctamente: $result" }
                    notifyAndReload("Compilación remota completada correctamente.")
                } finally { session.disconnect() }
            }
        }

        @JavascriptInterface
        fun sharePackage(folderName: String) {
            val file = File(buildsDir, "${File(folderName).name}.iflapp")
            if (!file.isFile) { toast("Primero genera el paquete"); return }
            val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
            startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
                type = "application/octet-stream"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }, "Compartir paquete"))
        }

        private fun githubRequest(path: String, method: String, body: String?, token: String): ApiResponse {
            val connection = (URL("https://api.github.com$path").openConnection() as HttpsURLConnection).apply {
                requestMethod = method
                connectTimeout = 20_000; readTimeout = 30_000
                setRequestProperty("Authorization", "Bearer $token")
                setRequestProperty("Accept", "application/vnd.github+json")
                setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
                setRequestProperty("User-Agent", "PackageMaker-Android")
                if (body != null) { doOutput = true; setRequestProperty("Content-Type", "application/json") }
            }
            if (body != null) connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            val stream = if (connection.responseCode >= 400) connection.errorStream else connection.inputStream
            val text = stream?.bufferedReader()?.use { it.readText() } ?: ""
            return ApiResponse(connection.responseCode, text)
        }

        private fun encodePath(path: String) = path.split('/').joinToString("/") { java.net.URLEncoder.encode(it, "UTF-8").replace("+", "%20") }
        private fun saveGithubToken(token: String) {
            val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            if (!keyStore.containsAlias("packagemaker_github")) { val generator = KeyGenerator.getInstance("AES", "AndroidKeyStore"); generator.init(256); generator.generateKey() }
            val key = (keyStore.getEntry("packagemaker_github", null) as KeyStore.SecretKeyEntry).secretKey
            val cipher = Cipher.getInstance("AES/GCM/NoPadding"); cipher.init(Cipher.ENCRYPT_MODE, key)
            prefs.edit().putString("github_token_enc", Base64.encodeToString(cipher.doFinal(token.toByteArray()), Base64.NO_WRAP)).putString("github_token_iv", Base64.encodeToString(cipher.iv, Base64.NO_WRAP)).apply()
        }
        private fun readGithubToken(): String? {
            return try {
                val enc = prefs.getString("github_token_enc", null) ?: return null
                val iv = Base64.decode(prefs.getString("github_token_iv", ""), Base64.DEFAULT)
                val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
                val key = (keyStore.getEntry("packagemaker_github", null) as KeyStore.SecretKeyEntry).secretKey
                val cipher = Cipher.getInstance("AES/GCM/NoPadding")
                cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
                String(cipher.doFinal(Base64.decode(enc, Base64.DEFAULT)), Charsets.UTF_8)
            } catch (_: Exception) { null }
        }

        private fun resolveProjectFile(folderName: String, relativePath: String): DocumentFile? {
            require(relativePath.isNotBlank() && !relativePath.contains("..") && !relativePath.startsWith("/"))
            var current = projectsFolder()?.findFile(folderName) ?: return null
            relativePath.split('/').filter { it.isNotBlank() }.forEach { segment -> current = current.findFile(segment) ?: return null }
            return current
        }

        private fun createStructure(folder: DocumentFile, pub: String, app: String, ver: String, author: String, name: String, description: String) {
            val folders = listOf("app", "assets", "config", "docs", "source", "lib")
            folders.forEach { child ->
                val dir = folder.createDirectory(child) ?: error("No se pudo crear $child")
                writeText(dir, ".$child-container", "PackageMaker container: $child\n")
            }
            val hash = "$pub.$app.$ver".sha256()
            writeText(folder, "details.xml", """<?xml version="1.0" encoding="UTF-8"?>
<app>
  <publisher>$pub</publisher>
  <app>$app</app>
  <name>${xmlEscape(name)}</name>
  <version>v$ver</version>
  <correlationid>$hash</correlationid>
  <rate>Todas las edades</rate>
  <author>${xmlEscape(author)}</author>
  <platform>AlphaCube</platform>
  <description>${xmlEscape(description)}</description>
</app>
""")
            writeText(folder, "$app.py", """# Entry point generado por PackageMaker Mobile

def main():
    print('Proyecto listo para compilar con PackageMaker')

if __name__ == '__main__':
    main()
""")
            writeText(folder, "README.md", "# $name\n\n$description\n\nProyecto creado en Documentos/PackageMaker Projects.\n")
            writeText(folder, "LICENSE", "MIT License\n\nCopyright (c) $author\n")
            writeText(folder, "updater.py", "# Script de actualización generado por PackageMaker\n")
            writeText(folder, "autorun", "#!/bin/sh\npython3 $app.py\n")
            writeText(folder, "autorun.bat", "@echo off\npython $app.py\n")
            writeText(folder, ".storedetail", "<storedetail><correlationid>$hash</correlationid></storedetail>\n")
            writeText(folder, "version.res", "PackageMaker version $ver\n")
            writeText(folder, "manifest.res", "platform=AlphaCube\n")
            writeText(folder.findFile("config")!!, "settings.json", "{\n  \"publisher\": \"$pub\",\n  \"app\": \"$app\",\n  \"version\": \"$ver\",\n  \"platform\": \"AlphaCube\"\n}\n")
            writeText(folder.findFile("lib")!!, "requirements.txt", "# Dependencias del proyecto\n")
            writeText(folder.findFile("docs")!!, "index.html", "<!doctype html><html><body><h1>${xmlEscape(name)}</h1><p>${xmlEscape(description)}</p></body></html>\n")
        }

        private fun writeText(parent: DocumentFile, name: String, text: String) {
            val file = parent.findFile(name) ?: parent.createFile("text/plain", name) ?: error("No se pudo crear $name")
            contentResolver.openOutputStream(file.uri, "wt")!!.use { it.write(text.toByteArray(Charsets.UTF_8)) }
        }

        private fun zipDocumentTree(root: DocumentFile, output: File) {
            ZipOutputStream(BufferedOutputStream(FileOutputStream(output))).use { zip ->
                fun visit(dir: DocumentFile, prefix: String) {
                    dir.listFiles().forEach { child ->
                        val name = child.name ?: return@forEach
                        val entryName = if (prefix.isEmpty()) name else "$prefix/$name"
                        if (child.isDirectory) {
                            zip.putNextEntry(ZipEntry("$entryName/")); zip.closeEntry(); visit(child, entryName)
                        } else {
                            zip.putNextEntry(ZipEntry(entryName))
                            contentResolver.openInputStream(child.uri)?.use { it.copyTo(zip) }
                            zip.closeEntry()
                        }
                    }
                }
                visit(root, "")
            }
        }

        private fun validateSegment(value: String, label: String): String {
            val clean = value.trim()
            require(safeSegment.matcher(clean).matches()) { "$label: usa letras, números, guion o guion bajo" }
            return clean
        }

        private fun validateVersion(value: String): String {
            val clean = value.trim().removePrefix("v")
            require(clean.matches(Regex("[0-9]+\\.[0-9]+\\.[0-9]+"))) { "La versión debe usar formato X.Y.Z" }
            return clean
        }

        private fun xmlEscape(value: String) = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")
        private fun String.sha256(): String = java.security.MessageDigest.getInstance("SHA-256").digest(toByteArray()).joinToString("") { "%02x".format(it) }
        private fun runAsync(task: () -> Unit) { Thread { try { task() } catch (e: Exception) { toast("Error: ${e.message ?: "operación no completada"}") } }.start() }
        private fun notifyAndReload(message: String) { toast(message); runOnUiThread { webView.postDelayed({ webView.reload() }, 250) } }
    }
}
