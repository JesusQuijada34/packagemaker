#include <QApplication>
#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>
#include <QTimer>
#include <QPropertyAnimation>
#include <QCommandLineParser>
#include <QGraphicsDropShadowEffect>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOption({ "title", "Título de la ventana", "title" });
    parser.addOption({ "message", "Mensaje a mostrar", "message" });
    parser.addOption({ "duration", "Duración en segundos", "duration", "10" });
    parser.process(app);

    QString title = parser.value("title");
    QString message = parser.value("message");
    int duration = parser.value("duration").toInt();

    QWidget window;
    window.setWindowTitle(title);
    window.setFixedSize(420, 220);
    window.setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::Tool);

    // Estilo embestido
    QVBoxLayout *layout = new QVBoxLayout(&window);
    layout->setContentsMargins(20, 20, 20, 20);

    QLabel *label = new QLabel(message);
    label->setAlignment(Qt::AlignCenter);
    label->setStyleSheet("font-size: 17px; color: #202124; font-weight: 500;");
    layout->addWidget(label);

    // Sombra embestida
    QGraphicsDropShadowEffect *shadow = new QGraphicsDropShadowEffect();
    shadow->setBlurRadius(25);
    shadow->setOffset(0, 4);
    shadow->setColor(QColor(0, 0, 0, 160));
    window.setGraphicsEffect(shadow);

    // Animación estilo boom
    QPropertyAnimation *anim = new QPropertyAnimation(&window, "windowOpacity");
    anim->setDuration(800);
    anim->setStartValue(0.0);
    anim->setEndValue(1.0);
    anim->start();

    // Posición en esquina inferior derecha
    QRect screen = QApplication::primaryScreen()->availableGeometry();
    int x = screen.width() - window.width() - 50;
    int y = screen.height() - window.height() - 50;
    window.move(x, y);

    window.show();

    // Cierre automático
    QTimer::singleShot(duration * 1000, &app, SLOT(quit()));
    return app.exec();
}
