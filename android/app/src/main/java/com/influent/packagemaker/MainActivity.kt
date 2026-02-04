package com.influent.packagemaker

import android.annotation.SuppressLint
import android.content.Context
import android.os.Bundle
import android.os.Environment
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.*
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        
        // Register the bridge
        webView.addJavascriptInterface(WebAppInterface(this), "AndroidBridge")
        
        setContentView(webView)
        webView.loadUrl("file:///android_asset/index.html")
    }

    inner class WebAppInterface(private val context: Context) {

        private val baseDir: File by lazy {
            File(context.getExternalFilesDir(null), "IPM_Projects").apply {
                if (!exists()) mkdirs()
            }
        }

        @JavascriptInterface
        fun getProjectsJson(): String {
            val list = mutableListOf<Map<String, String>>()
            baseDir.listFiles()?.filter { it.isDirectory }?.forEach { dir ->
                val details = File(dir, "details.xml")
                if (details.exists()) {
                    list.add(mapOf("name" to dir.name, "path" to dir.absolutePath))
                }
            }
            return JSONObject(mapOf("projects" to list)).toString()
        }

        @JavascriptInterface
        fun createProject(publisher: String, appName: String, version: String, author: String) {
            try {
                val folderName = "${publisher}.${appName}.v${version}"
                val projectDir = File(baseDir, folderName)
                
                // Create structure
                val subdirs = listOf("app", "assets", "lib", "config", "docs")
                subdirs.forEach { File(projectDir, it).mkdirs() }

                // Write details.xml
                val xml = """
                    <app>
                        <publisher>$publisher</publisher>
                        <app>$appName</app>
                        <name>${appName.uppercase()}</name>
                        <version>$version</version>
                        <author>$author</author>
                        <platform>Android</platform>
                    </app>
                """.trimIndent()
                
                File(projectDir, "details.xml").writeText(xml)
                File(projectDir, "$appName.py").writeText("# Main Script for $appName\ndef main():\n    print('Hello from Android')")
                File(projectDir, "README.md").writeText("# $appName\nProject generated on Android.")

                runOnUiThread {
                    Toast.makeText(context, "Proyecto Creado: $folderName", Toast.LENGTH_SHORT).show()
                    webView.reload()
                }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show() }
            }
        }

        @JavascriptInterface
        fun buildPackage(folderName: String) {
            try {
                val sourceDir = File(baseDir, folderName)
                val outDir = File(context.getExternalFilesDir(null), "IPM_Builds").apply { if(!exists()) mkdirs() }
                val zipFile = File(outDir, "${folderName}.iflapp.zip")
                
                zipDirectory(sourceDir, zipFile)
                
                runOnUiThread {
                    Toast.makeText(context, "Paquete Generado: ${zipFile.name}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(context, "Error de Compilación: ${e.message}", Toast.LENGTH_LONG).show() }
            }
        }

        private fun zipDirectory(sourceDir: File, outputFile: File) {
            ZipOutputStream(BufferedOutputStream(FileOutputStream(outputFile))).use { zos ->
                sourceDir.walkTopDown().forEach { file ->
                    val zipFileName = file.absolutePath.removePrefix(sourceDir.absolutePath).removePrefix(File.separator)
                    if (zipFileName.isNotEmpty()) {
                        val entry = ZipEntry("$zipFileName${if (file.isDirectory) "/" else ""}")
                        zos.putNextEntry(entry)
                        if (file.isFile) {
                            file.inputStream().use { it.copyTo(zos) }
                        }
                    }
                }
            }
        }
        
        @JavascriptInterface
        fun showToast(msg: String) {
            Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
        }
    }
}
