using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.NetworkInformation;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using Windows.UI;

namespace PackagemakerUWP
{
    public sealed partial class MainWindow : Window
    {
        private static readonly string[] DEFAULT_FOLDERS = { "app", "assets", "config", "docs", "source", "lib" };
        
        private static readonly Dictionary<string, string> AGE_RATINGS = new()
        {
            { "adult", "ADULTS ONLY" },
            { "kids", "FOR KIDS" },
            { "social", "PUBLIC CONTENT" },
            { "ai", "PUBLIC ALL" },
            { "default", "EVERYONE" }
        };

        public MainWindow()
        {
            this.InitializeComponent();
            CheckConnectionStatus();
        }

        private async void CheckConnectionStatus()
        {
            try
            {
                bool isConnected = await CheckInternetConnection();
                if (isConnected)
                {
                    ConnectionStatusText.Text = "Conexión: ONLINE";
                    ConnectionStatusIndicator.Fill = new SolidColorBrush(Colors.Green);
                }
                else
                {
                    ConnectionStatusText.Text = "Conexión: OFFLINE (Usando Fallback)";
                    ConnectionStatusIndicator.Fill = new SolidColorBrush(Colors.Orange);
                }
            }
            catch
            {
                ConnectionStatusText.Text = "Conexión: OFFLINE (Usando Fallback)";
                ConnectionStatusIndicator.Fill = new SolidColorBrush(Colors.Orange);
            }
        }

        private async Task<bool> CheckInternetConnection()
        {
            try
            {
                bool networkAvailable = await Task.Run(() => NetworkInterface.GetIsNetworkAvailable());
                
                if (!networkAvailable)
                {
                    return false;
                }
                
                // Verificación adicional con ping
                var ping = new Ping();
                try
                {
                    var reply = await ping.SendPingAsync("8.8.8.8", 3000);
                    return reply.Status == System.Net.NetworkInformation.IPStatus.Success;
                }
                catch
                {
                    return false;
                }
            }
            catch
            {
                return false;
            }
        }

        private async void CreateButton_Click(object sender, RoutedEventArgs e)
        {
            string empresa = EmpresaTextBox.Text.Trim();
            string nombreLogico = NombreLogicoTextBox.Text.Trim();
            string nombreCompleto = NombreCompletoTextBox.Text.Trim();
            string version = VersionTextBox.Text.Trim();

            if (string.IsNullOrWhiteSpace(empresa) || 
                string.IsNullOrWhiteSpace(nombreLogico) || 
                string.IsNullOrWhiteSpace(nombreCompleto) || 
                string.IsNullOrWhiteSpace(version))
            {
                await ShowMessageDialog("Datos Incompletos", "Por favor, complete todos los campos.");
                return;
            }

            try
            {
                string baseDir = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "Influent Packages");
                string projectDir = Path.Combine(baseDir, nombreLogico);

                // Verificar si el proyecto ya existe
                if (Directory.Exists(projectDir))
                {
                    var dialog = new ContentDialog
                    {
                        Title = "Proyecto Existente",
                        Content = $"El proyecto '{nombreLogico}' ya existe. ¿Desea sobrescribirlo?",
                        PrimaryButtonText = "Sí",
                        SecondaryButtonText = "No",
                        XamlRoot = this.Content.XamlRoot
                    };

                    var result = await dialog.ShowAsync();
                    if (result != ContentDialogResult.Primary)
                    {
                        return;
                    }

                    Directory.Delete(projectDir, true);
                }

                // Crear estructura del proyecto
                Directory.CreateDirectory(projectDir);
                await CreatePackageStructure(projectDir, empresa, nombreLogico, nombreCompleto, version);

                await ShowMessageDialog("Éxito", 
                    $"Estructura del proyecto '{nombreLogico}' creada en:\n{projectDir}");
            }
            catch (Exception ex)
            {
                await ShowMessageDialog("Error de Creación", $"Fallo al crear el proyecto: {ex.Message}");
            }
        }

        private async Task CreatePackageStructure(string fullPath, string empresa, string nombreLogico, 
            string nombreCompleto, string version)
        {
            // Crear carpetas
            foreach (string folder in DEFAULT_FOLDERS)
            {
                Directory.CreateDirectory(Path.Combine(fullPath, folder));
            }

            // Archivo principal .py
            string mainScript = Path.Combine(fullPath, $"{nombreLogico}.py");
            string pythonCode = $@"# -*- coding: utf-8 -*-
# Script principal para el paquete {nombreLogico}
import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel('¡Hola desde {nombreLogico}! Paquete .iflapp creado con éxito.')
label.show()
sys.exit(app.exec_())
";
            await File.WriteAllTextAsync(mainScript, pythonCode);

            // Archivo README.md
            string readmePath = Path.Combine(fullPath, "README.md");
            string readmeContent = $@"# Paquete: {nombreCompleto}

Creado por: {empresa}
Versión: v{version}

Este es un paquete modular .iflapp de Influent Package Maker.
";
            await File.WriteAllTextAsync(readmePath, readmeContent);

            // Archivo requirements.txt
            string requirementsPath = Path.Combine(fullPath, "lib", "requirements.txt");
            await File.WriteAllTextAsync(requirementsPath, "PyQt5\n");

            // Crear details.xml
            await CreateDetailsXml(fullPath, empresa, nombreLogico, nombreCompleto, version);
        }

        private async Task CreateDetailsXml(string path, string empresa, string nombreLogico, 
            string nombreCompleto, string version)
        {
            string newVersion = DateTime.Now.ToString("yy.MM-HH.mm");
            string capitalizedEmpresa = char.ToUpper(empresa[0]) + empresa.Substring(1).ToLower();
            string fullName = $"{capitalizedEmpresa}.{nombreLogico}.v{version}";
            string hashVal = ComputeSHA256(fullName);
            string rating = GetAgeRating(nombreLogico, nombreCompleto);

            var xml = new XElement("app",
                new XElement("publisher", capitalizedEmpresa),
                new XElement("app", nombreLogico),
                new XElement("name", nombreCompleto),
                new XElement("version", $"v{version}"),
                new XElement("platform", "win32"),
                new XElement("danenone", newVersion),
                new XElement("correlationid", hashVal),
                new XElement("rate", rating)
            );

            string xmlPath = Path.Combine(path, "details.xml");
            XDocument doc = new XDocument(new XDeclaration("1.0", "utf-8", null), xml);
            await File.WriteAllTextAsync(xmlPath, doc.ToString());
        }

        private string ComputeSHA256(string input)
        {
            using (SHA256 sha256 = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(input);
                byte[] hash = sha256.ComputeHash(bytes);
                return BitConverter.ToString(hash).Replace("-", "").ToLower();
            }
        }

        private string GetAgeRating(string name, string title)
        {
            string searchString = (name + title).ToLower();
            foreach (var kvp in AGE_RATINGS)
            {
                if (searchString.Contains(kvp.Key))
                {
                    return kvp.Value;
                }
            }
            return AGE_RATINGS["default"];
        }

        private async Task ShowMessageDialog(string title, string message)
        {
            var dialog = new ContentDialog
            {
                Title = title,
                Content = message,
                CloseButtonText = "OK",
                XamlRoot = this.Content.XamlRoot
            };

            await dialog.ShowAsync();
        }
    }
}

